#!/usr/bin/env python3
"""Static accessibility checks on markup (HTML, JSX/TSX, Vue, Svelte, Razor).

Heuristic and advisory. It catches common, mechanical problems only; keyboard and
screen-reader testing are still required. Reported as path:line: [WCAG] message.
A line containing `a11y:ok` is skipped. Exit code 1 if anything was found.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

EXTS = {".html", ".htm", ".jsx", ".tsx", ".vue", ".svelte", ".razor", ".cshtml"}
SKIP = (".agentic/", "node_modules/", "dist/", "build/", "coverage/", "bin/", "obj/")
TAG = re.compile(r"<(?P<name>[A-Za-z][\w.-]*)(?P<attrs>(?:[^>\"'{}]|\"[^\"]*\"|'[^']*'|\{[^{}]*\})*)/?>", re.S)


def has(attrs: str, *names: str) -> bool:
    return any(re.search(rf"(?<![\w-]){re.escape(n)}\s*=", attrs, re.I) for n in names)


def check_tag(name: str, attrs: str) -> list[str]:
    n = name.lower()
    out = []
    if n == "img" and not has(attrs, "alt"):
        out.append("[1.1.1] <img> has no alt attribute (use alt=\"\" if decorative)")
    if n == "html" and not has(attrs, "lang"):
        out.append("[3.1.1] <html> has no lang attribute")
    m = re.search(r"tab[iI]ndex\s*=\s*[\"'{]?\s*(\d+)", attrs)
    if m and int(m.group(1)) > 0:
        out.append(f"[2.4.3] positive tabindex ({m.group(1)}) breaks the natural focus order")
    if n in ("div", "span", "li", "td", "img", "p") and has(attrs, "onclick", "onClick", "@click", "v-on:click", "on:click"):
        if not has(attrs, "role") or not has(attrs, "tabindex", "tabIndex"):
            out.append(f"[2.1.1] clickable <{n}> without role and tabindex. Use a <button>")
    if n == "a" and not has(attrs, "href") and has(attrs, "onclick", "onClick", "@click", "on:click"):
        out.append("[2.1.1] <a> without href used as a button. Use a <button>")
    if n in ("input", "select", "textarea"):
        itype = re.search(r"type\s*=\s*[\"']?(\w+)", attrs, re.I)
        if not (itype and itype.group(1).lower() in ("hidden", "submit", "button", "reset", "image")):
            if not has(attrs, "id", "aria-label", "aria-labelledby", "title"):
                out.append(f"[1.3.1] <{n}> has no id (for a <label for>), aria-label or aria-labelledby")
    if n in ("button", "a") and has(attrs, "aria-hidden") and re.search(r"aria-hidden\s*=\s*[\"'{]?\s*true", attrs):
        out.append(f"[4.1.2] focusable <{n}> is aria-hidden")
    if n in ("video", "audio") and has(attrs, "autoplay", "autoPlay") and not has(attrs, "muted"):
        out.append(f"[1.4.2] <{n}> autoplays with sound")
    return out


def files() -> list[str]:
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"], capture_output=True,
                             text=True, check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        out = [p.as_posix() for p in Path(".").rglob("*") if p.is_file()]
    return [f for f in out if Path(f).suffix.lower() in EXTS and not f.startswith(SKIP)]


def main() -> int:
    hits = 0
    for f in files():
        try:
            text = Path(f).read_text("utf-8", errors="replace")
        except OSError:
            continue
        lines = text.splitlines()
        for m in TAG.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            if line_no <= len(lines) and "a11y:ok" in lines[line_no - 1]:
                continue
            for msg in check_tag(m.group("name"), m.group("attrs")):
                print(f"{f}:{line_no}: {msg}")
                hits += 1
    if hits:
        print(f"\n{hits} possible accessibility issue(s). Mark false positives with 'a11y:ok' on the line.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
