## Enforced by tooling
Checked by `ruff format` and `ruff check` through `ruff.toml`. Reviewers skip these:
- Layout, whitespace, line length (88), quotes, import order and grouping.
- PEP 8 naming: `snake_case` functions and variables, `PascalCase` classes,
  `UPPER_CASE` constants, no single-letter `l`/`O`/`I`.
- Docstring formatting (PEP 257), when a docstring is present.
- Unused imports and variables, outdated syntax, common bug patterns (bugbear).

## Design
- Modules and functions do one thing. A module's public interface is what isn't prefixed
  with `_`. Use `__all__` in packages that re-export names.
- Prefer plain functions and dataclasses over classes with only `__init__` and one method.
- Make side effects explicit. Nothing runs at import time except definitions and constants.
- Pass dependencies in (arguments or constructor parameters), instead of reaching for
  module-level globals or singletons.
- Type hints on every public function signature. Use `collections.abc` types for parameters
  (`Iterable`, `Mapping`) and concrete types for return values.
- Use `pathlib` for paths, context managers for resources, and `enum` for fixed sets of values.

## Naming
- Use the glossary's terms. Name functions after what they return or do (`load_orders`,
  `is_expired`), and booleans as predicates.
- Don't encode types in names (`order_list` → `orders`). Avoid abbreviations except
  well-known ones (`id`, `url`, `db`).

## Errors
- Raise specific exceptions (built-in where one fits, otherwise a small hierarchy rooted in
  one project exception). Never use a bare `except:`, and use `except Exception` only at
  top-level boundaries, where the error is logged.
- Chain exceptions with `raise … from err` when translating them.
- Library code doesn't `print`. It uses `logging.getLogger(__name__)`, with lazy `%`
  formatting in log calls.
- Don't use `assert` for runtime validation. It is stripped by `-O`.

## Tests
- pytest, with plain `assert`. Fixtures for setup, `parametrize` for tables of cases, and
  `tmp_path` for files.
- No network or clock dependence: inject them, or use fakes.

## Documentation
- Public modules, classes and functions get a docstring: a one-line summary in the
  imperative mood, then details only where they add information (units, invariants, raised
  exceptions).
- Comments explain why. Delete commented-out code.
