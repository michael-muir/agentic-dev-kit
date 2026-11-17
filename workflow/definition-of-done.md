# Definition of done

A task is `done` only when every line below is true **and evidenced**: a file path, test name
or report. "I checked" is not evidence.

- [ ] Every acceptance criterion in the task has at least one test naming its id, and the
      test was observed failing before the implementation.
- [ ] `gate.py run --stage ci` passes for the PR's HEAD commit. The report is in
      `.agentic/reports/gate-latest.md` and is linked from the PR.
- [ ] Locked tests are unchanged, or re-locked by test-designer/adversary with a reason in a
      handoff note.
- [ ] Every reviewer for the track returned `pass`, or a human accepted the open findings in writing.
- [ ] No debug instrumentation, commented-out code, or TODO without a task reference.
- [ ] New terms are in `.agentic/GLOSSARY.md`, and decisions that are hard to reverse have an ADR.
- [ ] If the task's Docs field is `needed`: user-facing docs are updated, their examples have
      been run, and `CHANGELOG.md` has an Unreleased entry.
- [ ] If the task has a performance budget: the performance-reviewer's measurements show it is
      met, and the benchmarks are committed.
- [ ] The PR follows `workflow/templates/pull-request.md`, including the merge-risk section.
- [ ] `STATE.md` and the task file reflect the final status, and a handoff note exists.
