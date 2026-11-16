# Tracks

The Orchestrator picks a track per task and records it in the task file. If in doubt, choose
**full**. The human can always override.

## Choosing

Answer these four questions about the change:

| Question | Any "yes" → full |
|---|---|
| **Door**: is it hard to reverse? Data migrations, public API or file-format changes, deletions, published releases. | yes |
| **Blast radius**: does it reach beyond one module, or affect users, consumers, other teams, or safety? | yes |
| **Sensitivity**: does it touch auth, secrets, untrusted input, money, network, file system, or concurrency? | yes |
| **Domain**: does an enabled domain expert's trigger match the task? | yes |

All "no" → **lite**.

## Lite

`tests → implement → verify → review (spec + standards)`

- No separate design phase. The Test Designer agrees seams in the task file.
- The adversary is optional. Run it if the verifier reports mutation survivors.

## Full

`spec → design → tests → implement → verify → review (spec + standards + adversary + security + domain) → integrate`

- Human approves the spec and the task breakdown.
- The adversary is mandatory, ideally on a different model or vendor from the implementer.
- The PR is labeled `one-way-door` when the Door answer was yes, and needs human sign-off.

## Bug fixes

Bugs enter at `tests`: the Debugger (or Test Designer) writes a failing regression test that
reproduces the reported symptom. Then apply the track rules above to the fix.
