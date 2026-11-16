---
name: slice-into-tasks
description: Use when an approved spec or design must be broken into tasks, to produce thin end-to-end vertical slices with explicit blockers, each small enough for one fresh session.
---

# Slice into tasks

## What a good task is
- **Vertical:** a narrow path through every layer it needs (data, logic, interface, tests),
  ending in behaviour someone could demo. "Add the database table" is a layer, not a slice.
- **One session:** an implementer can finish it in one fresh context window. If you hesitate, split it.
- **Independently verifiable:** it has its own ACs (a subset of the spec's) and its own tests.
- **Stable wording:** describe behaviour, not file paths or code. They go stale. A short
  schema, enum or state machine is fine when it pins a decision more precisely than prose.

## Steps
1. **List the slices.** Start with the thinnest slice that proves the whole path works (a
   tracer bullet), then add slices that widen it.
   **Done when:** every spec AC is assigned to exactly one task.
2. **Put prefactoring first.** If existing code must be reshaped before the first slice, that
   is task 01. It changes structure only, and the existing tests stay green.
   **Done when:** no feature task includes unrelated restructuring.
3. **Wide changes use expand → migrate → contract.** For a rename or retype that touches many
   files: add the new form beside the old one, migrate the callers in batches sized by risk,
   then remove the old form. Each batch is a task that keeps the gate green.
   **Done when:** no single task changes more callers than one session can review.
4. **Set the blockers.** Each task lists the tasks it needs finished first. Tasks with no
   blockers form the **frontier** and can run in parallel, each on its own branch or worktree.
   **Done when:** the blocker graph has no cycles.
5. **Write the files** as `.agentic/tasks/NN-<slug>.md` from the task template. Number them in
   dependency order (blockers first), and set Status `ready` on the frontier, `draft` elsewhere.
   **Done when:** the files exist, and the human has approved the breakdown (full track).

## Parallel work
Run several tasks at once only when they touch different files. Each runs on
`task/NN-slug`, in its own worktree where the tool supports it. Merge into the integration
branch one at a time, re-running the gate after each merge.
