#!/usr/bin/env python3
"""End-to-end smoke test for agentic-dev-kit. See docs/testing-the-kit.md."""
from __future__ import annotations

import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

KIT = Path(__file__).resolve().parents[1]
WORK = Path(tempfile.gettempdir()) / "agentic-dev-kit-smoke" / "project"


def run(*cmd: str, cwd: Path = WORK, expect: int | None = 0) -> subprocess.CompletedProcess:
    proc = subprocess.run(list(cmd), cwd=cwd, capture_output=True, text=True, errors="replace")
    if expect is not None and proc.returncode != expect:
        print(proc.stdout, proc.stderr, sep="\n")
        raise SystemExit(f"FAILED: {' '.join(cmd)} exited {proc.returncode}, expected {expect}")
    return proc


def gate(*args: str, expect: int) -> str:
    return run(sys.executable, ".agentic/kit/gates/gate.py", *args, expect=expect).stdout


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(f"FAILED: {msg}")
    print(f"  ok  {msg}")


def on_rm_error(func, path, _exc):  # read-only git objects on Windows
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def main() -> int:
    if WORK.parent.exists():
        shutil.rmtree(WORK.parent, onexc=on_rm_error)
    WORK.mkdir(parents=True)
    run("git", "init", "-q")
    run("git", "config", "user.email", "smoke@example.invalid")
    run("git", "config", "user.name", "smoke")
    (WORK / "AGENTS.md").write_text("# My project\nHand-written note.\n", "utf-8")

    print("install")
    out = run(sys.executable, str(KIT / "install" / "install.py"), "--target", str(WORK), "--stacks", "python",
              "--domains", "aerospace-engineer,unreal-technical-artist",
              "--tools", "claude,copilot,cursor,gemini,generic").stdout
    check("available for python: python-pep8, python-strict" in out, "hint lists packs when none selected")
    for rel in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".agentic/REGISTRY.md", ".agentic/config.toml",
                ".agentic/STATE.md", ".claude/agents/orchestrator.md", ".claude/agents/aerospace-engineer.md",
                ".claude/skills/test-driven-slices/SKILL.md", ".claude/skills/units-and-frames-review/SKILL.md",
                ".github/agents/adversary.agent.md", ".github/skills/handoff/SKILL.md",
                ".cursor/rules/agentic-implementer.mdc", ".agentic/prompts/verifier.md",
                ".github/workflows/agent-gate.yml"):
        check((WORK / rel).exists(), f"generated {rel}")
    agents_md = (WORK / "AGENTS.md").read_text("utf-8")
    check("agentic-dev-kit:begin" in agents_md and "Hand-written note." in agents_md, "AGENTS.md merged, note kept")
    check("gates/hooks/* text eol=lf" in (WORK / ".gitattributes").read_text("utf-8"), ".gitattributes LF rule")
    hooks = run("git", "config", "--get", "core.hooksPath").stdout.strip()
    check(hooks == ".agentic/kit/gates/hooks", "core.hooksPath set")
    claude = (WORK / ".claude/agents/adversary.md").read_text("utf-8")
    check(claude.startswith("---\nname: adversary\n") and "tools: Read, Grep, Glob, Edit, Write, Bash, Skill" in claude,
          "Claude agent frontmatter")

    print("update keeps state")
    (WORK / ".agentic/STATE.md").write_text("# custom state\n", "utf-8")
    run(sys.executable, str(KIT / "install" / "install.py"), "--target", str(WORK), "--update")
    check((WORK / ".agentic/STATE.md").read_text("utf-8") == "# custom state\n", "STATE.md untouched by update")
    check("Hand-written note." in (WORK / "AGENTS.md").read_text("utf-8"), "AGENTS.md note kept by update")

    print("built-in gate checks")
    only = ("run", "--stage", "ci", "--only")
    spec = WORK / ".agentic/specs/login.md"
    spec.write_text("---\nid: LOGIN\nstatus: approved\n---\n# Spec\n- LOGIN-AC-1: Given a user...\n", "utf-8")
    check("LOGIN-AC-1" in gate(*only, "builtin:trace", expect=1), "trace fails for an untested AC")
    test = WORK / "tests/test_login.py"
    test.parent.mkdir()
    test.write_text("def test_login_ac_1_accepts_valid_user():\n    assert True\n", "utf-8")
    gate(*only, "builtin:trace", expect=0)
    check(True, "trace passes once a test names the AC")

    out = run(sys.executable, ".agentic/kit/gates/gate.py", "lock-tests", "--by", "test-designer").stdout
    check("+1" in out, "lock-tests locked the AC test")
    gate(*only, "builtin:test-lock", expect=0)
    test.write_text("def test_login_ac_1_accepts_valid_user():\n    pass\n", "utf-8")
    check("modified" in gate(*only, "builtin:test-lock", expect=1), "test-lock catches an edited locked test")
    run(sys.executable, ".agentic/kit/gates/gate.py", "lock-tests", "--by", "adversary")
    gate(*only, "builtin:test-lock", expect=0)
    check(True, "re-lock by an allowed role restores the gate")

    src = WORK / "src/app.py"
    src.parent.mkdir()
    src.write_text("print('DEBUG-a1b2 here')\n", "utf-8")
    gate(*only, "builtin:debug-tags", expect=1)
    check(True, "debug-tags catches leftover instrumentation")
    src.write_text("API_KEY = 'AKIA" + "ABCDEFGHIJKLMNOP'\n", "utf-8")
    if not shutil.which("gitleaks"):
        gate(*only, "builtin:secrets", expect=1)
        check(True, "secrets catches a fake AWS key")
    src.write_text("altitude = 1200\naltitude_m = 1200\n", "utf-8")
    out = run(sys.executable, ".agentic/kit/gates/gate.py", *only, "aerospace-engineer:unit-suffixes",
              expect=0).stdout
    check("WARN" in out, "aerospace unit-suffix check warns (advisory)")

    report = (WORK / ".agentic/reports/gate-latest.md").read_text("utf-8")
    check(report.startswith("# Gate report"), "report written")

    test_standards()
    print("SMOKE OK")
    return 0


