---
name: process-retrospective
description: Use after a spec ships, after a painful session, or on request, to find what slowed agents down or let defects through, and turn each cause into a concrete change to checks, standards, docs or agent files.
---

# Process retrospective

Fix the environment, not the agent. A rule an agent has to remember fails some of the time.
A check fails the build every time.

## Steps
1. **Gather the evidence.** Read the handoffs, findings and gate reports for the period. Count
   repeated findings, review rounds per task, debug sessions, and "Unverified" items.
   **Done when:** you have a list of incidents, each with a file reference.
2. **Find candidates** in each category:

| Category | Ask |
|---|---|
| Missing checks | Could a linter, type check, test or gate step have caught it? Is an existing check silently not running (wrong stage, skipped, tool missing in CI)? |
| Standards | Was a judgement rule broken repeatedly, or is a rule unclear or obsolete? |
| Navigation | Did agents spend long finding something? Would a pointer in AGENTS.md or a doc help? |
| Information access | Did an agent lack something it needed: logs, a service, credentials, a test environment? |
| Agent files | Are there instructions agents ignore, contradict, or already follow by default (no-ops)? Is a file so long that key rules get lost? |
| Process | Did tasks exceed one session? Did reviews repeat each other? Was the track choice wrong? |
| Tool economy | Were there expensive or repetitive tool calls a script would replace? |

3. **Choose where each fix lives**, preferring the most deterministic option:
   1. A gate step, linter rule or type (mechanical rules always go here).
   2. A test or fixture.
   3. `CODING_STANDARDS.md` (judgement rules).
   4. A doc, with a pointer from `AGENTS.md`.
   5. An agent or skill file in the kit repo (as an upstream proposal).
   **Done when:** each candidate has one location and the exact change.
4. **Prune.** Propose removing instructions that changed nothing, duplicates, and stale
   rules. Always-loaded files (`AGENTS.md`) stay short: pointers, not content.
5. **Present the candidates by severity** (defects that escaped, then wasted rounds, then
   friction), and apply the approved project changes.
   **Done when:** `.agentic/findings/retro-YYYY-MM-DD.md` records each one and its status.
