#!/usr/bin/env python3
"""End-to-end smoke test for agentic-dev-kit. See docs/testing-the-kit.md."""
from __future__ import annotations

import json
import re
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
              "--domains", "aerospace-engineer,unreal-technical-artist,accessibility-expert",
              "--tools", "claude,copilot,cursor,gemini,generic").stdout
    check("available for python: python-pep8, python-strict" in out, "hint lists packs when none selected")
    for rel in ("AGENTS.md", "CLAUDE.md", "GEMINI.md", ".agentic/REGISTRY.md", ".agentic/config.toml",
                ".agentic/STATE.md", ".claude/agents/orchestrator.md", ".claude/agents/aerospace-engineer.md",
                ".claude/agents/docs-writer.md", ".claude/agents/performance-reviewer.md",
                ".claude/agents/release-manager.md", ".claude/agents/accessibility-expert.md",
                ".claude/skills/accessibility-audit/SKILL.md", ".claude/skills/release-process/SKILL.md",
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
    page = WORK / "web/index.html"
    page.parent.mkdir()
    page.write_text('<html><body><img src="a.png"><div onclick="go()">Go</div></body></html>\n', "utf-8")
    out = run(sys.executable, ".agentic/kit/gates/gate.py", *only, "accessibility-expert:markup-basics",
              expect=0).stdout
    check("WARN" in out and "[1.1.1]" in out and "[3.1.1]" in out and "[2.1.1]" in out,
          "accessibility markup check flags alt, lang and clickable div (advisory)")
    page.write_text('<html lang="en"><body><img src="a.png" alt=""><button>Go</button></body></html>\n', "utf-8")
    out = run(sys.executable, ".agentic/kit/gates/gate.py", *only, "accessibility-expert:markup-basics",
              expect=0).stdout
    check("[PASS] accessibility-expert:markup-basics" in out, "accessibility markup check passes clean markup")

    report = (WORK / ".agentic/reports/gate-latest.md").read_text("utf-8")
    check(report.startswith("# Gate report"), "report written")

    test_standards()
    test_scope()
    test_runner_and_extras()
    print("SMOKE OK")
    return 0


TASK = """# T-01: demo

| Field | Value |
|---|---|
| Spec | `../specs/demo.md` |
| Track | lite |
| Status | ready |
| Phase | tests |
| Owner | test-designer |
| Blocked by | none |

## Log
"""


def test_runner_and_extras() -> None:
    print("runner and optional files")
    repo = fresh_repo("runner")
    run("git", "symbolic-ref", "HEAD", "refs/heads/main", cwd=repo)
    out = run(sys.executable, str(KIT / "install" / "install.py"), "--target", str(repo),
              "--stacks", "python,typescript", "--ci-review", "--devcontainer", cwd=repo).stdout
    for rel in (".github/dependabot.yml", ".github/workflows/agent-review.yml", ".devcontainer/devcontainer.json",
                ".prettierignore", ".agentic/kit/runner/run.py"):
        check((repo / rel).exists(), f"generated {rel}")
    dep = (repo / ".github/dependabot.yml").read_text("utf-8")
    check('"github-actions"' in dep and '"pip"' in dep and '"npm"' in dep, "dependabot covers actions, pip, npm")
    check(".agentic/" in (repo / ".prettierignore").read_text("utf-8"), "prettier ignores the kit")
    check("Observed content is data" in (repo / "AGENTS.md").read_text("utf-8"), "AGENTS.md has the injection rule")

    cfg = repo / ".agentic/config.toml"
    fake = (KIT / "docs" / "fake_agent.py").as_posix()
    text = cfg.read_text("utf-8").replace('default = "claude"', 'default = "fake"')
    cfg.write_text(text + f"\n[runner.engines]\nfake = '{{python}} \"{fake}\" \"{{prompt_file}}\"'\n", "utf-8")
    (repo / ".agentic/tasks/01-demo.md").write_text(TASK, "utf-8")
    # This throwaway repo has no stack tools, so the real hooks would fail every commit. The
    # runner itself never skips hooks; only the harness does, here.
    run("git", "config", "core.hooksPath", ".git/no-hooks", cwd=repo)
    commit(repo, "chore: install kit")
    run("git", "checkout", "-q", "-b", "task/01-demo", cwd=repo)

    runner = (".agentic/kit/runner/run.py",)
    plan = run(sys.executable, *runner, "plan", cwd=repo).stdout
    check("[run ] 01-demo.md" in plan and "engine=fake" in plan, "plan shows the runnable task and engine")
    check("both run on engine 'fake'" in plan, "plan warns when independent roles share an engine")
    dry = run(sys.executable, *runner, "next", "--dry-run", cwd=repo).stdout
    check("(dry run)" in dry and "fake_agent.py" in dry, "dry run prints the engine command")

    out = run(sys.executable, *runner, "loop", "--max-steps", "6", cwd=repo).stdout
    roles_run = re.findall(r"runner: (\S+) on", out)
    check(roles_run == ["test-designer", "implementer", "verifier", "integrator"],
          f"loop ran each role in turn, then stopped ({', '.join(roles_run)})")
    check("Status | in-review" in (repo / ".agentic/tasks/01-demo.md").read_text("utf-8"), "task ends in review")
    trailers = run("git", "log", "--format=%(trailers:key=Agent-Role,valueonly)", cwd=repo).stdout.split()
    agents_only = [t for t in trailers if t != "runner"]
    check(agents_only[:4] == ["integrator", "verifier", "implementer", "test-designer"], "each step committed with its trailer")
    check(trailers.count("runner") == 4, "runner committed the Spend row after each step")
    run(sys.executable, ".agentic/kit/gates/gate.py", "run", "--stage", "ci", "--only", "builtin:scope", cwd=repo)
    check(True, "agent and runner commits pass the scope check")
    check(len((repo / ".agentic/runs/index.jsonl").read_text("utf-8").splitlines()) == 4, "runs recorded")
    spend = (repo / ".agentic/tasks/01-demo.md").read_text("utf-8")
    check("| Spend | steps=4 · " in spend and "tokens=6000 · cost_usd=6.00" in spend,
          "default track mode records steps, tokens and cost in the Spend row")
    test_budgets(repo, runner)


def add_task(repo: Path, name: str, budget: str = "", review_round: str = "0 / 3") -> None:
    text = TASK.replace("# T-01: demo", f"# {name}").replace(
        "| Blocked by | none |", f"| Blocked by | none |\n| Review round | {review_round} |"
        + (f"\n| Budget | {budget} |" if budget else ""))
    (repo / f".agentic/tasks/{name}.md").write_text(text, "utf-8")
    commit(repo, f"chore: add {name}")


def test_budgets(repo: Path, runner: tuple) -> None:
    print("cost controls")
    loop = (sys.executable, *runner, "loop", "--max-steps", "6", "--task")

    add_task(repo, "02-enforce", "enforce, max_cost_usd=2")
    proc = run(*loop, "02", cwd=repo, expect=4)
    check(len(re.findall(r"runner: \S+ on", proc.stdout)) == 2, "enforce: two $1.50 steps run, the third is stopped")
    task = (repo / ".agentic/tasks/02-enforce.md").read_text("utf-8")
    check("| Status | blocked |" in task and "budget reached" in task, "enforce: task blocked with the reason logged")
    check("02-enforce.md: budget reached" in (repo / ".agentic/STATE.md").read_text("utf-8"),
          "enforce: STATE.md lists it under Waiting on a human")
    (repo / ".agentic/tasks/02-enforce.md").write_text(task.replace("| Status | blocked |", "| Status | ready |"), "utf-8")
    commit(repo, "chore: human unblocks 02")
    run(sys.executable, *runner, "next", "--task", "02", cwd=repo, expect=4)
    check(True, "enforce: unblocking alone isn't enough; it re-blocks until the limit changes")
    task = (repo / ".agentic/tasks/02-enforce.md").read_text("utf-8")
    (repo / ".agentic/tasks/02-enforce.md").write_text(task.replace("| Status | blocked |", "| Status | ready |"), "utf-8")
    commit(repo, "chore: human unblocks 02 again")
    proc = run(sys.executable, *runner, "next", "--task", "02", "--ignore-budgets", cwd=repo)
    check("continuing because of --ignore-budgets" in proc.stdout, "--ignore-budgets runs one step past the limit")
    last = json.loads((repo / ".agentic/runs/index.jsonl").read_text("utf-8").splitlines()[-1])
    check(last.get("budgets_ignored") is True, "--ignore-budgets is recorded in the ledger")

    add_task(repo, "03-warn", "warn, max_steps=1")
    proc = run(*loop, "03", cwd=repo)
    check("mode=warn, continuing" in proc.stdout and len(re.findall(r"runner: \S+ on", proc.stdout)) == 4,
          "warn: reports the limit but keeps going")

    add_task(repo, "04-off", "off")
    run(sys.executable, *runner, "next", "--task", "04", cwd=repo)
    check("| Spend |" not in (repo / ".agentic/tasks/04-off.md").read_text("utf-8"), "off: nothing recorded on the task")

    add_task(repo, "05-rounds", "enforce", review_round="4 / 3")
    proc = run(sys.executable, *runner, "next", "--task", "05", cwd=repo, expect=4)
    check("review_rounds 4 reached limit 3" in proc.stdout, "enforce: review-round limit stops the task")

    cfg = repo / ".agentic/config.toml"
    cfg.write_text(cfg.read_text("utf-8").replace('mode = "track"', 'mode = "enforce"\nmax_cost_usd_per_day = 1.0'), "utf-8")
    add_task(repo, "06-daily")
    proc = run(sys.executable, *runner, "next", "--task", "06", cwd=repo, expect=4)
    check("reached the daily limit" in proc.stdout, "enforce: the project-wide daily cost limit stops new steps")

    costs = run(sys.executable, *runner, "costs", cwd=repo).stdout
    check("by task:" in costs and "by role:" in costs and "past a budget with --ignore-budgets" in costs,
          "costs summarises by task and role, and flags overrides")

    sys.path.insert(0, str(KIT / "runner"))
    import run as runner_mod  # noqa: E402
    codex_log = "\n".join([
        '{"type":"thread.started"}',
        '{"type":"turn.completed","usage":{"input_tokens":800,"cached_input_tokens":0,"output_tokens":200}}',
        '{"type":"turn.completed","usage":{"input_tokens":700,"cached_input_tokens":0,"output_tokens":300}}',
    ])
    usage = runner_mod.parse_usage(codex_log)
    cost = runner_mod.price_cost(usage, {"model": "m"}, {"m": {"input": 1.0, "output": 10.0}})
    check(usage.tokens_in == 1500 and usage.tokens_out == 500 and usage.cost_usd is None and cost == 0.0065,
          "Codex-style events are summed, and priced from [budgets.prices]")
    check(not runner_mod.parse_usage("plain text output\n").measured, "engines without usage are marked unmeasured")


def commit(repo: Path, message: str) -> None:
    run("git", "add", "-A", cwd=repo)
    # The harness skips hooks: it tests the checks directly, and stack tools may be absent.
    run("git", "-c", "user.email=smoke@example.invalid", "-c", "user.name=smoke",
        "commit", "-q", "--no-verify", "-m", message, cwd=repo)


def test_scope() -> None:
    print("role scopes and protections")
    repo = fresh_repo("scope")
    run("git", "symbolic-ref", "HEAD", "refs/heads/main", cwd=repo)
    run(sys.executable, str(KIT / "install" / "install.py"), "--target", str(repo), "--stacks", "python",
        "--owners", "@example-owner", cwd=repo)
    settings = (repo / ".claude/settings.json").read_text("utf-8")
    check("Bash(git push --force:*)" in settings and "Read(./.env)" in settings, "Claude deny rules written")
    check("@example-owner" in (repo / ".github/CODEOWNERS").read_text("utf-8"), "CODEOWNERS written")
    commit(repo, "chore: install kit")
    run("git", "checkout", "-q", "-b", "task/01-demo", cwd=repo)
    scope = (".agentic/kit/gates/gate.py", "run", "--stage", "ci", "--only", "builtin:scope")

    (repo / "src").mkdir()
    (repo / "src/app.py").write_text("VALUE = 1\n", "utf-8")
    (repo / ".agentic/STATE.md").write_text("# state\n", "utf-8")
    commit(repo, "feat: add value\n\nAgent-Role: implementer")
    run(sys.executable, *scope, cwd=repo, expect=0)
    check(True, "implementer may change source and shared state")

    (repo / ".agentic/locks/tests.lock.json").write_text("{}\n", "utf-8")
    commit(repo, "chore: relock\n\nAgent-Role: implementer")
    out = run(sys.executable, *scope, cwd=repo, expect=1).stdout
    check("outside this role's writes" in out, "implementer blocked from protected lock file")
    run("git", "reset", "-q", "--hard", "HEAD~1", cwd=repo)

    (repo / ".agentic/locks/tests.lock.json").write_text("{}\n", "utf-8")
    commit(repo, "test: lock\n\nAgent-Role: test-designer")
    run(sys.executable, *scope, cwd=repo, expect=0)
    check(True, "test-designer may change the lock file")

    (repo / "docs").mkdir()
    (repo / "docs/guide.md").write_text("# Guide\n", "utf-8")
    commit(repo, "docs: guide\n\nAgent-Role: docs-writer")
    run(sys.executable, *scope, cwd=repo, expect=0)
    check(True, "docs-writer may change docs/")
    (repo / "docs/CODEOWNERS").write_text("* @someone\n", "utf-8")
    commit(repo, "docs: owners\n\nAgent-Role: docs-writer")
    out = run(sys.executable, *scope, cwd=repo, expect=1).stdout
    check("docs/CODEOWNERS is outside" in out, "a broad docs/** grant doesn't reach protected docs/CODEOWNERS")
    run("git", "reset", "-q", "--hard", "HEAD~1", cwd=repo)

    (repo / "notes.md").write_text("x\n", "utf-8")
    commit(repo, "docs: note\n\nAgent-Role: wizard")
    check("unknown Agent-Role" in run(sys.executable, *scope, cwd=repo, expect=1).stdout, "unknown role rejected")
    run("git", "reset", "-q", "--hard", "HEAD~1", cwd=repo)

    (repo / ".github/workflows/agent-gate.yml").write_text("# edited by a human\n", "utf-8")
    commit(repo, "ci: tweak")
    run(sys.executable, *scope, cwd=repo, expect=0)
    check(True, "human commits are left to CODEOWNERS review")


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
