#!/usr/bin/env python3
"""Install or update agentic-dev-kit in a project.

    install.py --target PATH --stacks python,rust [--domains aerospace-engineer]
               [--standards python-pep8,rust-api-guidelines]
               [--tools claude,copilot,cursor,gemini,generic] [--no-hooks] [--no-ci]
    install.py --target PATH --update

First install: vendors the kit into <target>/.agentic/kit, creates the .agentic state
skeleton and config.toml, writes or merges AGENTS.md (between markers), adds CLAUDE.md /
GEMINI.md pointers, copies standards-pack configs and generates CODING_STANDARDS.md from the
chosen packs, generates tool files, sets core.hooksPath, and adds the CI workflow.

Update: replaces .agentic/kit and the generated files, and refreshes the managed blocks in
AGENTS.md and CODING_STANDARDS.md. State, config, glossary, project rules, existing tool
configs, specs, tasks and handoffs are never overwritten.
Standard library only (Python 3.11+).
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    sys.exit("install.py needs Python 3.11 or newer.")

KIT = Path(__file__).resolve().parents[1]
KIT_PARTS = ("agents", "skills", "standards", "workflow", "gates", "adapters", "runner", "ci", "VERSION",
             "CHANGELOG.md", "LICENSE")
STACKS = ("python", "lua", "cpp", "dotnet", "javascript", "typescript", "rust", "go")
TOOLS = ("claude", "copilot", "cursor", "gemini", "generic")
BEGIN, END = "<!-- agentic-dev-kit:begin", "<!-- agentic-dev-kit:end -->"
STD_BEGIN, STD_END = "<!-- agentic-dev-kit:standards:begin", "<!-- agentic-dev-kit:standards:end -->"
PROJECT_RULES = """## Project rules

Rules specific to this project. They take precedence over the packs above. The installer
never changes this section. Rules that a tool can check belong in a linter config or gate
step, not here.

- <rule>
"""
POINTER = "@AGENTS.md"


def csv(value: str | None) -> list[str]:
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def say(msg: str) -> None:
    print(f"  {msg}")


def is_git(target: Path) -> bool:
    return subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=target,
                          capture_output=True, text=True).returncode == 0


def toml_list(items: list[str]) -> str:
    return "[" + ", ".join(f'"{i}"' for i in items) + "]"


def config_text(stacks: list[str], domains: list[str], standards: list[str], tools: list[str],
                name: str) -> str:
    return f"""# agentic-dev-kit project configuration. Edit freely; the installer never overwrites it.
# After changing stacks, domains, standards or tools, re-run the installer with --update.

[project]
name = "{name}"
stacks = {toml_list(stacks)}     # {", ".join(STACKS)}
domains = {toml_list(domains)}   # folder names under .agentic/kit/agents/domains/
standards = {toml_list(standards)}   # coding-standards packs under .agentic/kit/standards/
tools = {toml_list(tools)}       # {", ".join(TOOLS)}

[workflow]
max_review_rounds = 3      # after this many verify/review rounds a task is blocked for a human
default_track = "auto"     # auto | lite | full  (see .agentic/kit/workflow/tracks.md)

[tests]
globs = []                 # extra test globs on top of each stack profile's test_globs

[safety]
# Paths agents must not read (secrets, credentials, personal data). Mirrored into Claude Code
# deny rules; other tools get it through AGENTS.md.
no_read = [".env", ".env.*", "**/secrets/**", "**/*.pem", "**/*.key", "**/*.pfx"]

[gate]
skip = []                  # step ids to skip, e.g. ["python:types"]. Comment why.
base_branch = "main"       # builtin:scope checks agent commits since the merge-base with this branch

[gate.overrides]
# "python:test" = "pytest -q --cov=src --cov-fail-under=90"
# "aerospace-engineer:unit-suffixes" = {{ advisory = false }}

