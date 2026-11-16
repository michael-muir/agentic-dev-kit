---
name: pull-request-evidence
description: Use when opening a pull request, to write a PR body that shows what changed in the smallest clear form, proves it works with before/after evidence, and rates merge risk by reversibility and blast radius.
---

# Pull-request evidence

The reader is a busy human deciding whether to merge. Give them the shape of the change, the
proof that it works, and the risk, in that order. Skip preambles.

## Steps
1. **Summary: show, then tell.** Pick the smallest view that makes the point:
   - pseudocode, for logic
   - a call tree, for control flow across functions
   - a mermaid diagram, for interactions between components or data flow
   - a shallow file tree, for a reorganisation
   - a focused diff, when the surrounding structure already exists
   Put one or two sentences beside each visual. Use the glossary's terms.
   **Done when:** a reviewer can describe the change after reading the Summary alone.
2. **AC → evidence table.** One row per acceptance criterion, with the test that proves it,
   and its result at the PR's HEAD sha.
   **Done when:** every task AC has a row.
3. **Before / after.** Visual changes get screenshots. Everything else gets the test or
   command that failed before and passes now, with the output trimmed to the lines that matter.
   **Done when:** at least one before/after pair is shown.
4. **Gate and review record.** Paste the gate summary, with the sha it ran against. Then add a
   table of reviewers, rounds, verdicts, and how many findings were fixed or accepted, with
   links. Flag any `same-context` review.
5. **Merge risk.**
   - **Door:** *one-way* (hard or impossible to undo: data migrations, deletions, public
     contracts, releases) or *two-way* (a revert undoes it). Say why.
   - **Blast radius:** one word (`local`, `module`, `service`, `users`, `ecosystem`), then what
     could break: consumers, performance, data, layout, compatibility.
   - **Rollback:** the steps, and anything that can't be rolled back.
   **Done when:** all three are filled in. One-way doors get the `one-way-door` label.
