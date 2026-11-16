## Enforced by tooling
Checked by `clang-format` and `clang-tidy` (`cppcoreguidelines-*`, `bugprone-*`,
`modernize-*`, `performance-*`, `readability-*`). Reviewers skip these:
- Layout, braces on every block, include order.
- Owning raw pointers, C-style casts, `new`/`delete` outside RAII, uninitialised members,
  narrowing conversions, missing `override`, `nullptr` over `0`/`NULL`, rule-of-five gaps.
- Pass-by-value of expensive types, unnecessary copies, const-correctness of locals.

## Design (guidelines P, I, C, R)
- Express intent in types. Strong types for ids and units, `enum class` for closed sets,
  `std::span` and `std::string_view` for non-owning views (I.4, I.13).
- Make interfaces precise and hard to misuse. Preconditions are stated and checked at the
  boundary (`Expects`/`assert`, or the project's contract macro) (I.6, I.7).
- RAII for every resource. Ownership is visible in the type: `std::unique_ptr` by default,
  `std::shared_ptr` only for genuinely shared lifetime, and raw pointers and references are
  non-owning (R.1, R.20, R.21).
- Rule of zero by default. If you define one special member, define or delete all five (C.20, C.21).
- Prefer composition. Keep class hierarchies shallow, and give polymorphic bases a public
  virtual or protected non-virtual destructor (C.35).
- Keep headers minimal: forward-declare where possible, and no `using namespace` in headers (SF.7).
- Concurrency: no data races. Prefer tasks and message passing to shared mutable state, and
  guard shared state with a mutex owned next to the data it guards (CP.2, CP.50).

## Naming
- Pick one project convention and record it in Project rules below. The guidelines suggest
  `underscore_style` for functions and variables and `PascalCase` or `underscore_style` for
  types (NL.8, NL.10). Use glossary terms.
- No Hungarian notation, and no `ALL_CAPS` except macros (NL.5, ES.9).

## Errors (guidelines E)
- Use exceptions for errors a caller can't reasonably check in advance, or `std::expected`
  (C++23) / an outcome type where the project's ADRs choose it. Be consistent per module (E.2, E.27).
- Throw by value, catch by reference, and never throw from destructors, `swap` or move
  operations (E.15, C.36, C.66). Mark functions `noexcept` when they can't throw.
- Don't use error codes and exceptions for the same condition.

## Tests
- Tests go through the public interface. Build and run them with sanitizers
  (`-fsanitize=address,undefined`) in CI.
- No reliance on undefined or implementation-defined behaviour in expected values.

## Documentation
- Headers document the contract (preconditions, postconditions, ownership, thread safety)
  for each public function and type. Implementation files explain why.
