#!/usr/bin/env python3
"""Flag numeric assignments to physical-quantity variables whose names carry no unit.

Heuristic and advisory. It flags `altitude = 1200` and `float airSpeed = 10;`, but accepts
`altitude_m = 1200`, `airSpeedKts = 10`, a typed quantity (`altitude: Meters = ...`), or any
line containing `units:ok`. Matches print as path:line: message.
Exit code 1 if any were found, 0 otherwise.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

QUANTITIES = {
    "altitude", "alt", "height", "elevation", "range", "distance", "velocity", "vel", "speed",
    "airspeed", "groundspeed", "accel", "acceleration", "thrust", "force", "torque", "moment",
    "mass", "weight", "pressure", "temperature", "temp", "density", "angle", "heading",
    "bearing", "pitch", "roll", "yaw", "azimuth", "latitude", "lat", "longitude", "lon",
    "omega", "duration", "timeout", "period", "frequency", "freq",
}
UNITS = {
    "m", "km", "ft", "nm", "nmi", "mi", "mm", "cm", "mps", "kmh", "kph", "fps", "kts", "kt",
    "knots", "mach", "g", "mps2", "fps2", "n", "kn", "lbf", "nm", "kg", "lb", "lbs", "slug",
    "pa", "kpa", "hpa", "mbar", "bar", "psi", "inhg", "k", "c", "f", "degc", "degf", "kgm3",
    "deg", "degs", "rad", "rads", "mrad", "dps", "radps", "rpm", "hz", "khz", "s", "sec", "ms",
    "msec", "us", "ns", "min", "hr", "h",
}
EXTS = {".py", ".cpp", ".cc", ".cxx", ".h", ".hpp", ".cs", ".rs", ".go", ".ts", ".js", ".lua"}

ASSIGN = re.compile(
    r"\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?::\s*(?P<type>[A-Za-z_][\w:<>]*))?\s*:?=\s*-?\d"
)
TYPED = re.compile(r"meter|feet|foot|second|radian|degree|newton|kilogram|pascal|kelvin|quantity|unit", re.I)


def tokens(name: str) -> list[str]:
    """Split snake_case and camelCase identifiers into lowercase tokens."""
    parts: list[str] = []
    for chunk in name.split("_"):
        parts += re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", chunk)
    return [p.lower() for p in parts if p]


def is_unitless_quantity(name: str, type_name: str) -> bool:
    toks = tokens(name)
    if not toks or not any(t in QUANTITIES for t in toks):
        return False
    if TYPED.search(type_name or ""):
        return False
    # the last token must be a unit, and must not itself be the quantity word
    return not (len(toks) > 1 and toks[-1] in UNITS)


def tracked_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard"],
                             capture_output=True, text=True, check=True).stdout
        names = out.splitlines()
    except (OSError, subprocess.CalledProcessError):
        names = [p.as_posix() for p in Path(".").rglob("*")]
    return [Path(p) for p in names if Path(p).suffix in EXTS and not p.startswith(".agentic/")]


def main() -> int:
    hits = 0
    for path in tracked_files():
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        for no, line in enumerate(lines, 1):
            if "units:ok" in line:
                continue
            for m in ASSIGN.finditer(line):
                if is_unitless_quantity(m.group("name"), m.group("type")):
                    name = m.group("name")
                    print(f"{path.as_posix()}:{no}: '{name}' looks like a physical quantity without a unit "
                          f"(e.g. {name}_m, {name}_deg). Add a unit suffix or type, or 'units:ok' to silence.")
                    hits += 1
    if hits:
        print(f"\n{hits} possible unit-less quantities.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
