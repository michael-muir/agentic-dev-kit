---
name: adversarial-attack
description: Use when red-teaming a change as the adversary, for a catalogue of attack angles, property-based, fuzz and mutation techniques per stack, and the rule that every finding is a failing test or a reproduction.
---

# Adversarial attack

Assume the code is wrong. Your output is **tests that fail** (findings) and **tests that
pass** (hardening). Write every test so it would still be correct for any valid implementation.

## Steps
1. **Start from the leads.** Mutation survivors and advisory failures from the verifier point
   at weakly tested code. For each survivor, write a test that kills it, or explain why the
   mutant is equivalent.
   **Done when:** every survivor is killed, or marked equivalent with a reason.
2. **Hunt for spec loopholes.** For each AC, ask how an implementation could satisfy its
   words and still be wrong for the user. Write that case as a test.
   **Done when:** each AC has at least one loophole test, or a note saying why there isn't one.
3. **Work through the catalogue** below, choosing the sections that apply to the change.
   **Done when:** every section is marked tried or not applicable in your findings.
4. **Generalise with properties.** Where behaviour has an invariant (round-trips, ordering,
   idempotency, conservation, bounds), write a property-based test, and fuzz parsers or
   decoders of untrusted input.
   **Done when:** each invariant you identified has a property test, or a note on why not.
5. **Review the existing tests** for the smells in `test-driven-slices`: tautological,
   assertion-free, over-mocked. Each one is a finding against the test, routed to the test-designer.
6. **File findings.** Each failing test becomes one finding row, with the test name as its evidence.

## Attack catalogue
| Area | Try |
|---|---|
| Boundaries | 0, 1, max, max+1, empty, single element, exactly-at-limit, off-by-one on ranges |
| Absence | null/None/nil, missing keys, empty strings vs missing, optional fields omitted |
| Size | very large inputs, deep nesting, long strings, many small items |
| Text | Unicode (combining marks, RTL, emoji, normalisation), case, whitespace, line endings, encodings |
| Numbers | negative, zero, NaN, ±Inf, overflow, underflow, precision loss, rounding modes, unit mix-ups, integer division |
| Time | time zones, DST transitions, leap days/seconds, clock going backwards, epoch boundaries, timeouts |
| Order & concurrency | different orderings, duplicates, concurrent calls, re-entrancy, races on shared state, cancellation |
| Failure paths | dependency errors, partial writes, retries, idempotency of retried operations, cleanup after failure |
| State | calling things in the wrong order, calling twice, using after close/dispose, stale caches |
| Platform | path separators, case-insensitive file systems, permissions, locale, 32/64-bit, endianness |
| Contracts | what callers of a changed interface assume (types, error behaviour, performance) |
| Hostile input | injection-shaped strings, path traversal (`../`), oversized headers, malformed encodings |

## Tools by stack
| Stack | Property-based | Fuzz | Mutation |
|---|---|---|---|
| python | hypothesis | atheris | mutmut |
| javascript / typescript | fast-check | jsfuzz / fast-check | StrykerJS |
| rust | proptest, quickcheck | cargo-fuzz | cargo-mutants |
| go | rapid, testing/quick | `go test -fuzz` | go-mutesting |
| dotnet | FsCheck, CsCheck | SharpFuzz | Stryker.NET |
| cpp | RapidCheck | libFuzzer, AFL++ | Mull |
| lua | lua-quickcheck | — | — |

When a tool isn't installed, write an example-based test for the same idea, and note the
missing tool for the retro.

## Limits
- Stop at full catalogue coverage, or 5 critical/major findings, whichever comes first.
- Behaviour changes are the implementer's job. If a fix would require the spec to change,
  file `needs-human`.
