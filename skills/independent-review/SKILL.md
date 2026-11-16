---
name: independent-review
description: Use when reviewing a diff as spec-reviewer or standards-reviewer, for an isolated single-lens review with restricted inputs, cited findings, a severity scale, and a built-in code-smell baseline.
---

# Independent review

Each review looks through **one lens**, in a **fresh context**, with **restricted inputs**.
Running two lenses separately means a clean result on one can't hide a failure on the
other. Code can follow every standard and still build the wrong thing, or build the right
thing and break every convention.

## Common steps
1. **Pin the range.** Use `git diff <base>...HEAD` (three dots, so it's measured from the
   merge-base) and `git log <base>..HEAD --oneline`. Confirm the diff isn't empty.
   **Done when:** the base, the HEAD sha and the file count are recorded at the top of your findings.
2. **Read only your lens's inputs** (listed in your role file). Use no implementer reasoning,
   and no other reviewer's output.
3. **Review hunk by hunk.** Each finding cites a **location** (`path:line`), the **rule or spec
   line** it breaks (quoted), and the **evidence** (a quoted hunk, a failing test, or a command
   and its output).
   **Done when:** every changed file was looked at, and every finding has all three.
4. **Classify** each finding with the findings template's severities: `critical`, `major`,
   `minor`, `judgement`. A judgement call is never `major`.
5. **Verdict.** `changes-requested` if any critical or major finding exists; `needs-human` if
   the right answer depends on a decision nobody has made; otherwise `pass`.
6. **Report your lens only.** Keep the other lens out, and compare severity only within your lens.

## Spec lens (spec-reviewer)
Look for:
- **Missing or partial:** an AC with no implementation, or one that covers only some of its cases.
- **Wrong:** it looks implemented, but behaves differently from the AC on some input. Show the input.
- **Unproven:** a test that names the AC but would still pass if the behaviour were removed.
- **Unrequested:** behaviour that no AC or non-goal covers (scope creep).
- **Spec gaps:** cases the spec doesn't decide, which come out as `needs-human`.

## Standards lens (standards-reviewer)
Sources, in priority order: the project's `CODING_STANDARDS.md` and contributor docs, then the
ADRs and the glossary, then the baseline below. A documented project rule overrides the
baseline. Skip what the gate's linters already enforce.

Baseline smells. Each is always a `judgement`, never a hard violation:

| Smell | What it looks like | Usual direction |
|---|---|---|
| Unclear name | Name doesn't say what it is, or uses a word the glossary says to avoid | Rename with the glossary term |
| Duplication | The same logic in two or more places in the diff, or copied from existing code | Extract once, call twice |
| Long function | One function doing several things you'd describe with "and" | Split by step |
| Long parameter list | More than about 4 parameters, or parameters that always travel together | Introduce a parameter object |
| Primitive obsession | Domain concepts passed as bare strings or ints (ids, money, units) | A small type |
| Feature envy | A function mostly using another module's data | Move the behaviour to the data |
| Shotgun surgery | One conceptual change needing edits in many unrelated places | Gather the responsibility |
| Leaky abstraction | Callers must know internals to use an interface correctly | Deepen the module, and narrow the interface |
| Speculative generality | Options, hooks or layers no test or AC needs | Delete until needed |
| Dead code | Unreachable branches, unused exports, commented-out blocks | Delete |
| Hidden side effect | A function whose name suggests a query but which mutates state or does I/O | Separate query from command, or rename |
| Inconsistent errors | Mixed error styles: exceptions, codes, silent nulls, printing | Follow the project's documented style |
| Magic values | Unexplained literals, especially units, limits and timeouts | A named constant with its unit |

Mechanical issues (formatting, import order, a banned API) are tagged `automatable`, so the
retro agent can turn them into a check.