# Cost controls for headless runs (.agentic/kit/runner/run.py). Interactive sessions aren't
# metered by the kit; use your tools' own limits for those.
#   off     record nothing
#   track   record time, tokens and cost per task (Spend row); never stop   <- default
#   warn    also warn at warn_at of a limit, and when it's reached
#   enforce also block the task for a human when a limit is reached
# Leave a limit out (or set it to 0) to turn it off. A task's `Budget` row overrides these,
# e.g. "| Budget | enforce, max_cost_usd=5 |" or "| Budget | off |". `run.py ... --ignore-budgets`
# overrides them for one run, and is recorded in the ledger.
[budgets]
mode = "track"
warn_at = 0.8
# max_review_rounds = 3      # defaults to [workflow] max_review_rounds
# max_steps = 15
# max_minutes = 180
# max_tokens = 5000000
# max_cost_usd = 20.0
# max_cost_usd_per_day = 50.0    # across all tasks, from this machine's ledger
max_cost_usd_per_step = 5.0      # hard cap passed to engines that support one (Claude: --max-budget-usd)

# $ per million tokens, for engines that report tokens but not cost. The engine's `model` picks
# the row, e.g. [runner.engines] codex = {{ cmd = "...", model = "gpt-5" }}
[budgets.prices]
# "gpt-5" = {{ input = 1.25, output = 10.0 }}

# Headless runner (.agentic/kit/runner/run.py). Map independent roles to a different engine.
[runner]
default = "claude"
max_steps = 10
timeout_minutes = 60
# [runner.roles]
# adversary = "codex"
# [runner.engines]
# codex = 'codex exec --json --sandbox workspace-write - < "{{prompt_file}}"'

