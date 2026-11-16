## Enforced by tooling
Checked by Prettier, ESLint (`typescript-eslint` strict and stylistic, type-checked) and
`tsc --noEmit` with `tsconfig.strict.json`. Reviewers skip these:
- Formatting, `===` only, no stray `console.log`.
- No `any` leaks (`no-unsafe-*`), no floating promises, no unnecessary conditions or
  assertions, exhaustive `switch` over unions, type-only imports marked `import type`.
- Strict null checks, unchecked index access returning `T | undefined`, exact optional
  properties, explicit return types on exported functions.

**Setup:** add `"extends": "./tsconfig.strict.json"` to the project's `tsconfig.json`, and
install `eslint @eslint/js typescript-eslint typescript prettier` as devDependencies.

## Design
- Model the domain in types. Use discriminated unions for states and results, branded types
  for ids and units, and `readonly` arrays and properties for data that mustn't change.
  Make illegal states unrepresentable.
- Validate untrusted input (HTTP, files, env) at the boundary with a schema (zod, valibot,
  or the project's choice), and pass typed values inward.
- Prefer functions and modules to classes. Use classes where identity, lifecycle or
  `instanceof` matter.
- No default exports. Named exports keep imports and renames consistent.
- `async`/`await` over raw promise chains. Run independent work concurrently with `Promise.all`.
- No global mutable state. Inject dependencies (clock, fetch, storage) at the seams tests fake.

## Naming
- `camelCase` values and functions, `PascalCase` types, classes and components,
  `UPPER_SNAKE_CASE` only for true constants. No `I` prefix on interfaces.
- Glossary terms in names. Booleans read as predicates (`isReady`, `hasErrors`).

## Errors
- Throw `Error` subclasses (never strings or plain objects), and set `cause` when wrapping.
  Expected failures in domain logic can return a result union instead. Be consistent per module.
- `catch (err: unknown)`. Narrow it before use, and never swallow it silently.
- Casts (`as`) and non-null assertions (`!`) in production code need a comment justifying them.

## Tests
- The project's runner (vitest or jest), used consistently. Type-check test files too.
- Test behaviour through exported functions and components. For UI, use role-based queries
  (Testing Library), not CSS selectors.

## Documentation
- TSDoc on exported functions and types whose behaviour isn't evident from the signature:
  units, invariants, thrown errors.
