## Enforced by tooling
Checked by `cargo fmt` and `cargo clippy` with pedantic lints and `missing_docs` as errors.
Reviewers skip these:
- Formatting, and naming case (`snake_case`, `UpperCamelCase`, `SCREAMING_SNAKE_CASE`).
- Missing docs on public items, needless borrows and clones, casts that lose precision,
  `unwrap` in places clippy flags, redundant closures, and similar lint-level issues.

## Design (API Guidelines C-*)
- Implement the common traits eagerly where they make sense: `Debug` always, then `Clone`,
  `PartialEq`/`Eq`, `Hash`, `Default`, `Display` for user-facing types (C-COMMON-TRAITS).
- Conversions use the standard traits (`From`, `TryFrom`, `AsRef`), and conversion method
  names follow `as_` (free), `to_` (expensive), `into_` (consuming) (C-CONV).
- Constructors are `new` or `with_*`. Use builders for types with many optional parameters (C-BUILDER).
- Arguments express ownership needs: take `&str`/`&[T]`/`impl AsRef<…>` where borrowing is
  enough, and `impl Into<…>` sparingly (C-GENERIC).
- Use newtypes for ids, units and validated values (C-NEWTYPE). Make invalid states
  unrepresentable with enums.
- Keep `pub` minimal. Use `pub(crate)` for internal sharing, and seal traits that downstream
  code mustn't implement (C-SEALED).
- `unsafe` only where needed, wrapped in a safe API, with a `// SAFETY:` comment on every block
  stating the invariant relied on.

## Naming
- Follow RFC 430 casing, which tooling enforces, and the getter convention: `name()`, not
  `get_name()` (C-GETTER). Iterator methods are `iter`, `iter_mut`, `into_iter` (C-ITER).
- Glossary terms in type and function names. Avoid stuttering (`config::ConfigError` → `config::Error`).

## Errors
- Libraries return `Result<T, E>` with a meaningful error type that implements
  `std::error::Error` (thiserror is fine). Applications may use `anyhow` at the top level.
- No `unwrap`/`expect` on recoverable paths. `expect("reason")` is acceptable only for
  invariants, and states the invariant.
- Panics are for bugs. Document them under `# Panics` (C-FAILURE).

## Tests
- Unit tests live in `#[cfg(test)] mod tests` next to the code. The kit's locked acceptance
  and adversarial tests live in `tests/` as integration tests.
- Doc examples compile and run. Prefer `?` in examples over `unwrap` (C-QUESTION-MARK).

## Documentation
- Every public item has docs, starting with a one-line summary. Include `# Examples` for
  key APIs, and `# Errors`, `# Panics`, `# Safety` sections where they apply (C-FAILURE).
- Crate-level docs (`//!`) explain what the crate is for and how to start.
