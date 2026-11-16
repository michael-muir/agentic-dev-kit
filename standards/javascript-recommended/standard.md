## Enforced by tooling
Checked by Prettier and ESLint through `eslint.config.mjs`. Reviewers skip these:
- Formatting, braces on every block, `===` only, `const`/`let` (never `var`), no unused
  variables, no shadowing, no parameter reassignment, no implicit globals or coercion, and
  no stray `console.log`.

**Setup:** install `eslint @eslint/js globals prettier` as devDependencies.

## Design
- ES modules (`import`/`export`), with named exports. One clear purpose per module.
- Validate untrusted input at the boundary, and document the shape of objects passed
  between modules with JSDoc `@typedef`, or move to TypeScript (the typescript-strict pack).
- Prefer pure functions. Isolate I/O (network, storage, DOM) behind small modules that
  tests can replace.
- `async`/`await` over promise chains. Never leave a promise unhandled.
- Don't mutate arguments. Return new objects and arrays.

## Naming
- `camelCase` values and functions, `PascalCase` classes and components,
  `UPPER_SNAKE_CASE` for true constants. Glossary terms. Booleans read as predicates.

## Errors
- Throw `Error` (or subclasses), never strings, and set `cause` when wrapping.
- Catch only where you can handle or add context. Never swallow silently.

## Tests
- The project's runner (vitest, jest or node:test), used consistently. Test through
  exported functions, and use role-based queries for UI.

## Documentation
- JSDoc on exported functions: parameters, return value, thrown errors and units, where
  they aren't evident.
