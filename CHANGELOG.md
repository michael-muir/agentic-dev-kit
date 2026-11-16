# Changelog

## 0.2.0 — 2026-11-16

- Coding-standards packs (`standards/`): dotnet-microsoft, dotnet-stylecop, python-pep8,
  python-strict, cpp-core-guidelines, cpp-google, javascript-recommended, typescript-strict,
  rust-api-guidelines, go-effective, go-uber, lua-default, plus a template.
- Installer `--standards` / `-Standards`: copies pack configs and generates
  `.agentic/CODING_STANDARDS.md` from the chosen packs, keeping a Project rules section.
- Gate loads pack `gates.toml` steps; new step field `replaces`.
- `build.py --check` validates packs; REGISTRY.md lists active packs.
- MIT license, vendored into installed projects.

## 0.1.0 — 2026-11-16

- Initial kit: 13 core agents, 13 skills, 2 domain experts plus a template.
- Gate runner with profiles for python, lua, cpp, dotnet, javascript, typescript, rust, go.
- Built-in checks: secret scan, debug-tag leftovers, locked-test integrity, spec traceability.
- Adapters for Claude Code, GitHub Copilot, Cursor, Gemini and generic prompts.
- Installer and updater, git hooks, and a GitHub Actions workflow.
