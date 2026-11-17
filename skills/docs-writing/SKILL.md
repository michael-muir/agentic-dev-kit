---
name: docs-writing
description: Use when writing or updating user-facing documentation (README, guides, API reference, examples, changelog), to document what changed for readers, keep every example runnable, and avoid docs that drift from the code.
---

# Docs writing

Write for someone arriving cold who wants to get something done. Docs that are wrong are
worse than missing docs, so everything you write must be checkable against the code.

## Steps
1. **Know the reader's task.** For each change, name who reads about it (a new user, an
   integrator, an operator, a contributor) and what they're trying to do.
   **Done when:** each change has a reader and a task in your notes.
2. **Put it where they'll look.**
   | Reader needs | Goes in |
   |---|---|
   | What it is, and the first five minutes | `README.md` |
   | How to do a specific task | a guide in `docs/` |
   | Exact options, parameters, errors | reference docs, or generated API docs |
   | What changed since last time | `CHANGELOG.md` → `## Unreleased` |
   | Why it's built this way | an ADR (architect), linked from the docs |
   **Done when:** each change lands in one place, and other places link to it rather than repeating it.
3. **Write it.** Task-first headings ("Rotate an API key", not "Key management"). Steps
   numbered, with one action each. Examples you can copy as they are, with real values or
   obvious placeholders (`<your-token>`). State defaults, limits and units. Use glossary terms.
   **Done when:** a reader can complete the task without opening the source code.
4. **Prove it.** Run every command and example, or turn it into a doc test (Python
   doctest, Rust doc tests, `go test` examples, .NET `<example>` blocks compiled in a test
   project). Check that every link resolves.
   **Done when:** each example has an observed result in the handoff. An example that can't
   be run is marked as illustrative.
5. **Remove what's stale.** Search the docs for the old names, flags and behaviour you
   changed, and update or delete each hit.
   **Done when:** the search for old terms returns nothing outside the changelog.

## Changelog entries
- Write from the user's side: "You can now export reports as CSV", not "Added CsvWriter class".
- Mark breaking changes **Breaking**, with the migration step in the same entry.
- One line per change, with the task or AC id at the end: `(T-04, REPORT-AC-2)`.
