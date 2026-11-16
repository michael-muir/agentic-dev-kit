# Agent file schema

Each agent is one Markdown file with YAML-style frontmatter. `adapters/build.py` reads these
files and generates the tool-specific versions, so stick to the subset below: `key: value`
scalars and `[a, b]` inline lists.

```yaml
---
id: implementer                 # kebab-case, unique; file name for core agents
name: Implementer               # display name
kind: core                      # core | domain
summary: >-                     # one line; becomes the tool's "description" used for routing
  Makes locked acceptance tests pass with the smallest clean change.
tools: [read, search, edit, shell]   # abstract: read, search, edit, shell, web
skills: [test-driven-slices, systematic-debugging]
writes: [src/**, "tests/unit/**"]    # paths this role may change (enforced by review + gates)
fresh_context: true             # must start without other roles' conversation
model_hint: any                 # any | strong | different-from:<role id>
# domain agents only:
trigger_keywords: [orbit, thrust]
trigger_paths: ["**/guidance/**"]
consulted_by: [architect, adversary, spec-reviewer]
---
```

The body uses these sections, in this order:

1. `## Mission`: one paragraph. What this role is accountable for.
2. `## Read first`: the exact files to load, in order.
3. `## Procedure`: numbered steps, each ending with **Done when:** and a checkable condition.
4. `## Outputs`: files produced and the template each one follows.
5. `## Boundaries`: what the role leaves to others, phrased as who does it instead.
6. `## Hand off`: which role comes next, and under what condition.

Authoring rules are in `skills/agent-authoring-guide/SKILL.md`.
