#!/usr/bin/env python3
"""Run the real gate against a tiny sample project for one stack (and optional standards packs).

    python fixtures/fixture_test.py --stack python [--standards python-strict]

Copies fixtures/<stack>/project to a temp repo, adds fixtures/<stack>/default/ configs when no
pack is chosen, installs the kit, adds an approved spec whose AC the sample test names, runs the
stack's setup and format-fix commands from fixtures/<stack>/fixture.toml, commits, locks the
acceptance test, and runs `gate.py run --stage ci`. Exit code is the gate's.

This checks that the profiles, the pack configs and the built-in checks work with the real
tools. The sample code is formatted automatically first, so one fixture serves every pack's
layout rules. Lint, type, build and test rules are what's actually being tested.
"""
from __future__ import annotations

import argparse
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    sys.exit("needs Python 3.11+")

KIT = Path(__file__).resolve().parents[1]
SPEC = """---
id: DEMO
status: approved
---
# Spec: demo
## Acceptance criteria
- DEMO-AC-1: Given two integers, when they are added, then the result is their sum.
"""


def sh(cmd: str | list[str], cwd: Path, check: bool = True) -> int:
    print(f"$ {cmd if isinstance(cmd, str) else ' '.join(cmd)}", flush=True)
    code = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str)).returncode
    if check and code != 0:
        sys.exit(f"fixture step failed ({code}): {cmd}")
    return code


def on_rm_error(func, path, _exc):
    Path(path).chmod(stat.S_IWRITE)
    func(path)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--stack", required=True)
    p.add_argument("--standards", default="")
    p.add_argument("--keep", action="store_true", help="leave the temp repo for inspection")
    a = p.parse_args()
    src = KIT / "fixtures" / a.stack
    if not (src / "project").exists():
        sys.exit(f"no fixture for stack '{a.stack}'")
    meta = tomllib.loads((src / "fixture.toml").read_text("utf-8")) if (src / "fixture.toml").exists() else {}
    standards = [s for s in a.standards.split(",") if s.strip()]

    work = Path(tempfile.mkdtemp(prefix=f"adk-fixture-{a.stack}-"))
    repo = work / "repo"
    shutil.copytree(src / "project", repo)
    if not standards and (src / "default").exists():
        shutil.copytree(src / "default", repo, dirs_exist_ok=True)
    sh(["git", "init", "-q", "-b", "main"], repo)

    args = [sys.executable, str(KIT / "install" / "install.py"), "--target", str(repo),
            "--stacks", a.stack, "--tools", "generic", "--no-hooks", "--no-ci"]
    if standards:
        args += ["--standards", ",".join(standards)]
    sh(args, repo)
    (repo / ".agentic" / "specs" / "demo.md").write_text(SPEC, "utf-8")

    for cmd in meta.get("setup", []):
        sh(cmd, repo)
    for cmd in meta.get("format", []):
        sh(cmd, repo)

    sh([sys.executable, ".agentic/kit/gates/gate.py", "lock-tests", "--by", "test-designer"], repo)
    sh(["git", "add", "-A"], repo)
    sh(["git", "-c", "user.email=ci@example.invalid", "-c", "user.name=ci", "commit", "-q",
        "--no-verify", "-m", "fixture"], repo)
    code = sh([sys.executable, ".agentic/kit/gates/gate.py", "run", "--stage", "ci"], repo, check=False)
    report = repo / ".agentic" / "reports" / "gate-latest.md"
    if report.exists():
        print(report.read_text("utf-8"))
    if a.keep:
        print(f"kept: {repo}")
    else:
        shutil.rmtree(work, onexc=on_rm_error)
    print(f"FIXTURE {a.stack} [{','.join(standards) or 'no pack'}]: {'PASS' if code == 0 else 'FAIL'}")
    return code


if __name__ == "__main__":
    sys.exit(main())
