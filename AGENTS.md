# Working on agentic-dev-kit itself

This repo is the source of a kit that gets installed into other projects. These notes are for
agents changing the kit. The instructions installed into projects are
`project-skeleton/AGENTS.md`.

- Agent roles: `agents/core/*.md` and `agents/domains/*/agent.md`. They follow `agents/_schema.md`.
- Procedures: `skills/<name>/SKILL.md`. Write them using `skills/agent-authoring-guide/SKILL.md`.
- Anything tool-specific (Claude, Copilot, Cursor) is **generated** by `adapters/build.py`.
  Edit the neutral source files, never the generated output.
- `gates/gate.py`, `adapters/build.py` and `install/install.py` use only the Python 3.11+
  standard library. Keep it that way, so the kit runs wherever Python does.
- After changing scripts, run the smoke test in `docs/testing-the-kit.md` and include its
  result in the PR. After changing a gate profile or standards pack, also run its fixture
  (`python fixtures/fixture_test.py --stack <stack> --standards <pack>`).
- Bump `VERSION` and add a `CHANGELOG.md` entry with every change that alters installed files.
