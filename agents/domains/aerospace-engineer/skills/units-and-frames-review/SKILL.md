---
name: units-and-frames-review
description: Use when reviewing or designing code that handles physical quantities, vectors, rotations or time in aerospace or simulation contexts, to trace units, reference frames and conventions across every interface.
---

# Units and frames review

## Steps
1. **List the interfaces.** For each function, message, file format or API that the diff
   touches and that carries a physical quantity, list the quantity, its unit, its frame (for
   vectors), and its convention (for angles and rotations).
   **Done when:** every changed interface has a row, and any unknown value is marked "unstated".
2. **Trace each value end to end.** Follow each quantity from its source (a sensor, a file,
   the user, a constant) to its sink. At each hop, check that the unit and frame are
   unchanged, or explicitly converted.
   **Done when:** every conversion is located, and checked against an independent value (a
   conversion factor from a standard, or a hand calculation).
3. **Check rotations.** For each rotation, confirm the direction (frame A→B or B→A), the
   composition order, the quaternion component order, and the handedness. Write one test that
   rotates a known vector and compares it with a hand-computed result.
   **Done when:** each rotation has a known-vector test, or a finding.
4. **Check time.** Confirm the time scale, epoch, and units (s, ms, ticks) at each interface,
   and how leap seconds and wrap-around are handled.
   **Done when:** each time value has a stated scale and unit.
5. **Record.** "Unstated" entries become `major` findings when they cross a module or process
   boundary, and `minor` inside one function.