def fresh_repo(name: str) -> Path:
    path = WORK.parent / name
    path.mkdir(parents=True)
    run("git", "init", "-q", cwd=path)
    return path


def test_standards() -> None:
    print("standards packs")
    installer = str(KIT / "install" / "install.py")
    proj = fresh_repo("standards")
    (proj / ".editorconfig").write_text("root = true\n# mine\n", "utf-8")
    run(sys.executable, installer, "--target", str(proj), "--stacks", "dotnet,typescript,rust",
        "--standards", "dotnet-microsoft,typescript-strict,rust-api-guidelines", cwd=proj)
    for rel in ("Directory.Build.props", "eslint.config.mjs", "tsconfig.strict.json", "rustfmt.toml", "clippy.toml"):
        check((proj / rel).exists(), f"pack config {rel} copied")
    check((proj / ".editorconfig").read_text("utf-8") == "root = true\n# mine\n", "existing .editorconfig kept")

    cs = proj / ".agentic/CODING_STANDARDS.md"
    text = cs.read_text("utf-8")
    check("agentic-dev-kit:standards:begin" in text and "agentic-dev-kit:standards:end" in text, "managed block present")
    for sid in ("dotnet-microsoft", "typescript-strict", "rust-api-guidelines"):
        check(f"(`{sid}`)" in text, f"CODING_STANDARDS.md has a {sid} section")
    check("\n### Enforced by tooling" in text and "\n## Project rules" in text, "headings nested, Project rules present")

    cs.write_text(text.replace("- <rule>", "- Prefer spans over arrays in hot paths."), "utf-8")
    run(sys.executable, installer, "--target", str(proj), "--update", cwd=proj)
    text = cs.read_text("utf-8")
    check("Prefer spans over arrays in hot paths." in text and text.count("standards:begin") == 1,
          "update refreshes packs and keeps Project rules")

    listing = run(sys.executable, ".agentic/kit/gates/gate.py", "list", cwd=proj).stdout
    check("rust-api-guidelines:clippy-pedantic" in listing and "rust:clippy " not in listing,
          "pack gate step replaces rust:clippy")
    check("rust-api-guidelines" in (proj / ".agentic/REGISTRY.md").read_text("utf-8"), "registry lists packs")

    bad = fresh_repo("conflict")
    out = run(sys.executable, installer, "--target", str(bad), "--stacks", "python",
              "--standards", "python-pep8,python-strict", cwd=bad, expect=2)
    check("conflict" in out.stderr, "conflicting packs rejected")
    out = run(sys.executable, installer, "--target", str(bad), "--stacks", "python",
              "--standards", "dotnet-microsoft", cwd=bad, expect=2)
    check("isn't in --stacks" in out.stderr, "pack for an unselected stack rejected")


if __name__ == "__main__":
    sys.exit(main())
