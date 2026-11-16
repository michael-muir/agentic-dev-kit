# agentic-dev-kit

A portable, LLM-agnostic setup for AI-assisted software development. Every change is
specified, built test-first, reviewed by independent agents, attacked by an adversary, and
then **gated by deterministic checks** before it reaches the repository.

Install it into any project with one command. All agent state lives in plain Markdown inside
the project, so any LLM in any tool (Claude Code, Copilot, Cursor, Codex, Gemini, a raw API
loop) can pick up exactly where the last one stopped.

---

## How it works

```
 Request
   │
   ▼
 Orchestrator ── reads .agentic/STATE.md, picks the track (lite / full), routes work
   │
   ▼
 Spec Writer ──► spec with numbered, testable acceptance criteria   (human approves)
   │
   ▼
 Architect ──► design note, ADRs, test seams, vertical-slice tasks  ◄── Domain experts
   │
   ▼  (per task / slice)
 Test Designer ──► failing acceptance tests named by AC id → locked
   │
   ▼
 Implementer ──► smallest change that turns them green (cannot edit locked tests)
   │
   ▼
 Verifier ──► runs the gate: format, lint, types, build, tests, coverage, mutation
   │   fail → Implementer (or Debugger)
   ▼
 Spec Reviewer │ Standards Reviewer │ Adversary │ Security Reviewer
   (each in a fresh context, none sees the others' findings)
   │   findings → Implementer, max N rounds, then escalate to human
   ▼
 Integrator ──► commit + PR with evidence and merge-risk rating → CI gate → human merges
   │
   ▼
 Retro ──► turns recurring problems into new checks or standards
```

Three rules hold the design together:

1. **Gates are code, not promises.** `gate.py` and CI decide pass or fail. An agent's claim
   that "tests pass" counts for nothing without a gate report for that commit.
2. **The author never grades the work.** Tests come from the spec, not the code. Reviewers
   and the adversary get the spec and the diff, never the implementer's reasoning. Where
   possible, run the adversary on a different model or vendor.
3. **State lives in files.** `.agentic/STATE.md`, task files and handoff notes are committed
   with the code. Nothing important exists only in a chat.

## What's in the kit

| Path | Contents |
|---|---|
| `agents/core/` | 13 role definitions (who does what, with which permissions) |
| `agents/domains/` | Domain experts that plug in as consultants (aerospace, Unreal TA, plus a template) |
| `skills/` | Reusable procedures with completion criteria (how each job is done) |
| `standards/` | Coding-standards packs (tool configs + review rules) you choose per project |
| `workflow/` | Pipeline, tracks, definition of done, document templates |
| `gates/` | `gate.py` runner, per-stack profiles, git hooks |
| `adapters/` | `build.py`, which turns neutral agent and skill files into Claude Code, Copilot, Cursor and generic prompt formats |
| `ci/` | GitHub Actions workflow that runs the same gate |
| `install/` | Installer and updater |
| `project-skeleton/` | The `.agentic/` state folder and `AGENTS.md` copied into each project |

Agents and skills are separate on purpose. An **agent** is a role: its mission, boundaries,
what it may write, and which skills it loads. A **skill** is a procedure that several agents
can share. Domain experts bring their own skills and gate checks.

## Install into a project

Requirements: Python 3.11+ and git. You also need each stack's own tools, such as `ruff`,
`cargo` or `dotnet`.

```powershell
# Windows
D:\GitHub\agentic-dev-kit\install\install.ps1 -Target D:\GitHub\my-project -Stacks python,typescript -Tools claude,copilot
```

```bash
# macOS / Linux / Git Bash
~/agentic-dev-kit/install/install.sh --target ~/code/my-project --stacks rust --domains aerospace-engineer
```

Options:

| Option | Values | Default |
|---|---|---|
| `--stacks` | `python, lua, cpp, dotnet, javascript, typescript, rust, go` (comma-separated) | required on first install |
| `--domains` | folder names under `agents/domains/` | none |
| `--standards` | coding-standards packs under `standards/` (comma-separated) | none |
| `--tools` | `claude, copilot, cursor, gemini, generic` | `claude,generic` |
| `--no-hooks` | skip setting `core.hooksPath` | hooks on |
| `--no-ci` | skip copying the GitHub workflow | CI on |
| `--update` | refresh `.agentic/kit/` and generated files; never touches state | — |

What the installer does to the target project:

- Copies the kit to `.agentic/kit/`, a vendored copy pinned to this repo's `VERSION`.
- Creates `.agentic/` state files (`STATE.md`, `config.toml`, `GLOSSARY.md`,
  `CODING_STANDARDS.md`, and the task, spec and handoff folders) if they don't exist.
- With `--standards`: copies each pack's tool configs to the project root (never overwriting
  existing ones), and generates `.agentic/CODING_STANDARDS.md` from the packs, with a
  **Project rules** section of your own.
- Writes or merges `AGENTS.md`, inside marker comments, so your own notes are kept. Adds
  `CLAUDE.md` / `GEMINI.md` pointers when those tools are selected.
- Generates tool-specific agent and skill files, such as `.claude/agents/` and `.github/agents/`.
- Points git hooks at `.agentic/kit/gates/hooks/` (pre-commit and pre-push run the gate).
- Adds `.github/workflows/agent-gate.yml`.

After installing:

1. Commit everything.
2. On GitHub, protect `main`: require the `agent-gate` check and at least one human approval.
   This is the final enforcement layer, and agents cannot get around it.
3. Open your LLM tool in the project and say *"Read AGENTS.md and start."*

### Updating

Pull the latest kit, then:

```powershell
install\install.ps1 -Target D:\GitHub\my-project -Update
```

