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
KIT_PARTS = ("agents", "skills", "standards", "workflow", "gates", "adapters", "ci", "VERSION",
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

[gate]
skip = []                  # step ids to skip, e.g. ["python:types"]. Comment why.

[gate.overrides]
# "python:test" = "pytest -q --cov=src --cov-fail-under=90"
# "aerospace-engineer:unit-suffixes" = {{ advisory = false }}
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
    if "claude" in tools:
        pointer_file(target, "CLAUDE.md")
    if "gemini" in tools:
        pointer_file(target, "GEMINI.md")

    sys.path.insert(0, str(target / ".agentic" / "kit" / "adapters"))
    import build  # the vendored copy, so generated paths point at .agentic/kit
    build.build(target, tools, domains, standards)

    ensure_gitattributes(target)
    if not a.no_hooks:
        set_hooks(target)
    if not a.no_ci and not a.update:
        copy_ci(target)

    print("\nNext steps:")
    print("  1. Install each stack's tools, then check:  python .agentic/kit/gates/gate.py list")
    print("  2. Commit the result (git add -A && git commit -m \"chore: add agentic-dev-kit\")")
    print("  3. On GitHub, protect main: require the 'agent-gate' check and one human approval.")
    print("  4. Open your LLM tool here and say: \"Read AGENTS.md and start.\"")
    return 0


if __name__ == "__main__":
    sys.exit(main())
