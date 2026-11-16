## Enforced by tooling
Checked by `gofmt`, `go vet` and `golangci-lint` (standard set + revive, errorlint,
misspell, goimports, errname, gocritic, nolintlint, exhaustive, bodyclose, noctx,
prealloc, unconvert). Reviewers skip these:
- Formatting and import grouping, unchecked errors, unused code, vet findings,
  staticcheck issues.
- Doc comments on exported identifiers, receiver and initialism naming (`ID`, `URL`),
  error wrapping with `%w` and inspection with `errors.Is`/`errors.As`.
- Exhaustive enum switches, closed HTTP bodies, `context` on requests, and `//nolint` only
  with the linter named and a reason given.

## Design
- Keep packages small and focused, named for what they provide (`order`, not `util`). Avoid
  package-level mutable state.
- Accept interfaces, return concrete types. Define interfaces where they're used, keep them
  small (one or two methods), and add them only when a second implementation or a test
  seam needs one.
- Make the zero value useful where you can. Constructors (`NewX`) only when setup is required.
- Pass `context.Context` as the first parameter of anything that blocks or does I/O. Never
  store it in a struct.
- Concurrency: whoever starts a goroutine owns its lifetime and makes sure it ends. Prefer
  channels for handing over ownership, and mutexes for protecting state.
- Return early. Keep the happy path at the left edge.

## Uber-specific rules
- Verify interface compliance at compile time where it matters: `var _ http.Handler = (*Handler)(nil)`.
- Copy slices and maps at API boundaries when storing or returning internal state.
- Use `defer` to clean up locks and files. Channel size is 0 or 1 unless a larger buffer is justified.
- Start enums at `iota + 1`, so the zero value means "unset".
- Avoid `init()`, mutable globals and embedding types in public structs. Use functional
  options for constructors with optional parameters.
- Use `time.Duration` and `time.Time` for time, never bare ints.
- Exit only in `main()`, and call `os.Exit`/`log.Fatal` at most once, at the end of `run()`.

## Naming
- Short, clear names, scaled to scope: one letter for short loops, descriptive names for
  package-level identifiers. No `Get` prefix on getters.
- Package names are lower-case single words. Don't repeat them in identifiers
  (`order.Order`, not `order.OrderStruct`).
- Error variables are `ErrX`, and error types are `XError`.

## Errors
- Errors are values: return them, and handle each one once (log *or* return, not both).
- Add context when wrapping (`fmt.Errorf("load order %s: %w", id, err)`). Error strings are
  lower-case, with no trailing punctuation.
- `panic` only for programmer errors that are truly unrecoverable, never across package APIs.

## Tests
- Table-driven tests with `t.Run` subtests, and `t.Helper()` in helpers. Compare with `cmp`
  or explicit checks, and report as `got X, want Y`.
- Tests use the package's exported API where possible (`package foo_test`).

## Documentation
- Every exported identifier has a doc comment beginning with its name. Package docs go in
  `doc.go` for non-trivial packages.
