<!-- agentic-dev-kit:begin (managed by the installer; edits inside these markers are replaced on update) -->
# Agent instructions

This project uses **agentic-dev-kit**. Work is done by role-based agents, and all state lives
in `.agentic/`.

## Start of every session
Follow `.agentic/kit/skills/resume-session/SKILL.md`. In short:
1. Read `.agentic/STATE.md`, then the newest file in `.agentic/handoffs/`.
2. Open the active task in `.agentic/tasks/`. Its **Owner** field is the role you play.
3. Load that role from `.agentic/kit/agents/core/<role>.md` (domain experts:
   `.agentic/kit/agents/domains/<id>/agent.md`), plus every skill it lists from
   `.agentic/kit/skills/`.
4. If there is no active task, or you were given a new request, act as **orchestrator**.

## End of every session
Follow `.agentic/kit/skills/handoff/SKILL.md`: write a handoff note and update `STATE.md`.
If it isn't written down, the next agent can't know it happened.

## Ground rules
- **The gate decides.** `python .agentic/kit/gates/gate.py run --stage pre-push` (CI runs
  `--stage ci`). Quote its result; never claim a pass you didn't observe for the current commit.
- **Locked tests** (`.agentic/locks/tests.lock.json`) change only through test-designer or
  adversary. Never bypass hooks (`--no-verify`).
- Stay inside your role's `writes:` list. Anything outside it goes in your handoff as a request.
- Agent and domain-expert directory: `.agentic/REGISTRY.md`. Workflow:
  `.agentic/kit/workflow/pipeline.md`.
- Vocabulary: `.agentic/GLOSSARY.md` · Decisions: `.agentic/decisions/` · Standards (read at
  review): `.agentic/CODING_STANDARDS.md`.
<!-- agentic-dev-kit:end -->

## Project notes
<Anything specific to this project that every agent needs: how to run it, where things live.
 Keep it short. Rules belong in CODING_STANDARDS.md or in a gate check.>
