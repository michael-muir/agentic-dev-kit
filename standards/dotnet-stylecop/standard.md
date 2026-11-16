## Enforced by tooling
Checked by `dotnet format` and `dotnet build -warnaserror` through `.editorconfig` and
`Directory.Build.props`. Reviewers skip these:
- Formatting, Allman braces, file-scoped namespaces, `using` placement and order.
- Naming: PascalCase types and members, `I` on interfaces, `T` on type parameters,
  `_camelCase` private fields, camelCase locals and parameters.
- Language keywords over BCL type names (`int`, not `Int32`), no `this.`, explicit accessibility.
- Nullable reference types are on, and their warnings are errors.
- The recommended .NET analyzer set, with Security-category rules as errors.
- StyleCop: member order (fields, constructors, properties, methods; public before private;
  static before instance), one type per file with a matching file name, and spacing/readability rules.
- XML documentation on public API is required (CS1591 is an error outside test projects).

## Design
- Follow the .NET Framework Design Guidelines for public API: types are nouns, methods are
  verbs, and properties have no observable side effects or heavy work.
- Keep the public surface small. Default to `internal` and `sealed`, and open up deliberately.
  `InternalsVisibleTo` is fine for tests.
- Prefer composition and small interfaces over deep inheritance. Define an interface when
  there are, or will soon be, two implementations, or at a seam tests need to fake.
- Use records (or `readonly record struct`) for values and DTOs. Use classes for entities
  with identity and behaviour.
- Use dependency injection through constructors. Avoid the service-locator pattern and
  static mutable state.
- Async all the way: `async`/`await` end to end, a `CancellationToken` last on I/O-bound
  methods, and no `.Result` or `.Wait()`. In library code, use `ConfigureAwait(false)` where the
  project's ADRs say so.
- Use `IReadOnlyList<T>` or `IEnumerable<T>` for inputs and outputs that callers must not mutate.

## Naming
- Names say what something *is* or *does* in the domain's terms (GLOSSARY.md). No
  abbreviations except well-known ones (`Id`, `Uri`, `Xml`).
- Async methods end in `Async`. Boolean properties read as assertions (`IsEnabled`, `HasItems`).
- Don't use Hungarian notation or type names in identifiers (`customerList` → `customers`).
- Exception types end in `Exception`, and event-argument types end in `EventArgs`.

## Errors
- Throw exceptions for exceptional conditions, not for control flow. Use the `Try…` pattern
  (`bool TryParse(…, out T)`) where failure is expected and frequent.
- Throw the most specific built-in exception that fits (`ArgumentNullException`,
  `ArgumentOutOfRangeException`, `InvalidOperationException`). Create custom exceptions only
  when callers need to catch them specifically.
- Validate public arguments early with `ArgumentNullException.ThrowIfNull` and its relatives.
- Catch only what you can handle. Never swallow exceptions. Rethrow with `throw;` to keep the stack trace.
- Log through `ILogger<T>` with structured message templates (`"Order {OrderId} failed"`), not
  string interpolation.

## Tests
- One test project per production project (`<Project>.Tests`), using the project's chosen
  framework (xUnit, NUnit or MSTest), consistently.
- Test names state the behaviour: `Method_Condition_ExpectedResult`, or the AC-id form
  required by the kit (`FEAT_AC_1_RejectsExpiredToken`).
- Arrange / Act / Assert, with one behaviour per test. Fake only at process edges, through
  interfaces (clock: `TimeProvider`).

## Documentation
- The build requires a doc comment on public API. The review judges its quality: the
  `<summary>` says what the member does for the caller, in one sentence; `<param>` and
  `<returns>` add constraints (units, ranges, null meaning) instead of repeating the name;
  `<exception>` lists what callers should expect to catch.
- Doc comments on internal members are optional. Add them where behaviour isn't obvious.
- Comments explain *why*, not *what*. Delete commented-out code.
