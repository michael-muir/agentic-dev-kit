# Adding a domain expert

Domain experts are **consultants**, not pipeline stages. The orchestrator matches them to
tasks with their triggers. The architect and spec-writer ask them design questions, and the
adversary and spec-reviewer have them review the diff. You add one without editing any core
agent.

## 1. Copy the template

```powershell
Copy-Item -Recurse agents\domains\_template agents\domains\robotics-engineer
```

```
agents/domains/robotics-engineer/
├── agent.md        role definition (required)
├── checklist.md    review checklist (required)
├── gates.toml      deterministic checks (optional)
├── checks/         scripts the gates call (optional)
└── skills/         domain procedures, one folder per skill with SKILL.md (optional)
```

## 2. Fill in `agent.md`

- `id` must equal the folder name.
- `summary` is the one line every tool uses to decide when to call this agent. Name the
  domain and what it checks.
- `trigger_keywords`: words that appear in specs or tasks for this domain.
- `trigger_paths`: globs for the files this domain owns (`**/*.urdf`, `**/kinematics/**`).
- `consulted_by`: usually `[spec-writer, architect, adversary, spec-reviewer]`.
- `skills`: list your domain skills, plus `handoff`.
- Body: keep the template's sections. The procedure has two modes, **design consult** and
  **review**. Each step ends with "Done when:".

See `skills/agent-authoring-guide/SKILL.md` for the writing rules.

## 3. Write `checklist.md`

Yes/no questions that a reviewer can answer from a diff and the spec, grouped by concern
(correctness, safety, performance, conventions). This is where most of the expertise lives.

## 4. Add gates (optional)

Anything in the checklist that a script can decide belongs in `gates.toml`, so it's checked
on every commit instead of remembered at review. Start new checks as `advisory = true`, and
make them blocking once they've stopped producing false positives. Helper scripts go in
`checks/`, use only the Python standard library, and are called as
`{python} {kit}/agents/domains/<id>/checks/<script>.py`.

## 5. Validate and enable

```powershell
python adapters\build.py --check
```

Then, in each project that needs it, add the id to `domains` in `.agentic/config.toml` and run:

```powershell
D:\GitHub\agentic-dev-kit\install\install.ps1 -Target <project> -Update
```

The expert now appears in `.agentic/REGISTRY.md` and in the generated tool files, and its
gates run with the project's gate.

## Ideas for experts

| Expert | Typical triggers | Gate ideas |
|---|---|---|
| Robotics engineer | kinematics, ROS, URDF, controller | URDF validation, unit suffixes |
| Embedded / firmware | MCU, RTOS, ISR, register | stack-usage report, no dynamic allocation in ISRs |
| Data / ML engineer | dataset, training, model, feature | schema checks, data-leakage tests, deterministic seeds |
| Game designer | balance, economy, progression | data-table range checks |
| Accessibility | UI, screen reader, contrast | axe or pa11y run in CI |
| Database / SQL | migration, schema, index | migration reversibility, lint (sqlfluff) |