# Extend a role's write scope for this project's layout (humans only; this file is protected).
# [roles.test-designer]
# writes = ["MyApp.Specs/**"]
"""


def copy_kit(target: Path) -> None:
    dest = target / ".agentic" / "kit"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for part in KIT_PARTS:
        src = KIT / part
        if src.is_dir():
            shutil.copytree(src, dest / part, ignore=ignore)
        elif src.exists():
            shutil.copy2(src, dest / part)
    say(f".agentic/kit  (kit {(KIT / 'VERSION').read_text().strip()})")


def copy_skeleton(target: Path) -> None:
    src_root = KIT / "project-skeleton" / ".agentic"
    created = 0
    for src in sorted(src_root.rglob("*")):
        rel = src.relative_to(src_root)
        dst = target / ".agentic" / rel
        if src.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
        elif not dst.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            created += 1
    say(f".agentic state skeleton ({created} new file(s), existing files kept)")


def merge_agents_md(target: Path) -> None:
    template = (KIT / "project-skeleton" / "AGENTS.md").read_text("utf-8")
    start = template.index(BEGIN)
    block = template[start: template.index(END) + len(END)]
    path = target / "AGENTS.md"
    if not path.exists():
        path.write_text(template, "utf-8", newline="\n")
        say("AGENTS.md created")
        return
    text = path.read_text("utf-8")
    if BEGIN in text and END in text:
        s, e = text.index(BEGIN), text.index(END) + len(END)
        path.write_text(text[:s] + block + text[e:], "utf-8", newline="\n")
        say("AGENTS.md managed block refreshed")
    else:
        path.write_text(block + "\n\n" + text, "utf-8", newline="\n")
        say("AGENTS.md: managed block added at the top (your content kept below)")


def pointer_file(target: Path, name: str) -> None:
    path = target / name
    if not path.exists():
        path.write_text(f"{POINTER}\n\nAll agent instructions live in AGENTS.md.\n", "utf-8", newline="\n")
        say(f"{name} created (imports AGENTS.md)")
    elif "AGENTS.md" not in path.read_text("utf-8"):
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(f"\n\n{POINTER}\n")
        say(f"{name}: AGENTS.md import appended")


def set_hooks(target: Path) -> None:
    if not is_git(target):
        say("not a git repository: hooks skipped (run `git init`, then --update)")
        return
    current = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=target,
                             capture_output=True, text=True).stdout.strip()
    wanted = ".agentic/kit/gates/hooks"
    if current and current != wanted:
        say(f"core.hooksPath is already '{current}'. Left unchanged; chain {wanted}/pre-commit "
            f"and pre-push from your hooks.")
        return
    subprocess.run(["git", "config", "core.hooksPath", wanted], cwd=target, check=True)
    for hook in ("pre-commit", "pre-push"):  # executable bit for macOS/Linux checkouts
        subprocess.run(["git", "update-index", "--chmod=+x", f"{wanted}/{hook}"], cwd=target,
                       capture_output=True)
        p = target / wanted / hook
        if p.exists():
            p.chmod(p.stat().st_mode | 0o111)
    say(f"git hooks -> {wanted}")


def load_pack(pack_id: str) -> dict | None:
    path = KIT / "standards" / pack_id / "pack.toml"
    if pack_id.startswith("_") or not path.exists():
        return None
    return tomllib.loads(path.read_text("utf-8"))


def check_standards(standards: list[str], stacks: list[str]) -> list[str]:
    errors, packs = [], {}
    for sid in standards:
        pack = load_pack(sid)
        if pack is None:
            errors.append(f"unknown standards pack '{sid}' (see .agentic/kit/standards/README.md)")
            continue
        packs[sid] = pack
        if pack.get("stack") not in stacks:
            errors.append(f"standards pack '{sid}' is for stack '{pack.get('stack')}', which isn't in --stacks")
    for sid, pack in packs.items():
        for other in pack.get("conflicts", []):
            if other in packs and sid < other:
                errors.append(f"standards packs '{sid}' and '{other}' conflict; choose one")
    return errors


def standards_hint(stacks: list[str]) -> None:
    """Point at the packs available for the chosen stacks when none were selected."""
    root = KIT / "standards"
    by_stack: dict[str, list[str]] = {}
    for folder in sorted(root.iterdir()) if root.exists() else []:
        pack = load_pack(folder.name) if folder.is_dir() else None
        if pack and pack.get("stack") in stacks:
            by_stack.setdefault(pack["stack"], []).append(folder.name)
    if not by_stack:
        return
    say("No coding-standards packs selected. Tools use their defaults, and CODING_STANDARDS.md stays blank.")
    for stack in stacks:
        if stack in by_stack:
            say(f"  available for {stack}: {', '.join(by_stack[stack])}")
    say("  To use one, add it to 'standards' in .agentic/config.toml and re-run with --update "
        "(see .agentic/kit/standards/README.md).")


def normalized(text: str) -> str:
    return text.replace("\r\n", "\n").strip()


def nest_headings(markdown: str) -> str:
    """Push every heading down one level so a pack's ## sections sit under its ## title as ###."""
    out, fence = [], False
    for line in markdown.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
        out.append("#" + line if not fence and line.startswith("#") else line)
    return "\n".join(out).strip() + "\n"


def standards_block(standards: list[str]) -> str:
    parts = [
        f"{STD_BEGIN} (generated from packs: {', '.join(standards)}. Refreshed by install --update; "
        "edit Project rules below instead) -->",
        "# Coding standards",
        "",
        "Read by the **standards-reviewer** at review time. Precedence: **Project rules** (at the "
        "end of this file), then the packs below, in order, then the built-in smell baseline in "
        "`.agentic/kit/skills/independent-review/SKILL.md`.",
        "",
        "Each pack starts with what its tool configs already enforce through the gate. Reviewers "
        "skip those items and judge the rest.",
    ]
    for sid in standards:
        pack = load_pack(sid) or {}
        body = (KIT / "standards" / sid / "standard.md").read_text("utf-8")
        sources = " · ".join(f"<{s}>" for s in pack.get("sources", []))
        parts += ["", f"<!-- pack:{sid} -->", f"## {pack.get('name', sid)} (`{sid}`)", "",
                  pack.get("summary", ""), "", f"Sources: {sources}" if sources else "", "",
                  nest_headings(body).rstrip()]
    parts.append(STD_END)
    return "\n".join(p for p in parts) + "\n"


