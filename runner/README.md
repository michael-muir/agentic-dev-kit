# Runner

`run.py` drives the pipeline without a human starting each role. Each step:
1. picks the next runnable task (Owner is a role; Status is `ready`, `in-progress` or `changes-requested`);
2. builds a self-contained prompt from an unattended-run header plus the role and its skills;
3. starts the **engine** mapped to that role as a new process, so it gets a fresh context;
4. records the result in `.agentic/runs/index.jsonl`, with the prompt and log next to it.

```bash
python .agentic/kit/runner/run.py plan               # what would run next, on which engine
python .agentic/kit/runner/run.py next --dry-run     # show the command without running it
python .agentic/kit/runner/run.py next               # run one role
python .agentic/kit/runner/run.py loop --max-steps 8 # run until a human checkpoint
```

`loop` stops when nothing is runnable (blocked, in review, done, waiting on a human), when a
step makes no progress (no new commit and no change of owner), or after the step limit.
Merging stays with a human. The integrator opens the PR, and branch protection does the rest.

## Engines and cross-model review

```toml
# .agentic/config.toml
[runner]
default = "claude"          # engine for any role not listed below
max_steps = 10
timeout_minutes = 60

[runner.roles]              # put the independent roles on a different vendor
adversary = "codex"
test-designer = "codex"
spec-reviewer = "codex"

[runner.engines]            # override or add engines; the prompt file arrives on stdin
claude = 'claude -p --model claude-opus-5-5 --permission-mode acceptEdits --allowedTools "Bash,Read,Edit,Write,Grep,Glob" < "{prompt_file}"'
codex = 'codex exec --sandbox workspace-write - < "{prompt_file}"'
# gemini = 'gemini --yolo < "{prompt_file}"'      # check your CLI's non-interactive flags
# local = '{python} my_llm_loop.py "{prompt_file}"'
```

Placeholders: `{prompt_file}`, `{role}`, `{task}`, `{python}`. `plan` and `next` warn when a
role whose `model_hint` is `different-from:<role>` runs on the same engine as that role.

## Cost controls

Set in `.agentic/config.toml` `[budgets]`. They can be turned on and off at four levels.

**1. Project mode**
| `mode` | Records usage | Warns | Blocks at the limit |
|---|---|---|---|
| `off` | – | – | – |
| `track` (default) | ✓ | – | – |
| `warn` | ✓ | at `warn_at` (80%) and at the limit | – |
| `enforce` | ✓ | at `warn_at` | ✓ (the task becomes `blocked`, with an entry in STATE.md) |

**2. Each limit.** Leave it out, or set it to `0`, to turn it off:
`max_review_rounds`, `max_steps`, `max_minutes`, `max_tokens`, `max_cost_usd` (per task), and
`max_cost_usd_per_day` (all tasks, from this machine's ledger).
`max_cost_usd_per_step` is passed to engines that support a hard cap (Claude Code's `--max-budget-usd`).

**3. Per task.** A `Budget` row overrides the project setting:
```
| Budget | enforce, max_cost_usd=5, max_steps=8 |
| Budget | off |
```

**4. Per run.** `run.py next|loop --ignore-budgets` runs past an enforced limit for that
run only. It's recorded in the ledger, and `run.py costs` reports it. A task blocked by a
budget also needs its Status set back by a human first.

**What gets measured.** Time and steps always. Tokens and cost when the engine reports them:
- Claude Code: `-p --output-format json` reports tokens and cost (the default engine command).
- Codex: `exec --json` reports tokens per turn. Cost comes from `[budgets.prices]` when the
  engine has a `model` (`codex = { cmd = "...", model = "gpt-5" }`).
- Other engines: time and steps only. The Spend row says so.

The runner keeps a committed `Spend` row on each task
(`steps=4 · minutes=52.3 · tokens=1300000 · cost_usd=3.80`). It commits that row (and any
budget block) with `Agent-Role: runner`, through the normal hooks. If a hook rejects that
commit, the row stays in the working tree for the next agent's commit. `run.py costs` totals
spend by task, role and engine.

**Not covered:** interactive sessions (chatting with Claude Code, Copilot or Cursor directly)
don't go through the runner. For those, use each tool's own limits: plan usage limits,
organisation spend caps, Claude Code's `/cost`. In the CI review workflow, each review is
capped by `--max-budget-usd`, a 30-minute job timeout, and cancel-on-new-push.

## Safety

- Headless sessions act without asking. Run them in the devcontainer
  (`install --devcontainer`), or another sandbox, rather than on a machine that holds credentials.
- The guardrails still apply: Claude's deny rules, git hooks (`--no-verify` is denied), the
  gate's `builtin:scope` and `builtin:test-lock` checks, CODEOWNERS, and branch protection.
- `.agentic/runs/` holds full prompts and transcripts. It's git-ignored. Review it before sharing.

## PR reviews in CI

`install --ci-review` adds `.github/workflows/agent-review.yml`. On each PR it runs the
spec-reviewer and the adversary in parallel fresh sessions (Claude Code GitHub Action), and
each posts its findings as a comment. It needs an `ANTHROPIC_API_KEY` repository secret.
