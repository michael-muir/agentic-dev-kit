# Coding standards

Read by the **standards-reviewer** at review time. It isn't loaded into every agent's
context, so it can be detailed.

To start from a published standard instead of a blank page, choose one or more packs
(`.agentic/kit/standards/README.md`). Add them to `standards` in `.agentic/config.toml`
and run the installer with `--update`. This file is then generated from the packs, with
your own rules kept in a **Project rules** section at the end.

Put a rule here only if it **needs judgement**. Anything mechanical (formatting, banned APIs,
import order, file locations) belongs in a linter rule or a gate step, so it's checked every
time instead of remembered sometimes. The retro agent moves rules out of this file as checks
become possible.

Where a rule here conflicts with the kit's built-in smell baseline
(`.agentic/kit/skills/independent-review/SKILL.md`), this file wins.

## Design
- <e.g. Prefer a few deep modules (simple interface, lots of behaviour) over many shallow ones.>

## Naming
- <e.g. Use GLOSSARY terms in type and function names.>

## Errors
- <e.g. Library code never prints; it returns or raises typed errors.>

## Tests
- <e.g. Acceptance tests go through public interfaces only. Mock only at process boundaries.>

## Per-language notes
<Add sections per stack as needed.>
