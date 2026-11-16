# Gates

`gate.py` is the single source of pass/fail, run the same way by git hooks, agents and CI.

```bash
python .agentic/kit/gates/gate.py run --stage pre-commit   # fast: format, lint, secrets, debug tags, test lock
python .agentic/kit/gates/gate.py run --stage pre-push     # + types, build, tests, traceability
python .agentic/kit/gates/gate.py run --stage ci           # + audits, static analysis, mutation
python .agentic/kit/gates/gate.py run --only builtin:trace python:test
python .agentic/kit/gates/gate.py list --stage ci          # what will run, and which tools are missing
python .agentic/kit/gates/gate.py lock-tests --by test-designer
```

Each run writes `.agentic/reports/gate-latest.json` and `.md`, with the commit sha, so a
claim of "it passed" can be checked against HEAD.

## Step fields (profiles and domain `gates.toml`)

| Field | Meaning |
|---|---|
| `name` | Step name. Its id becomes `<stack or domain>:<name>`. |
| `cmd` | Shell command, run from the repo root. Placeholders: `{python}` (this interpreter), `{kit}` (the kit directory), `{files:glob1,glob2}` (matching tracked files; the step is skipped if there are none). |
| `stages` | Any of `pre-commit`, `pre-push`, `ci`. |
| `category` | Label for reports: format, lint, types, build, test, coverage, security, mutation, domain. |
| `when_files` | Run only if a tracked file matches one of these globs. |
| `requires_paths` | Run only if these paths exist (e.g. `Cargo.toml`, `node_modules`). |
| `tool` | Executable to look for on PATH. Defaults to the first word of `cmd`. |
| `optional` | When the tool is missing: skip, instead of fail. |
| `advisory` | Report failures as WARN, never failing the gate (mutation and heuristic checks). |
| `fail_on_output` | Fail if the command prints anything (e.g. `gofmt -l`). |
| `fail_on_match` | Fail if the output matches this regex. |
| `timeout` | Seconds (default 1800). |
| `install` | Hint printed when the tool is missing. |
| `replaces` | (standards packs) The id of a profile step this step takes the place of, e.g. `rust:clippy`. |

Steps with identical `cmd` run once, so `javascript` and `typescript` together don't run prettier twice.

## Project configuration (`.agentic/config.toml`)

```toml
[gate]
skip = ["python:types"]                  # skip by id. Say why in a comment, and expect the retro to ask.

[gate.overrides]
"python:test" = "pytest -q --cov=src --cov-fail-under=90"        # replace the command
"aerospace-engineer:unit-suffixes" = { advisory = false }        # or change fields
```

## Built-in checks

| Id | Stages | Fails when |
|---|---|---|
| `builtin:secrets` | all | gitleaks (if installed) or a regex scan finds a credential. Put `agentic:allow-secret` on a false-positive line. |
| `builtin:debug-tags` | all | a non-Markdown file still contains a temporary `DEBUG-` + 4 hex digits marker. |
| `builtin:test-lock` | all | a file in `.agentic/locks/tests.lock.json` was modified or deleted. |
| `builtin:trace` | pre-push, ci | an AC id in an `approved`/`implemented` spec isn't named by any test file (matched case-insensitively, `-` or `_`). |

### What gets locked
`lock-tests` locks test files (matched by the stack's `test_globs`) that **name an AC id**
(`FEAT-AC-1` or `feat_ac_1`), or that live in an adversarial area (`/adversarial/`,
`/security/`, `/regression/`, `*_adversarial_test.*`, `*_regression_test.*`). The
implementer's own unit tests stay unlocked. Hashes ignore CRLF/LF differences.

The lock is a tripwire, not a security boundary: anyone can re-run `lock-tests`. It works
because every re-lock shows up in the diff (`tests.lock.json`, including `locked_by`), and
reviewers and the integrator check it.
