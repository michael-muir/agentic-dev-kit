# Pipeline

The Orchestrator moves each task through these phases. The phase is recorded in the task
file and in `STATE.md`, so any agent can tell where work stands.

| Phase | Role | Leaves the phase when | Next |
|---|---|---|---|
| `spec` | spec-writer | Spec `status: approved` by a human | `design` (full) / `tests` (lite) |
| `design` | architect (+ domain consults) | Design note, ADRs for one-way doors, tasks sliced with seams | `tests` |
| `tests` | test-designer | Every task AC has a test naming its id, observed red, tests locked | `implement` |
| `implement` | implementer | Task ACs green, `gate run --stage pre-push` passes | `verify` |
| `verify` | verifier | `gate run --stage ci` report for HEAD is a pass | `review` |
| `review` | spec-reviewer, standards-reviewer, + (full) adversary, security-reviewer, domain experts | Every reviewer verdict is `pass`, or remaining findings are explicitly accepted by a human | `integrate` |
| `integrate` | integrator | PR open with evidence; CI green | `done` once a human merges |

A failure in `verify` or `review` sends the task back to `implement` with the findings file
as input, and increments **Review round** in the task. When `round > max_review_rounds`
(`.agentic/config.toml`, default 3), the task becomes `blocked` and a human decides.

When a failure's cause isn't obvious after one attempt, the Implementer or Verifier calls in
the **Debugger**. A flaky test always goes to the Debugger.

## Context isolation

Each role runs in a **fresh context**: a sub-agent, a new chat, or a new API conversation.
It receives **pointers**, not summaries:

| Role | Receives | Never receives |
|---|---|---|
| test-designer | spec, task, design note, public interface signatures | implementation bodies, implementer handoffs |
| implementer | task, locked tests, design note, findings to address | — |
| spec-reviewer | spec, task, diff range | implementer handoffs or reasoning, other reviewers' findings |
| standards-reviewer | diff range, CODING_STANDARDS, GLOSSARY | implementer reasoning, other reviewers' findings |
| adversary | spec, diff range, mutation survivors from the verifier | implementer reasoning, other reviewers' findings |
| security-reviewer | diff range, threat notes in the design | implementer reasoning |

A tool without sub-agents runs these as separate sessions, using
`.agentic/prompts/<role>.md`. If a single session must play two roles, it says so in the
handoff, and the reviewer verdict is marked `same-context` so the Integrator flags it in the PR.

## Who may write what

Every agent's `writes:` frontmatter lists the paths it may change. Two rules are also
enforced by the gate:

- **Locked tests** (`.agentic/locks/tests.lock.json`) may only be changed by test-designer or
  adversary, who re-run `gate.py lock-tests --by <role>`. Any other change fails `builtin:test-lock`.
- **Traceability**: every acceptance criterion in an approved spec must be named by at least
  one test (`builtin:trace`).

## Human checkpoints

1. Approving the spec.
2. Approving the task breakdown (full track).
3. Any finding a reviewer marks `needs-human`.
4. Review-round limit reached.
5. Merging. Agents open PRs. Only a human merges, and branch protection requires `agent-gate`.
