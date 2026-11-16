---
name: agent-authoring-guide
description: Use when writing or editing an agent file, a skill, AGENTS.md, or any document agents are pointed at, including when adding a new domain expert, for the schema and the writing rules that make agents behave predictably.
---

# Agent authoring guide

## Files and their jobs
| File | Loaded | Keep it |
|---|---|---|
| `AGENTS.md` | every session, every agent | short: a start/end routine, ground rules, and pointers |
| `agents/**.md` | when that role is active | one role: mission, inputs, steps, boundaries |
| `skills/*/SKILL.md` | when a role lists it, or a tool matches its description | one procedure, with completion criteria |
| `CODING_STANDARDS.md` | at review only | detailed judgement rules |
| docs, checklists | on demand, through a pointer | reference material |

Agent frontmatter follows `agents/_schema.md`. Skill frontmatter is `name` (the folder name)
plus `description`: one sentence starting "Use when…", naming the situations that should
trigger it.

## Writing rules
1. **Every step ends with "Done when:"** followed by a condition someone else could check.
   Vague endings ("review carefully") lead to stopping early.
2. **Say what to do, rather than what not to do.** Prohibitions can prime the very behaviour
   they forbid. Keep a "never" only for a hard guardrail, and pair it with the alternative
   ("Locked tests change only through test-designer. If one looks wrong, explain it in the handoff").
3. **Point to material, don't paste it.** A pointer says what the material is and when to
   read it. Inline only what every path through the procedure needs.
4. **One home per fact.** If two files say the same thing, one of them will go stale.
5. **Don't restate the discoverable.** Directory layouts, scripts and config can be read
   directly. Document what can't be: conventions, reasons, and traps.
6. **Use established terms** ("red", "seam", "frontier", "one-way door") and define new ones once, in the glossary.
7. **Cut no-ops.** If deleting a sentence doesn't change behaviour when you test the file, delete it.
8. **Steps for sequences, tables for reference.** Split a file when later steps tempt agents
   to rush earlier ones, or when it serves two unrelated situations.

## Adding a domain expert
1. Copy `agents/domains/_template/` to `agents/domains/<id>/`.
2. In `agent.md`, fill in `trigger_keywords` and `trigger_paths` (how the orchestrator finds
   you) and `consulted_by` (which roles ask you questions), then the mission and procedure:
   what you check, and how you answer a consult.
3. In `checklist.md`, write the domain's review checklist. Reviewers and the adversary read it.
4. In `gates.toml` (optional), add deterministic checks in gate-profile format. Put scripts in `checks/`.
5. In `skills/<name>/SKILL.md` (optional), add domain procedures.
6. Enable it per project (`--domains <id>`, or `domains` in `.agentic/config.toml`), then run `install --update`.
**Done when:** `adapters/build.py` lists the agent in REGISTRY.md, and a consult on a sample task produces a useful answer.
