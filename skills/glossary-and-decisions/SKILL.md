---
name: glossary-and-decisions
description: Use whenever a domain term is introduced, used inconsistently, or a hard-to-reverse decision is made, to keep .agentic/GLOSSARY.md and .agentic/decisions/ (ADRs) current.
---

# Glossary and decisions

A shared vocabulary keeps specs, tests, code and PRs saying the same thing. ADRs keep the
"why" so later agents don't undo it by accident.

## Glossary entries

One row per term in `.agentic/GLOSSARY.md`:

| Column | Rule |
|---|---|
| Term | The single word the project uses. Singular, in the domain's language, not the code's. |
| Meaning | One sentence. Test it against an edge case: does the definition still decide it? |
| Avoid saying | Synonyms that cause confusion. Reviewers flag them in code and docs. |
| Example | One concrete instance. |

Steps:
1. Check whether the term or a synonym already exists. If it does, use it, or propose a rename
   to the human.
   **Done when:** there are no duplicate meanings in the file.
2. Stress-test the definition with one edge case the human confirms.
   **Done when:** the edge case is decided by the definition.

## ADRs

Write one (from `.agentic/kit/workflow/templates/adr.md`) when a decision is **hard to
reverse**, **surprising** to a newcomer, or a **real trade-off** between options with costs.
Number them in order: `.agentic/decisions/ADR-0001-<slug>.md`.

Steps:
1. Record at least two options that were considered, with their costs.
2. State the decision so it can be checked: a reviewer should be able to say whether a diff violates it.
3. When a decision changes, supersede the ADR. The old one is kept and marked "superseded by ADR-NNNN".

**Done when:** the ADR is linked from the spec or design note that needed it.
