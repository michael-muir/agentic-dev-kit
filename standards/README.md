# Coding standards packs

A pack is a named coding standard you choose at install time. It has two halves, matching
the two ways rules get enforced:

| Half | File | Enforced by |
|---|---|---|
| Mechanical rules | `configs/`: tool configs copied into the project root (`.editorconfig`, `ruff.toml`, `.clang-tidy` …) | the gate. The stack profile's format, lint and build steps read these configs. |
| Judgement rules | `standard.md` | the standards-reviewer, through the generated `.agentic/CODING_STANDARDS.md` |

```
standards/<id>/
├── pack.toml       id, name, stack, summary, sources, conflicts
├── standard.md     judgement rules (## sections: Enforced by tooling, Design, Naming, …)
├── configs/        files copied to the project root if the project doesn't have them yet
└── gates.toml      optional extra gate steps (same format as gates/profiles/*.toml)
```

## Using packs

```powershell
install.ps1 -Target D:\GitHub\my-app -Stacks dotnet,typescript -Standards dotnet-microsoft,typescript-strict
```

This:

- records `standards = [...]` in `.agentic/config.toml`.
- copies each pack's `configs/` into the project root. An existing file is never
  overwritten. The installer reports the difference, and the pack's version stays at
  `.agentic/kit/standards/<id>/configs/` for comparison.
- generates `.agentic/CODING_STANDARDS.md`: a managed block with one section per pack, then
  **Project rules**, which are yours. Project rules override the packs, and the packs
  override the reviewer's built-in smell baseline.
- adds the packs' `gates.toml` steps to the gate. A step with `replaces = "<step id>"` takes
  the place of that profile step.

To change packs later, edit `standards` in `.agentic/config.toml` and run `install --update`.
The pack sections are regenerated, and Project rules are kept.

## Available packs

| Pack | Stack | Summary | Conflicts with |
|---|---|---|---|
| `dotnet-microsoft` | dotnet | Microsoft C# coding conventions and .NET design guidelines, through .editorconfig and built-in analyzers | dotnet-stylecop |
| `dotnet-stylecop` | dotnet | dotnet-microsoft plus StyleCop.Analyzers for layout, ordering and public-API documentation | dotnet-microsoft |
| `python-pep8` | python | PEP 8 and PEP 257 through ruff | python-strict |
| `python-strict` | python | PEP 8 plus a broad ruff rule set and strict mypy typing | python-pep8 |
| `cpp-core-guidelines` | cpp | C++ Core Guidelines through clang-tidy (cppcoreguidelines, bugprone, modernize, performance) | cpp-google |
| `cpp-google` | cpp | Google C++ Style Guide: clang-format Google style, clang-tidy google-* and naming | cpp-core-guidelines |
| `javascript-recommended` | javascript | ESLint recommended plus a few safety rules, with Prettier | typescript-strict |
| `typescript-strict` | typescript | strict tsconfig, plus typescript-eslint strict and stylistic type-checked rules | javascript-recommended |
| `rust-api-guidelines` | rust | Rust API Guidelines, plus clippy pedantic as errors | — |
| `go-effective` | go | Effective Go and Go Code Review Comments, through golangci-lint's standard set | go-uber |
| `go-uber` | go | Uber Go Style Guide, through a stricter golangci-lint set | go-effective |
| `lua-default` | lua | luacheck and StyLua defaults with common conventions | — |

## Adding a pack

1. Copy `_template/` to `standards/<id>/`. The id is `<stack>-<name>`.
2. Fill in `pack.toml`, put tool configs in `configs/`, and write `standard.md`. Start it
   with **Enforced by tooling** (what the configs already check, so the reviewer skips it),
   then only rules that need judgement. Use `##` headings. They're nested under the pack's
   heading when the installer generates the file.
3. Run `python adapters/build.py --check`.

### Licensed standards
Some standards, such as MISRA C/C++, AUTOSAR C++14 and parts of CERT, are licensed, and
their rule text can't be redistributed. A pack for one can enable the tool checks that
cover it (the cppcheck MISRA addon, clang-tidy `cert-*`), cite rules by number only, and
point to the team's licensed copy for the full wording.