def write_coding_standards(target: Path, standards: list[str]) -> None:
    path = target / ".agentic" / "CODING_STANDARDS.md"
    skeleton = (KIT / "project-skeleton" / ".agentic" / "CODING_STANDARDS.md").read_text("utf-8")
    text = path.read_text("utf-8") if path.exists() else ""
    has_block = STD_BEGIN in text and STD_END in text
    if not standards:
        if has_block:  # every pack was removed from config: drop the managed block, keep project rules
            s, e = text.index(STD_BEGIN), text.index(STD_END) + len(STD_END)
            path.write_text((text[:s] + text[e:]).lstrip(), "utf-8", newline="\n")
            say("CODING_STANDARDS.md: pack sections removed (no standards configured)")
        return
    block = standards_block(standards)
    if has_block:
        s, e = text.index(STD_BEGIN), text.index(STD_END) + len(STD_END)
        path.write_text(text[:s] + block.rstrip("\n") + text[e:], "utf-8", newline="\n")
        say(f"CODING_STANDARDS.md: pack sections refreshed ({', '.join(standards)})")
    elif not text or normalized(text) == normalized(skeleton):
        path.write_text(block + "\n" + PROJECT_RULES, "utf-8", newline="\n")
        say(f"CODING_STANDARDS.md generated from {', '.join(standards)}")
    else:
        kept = nest_headings(text)
        path.write_text(block + "\n## Project rules\n\n" + kept, "utf-8", newline="\n")
        say("CODING_STANDARDS.md: pack sections added above your existing rules (kept as Project rules)")


def copy_pack_configs(target: Path, standards: list[str]) -> None:
    for sid in standards:
        cdir = KIT / "standards" / sid / "configs"
        if not cdir.exists():
            continue
        for src in sorted(p for p in cdir.rglob("*") if p.is_file() and p.name != ".gitkeep"):
            rel = src.relative_to(cdir)
            dst = target / rel
            if not dst.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(src, dst)
                say(f"{rel.as_posix()} added ({sid})")
            elif normalized(dst.read_text("utf-8", errors="replace")) != normalized(src.read_text("utf-8")):
                say(f"{rel.as_posix()} exists and differs from {sid}'s. Kept yours; compare with "
                    f".agentic/kit/standards/{sid}/configs/{rel.as_posix()}")


def write_codeowners(target: Path, owners: list[str]) -> None:
    dst = target / ".github" / "CODEOWNERS"
    if dst.exists() or (target / "CODEOWNERS").exists() or (target / "docs" / "CODEOWNERS").exists():
        say("CODEOWNERS exists. Kept (compare with .agentic/kit/ci/github/CODEOWNERS.tmpl)")
        return
    if not owners:
        say("No --owners given: CODEOWNERS skipped. Add it later to make protected paths need a "
            "human's approval (see .agentic/kit/ci/github/CODEOWNERS.tmpl).")
        return
    bad = [o for o in owners if not o.startswith("@") and "@" not in o]
    if bad:
        say(f"CODEOWNERS skipped: owners must be @user, @org/team or an email ({', '.join(bad)})")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmpl = (KIT / "ci" / "github" / "CODEOWNERS.tmpl").read_text("utf-8")
    dst.write_text(tmpl.replace("{owners}", " ".join(owners)), "utf-8", newline="\n")
    say(f".github/CODEOWNERS added ({' '.join(owners)})")


