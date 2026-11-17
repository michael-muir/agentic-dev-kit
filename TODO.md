# To do

Planned improvements to agentic-dev-kit. Tick an item when it ships, and note the version
in `CHANGELOG.md`. Move an item to **Done** rather than deleting it.

## Backlog

- [ ] **Measuring the agents.** An evaluation suite: sample tasks with planted bugs, scored on
  whether the adversary and reviewers catch them. It shows whether a kit change made the
  agents better or worse.
- [ ] **Process visibility.** An `agentic status` command showing the frontier (tasks that
  can start), blocked tasks and review rounds per task, plus a metrics roll-up the retro
  agent can use.
- [ ] **Large codebases.** An `ARCHITECTURE.md` map that the architect keeps current, so
  agents don't re-explore the repo every session.
- [ ] **Monorepos.** Stacks per subdirectory (`[[project.paths]]` in `config.toml`). Today
  the gate assumes one project root.
- [ ] **More test types.** Gate profiles or steps for end-to-end tests (Playwright),
  contract tests, performance budgets with benchmark gates, and migration-reversibility checks.
- [ ] **Issue tracker.** Optional sync between `.agentic/tasks/` and GitHub Issues, for
  teams that work there.
- [ ] **Flaky tests.** A quarantine policy: a flaky test goes to the debugger, and can't be
  silently retried until it passes.
- [ ] **AI provenance.** Mark AI-authored commits with a trailer (beyond `Agent-Role`, e.g.
  `Agent-Model`), for organisations that need it for audit or licensing.

## Still to verify from 0.3.0

- [ ] Push and confirm `kit-ci` passes on GitHub: the workflow syntax, the pinned action
  versions, and the smoke test on Windows and Linux.
- [ ] Go, C++ and Lua fixtures pass in CI. They haven't run anywhere yet, and C++ is the
  most likely to need tweaks.
- [ ] `agent-review.yml` runs with a real `ANTHROPIC_API_KEY`, and the action inputs match
  claude-code-action v1.
- [ ] Runner end to end with real `claude` and `codex` sessions, not the scripted fake engine.
- [ ] Devcontainer builds and runs the gate. Consider adding a network allow-list.
- [ ] Cost capture against real engines: Claude Code's JSON result fields, and Codex's
  `turn.completed` usage events. So far only checked with the scripted fake engine and samples.

## Done

- [x] **More roles** (0.4.0). Docs writer, performance reviewer and release manager as core
  roles, plus an accessibility domain expert.
- [x] **Cost control** (0.5.0). `[budgets]` modes off/track/warn/enforce, per-task overrides,
  `--ignore-budgets`, a Spend row per task, and `run.py costs`.
