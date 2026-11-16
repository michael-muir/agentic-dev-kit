## Enforced by tooling
Checked by `clang-format` (Google style) and `clang-tidy`. Reviewers skip these:
- Layout: 80 columns, 2-space indent, brace placement, include order.
- Naming: `CamelCase` types and functions, `snake_case` variables, a trailing `_` on
  private/protected members, `kConstant` constants and enumerators, `lower_case` namespaces,
  `UPPER_CASE` macros.
- `google-*` checks: explicit single-argument constructors, no `using namespace`
  directives, no unnamed namespaces in headers, integer types, casting.

## Design
- Headers are self-contained, with `#define` guards named `<PROJECT>_<PATH>_<FILE>_H_`.
  Include what you use, and forward-declare only where the guide permits.
- Prefer composition to inheritance. Inheritance is public. Multiple inheritance is only
  for interfaces (pure abstract classes with an `Interface` suffix, where the project uses that).
- Mark single-argument and conversion constructors `explicit`. Copy and move are either
  supported, or explicitly deleted, in the public section.
- Use `std::unique_ptr` for ownership transfer. `std::shared_ptr` only with a clear reason.
- Avoid static and global variables with non-trivial destructors.
- Pass inputs as values or `const&`, and outputs as return values (or `std::optional`).
  Non-optional output parameters are references, and optional ones are pointers.
- Write short functions. Over about 40 lines, look for a split.

## Naming
- Names describe the purpose in the glossary's terms. Abbreviations only when widely known
  outside the project.
- Accessors and mutators may be `snake_case` matching the member (`count()`, `set_count()`).

## Errors
- Google style doesn't use C++ exceptions. Report errors with `absl::Status` /
  `absl::StatusOr<T>` (or the project's equivalent recorded in an ADR), and check every
  returned status.
- Use `CHECK`/`DCHECK` (or `assert`) for invariants, not for recoverable errors.

## Tests
- GoogleTest. Test names are `CamelCase` and describe the behaviour (`TEST(ParserTest,
  RejectsUnterminatedString)`), with the kit's AC id in the name where one applies.

## Documentation
- File comments where a file's purpose isn't obvious. Every class gets a comment saying
  what it is for and how to use it, with thread-safety noted.
- Function declarations get a comment describing inputs, outputs and side effects, unless
  they're obvious. Implementation comments explain tricky parts.
- `TODO(username or issue): explanation`. In this kit, reference the task id.
