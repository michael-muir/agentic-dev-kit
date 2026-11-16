# Findings: T-NN: <reviewer role>, round N

| Field | Value |
|---|---|
| Verdict | pass \| changes-requested \| needs-human |
| Reviewed | <diff range, e.g. main...task/03-slug @ abc1234> |
| Inputs | <spec, standards files, survivors list: paths> |
| Context | fresh \| same-context (explain) |

## Findings

| ID | Severity | Location | Finding | Evidence | Suggested direction |
|---|---|---|---|---|---|
| R1 | critical \| major \| minor \| judgement | `path:line` | <what is wrong, citing the spec line or rule> | <failing test name, repro command, or quoted hunk> | <direction, not a patch> |

Severity:
- **critical**: wrong behaviour, data loss, security hole, or a safety issue. Blocks merge.
- **major**: an AC is missing or wrong, or a documented standard is violated. Blocks merge.
- **minor**: should be fixed, but doesn't block on its own.
- **judgement**: a reasoned opinion (smell, naming). The implementer may decline, with a reason.

## Coverage of this review
<What was checked and what was not, e.g. the attack catalogue sections covered.>
