---
name: systematic-debugging
description: Use for any bug, flaky test or performance regression whose cause isn't obvious after one focused attempt, for a phase-gated loop that builds a reproducible signal before theorising and ends with a regression test.
---

# Systematic debugging

Work through the phases in order. Each phase ends with a gate. If you skip a phase, write
down why.

**Redact first.** Replace secrets in commands, logs and notes with `<REDACTED>`, and quote
only the lines that carry the signal.

## 1. Signal
Build one command that goes red on **this** bug: a failing test, a script, a replayed
request, a fuzz seed, or a bisect harness. Then make it faster, deterministic, and sharper.
For intermittent bugs, aim for a high reproduction rate, such as a loop of 100 runs.
**Gate:** you can name the command, you've run it, and it fails in seconds without anyone
watching. Hold off reading code for theories until this exists. If you can't build it, say
what you tried and ask the human for access, an artifact, or permission to add instrumentation.

## 2. Minimise
Confirm the failure matches the reported symptom, not a nearby one. Then cut the inputs,
steps, configuration and callers one at a time.
**Gate:** removing any remaining element makes the signal pass.

## 3. Hypothesise
Write 3–5 ranked hypotheses. Each one predicts something: "if X is the cause, then changing
Y makes it pass, or changing Z makes it worse."
**Gate:** every hypothesis has a prediction that can be tested. Sharpen or drop the rest.

## 4. Instrument
Test one prediction at a time, changing one variable at a time. Prefer a debugger or REPL,
then targeted logs at boundaries. Tag every temporary log line with a unique marker such as
`DEBUG-` plus 4 hex digits, so you can find and remove them all with one search. The gate's
`builtin:debug-tags` check fails if any are left. For performance problems, measure a
baseline first, then bisect.
**Gate:** one hypothesis is confirmed by its prediction, and the others are ruled out or deprioritised.

## 5. Fix behind a regression test
Turn the minimised reproduction into a test at a seam that exercises the real call path, and
watch it fail. Fix the root cause. Watch the test pass, then re-run the phase 1 signal on the
original scenario. If no honest seam exists, record that as a design finding.
**Gate:** the test went from red to green, and the original signal is green.

## 6. Clean up
- Remove all temporary logs, and delete throwaway harnesses (or move them to `.agentic/research/`).
- Record the confirmed hypothesis in the commit message and the handoff.
**Gate:** `gate.py run --stage pre-push` passes.
