# Changelog

## 0.3.0 — 2026-11-16

- Enforcement: `builtin:scope` checks each agent commit (`Agent-Role:` trailer) against its
  role's `writes:`. Protected paths need explicit grants. Installer `--owners` writes CODEOWNERS.
  Claude Code deny rules block force-push, hook bypass, protected-path edits and secret reads.
- Kit CI: smoke test on Windows + Linux, plus a fixture matrix running the real gate for every
  stack × standards pack (`fixtures/`, `.github/workflows/kit-ci.yml`).
- Runner (`runner/run.py`): headless plan/next/loop, one fresh session per role, with a per-role
  engine mapping for cross-vendor review. Optional AI PR-review workflow (`--ci-review`).
- Safety: prompt-injection and no-read rules in AGENTS.md, `[safety] no_read`, and an optional
  devcontainer (`--devcontainer`).
- Supply chain: actions pinned by SHA, gitleaks checksum-verified, Dependabot config, and a
  dependency licence/vulnerability review job on PRs.
- Fixes: the Python profile no longer lints the vendored kit. Prettier ignores kit and generated
  files. .NET packs exempt test names from the naming rule.

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