`.agentic/kit/` and generated files are replaced. Your state, config, glossary and standards
are never overwritten. Don't edit `.agentic/kit/` inside a project: changes are lost on
update. Improve the kit here and update the projects instead. The Retro agent proposes such
changes as patches to this repo.

## Resuming work with any LLM

`AGENTS.md` tells every agent to begin with the `resume-session` skill:

1. Read `.agentic/STATE.md`, the newest note in `.agentic/handoffs/`, and the active task.
2. Check git against what the handoff claims. If they disagree, git wins and the discrepancy
   is recorded.
3. Load the role named in the task (`.agentic/kit/agents/...`) and the skills it lists.
4. Before stopping, write a handoff note and update `STATE.md` (the `handoff` skill).

Tools that support sub-agents (Claude Code, Copilot) get generated agent files, so each role
runs in its own fresh context. Tools without sub-agents use `.agentic/prompts/<role>.md`: a
self-contained prompt with the role and its skills inlined. Paste it into any model or API.

## Tracks

The Orchestrator scales the amount of process to the risk of the change
(`workflow/tracks.md`):

- **Lite** (reversible, small blast radius): Test Designer → Implementer → Verifier → Spec and
  Standards review → Integrator.
- **Full** (hard to reverse, security-sensitive, domain-critical, or touches public
  contracts): adds the Architect, Adversary, Security Reviewer and domain consults, and needs
  explicit human sign-off.

## Coding standards

Pick published standards up front, one or more per stack:

```powershell
install\install.ps1 -Target D:\GitHub\my-app -Stacks dotnet,typescript -Standards dotnet-microsoft,typescript-strict
```

Each pack supplies **tool configs** (e.g. `.editorconfig` + `Directory.Build.props` for
.NET), which the gate enforces through the stack's existing format, lint and build steps. It
also supplies **review rules**, which are generated into `.agentic/CODING_STANDARDS.md` for
the standards-reviewer. Your own rules go in its **Project rules** section, and they win.

| Stack | Packs |
|---|---|
| .NET | `dotnet-microsoft`, `dotnet-stylecop` |
| Python | `python-pep8`, `python-strict` |
| C++ | `cpp-core-guidelines`, `cpp-google` |
| JavaScript / TypeScript | `javascript-recommended`, `typescript-strict` |
| Rust | `rust-api-guidelines` |
| Go | `go-effective`, `go-uber` |
| Lua | `lua-default` |

**Without `--standards`**, nothing breaks, and the installer lists the packs available for
your stacks so you can add one later. The gate still runs every format, lint, type,
build and test step for your stacks, but each tool uses its own defaults, or the configs the
project already has. `CODING_STANDARDS.md` stays a blank skeleton for you to fill in, and the
standards-reviewer applies what you write there plus the kit's built-in smell baseline
(unclear names, duplication, dead code, magic values …). What you miss is the
standard-specific layer, such as Microsoft's naming rules enforced at build time.

Add or change packs at any time by editing `standards` in `.agentic/config.toml` and running
`--update`. Anything already in `CODING_STANDARDS.md` is kept as Project rules. To add a new
pack to the kit, see `standards/README.md`.

## Adding a domain expert

```powershell
Copy-Item -Recurse agents\domains\_template agents\domains\my-expert
```

Then fill in `agent.md` (frontmatter `id`, triggers, `consulted_by`), `checklist.md`, and
optionally `gates.toml` and `skills/`. Enable it per project with `--domains my-expert`, or
add it to `domains` in `.agentic/config.toml` and run `--update`. No core agent needs editing:
the Architect and reviewers consult whichever experts' triggers match the task. See
`docs/adding-a-domain-expert.md`.

## Supported stacks

Profiles live in `gates/profiles/*.toml`. Each lists format, lint, type, build, test, audit
and mutation steps for that stack, with the stage each runs at (`pre-commit`, `pre-push`,
`ci`). Override or skip any step per project in `.agentic/config.toml`. See
`gates/README.md`.

| Stack | Format | Lint / types | Test | Extras (CI) |
|---|---|---|---|---|
| python | ruff format | ruff, mypy | pytest + coverage | pip-audit, mutmut |
| lua | stylua | luacheck | busted | — |
| cpp | clang-format | clang-tidy, cppcheck | CMake + CTest | — |
| dotnet | dotnet format | build -warnaserror | dotnet test + coverage | vulnerable packages, Stryker.NET |
| javascript | prettier | eslint | npm test | npm audit, StrykerJS |
| typescript | prettier | eslint, tsc | npm test | npm audit, StrykerJS |
| rust | cargo fmt | clippy -D warnings | cargo test | cargo-audit, cargo-mutants |
| go | gofmt | go vet, staticcheck | go test (-race in CI) | govulncheck |

Built-in checks run for every stack: secret scan, leftover debug tags, locked-test
integrity, and spec traceability (every approved acceptance criterion has a test that names it).

## Repository layout

```
agentic-dev-kit/
├── AGENTS.md                  instructions for agents working on this kit itself
├── VERSION  CHANGELOG.md
├── agents/
│   ├── _schema.md             frontmatter + section contract for agent files
│   ├── core/                  orchestrator … retro
│   └── domains/               _template, aerospace-engineer, unreal-technical-artist
├── skills/                    one folder per skill, each with SKILL.md
├── standards/                 coding-standards packs: pack.toml, standard.md, configs/, gates.toml
├── workflow/                  pipeline.md, tracks.md, definition-of-done.md, templates/
├── gates/                     gate.py, gate.ps1, gate.sh, profiles/, hooks/
├── adapters/build.py
├── ci/github/agent-gate.yml
├── install/                   install.py, install.ps1, install.sh
├── project-skeleton/          AGENTS.md + .agentic/ state skeleton
└── docs/
```

## License

MIT © 2026 Michael Muir. See [LICENSE](LICENSE).