def claude_deny_rules(no_read: list[str]) -> list[str]:
    rules = [
        "Bash(git push --force:*)", "Bash(git push -f:*)", "Bash(git push --force-with-lease:*)",
        "Bash(git commit --no-verify:*)", "Bash(git commit -n:*)", "Bash(git push --no-verify:*)",
        "Bash(git config core.hooksPath:*)", "Bash(git reset --hard:*)",
        "Edit(./.agentic/kit/**)", "Write(./.agentic/kit/**)",
        "Edit(./.agentic/locks/**)", "Write(./.agentic/locks/**)",
        "Edit(./.github/workflows/**)", "Write(./.github/workflows/**)",
        "Edit(./.github/CODEOWNERS)", "Write(./.github/CODEOWNERS)",
        "Edit(./.claude/settings.json)", "Write(./.claude/settings.json)",
    ]
    for pattern in no_read:
        path = pattern if pattern.startswith(("./", "**", "/")) else f"./{pattern}"
        rules.append(f"Read({path})")
    return rules


def merge_claude_settings(target: Path, no_read: list[str]) -> None:
    import json
    path = target / ".claude" / "settings.json"
    data = {}
    if path.exists():
        try:
            data = json.loads(path.read_text("utf-8"))
        except json.JSONDecodeError:
            say(".claude/settings.json isn't valid JSON. Left unchanged; add the deny rules by hand.")
            return
    deny = data.setdefault("permissions", {}).setdefault("deny", [])
    added = [r for r in claude_deny_rules(no_read) if r not in deny]
    if not added:
        return
    deny.extend(added)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", "utf-8", newline="\n")
    say(f".claude/settings.json: {len(added)} deny rule(s) added (force-push, hook bypass, protected paths, secrets)")


DEPENDABOT_ECOSYSTEMS = {"python": "pip", "javascript": "npm", "typescript": "npm", "dotnet": "nuget",
                         "rust": "cargo", "go": "gomod"}


def write_dependabot(target: Path, stacks: list[str]) -> None:
    dst = target / ".github" / "dependabot.yml"
    if dst.exists():
        say(".github/dependabot.yml exists. Kept")
        return
    ecosystems = ["github-actions"] + sorted({DEPENDABOT_ECOSYSTEMS[s] for s in stacks if s in DEPENDABOT_ECOSYSTEMS})
    lines = ["# agentic-dev-kit: weekly dependency and pinned-action updates. Review them like any other change.",
             "version: 2", "updates:"]
    for eco in ecosystems:
        lines += [f'  - package-ecosystem: "{eco}"', '    directory: "/"', "    schedule:",
                  '      interval: "weekly"', "    open-pull-requests-limit: 5"]
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text("\n".join(lines) + "\n", "utf-8", newline="\n")
    say(f".github/dependabot.yml added ({', '.join(ecosystems)})")


DEVCONTAINER_FEATURES = {
    "javascript": ("ghcr.io/devcontainers/features/node:1", {"version": "22"}),
    "typescript": ("ghcr.io/devcontainers/features/node:1", {"version": "22"}),
    "dotnet": ("ghcr.io/devcontainers/features/dotnet:2", {"version": "10.0"}),
    "go": ("ghcr.io/devcontainers/features/go:1", {}),
    "rust": ("ghcr.io/devcontainers/features/rust:1", {}),
}
DEVCONTAINER_APT = {"cpp": "cmake clang-format clang-tidy cppcheck", "lua": "lua5.4 liblua5.4-dev luarocks"}


def write_devcontainer(target: Path, stacks: list[str]) -> None:
    import json
    dst = target / ".devcontainer" / "devcontainer.json"
    if dst.exists():
        say(".devcontainer/devcontainer.json exists. Kept")
        return
    features = {"ghcr.io/devcontainers/features/python:1": {"version": "3.12"}}  # the kit itself needs Python
    for s in stacks:
        if s in DEVCONTAINER_FEATURES:
            ref, opts = DEVCONTAINER_FEATURES[s]
            features[ref] = opts
    post = ["python -m pip install --user ruff mypy pytest pytest-cov"] if "python" in stacks else []
    apt = " ".join(DEVCONTAINER_APT[s] for s in stacks if s in DEVCONTAINER_APT)
    if apt:
        post.insert(0, f"sudo apt-get update && sudo apt-get install -y {apt}")
    if "lua" in stacks:
        post.append("sudo luarocks install busted && sudo luarocks install luacheck")
    config = {
        "name": f"{target.name} (agentic-dev-kit sandbox)",
        "image": "mcr.microsoft.com/devcontainers/base:ubuntu-24.04",
        "features": features,
        "remoteUser": "vscode",
        "containerEnv": {"AGENTIC_SANDBOX": "1"},
        "postCreateCommand": " && ".join(post) or "true",
    }
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(json.dumps(config, indent=2) + "\n", "utf-8", newline="\n")
    say(".devcontainer/devcontainer.json added (sandbox for headless agent runs)")


