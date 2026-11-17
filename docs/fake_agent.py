#!/usr/bin/env python3
"""Stand-in for an LLM CLI, used by the smoke test to exercise runner/run.py.

Reads the prompt file, takes the role and task from its first line, hands the task to the next
role (as a real agent would through the handoff skill), and commits with the Agent-Role trailer.
"""
import re
import subprocess
import sys
from pathlib import Path

NEXT = {"test-designer": "implementer", "implementer": "verifier", "verifier": "integrator"}

first = Path(sys.argv[1]).read_text("utf-8").splitlines()[0]
m = re.match(r"# Unattended run: (\S+) on (\S+)", first)
role, task = m.group(1), Path(m.group(2))
text = task.read_text("utf-8")
if role in NEXT:
    text = re.sub(r"(\|\s*Owner\s*\|\s*)[^|]*?(\s*\|)", rf"\g<1>{NEXT[role]}\g<2>", text)
else:
    text = re.sub(r"(\|\s*Status\s*\|\s*)[^|]*?(\s*\|)", r"\g<1>in-review\g<2>", text)
text += f"- smoke {role}: done\n"
task.write_text(text, "utf-8")
subprocess.run(["git", "add", "-A"], check=True)
subprocess.run(["git", "-c", "user.email=fake@example.invalid", "-c", "user.name=fake", "commit", "-q",
                "--no-verify", "-m", f"chore(agentic): {role} step\n\nAgent-Role: {role}"], check=True)
print(f"fake agent: {role} done")
# Report usage the way Claude Code's `-p --output-format json` does.
print('{"type": "result", "total_cost_usd": 1.5, "usage": {"input_tokens": 1000, "output_tokens": 500}}')
