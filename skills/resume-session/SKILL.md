---
name: resume-session
description: Use at the start of every session in a project with a .agentic folder, to rebuild context from state files and git, check them against each other, and adopt the right role.
---

# Resume a session

The goal is to continue someone else's work as if you'd been there, trusting only what can
be checked.

## Steps

1. **Read the state.** Read `.agentic/STATE.md`, then the newest file in `.agentic/handoffs/`
   (names sort by time), then the task file that STATE.md marks as active.
   **Done when:** you can name the spec, task, phase, owner and next step.

2. **Check against git.** Run `git status`, `git branch --show-current`, and
   `git log --oneline -10`. Compare them with the handoff's "Branch @ commit".
   - Commits after the handoff's sha: someone worked without a handoff. Read those commits,
     and note it.
   - Uncommitted changes: they belong to an unfinished session. Read the diff before touching anything.
   - The handoff names a different branch: switch to it, or ask the human if it's unclear.
   **Done when:** you've written down any discrepancy, and git is the version you believe.

3. **Re-check claims that matter.** If the handoff says the gate passed but HEAD has moved,
   or the tree is dirty, that claim is stale. Treat it as unverified.
   **Done when:** each "Evidence" claim you rely on is either still valid for HEAD, or marked stale.

4. **Adopt the role.** Load `.agentic/kit/agents/core/<owner>.md` (or the domain agent file),
   and every skill in its `skills:` list. If you're the orchestrator, or there's no active
   task, load the orchestrator.
   **Done when:** you've read the role file and its skills in this session.

5. **Say where things stand.** In one short message, tell the human the role you're playing,
   the task, the next step, and any discrepancies from step 2. Then start.
   **Done when:** the message is sent.

## Notes
- STATE.md missing or empty: the project has just been installed. Act as orchestrator.
- If a handoff says `Context: same-context`, reviews from that session count less. The
  orchestrator may re-run them in a fresh context.