def copy_review_workflow(target: Path) -> None:
    dst = target / ".github" / "workflows" / "agent-review.yml"
    if dst.exists():
        say(".github/workflows/agent-review.yml exists. Kept")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT / "ci" / "github" / "agent-review.yml", dst)
    say(".github/workflows/agent-review.yml added (needs an ANTHROPIC_API_KEY repository secret)")


PRETTIER_IGNORE = (".agentic/", ".claude/", ".cursor/", ".github/agents/", ".github/skills/",
                   "AGENTS.md", "CLAUDE.md", "GEMINI.md")


def ensure_tool_ignores(target: Path, stacks: list[str]) -> None:
    """Keep stack tools from formatting or linting the kit's vendored and generated files."""
    if not {"javascript", "typescript"} & set(stacks):
        return
    path = target / ".prettierignore"
    text = path.read_text("utf-8") if path.exists() else ""
    have = {line.strip() for line in text.splitlines()}
    missing = [p for p in PRETTIER_IGNORE if p not in have]
    if missing:
        with path.open("a", encoding="utf-8", newline="\n") as fh:
            fh.write(("\n" if text and not text.endswith("\n") else "")
                     + "# agentic-dev-kit: vendored and generated files\n" + "\n".join(missing) + "\n")
        say(".prettierignore: kit and generated files excluded")


GITATTR_RULES = (
    "# agentic-dev-kit: hooks must keep LF endings or they fail in sh / Git Bash",
    ".agentic/kit/gates/hooks/* text eol=lf",
    ".agentic/kit/**/*.sh text eol=lf",
)


def ensure_gitattributes(target: Path) -> None:
    path = target / ".gitattributes"
    text = path.read_text("utf-8") if path.exists() else ""
    missing = [r for r in GITATTR_RULES if r not in text]
    if not missing:
        return
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(("\n" if text and not text.endswith("\n") else "") + "\n".join(missing) + "\n")
    say(".gitattributes: LF rule for hooks added")


