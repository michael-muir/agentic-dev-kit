## Summary
<The smallest view that makes the change clear: pseudocode, a call tree, a mermaid diagram,
 a shallow file tree, or a focused diff. Put each visual next to the sentence it supports.>

## Acceptance criteria → evidence

| AC | Test(s) | Result at <sha> |
|---|---|---|
| FEAT-AC-1 | `tests/test_feature.py::test_feat_ac_1_…` | pass |

## Before / after
<Screenshots for visual changes. Otherwise the test that failed before and passes after, or
 console output.>

## Gate
`gate.py run --stage ci` at <sha>: **pass**. Report: `.agentic/reports/gate-latest.md`
(summary pasted below).

## Review record

| Reviewer | Rounds | Verdict | Findings closed / accepted |
|---|---|---|---|
| spec-reviewer | 1 | pass | 2 / 0 |
| adversary (<model>) | 2 | pass | 3 / 1 accepted by <human> |

## Merge risk
- **Door:** one-way \| two-way: <why>
- **Blast radius:** <one word>: <ramifications for consumers, users, data, performance>
- **Rollback:** <how to undo, and what can't be undone>

Spec: <link> · Task: <link> · ADRs: <links>
