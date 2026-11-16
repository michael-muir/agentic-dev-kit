## Enforced by tooling
Checked by StyLua and luacheck. Reviewers skip these:
- Formatting (4 spaces, 120 columns, double quotes, parentheses on calls).
- Undefined and accidental globals, unused variables and arguments, shadowing, unreachable code.

## Design
- Every file is a module that returns one table (`local M = {} … return M`). No globals,
  and no side effects at `require` time beyond defining the module.
- `local` for everything. Cache frequently used library functions in locals only in hot
  paths, and comment why.
- Use plain tables and functions first. For objects, use one metatable-based class pattern
  across the project (record it in Project rules), with `:` for methods and `.` for functions.
- Keep host-engine APIs (game engine, editor, nginx, Neovim) behind a thin adapter module, so
  logic can be tested with busted outside the host.
- Be explicit about 1-based indexing, and about `#` on sequences only (never on tables with holes).

## Naming
- `snake_case` for variables and functions, `PascalCase` for classes and modules that act as
  constructors, `UPPER_CASE` for constants. `_` for ignored values. A leading `_` marks
  private module members.
- Glossary terms in names. Boolean names read as predicates (`is_ready`).

## Errors
- Pick one convention per module and document it: either `return nil, err_message` for
  expected failures, or `error({ code = …, message = … })` with `pcall` at boundaries.
- Never ignore the second return value of a function that can fail.
- `assert` for programmer errors (bad arguments), not for runtime failures.

## Tests
- busted specs (`describe`/`it`) in `spec/`, named `<module>_spec.lua`. Inject or stub
  host APIs through the adapter module.

## Documentation
- LuaLS/EmmyLua annotations (`---@param`, `---@return`, `---@class`) on public module
  functions, so editors and type checkers can use them.
