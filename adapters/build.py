#!/usr/bin/env python3
"""Generate tool-specific agent and skill files from the kit's neutral sources.

    build.py --target PROJECT [--tools claude,copilot,cursor,gemini,generic] [--domains a,b]
    build.py --check            # validate the kit's agent and skill files only

Reads <kit>/agents/core/*.md, <kit>/agents/domains/<id>/agent.md (enabled domains only),
<kit>/skills/*/SKILL.md and <kit>/agents/domains/<id>/skills/*/SKILL.md. Writes:

    claude   .claude/agents/<id>.md, .claude/skills/<name>/
    copilot  .github/agents/<id>.agent.md, .github/skills/<name>/
    cursor   .cursor/rules/agentic-<id>.mdc
    generic  .agentic/prompts/<id>.md   (self-contained: role + skills inlined, for any LLM/API)
    always   .agentic/REGISTRY.md

Files from a previous build that are no longer produced are removed (tracked in
.agentic/.generated.json). Hand-written files are never touched.
Standard library only (Python 3.11+).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    sys.exit("build.py needs Python 3.11 or newer.")

KIT = Path(__file__).resolve().parents[1]
TOOLS = ("claude", "copilot", "cursor", "gemini", "generic")
REQUIRED_AGENT = ("id", "name", "kind", "summary", "tools", "skills", "writes")
CLAUDE_TOOLS = {
    "read": ["Read"], "search": ["Grep", "Glob"], "edit": ["Edit", "Write"],
    "shell": ["Bash"], "web": ["WebFetch", "WebSearch"],
}


@dataclass
class Doc:
    meta: dict
    body: str
    source: Path


def parse_value(raw: str):
    raw = raw.strip()
    if raw.startswith("[") and raw.endswith("]"):
        inner = raw[1:-1].strip()
        return [unquote(x) for x in re.findall(r'"[^"]*"|\'[^\']*\'|[^,]+', inner) if x.strip()] if inner else []
    if raw in ("true", "false"):
        return raw == "true"
    return unquote(raw)


def unquote(s: str) -> str:
    s = s.strip()
    if len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        return s[1:-1]
    return s


def parse_doc(path: Path) -> Doc:
    text = path.read_text("utf-8")
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n?(.*)$", text, re.S)
    if not m:
        raise ValueError(f"{path}: missing frontmatter")
    meta: dict = {}
    key = None
    for line in m.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.match(r"^\s+-\s+(.*)$", line)
        if item and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(unquote(item.group(1)))
            continue
        kv = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if kv:
            key, val = kv.group(1), kv.group(2)
            val = re.sub(r"\s+#.*$", "", val) if not val.strip().startswith(("'", '"')) else val
            meta[key] = parse_value(val) if val.strip() else []
    return Doc(meta, m.group(2).strip() + "\n", path)


def rel_kit(path: Path) -> str:
    return ".agentic/kit/" + path.relative_to(KIT).as_posix()


# --------------------------------------------------------------------------- collection

def load_agents(domains: list[str]) -> list[Doc]:
    docs = [parse_doc(p) for p in sorted((KIT / "agents" / "core").glob("*.md"))]
    for d in domains:
        p = KIT / "agents" / "domains" / d / "agent.md"
        if not p.exists():
            raise SystemExit(f"unknown domain '{d}': {p} not found")
        docs.append(parse_doc(p))
    return docs


def load_skills(domains: list[str]) -> dict[str, Doc]:
    paths = sorted((KIT / "skills").glob("*/SKILL.md"))
    for d in domains:
        paths += sorted((KIT / "agents" / "domains" / d / "skills").glob("*/SKILL.md"))
    skills = {}
    for p in paths:
        doc = parse_doc(p)
        name = doc.meta.get("name")
        if name != p.parent.name:
            raise SystemExit(f"{p}: frontmatter name '{name}' must match folder '{p.parent.name}'")
        if not str(doc.meta.get("description", "")).strip():
            raise SystemExit(f"{p}: description is required")
        skills[name] = doc
    return skills


def validate(agents: list[Doc], skills: dict[str, Doc]) -> list[str]:
    errors, ids = [], set()
    for a in agents:
        for k in REQUIRED_AGENT:
            if k not in a.meta:
                errors.append(f"{a.source}: missing '{k}'")
        aid = a.meta.get("id")
        if aid in ids:
            errors.append(f"{a.source}: duplicate id '{aid}'")
        ids.add(aid)
        for s in a.meta.get("skills", []):
            if s not in skills:
                errors.append(f"{a.source}: skill '{s}' not found")
        for t in a.meta.get("tools", []):
            if t not in CLAUDE_TOOLS:
                errors.append(f"{a.source}: unknown tool class '{t}'")
        for section in ("## Mission", "## Procedure", "## Boundaries"):
            if section not in a.body:
                errors.append(f"{a.source}: missing section '{section}'")
    return errors


# --------------------------------------------------------------------------- rendering

HEADER = ("<!-- GENERATED by agentic-dev-kit from {src}. Edit the kit source and run the "
          "installer with --update; changes here are overwritten. -->")


def preamble(a: Doc) -> str:
    m = a.meta
    skills = ", ".join(f"`{s}`" for s in m.get("skills", [])) or "none"
    writes = ", ".join(f"`{w}`" for w in m.get("writes", [])) or "nothing"
    hint = m.get("model_hint", "any")
    lines = [
        f"You are the **{m['name']}** agent (`{m['id']}`) of this project's agentic-dev-kit workflow.",
        "",
        "- Start with `.agentic/kit/skills/resume-session/SKILL.md`, and end with "
        "`.agentic/kit/skills/handoff/SKILL.md`.",
        f"- Skills for this role: {skills}. Each is at `.agentic/kit/skills/<name>/SKILL.md` "
        "(domain skills under `.agentic/kit/agents/domains/<id>/skills/`).",
        f"- You may write: {writes}. Anything else goes in your handoff as a request.",
        "- Pass/fail comes from `python .agentic/kit/gates/gate.py`. Quote its result.",
    ]
    if m.get("fresh_context", False):
        lines.append("- Work only from the inputs listed under *Read first*. Leave other roles' reasoning out.")
    if str(hint).startswith("different-from:"):
        lines.append(f"- Ideally run on a different model from `{hint.split(':', 1)[1]}`, for independent judgement.")
    return "\n".join(lines) + "\n"


def agent_body(a: Doc) -> str:
    return f"{HEADER.format(src=rel_kit(a.source))}\n\n{preamble(a)}\n{a.body}"


def inline_prompt(a: Doc, skills: dict[str, Doc]) -> str:
    parts = [f"# {a.meta['name']}: self-contained prompt", "", HEADER.format(src=rel_kit(a.source)), "",
             preamble(a), a.body]
    for s in a.meta.get("skills", []):
        if s in skills:
            parts += ["", "---", "", f"# Skill: {s}", "", skills[s].body]
    return "\n".join(parts)


def frontmatter(fields: dict) -> str:
    lines = ["---"]
    for k, v in fields.items():
        if isinstance(v, bool):
            v = "true" if v else "false"
        elif isinstance(v, str) and (":" in v or v.startswith(("[", "{", "'", '"', "#"))):
            v = json.dumps(v)
        lines.append(f"{k}: {v}" if v != "" else f"{k}:")
    return "\n".join(lines + ["---", ""])


STACKS = ("python", "lua", "cpp", "dotnet", "javascript", "typescript", "rust", "go")


def load_pack(pack_id: str) -> dict:
    return tomllib.loads((KIT / "standards" / pack_id / "pack.toml").read_text("utf-8"))


def validate_packs() -> list[str]:
    errors, root = [], KIT / "standards"
    ids = sorted(d.name for d in root.iterdir() if d.is_dir() and not d.name.startswith("_")) if root.exists() else []
    for pid in ids:
        folder = root / pid
        if not (folder / "pack.toml").exists():
            errors.append(f"{folder}: missing pack.toml")
            continue
        pack = load_pack(pid)
        for key in ("id", "name", "stack", "summary", "sources"):
            if key not in pack:
                errors.append(f"{folder}/pack.toml: missing '{key}'")
        if pack.get("id") != pid:
            errors.append(f"{folder}/pack.toml: id '{pack.get('id')}' must equal folder name")
        if pack.get("stack") not in STACKS:
            errors.append(f"{folder}/pack.toml: unknown stack '{pack.get('stack')}'")
        for other in pack.get("conflicts", []):
            if other not in ids:
                errors.append(f"{folder}/pack.toml: conflicts with unknown pack '{other}'")
            elif pid not in load_pack(other).get("conflicts", []):
                errors.append(f"{folder}/pack.toml: conflict with '{other}' must be declared on both sides")
        std = folder / "standard.md"
        if not std.exists():
            errors.append(f"{folder}: missing standard.md")
        elif "## Enforced by tooling" not in std.read_text("utf-8"):
            errors.append(f"{std}: must start with an '## Enforced by tooling' section")
        if (folder / "gates.toml").exists():
            tomllib.loads((folder / "gates.toml").read_text("utf-8"))  # raises on bad TOML
    return errors


def registry(agents: list[Doc], skills: dict[str, Doc], standards: list[str] | tuple = ()) -> str:
    out = ["# Agent registry", "", HEADER.format(src="agents/ and skills/"), "",
           "Start every session with `.agentic/kit/skills/resume-session/SKILL.md`.", "",
           "## Core roles", "", "| Role | Summary | Skills |", "|---|---|---|"]
    for a in agents:
        if a.meta.get("kind") == "core":
            out.append(f"| `{a.meta['id']}` | {a.meta['summary']} | {', '.join(a.meta.get('skills', []))} |")
    domains = [a for a in agents if a.meta.get("kind") == "domain"]
    out += ["", "## Domain experts", ""]
    if domains:
        out += ["Consult an expert when a task's text matches a keyword, or its changes touch a path.", "",
                "| Expert | Summary | Keywords | Paths | Consulted by |", "|---|---|---|---|---|"]
        for a in domains:
            m = a.meta
            out.append(f"| `{m['id']}` | {m['summary']} | {', '.join(m.get('trigger_keywords', []))} | "
                       f"{', '.join(f'`{p}`' for p in m.get('trigger_paths', []))} | "
                       f"{', '.join(m.get('consulted_by', []))} |")
    else:
        out.append("None enabled. Add ids to `domains` in `.agentic/config.toml`, then run the installer with `--update`.")
    out += ["", "## Coding standards packs", ""]
    if standards:
        out += ["Their rules are generated into `.agentic/CODING_STANDARDS.md`, and their tool configs "
                "are in the project root.", "", "| Pack | Stack | Summary |", "|---|---|---|"]
        for sid in standards:
            pack = load_pack(sid)
            out.append(f"| `{sid}` | {pack.get('stack')} | {pack.get('summary')} |")
    else:
        out.append("None selected. Add ids to `standards` in `.agentic/config.toml` (see "
                   "`.agentic/kit/standards/README.md`), then run the installer with `--update`.")
    out += ["", "## Skills", "", "| Skill | Use when |", "|---|---|"]
    for name, s in sorted(skills.items()):
        out.append(f"| `{name}` | {s.meta['description']} |")
    return "\n".join(out) + "\n"


# --------------------------------------------------------------------------- writing

class Writer:
    def __init__(self, target: Path):
        self.target = target
        self.written: set[str] = set()

    def text(self, rel: str, content: str) -> None:
        p = self.target / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, "utf-8", newline="\n")
        self.written.add(rel)

    def tree(self, rel_dir: str, src_dir: Path, header_src: str) -> None:
        for f in sorted(src_dir.rglob("*")):
            if f.is_file():
                rel = f"{rel_dir}/{f.relative_to(src_dir).as_posix()}"
                if f.name == "SKILL.md":
                    doc = parse_doc(f)
                    fm = frontmatter({"name": doc.meta["name"], "description": doc.meta["description"]})
                    self.text(rel, f"{fm}{HEADER.format(src=header_src)}\n\n{doc.body}")
                else:
                    p = self.target / rel
                    p.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(f, p)
                    self.written.add(rel)

    def finish(self) -> tuple[int, int]:
        manifest = self.target / ".agentic" / ".generated.json"
        old = set(json.loads(manifest.read_text("utf-8"))) if manifest.exists() else set()
        removed = 0
        for rel in sorted(old - self.written):
            p = self.target / rel
            if p.is_file():
                p.unlink()
                removed += 1
                parent = p.parent
                while parent != self.target and parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
                    parent = parent.parent
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps(sorted(self.written), indent=1) + "\n", "utf-8")
        return len(self.written), removed


def build(target: Path, tools: list[str], domains: list[str], standards: list[str] | tuple = ()) -> None:
    agents, skills = load_agents(domains), load_skills(domains)
    errors = validate(agents, skills)
    if errors:
        raise SystemExit("kit validation failed:\n  " + "\n  ".join(errors))
    w = Writer(target)
    w.text(".agentic/REGISTRY.md", registry(agents, skills, standards))
    for a in agents:
        aid, m = a.meta["id"], a.meta
        if "claude" in tools:
            ctools: list[str] = []
            for t in m.get("tools", []):
                ctools += [x for x in CLAUDE_TOOLS[t] if x not in ctools]
            if m.get("skills"):
                ctools.append("Skill")
            fm = frontmatter({"name": aid, "description": m["summary"], "tools": ", ".join(ctools)})
            w.text(f".claude/agents/{aid}.md", fm + agent_body(a))
        if "copilot" in tools:
            fm = frontmatter({"name": aid, "description": m["summary"]})
            w.text(f".github/agents/{aid}.agent.md", fm + agent_body(a))
        if "cursor" in tools:
            fm = frontmatter({"description": f"{m['name']}: {m['summary']}", "globs": "", "alwaysApply": False})
            w.text(f".cursor/rules/agentic-{aid}.mdc", fm + inline_prompt(a, skills))
        if "generic" in tools or "gemini" in tools:
            w.text(f".agentic/prompts/{aid}.md", inline_prompt(a, skills))
    for name, s in skills.items():
        src = rel_kit(s.source)
        if "claude" in tools:
            w.tree(f".claude/skills/{name}", s.source.parent, src)
        if "copilot" in tools:
            w.tree(f".github/skills/{name}", s.source.parent, src)
    count, removed = w.finish()
    print(f"build: {len(agents)} agents, {len(skills)} skills -> {count} files for {', '.join(tools)}"
          + (f" ({removed} stale removed)" if removed else ""))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Generate tool-specific agent files from agentic-dev-kit sources.")
    p.add_argument("--target", type=Path, help="project root (default: current directory)")
    p.add_argument("--tools", help=f"comma list from {', '.join(TOOLS)} (default: from config)")
    p.add_argument("--domains", help="comma list of domain ids (default: from config)")
    p.add_argument("--check", action="store_true", help="validate every agent and skill in the kit, then exit")
    a = p.parse_args(argv)
    if a.check:
        all_domains = sorted(d.name for d in (KIT / "agents" / "domains").iterdir()
                             if d.is_dir() and not d.name.startswith("_"))
        errors = validate(load_agents(all_domains), load_skills(all_domains)) + validate_packs()
        packs = len([d for d in (KIT / "standards").iterdir() if d.is_dir() and not d.name.startswith("_")])
        print("\n".join(errors) if errors else
              f"kit ok: core + {len(all_domains)} domains + {packs} standards packs validated")
        return 1 if errors else 0
    target = (a.target or Path.cwd()).resolve()
    cfg_path = target / ".agentic" / "config.toml"
    cfg = tomllib.loads(cfg_path.read_text("utf-8")).get("project", {}) if cfg_path.exists() else {}
    tools = [t.strip() for t in (a.tools.split(",") if a.tools else cfg.get("tools", ["claude", "generic"])) if t.strip()]
    domains = [d.strip() for d in (a.domains.split(",") if a.domains else cfg.get("domains", [])) if d.strip()]
    bad = [t for t in tools if t not in TOOLS]
    if bad:
        raise SystemExit(f"unknown tool(s): {', '.join(bad)}; choose from {', '.join(TOOLS)}")
    build(target, tools, domains, cfg.get("standards", []))
    return 0


if __name__ == "__main__":
    sys.exit(main())
