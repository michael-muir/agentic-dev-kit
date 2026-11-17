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