def copy_ci(target: Path) -> None:
    dst = target / ".github" / "workflows" / "agent-gate.yml"
    if dst.exists():
        say(".github/workflows/agent-gate.yml exists. Kept (compare with .agentic/kit/ci/github/agent-gate.yml).")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(KIT / "ci" / "github" / "agent-gate.yml", dst)
    say(".github/workflows/agent-gate.yml added")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Install or update agentic-dev-kit in a project.")
    p.add_argument("--target", type=Path, default=Path.cwd(), help="project root")
    p.add_argument("--stacks", help=f"comma list: {', '.join(STACKS)}")
    p.add_argument("--domains", help="comma list of domain ids")
    p.add_argument("--standards", help="comma list of coding-standards packs (see standards/README.md)")
    p.add_argument("--tools", help=f"comma list: {', '.join(TOOLS)} (default claude,generic)")
    p.add_argument("--owners", help="comma list of CODEOWNERS for protected paths, e.g. @me,@org/leads")
    p.add_argument("--ci-review", action="store_true", help="add the AI PR-review workflow (needs ANTHROPIC_API_KEY)")
    p.add_argument("--devcontainer", action="store_true", help="add a devcontainer sandbox for headless agent runs")
    p.add_argument("--update", action="store_true", help="refresh kit + generated files only")
    p.add_argument("--no-hooks", action="store_true")
    p.add_argument("--no-ci", action="store_true")
    a = p.parse_args(argv)

    target = a.target.resolve()
    if not target.is_dir():
        print(f"target is not a directory: {target}", file=sys.stderr)
        return 2
    if target == KIT or KIT in target.parents:
        print("target must be a project, not the kit repository itself", file=sys.stderr)
        return 2
    cfg_path = target / ".agentic" / "config.toml"
    existing = tomllib.loads(cfg_path.read_text("utf-8")).get("project", {}) if cfg_path.exists() else None

    if a.update and existing is None:
        print("no .agentic/config.toml found: run a first install without --update", file=sys.stderr)
        return 2
    stacks = csv(a.stacks) or (existing or {}).get("stacks", [])
    domains = csv(a.domains) or (existing or {}).get("domains", [])
    standards = csv(a.standards) or (existing or {}).get("standards", [])
    tools = csv(a.tools) or (existing or {}).get("tools", ["claude", "generic"])
    if not stacks and existing is None:
        print(f"--stacks is required on first install ({', '.join(STACKS)})", file=sys.stderr)
        return 2
    errors = [f"unknown stack '{s}'" for s in stacks if s not in STACKS]
    errors += [f"unknown tool '{t}'" for t in tools if t not in TOOLS]
    errors += [f"unknown domain '{d}'" for d in domains
               if d.startswith("_") or not (KIT / "agents" / "domains" / d / "agent.md").exists()]
    if existing is not None and (csv(a.stacks) or csv(a.domains) or csv(a.standards) or csv(a.tools)):
        current = (existing.get("stacks", []), existing.get("domains", []), existing.get("standards", []),
                   existing.get("tools", []))
        if (stacks, domains, standards, tools) != current:
            print("note: .agentic/config.toml already exists and is never overwritten. Edit its [project] "
                  "stacks/domains/standards/tools, then re-run with --update.", file=sys.stderr)
            stacks, domains, standards, tools = current
    errors += check_standards(standards, stacks)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 2

    print(f"agentic-dev-kit {'update' if a.update else 'install'} -> {target}")
    copy_kit(target)
    if not a.update:
        copy_skeleton(target)
        if existing is None:
            cfg_path.write_text(config_text(stacks, domains, standards, tools, target.name), "utf-8",
                                newline="\n")
            say(".agentic/config.toml created")
    merge_agents_md(target)
    copy_pack_configs(target, standards)
    write_coding_standards(target, standards)
    if not standards:
        standards_hint(stacks)
    full_cfg = tomllib.loads(cfg_path.read_text("utf-8")) if cfg_path.exists() else {}
    no_read = full_cfg.get("safety", {}).get("no_read", [])
    if "claude" in tools:
        pointer_file(target, "CLAUDE.md")
        merge_claude_settings(target, no_read)
    if "gemini" in tools:
        pointer_file(target, "GEMINI.md")

    sys.path.insert(0, str(target / ".agentic" / "kit" / "adapters"))
    import build  # the vendored copy, so generated paths point at .agentic/kit
    build.build(target, tools, domains, standards)

    ensure_gitattributes(target)
    ensure_tool_ignores(target, stacks)
    if not a.no_hooks:
        set_hooks(target)
    if not a.no_ci and not a.update:
        copy_ci(target)
        write_dependabot(target, stacks)
    if a.ci_review:
        copy_review_workflow(target)
    if a.devcontainer:
        write_devcontainer(target, stacks)
    if not a.update or csv(a.owners):
        write_codeowners(target, csv(a.owners))

    print("\nNext steps:")
    print("  1. Install each stack's tools, then check:  python .agentic/kit/gates/gate.py list")
    print("  2. Commit the result (git add -A && git commit -m \"chore: add agentic-dev-kit\")")
    print("  3. On GitHub, protect main: require the 'agent-gate' check and one human approval.")
    print("  4. Open your LLM tool here and say: \"Read AGENTS.md and start.\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
