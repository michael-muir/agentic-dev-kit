---
name: handoff
description: Use before ending any session, switching roles, or running low on context, to write a handoff note and update STATE.md so any agent or model can continue the work.
---

# Write a handoff

A handoff is a note to a stranger who has your files but none of your memory. Write it so
they can start without asking you anything.

## Steps

1. **Commit or describe your changes.** Commit finished work on the task branch. For
   unfinished work, either commit it with `wip:` or leave it uncommitted and say exactly
   which files are half-done.
   **Done when:** `git status` matches what the note will say.

2. **Write the note** at `.agentic/handoffs/YYYY-MM-DD-HHMM-<role>-<task-slug>.md` (use the
   local time, 24-hour clock), following `.agentic/kit/workflow/templates/handoff.md`.
   - **Evidence** lists only what you observed this session: the command, its result, and the
     commit it ran against. Anything else goes under "Unverified".
   - **Pointers, not copies.** Link specs, ADRs, findings and commits by path instead of
     summarising them.
   - **One next step**, concrete enough to start on straight away.
   - **Redact** secrets, tokens, personal data and internal hostnames as `<REDACTED>`.
   **Done when:** every template section is filled, or says "none".

3. **Update STATE.md**: the timestamp and your role/model, the current focus row, the next
   step, the waiting-on-human list, the open-tasks table, and the handoff link at the top of
   "Recent handoffs" (keep 5).
   **Done when:** a reader of STATE.md alone would know the next step.

4. **Update the task file**: Status, Phase, Owner, and a Log line linking your note.
   **Done when:** the task's Owner names the role that acts next.

5. **Commit the state** with `chore(agentic): handoff <role> <task>`, so another machine or
   model can resume from the remote.
   **Done when:** the commit exists. Push it if the branch tracks a remote and the human allows pushes.
