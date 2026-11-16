---
name: test-driven-slices
description: Use whenever writing tests or making tests pass, for red-green-refactor one behaviour at a time through agreed public seams, with rules that separate tests that prove behaviour from tests that only look busy.
---

# Test-driven slices

## The loop
1. **Red:** one test, for one behaviour, at an agreed seam. Run it and watch it fail **for
   the right reason**: the behaviour is missing, not a typo or a fixture error.
2. **Green:** the least code that makes it pass. No options, branches or abstractions that no
   test asks for yet.
3. **Refactor:** only on green. Improve names and structure, and re-run after each change.
4. Repeat for the next behaviour. One slice at a time: each test teaches you something that
   shapes the next one.

In this kit the work is split across two roles. The **test-designer** writes the acceptance
tests for a task slice (one per AC) before implementation, and locks them. The
**implementer** then runs the inner loop above, adding their own small unit tests as needed.
Writing every test for the whole spec up front is avoided: tests written far ahead of the
code tend to pin imagined behaviour.

## Seams
Agree the seam (the public interface a test calls) before writing the test, and record what
it catches and misses. Prefer the highest seam that still runs fast and deterministically.

## A good test
- Calls only the public interface, and asserts **observable behaviour**: return values,
  emitted events, persisted state read back through the public interface, and errors.
- Reads like a line of the spec, with the AC id and the behaviour in the name.
- Takes its expected values from **an independent source**: the spec, a worked example by
  hand, or a known-good literal.
- Survives a refactor that keeps the behaviour.
- Is deterministic: it controls the clock, randomness, ordering and I/O.

## Smells to reject
| Smell | Sign | Instead |
|---|---|---|
| Tautological | The expected value is computed with the same logic as the code | Hard-code the value from the spec or a worked example |
| Implementation-coupled | Mocks internal collaborators, calls private functions, or checks a side channel | Go through the seam, and assert the outcome |
| Over-mocked | More mock setup than assertions; mocks of your own modules | Fake only at process edges: network, clock, randomness, external services |
| Assertion-free | It "passes" because nothing threw | Assert the specific outcome |
| Snapshot dump | A large snapshot accepted without reading it | Assert the few fields that matter |
| Flaky | It passes on re-run | Hand it to the debugger. It is a bug in the test or the code |

## Done when
- The test was seen failing first, and the failure reason is recorded.
- The test passes with the smallest implementation.
- Nobody can delete the behaviour and keep the test green. Mutation testing checks this in CI.
