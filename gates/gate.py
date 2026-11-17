#!/usr/bin/env python3
"""agentic-dev-kit gate runner.

Deterministic checks decide whether work passes, not an agent's say-so.

    gate.py run --stage pre-commit|pre-push|ci [--only ID ...] [--list]
    gate.py lock-tests --by test-designer|adversary
    gate.py list [--stage STAGE]
    gate.py print-stacks

Steps come from gates/profiles/<stack>.toml for every stack in .agentic/config.toml, from
agents/domains/<id>/gates.toml for every enabled domain, and from built-in checks. Results
are written to .agentic/reports/gate-latest.{json,md}. Exit code 0 = pass, 1 = fail.
Standard library only (Python 3.11+).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    sys.exit("gate.py needs Python 3.11 or newer (tomllib).")

KIT = Path(__file__).resolve().parents[1]
STAGES = ("pre-commit", "pre-push", "ci")
LOCK_ROLES = ("test-designer", "adversary")
# Generated or vendored content is never scanned by the built-in checks.
EXCLUDE_PREFIXES = (
    ".agentic/kit/", ".agentic/prompts/", ".agentic/reports/", ".claude/agents/", ".claude/skills/",
    ".github/agents/", ".github/skills/", ".cursor/rules/", "node_modules/", "target/", "build/",
    "bin/", "obj/", "dist/", ".venv/", "vendor/",
)
AC_ID = re.compile(r"\b([A-Z][A-Z0-9]*-AC-\d+)\b")
DEBUG_TAG = re.compile(r"DEBUG-[0-9a-fA-F]{4}\b")
ADVERSARIAL_MARKERS = ("/adversarial/", "/security/", "/regression/", "_adversarial_test",
                       "_regression_test", ".adversarial.test.")
SECRET_PATTERNS = [
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36}\b|\bgithub_pat_[A-Za-z0-9_]{60,}\b")),
    ("slack-token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("llm-api-key", re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("assigned-secret", re.compile(
        r"(?i)\b(?:api[_-]?key|secret|passwd|password|token|client[_-]?secret)\b\s*[:=]\s*['\"][^'\"\s]{12,}['\"]")),
]


# --------------------------------------------------------------------------- helpers

def find_root() -> Path:
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=True).stdout.strip()
        return Path(out)
    except (OSError, subprocess.CalledProcessError):
        return Path.cwd()


def git(root: Path, *args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def glob_regex(pattern: str) -> re.Pattern[str]:
    """Translate a glob with ** support into a regex over posix paths."""
    out, i = "", 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif pattern.startswith("**", i):
            out, i = out + ".*", i + 2
        elif pattern[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif pattern[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(pattern[i]), i + 1
    return re.compile("^" + out + "$")


def matches(path: str, globs: list[str]) -> bool:
    return any(glob_regex(g).match(path) for g in globs)


def list_files(root: Path) -> list[str]:
    listing = git(root, "ls-files", "-co", "--exclude-standard")
    if listing:
        files = listing.splitlines()
    else:
        files = [p.relative_to(root).as_posix() for p in root.rglob("*")
                 if p.is_file() and ".git" not in p.parts]
    return sorted(f for f in set(files) if (root / f).is_file())


def scannable(files: list[str]) -> list[str]:
    return [f for f in files if not f.startswith(EXCLUDE_PREFIXES)]


def read_text(path: Path, limit: int = 1_000_000) -> str | None:
    try:
        if path.stat().st_size > limit:
            return None
        data = path.read_bytes()
    except OSError:
        return None
    if b"\0" in data[:8192]:
        return None
    return data.decode("utf-8", errors="replace")


def normalized_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def quote(arg: str) -> str:
    if os.name == "nt":
        return subprocess.list2cmdline([arg])
    import shlex
    return shlex.quote(arg)


# --------------------------------------------------------------------------- config

@dataclass
class Step:
    id: str
    name: str
    category: str = "check"
    cmd: str = ""
    stages: list[str] = field(default_factory=lambda: list(STAGES))
    optional: bool = False          # skip (with a warning) when the tool is missing
    advisory: bool = False          # report failures but never fail the gate
    when_files: list[str] = field(default_factory=list)
    requires_paths: list[str] = field(default_factory=list)
    tool: str = ""
    fail_on_output: bool = False
    fail_on_match: str = ""
    timeout: int = 1800
    install: str = ""
    replaces: str = ""              # id of a profile step this one takes the place of
    builtin: object = None


@dataclass
class Config:
    root: Path
    stacks: list[str]
    domains: list[str]
    test_globs: list[str]
    skip: list[str]
    overrides: dict
    steps: list[Step]
    roles: dict = field(default_factory=dict)
    base_branch: str = "main"


def load_config(root: Path) -> Config:
    path = root / ".agentic" / "config.toml"
    data = tomllib.loads(path.read_text("utf-8")) if path.exists() else {}
    project = data.get("project", {})
    stacks, domains = list(project.get("stacks", [])), list(project.get("domains", []))
    standards = list(project.get("standards", []))
    gate_cfg = data.get("gate", {})
    test_globs = list(data.get("tests", {}).get("globs", []))
    steps: list[Step] = []
    seen_cmds: set[str] = set()

    def add(prefix: str, raw: dict) -> None:
        known = Step.__dataclass_fields__
        st = Step(id=f"{prefix}:{raw['name']}", **{k: v for k, v in raw.items() if k in known and k != "id"})
        if st.cmd and st.cmd in seen_cmds:   # e.g. javascript + typescript both run prettier
            return
        seen_cmds.add(st.cmd)
        steps.append(st)

    for stack in stacks:
        prof = KIT / "gates" / "profiles" / f"{stack}.toml"
        if not prof.exists():
            print(f"warning: no gate profile for stack '{stack}' ({prof})", file=sys.stderr)
            continue
        pdata = tomllib.loads(prof.read_text("utf-8"))
        test_globs += pdata.get("test_globs", [])
        for raw in pdata.get("step", []):
            add(stack, raw)
    for dom in domains:
        gfile = KIT / "agents" / "domains" / dom / "gates.toml"
        if gfile.exists():
            for raw in tomllib.loads(gfile.read_text("utf-8")).get("step", []):
                add(dom, raw)
    for pack in standards:
        gfile = KIT / "standards" / pack / "gates.toml"
        if gfile.exists():
            for raw in tomllib.loads(gfile.read_text("utf-8")).get("step", []):
                add(pack, raw)

    replaced = {s.replaces for s in steps if s.replaces}
    steps = builtin_steps() + [s for s in steps if s.id not in replaced]
    overrides = gate_cfg.get("overrides", {})
    for st in steps:
        ov = overrides.get(st.id)
        if isinstance(ov, str):
            st.cmd = ov
        elif isinstance(ov, dict):
            for k, v in ov.items():
                if k in Step.__dataclass_fields__ and k not in ("id", "builtin", "replaces"):
                    setattr(st, k, v)
    return Config(root, stacks, domains, sorted(set(test_globs)), list(gate_cfg.get("skip", [])),
                  overrides, steps, roles=data.get("roles", {}),
                  base_branch=gate_cfg.get("base_branch", "main"))


# --------------------------------------------------------------------------- built-in checks

def check_secrets(cfg: Config, files: list[str]) -> tuple[bool, str]:
    if shutil.which("gitleaks"):
        proc = subprocess.run(["gitleaks", "detect", "--no-banner", "--redact", "--source", str(cfg.root)],
                              capture_output=True, text=True, errors="replace")
        return proc.returncode == 0, (proc.stdout + proc.stderr)[-4000:] or "gitleaks: clean"
    hits = []
    for f in scannable(files):
        text = read_text(cfg.root / f)
        if text is None:
            continue
        for no, line in enumerate(text.splitlines(), 1):
            if "agentic:allow-secret" in line:
                continue
            for label, rx in SECRET_PATTERNS:
                if rx.search(line):
                    hits.append(f"{f}:{no}: possible {label}")
    if hits:
        return False, "\n".join(hits[:100]) + "\nMark a false positive with 'agentic:allow-secret' on the line."
    return True, "regex scan: clean (install gitleaks for a stronger scan)"


def check_debug_tags(cfg: Config, files: list[str]) -> tuple[bool, str]:
    hits = []
    for f in scannable(files):
        if f.endswith((".md", ".markdown", ".txt")):
            continue
        text = read_text(cfg.root / f)
        if text is None:
            continue
        for no, line in enumerate(text.splitlines(), 1):
            if DEBUG_TAG.search(line):
                hits.append(f"{f}:{no}: {line.strip()[:120]}")
    return (not hits), ("\n".join(hits) if hits else "no temporary debug tags")


def lock_path(root: Path) -> Path:
    return root / ".agentic" / "locks" / "tests.lock.json"


def lockable_tests(cfg: Config, files: list[str]) -> list[str]:
    """Acceptance and adversarial tests: test files that name an AC id or live in an adversarial area."""
    out = []
    for f in scannable(files):
        if not matches(f, cfg.test_globs):
            continue
        if any(m in f"/{f}" for m in ADVERSARIAL_MARKERS):
            out.append(f)
            continue
        text = read_text(cfg.root / f) or ""
        if AC_ID.search(text) or re.search(r"(?i)(?<![a-z0-9])[a-z][a-z0-9]*_ac_\d+", text):
            out.append(f)
    return out


def check_test_lock(cfg: Config, files: list[str]) -> tuple[bool, str]:
    lp = lock_path(cfg.root)
    if not lp.exists():
        return True, "no locked tests yet"
    lock = json.loads(lp.read_text("utf-8"))
    problems = []
    for rel, digest in sorted(lock.get("files", {}).items()):
        p = cfg.root / rel
        if not p.exists():
            problems.append(f"{rel}: locked test was deleted")
        elif normalized_hash(p) != digest:
            problems.append(f"{rel}: locked test was modified")
    if problems:
        return False, "\n".join(problems) + (
            "\nLocked tests change only through test-designer or adversary, who re-lock with "
            "`gate.py lock-tests --by <role>` and explain why in a handoff.")
    return True, f"{len(lock.get('files', {}))} locked test file(s) intact"


def check_trace(cfg: Config, files: list[str]) -> tuple[bool, str]:
    spec_dir = cfg.root / ".agentic" / "specs"
    ids: dict[str, str] = {}
    for spec in sorted(spec_dir.glob("*.md")) if spec_dir.exists() else []:
        if spec.name.endswith(".design.md"):
            continue
        text = spec.read_text("utf-8", errors="replace")
        status = re.search(r"(?im)^status:\s*([a-z-]+)", text)
        if not status or status.group(1) not in ("approved", "implemented"):
            continue
        for ac in AC_ID.findall(text):
            ids.setdefault(ac, spec.name)
    if not ids:
        return True, "no approved specs with acceptance criteria"
    corpus = "\n".join(read_text(cfg.root / f) or "" for f in scannable(files) if matches(f, cfg.test_globs))
    missing = []
    for ac, spec in sorted(ids.items()):
        flexible = r"[-_]".join(map(re.escape, ac.split("-")))
        if not re.search(rf"(?i)(?<![a-z0-9]){flexible}(?![0-9])", corpus):
            missing.append(f"{ac} ({spec}): no test names this criterion")
    if missing:
        return False, "\n".join(missing)
    return True, f"{len(ids)} acceptance criteria traced to tests"


# Paths that decide what "passing" means, or record verdicts. A role may change them only when
# its writes list names them explicitly. A catch-all "**" doesn't count.
PROTECTED = [
    ".agentic/kit/**", ".agentic/locks/**", ".agentic/config.toml", ".agentic/CODING_STANDARDS.md",
    ".agentic/GLOSSARY.md", ".agentic/specs/**", ".agentic/decisions/**", ".agentic/findings/**",
    ".github/workflows/**", ".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS",
    ".github/dependabot.yml", ".claude/settings.json", ".devcontainer/**",
]
# Every role keeps the shared state current (the handoff skill requires it).
UNIVERSAL = [".agentic/STATE.md", ".agentic/tasks/**", ".agentic/handoffs/**"]


def role_writes(cfg: Config) -> dict[str, list[str]]:
    sys.path.insert(0, str(KIT / "adapters"))
    from build import parse_doc  # noqa: E402  (kit-local module)
    files = sorted((KIT / "agents" / "core").glob("*.md"))
    files += [KIT / "agents" / "domains" / d / "agent.md" for d in cfg.domains]
    roles = {}
    for f in files:
        if f.exists():
            meta = parse_doc(f).meta
            roles[meta["id"]] = list(meta.get("writes", []))
    # The headless runner commits only the shared state it maintains (Spend rows, budget blocks),
    # which UNIVERSAL already covers.
    roles.setdefault("runner", [])
    for rid, extra in cfg.roles.items():
        roles.setdefault(rid, []).extend(extra.get("writes", []))
    return roles


def literal_prefix(pattern: str) -> str:
    """The part of a glob before its first wildcard, e.g. '.agentic/locks/' for '.agentic/locks/**'."""
    return re.split(r"[*?\[]", pattern, maxsplit=1)[0]


def allowed(path: str, patterns: list[str]) -> bool:
    if matches(path, UNIVERSAL):
        return True
    explicit = [p for p in patterns if p != "**"]
    guards = [g for g in PROTECTED if matches(path, [g])]
    if guards:
        # A protected path is granted only by a pattern that names its protected location, so a
        # broad grant like "docs/**" never reaches docs/CODEOWNERS.
        return any(matches(path, [p]) and p.startswith(literal_prefix(g)) for p in explicit for g in guards)
    return "**" in patterns or matches(path, explicit)


def scope_base(cfg: Config) -> str:
    candidates = [os.environ.get("AGENTIC_BASE", "")]
    if os.environ.get("GITHUB_BASE_REF"):
        candidates.append(f"origin/{os.environ['GITHUB_BASE_REF']}")
    branch = cfg.base_branch
    candidates += [f"origin/{branch}", branch]
    for ref in filter(None, candidates):
        base = git(cfg.root, "merge-base", "HEAD", ref)
        if base:
            return base
    return ""


def check_scope(cfg: Config, files: list[str]) -> tuple[bool, str]:
    base = scope_base(cfg)
    if not base:
        return True, f"no merge-base with '{cfg.base_branch}'; scope not checked"
    roles = role_writes(cfg)
    shas = git(cfg.root, "rev-list", "--no-merges", f"{base}..HEAD").split()
    problems, checked = [], 0
    for sha in shas:
        role = git(cfg.root, "log", "-1", "--format=%(trailers:key=Agent-Role,valueonly)", sha).strip()
        role = role.splitlines()[0].strip() if role else ""
        if not role:
            continue  # a human commit; humans are governed by CODEOWNERS and review
        checked += 1
        if role not in roles:
            problems.append(f"{sha[:10]}: unknown Agent-Role '{role}'")
            continue
        changed = git(cfg.root, "diff-tree", "--no-commit-id", "--name-only", "-r", sha).splitlines()
        for path in changed:
            if not allowed(path, roles[role]):
                problems.append(f"{sha[:10]} ({role}): {path} is outside this role's writes")
    if problems:
        return False, "\n".join(problems) + (
            "\nMove the change to the role that owns it, or (humans only) extend the role in "
            ".agentic/config.toml [roles.<id>] writes.")
    return True, f"{checked} agent commit(s) since {base[:10]} within their role scopes"


def builtin_steps() -> list[Step]:
    return [
        Step(id="builtin:secrets", name="secrets", category="security", builtin=check_secrets),
        Step(id="builtin:debug-tags", name="debug-tags", category="hygiene", builtin=check_debug_tags),
        Step(id="builtin:test-lock", name="test-lock", category="integrity", builtin=check_test_lock),
        Step(id="builtin:trace", name="trace", category="integrity", stages=["pre-push", "ci"],
             builtin=check_trace),
        Step(id="builtin:scope", name="scope", category="integrity", stages=["pre-push", "ci"],
             builtin=check_scope),
    ]


# --------------------------------------------------------------------------- running

class NoFiles(Exception):
    pass


def expand(cmd: str, files: list[str]) -> str:
    def rep(m: re.Match[str]) -> str:
        globs = [g.strip() for g in m.group(1).split(",") if g.strip()]
        hit = [f for f in scannable(files) if matches(f, globs)]
        if not hit:
            raise NoFiles
        return " ".join(quote(f) for f in hit)
    cmd = cmd.replace("{python}", quote(sys.executable)).replace("{kit}", quote(KIT.as_posix()))
    return re.sub(r"\{files:([^}]*)\}", rep, cmd)


def tool_of(step: Step) -> str:
    if step.tool:
        return step.tool
    first = step.cmd.split()[0] if step.cmd.split() else ""
    return "" if first.startswith("{") else first


def run_step(cfg: Config, step: Step, files: list[str]) -> dict:
    res = {"id": step.id, "category": step.category, "advisory": step.advisory}
    if step.id in cfg.skip:
        return res | {"status": "skip", "detail": "skipped in .agentic/config.toml [gate].skip"}
    if step.when_files and not any(matches(f, step.when_files) for f in files):
        return res | {"status": "skip", "detail": "no matching files"}
    missing = [p for p in step.requires_paths if not (cfg.root / p).exists()]
    if missing:
        return res | {"status": "skip", "detail": f"missing {', '.join(missing)}"}
    if step.builtin:
        ok, detail = step.builtin(cfg, files)
        return res | {"status": "pass" if ok else "fail", "detail": detail}
    tool = tool_of(step)
    if tool and not shutil.which(tool):
        hint = f" (install: {step.install})" if step.install else ""
        status = "skip" if step.optional else "fail"
        return res | {"status": status, "detail": f"tool not found: {tool}{hint}"}
    try:
        cmd = expand(step.cmd, files)
    except NoFiles:
        return res | {"status": "skip", "detail": "no matching files"}
    started = dt.datetime.now()
    try:
        proc = subprocess.run(cmd, shell=True, cwd=cfg.root, stdout=subprocess.PIPE,
                              stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                              errors="replace", timeout=step.timeout)
        output, code = proc.stdout or "", proc.returncode
    except subprocess.TimeoutExpired as exc:
        output, code = f"timed out after {step.timeout}s\n{exc.output or ''}", 124
    ok = code == 0
    if ok and step.fail_on_output and output.strip():
        ok = False
    if ok and step.fail_on_match and re.search(step.fail_on_match, output):
        ok = False
    return res | {"status": "pass" if ok else "fail", "cmd": cmd, "exit": code,
                  "seconds": round((dt.datetime.now() - started).total_seconds(), 1),
                  "detail": output[-4000:]}


def write_report(cfg: Config, stage: str, results: list[dict], passed: bool) -> Path:
    out_dir = cfg.root / ".agentic" / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    head = git(cfg.root, "rev-parse", "HEAD")
    dirty = bool(git(cfg.root, "status", "--porcelain", "--untracked-files=no"))
    report = {"stage": stage, "result": "pass" if passed else "fail", "head": head, "dirty": dirty,
              "time": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
              "stacks": cfg.stacks, "domains": cfg.domains, "results": results}
    (out_dir / "gate-latest.json").write_text(json.dumps(report, indent=2), "utf-8")
    lines = [f"# Gate report: {report['result'].upper()}", "",
             f"- Stage: `{stage}`  ", f"- Commit: `{head[:12] or 'n/a'}`{' (dirty tree)' if dirty else ''}  ",
             f"- Time: {report['time']}", "", "| Step | Status | Detail |", "|---|---|---|"]
    for r in results:
        status = r["status"] + (" (advisory)" if r.get("advisory") and r["status"] == "fail" else "")
        first = (r.get("detail") or "").strip().splitlines()
        lines.append(f"| `{r['id']}` | {status} | {(first[-1] if first else '')[:100].replace('|', '/')} |")
    failures = [r for r in results if r["status"] == "fail"]
    for r in failures:
        lines += ["", f"## {r['id']}", "```", (r.get("detail") or "").strip()[-3000:], "```"]
    path = out_dir / "gate-latest.md"
    path.write_text("\n".join(lines) + "\n", "utf-8")
    return path


def cmd_run(args: argparse.Namespace) -> int:
    root = find_root()
    cfg = load_config(root)
    files = list_files(root)
    steps = [s for s in cfg.steps if args.stage in s.stages]
    if args.only:
        steps = [s for s in cfg.steps if s.id in args.only]
        unknown = set(args.only) - {s.id for s in steps}
        if unknown:
            print(f"unknown step id(s): {', '.join(sorted(unknown))}", file=sys.stderr)
            return 2
    if not cfg.stacks:
        print("warning: no stacks configured in .agentic/config.toml; only built-in checks run.", file=sys.stderr)
    results, passed = [], True
    print(f"gate: stage={args.stage} steps={len(steps)} root={root}")
    for st in steps:
        r = run_step(cfg, st, files)
        results.append(r)
        mark = {"pass": "PASS", "fail": "FAIL", "skip": "skip"}[r["status"]]
        if r["status"] == "fail" and st.advisory:
            mark = "WARN"
        elif r["status"] == "fail":
            passed = False
        print(f"  [{mark}] {st.id}" + (f"  ({r['detail'].splitlines()[0][:90]})" if r["status"] == "skip" else ""))
        if r["status"] == "fail":
            tail = (r.get("detail") or "").strip().splitlines()[-15:]
            print("\n".join("        " + t for t in tail))
    report = write_report(cfg, args.stage, results, passed)
    print(f"gate: {'PASS' if passed else 'FAIL'} - report {report.relative_to(root).as_posix()}")
    return 0 if passed else 1


def cmd_lock(args: argparse.Namespace) -> int:
    root = find_root()
    cfg = load_config(root)
    files = list_files(root)
    if not cfg.test_globs:
        print("no test globs configured (stacks or [tests].globs in .agentic/config.toml)", file=sys.stderr)
        return 2
    lp = lock_path(root)
    old = json.loads(lp.read_text("utf-8")).get("files", {}) if lp.exists() else {}
    new = {f: normalized_hash(root / f) for f in lockable_tests(cfg, files)}
    # A file stays locked even if its AC marker disappeared, unless it was deleted on purpose.
    for rel in old:
        if rel not in new and (root / rel).exists():
            new[rel] = normalized_hash(root / rel)
    added = sorted(set(new) - set(old))
    changed = sorted(f for f in set(new) & set(old) if new[f] != old[f])
    removed = sorted(set(old) - set(new))
    lp.parent.mkdir(parents=True, exist_ok=True)
    lp.write_text(json.dumps({
        "locked_by": args.by,
        "locked_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "head": git(root, "rev-parse", "HEAD"),
        "files": dict(sorted(new.items())),
    }, indent=2) + "\n", "utf-8")
    print(f"locked {len(new)} test file(s) by {args.by}: +{len(added)} ~{len(changed)} -{len(removed)}")
    for label, items in (("added", added), ("changed", changed), ("removed", removed)):
        for f in items:
            print(f"  {label}: {f}")
    if changed or removed:
        print("Record why locked tests changed in your handoff note.")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    cfg = load_config(find_root())
    for st in cfg.steps:
        if args.stage and args.stage not in st.stages:
            continue
        tool = "" if st.builtin else tool_of(st)
        avail = "builtin" if st.builtin else ("ok" if not tool or shutil.which(tool) else "MISSING")
        flags = ",".join(f for f, on in (("optional", st.optional), ("advisory", st.advisory)) if on)
        print(f"{st.id:40} {'/'.join(st.stages):24} tool={tool or '-'}:{avail} {flags}")
    print(f"test globs: {', '.join(cfg.test_globs) or '(none)'}")
    return 0


def cmd_stacks(_: argparse.Namespace) -> int:
    print(",".join(load_config(find_root()).stacks))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="gate.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="command", required=True)
    r = sub.add_parser("run", help="run the gate for a stage")
    r.add_argument("--stage", choices=STAGES, default="pre-push")
    r.add_argument("--only", nargs="+", metavar="ID", help="run only these step ids")
    r.set_defaults(func=cmd_run)
    lk = sub.add_parser("lock-tests", help="lock acceptance/adversarial tests")
    lk.add_argument("--by", choices=LOCK_ROLES, required=True)
    lk.set_defaults(func=cmd_lock)
    ls = sub.add_parser("list", help="list configured steps and tool availability")
    ls.add_argument("--stage", choices=STAGES)
    ls.set_defaults(func=cmd_list)
    ps = sub.add_parser("print-stacks", help="print configured stacks (for CI)")
    ps.set_defaults(func=cmd_stacks)
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
