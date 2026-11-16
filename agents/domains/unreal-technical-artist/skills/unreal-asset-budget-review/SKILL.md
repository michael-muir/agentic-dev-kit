---
name: unreal-asset-budget-review
description: Use when reviewing or planning Unreal Engine content (materials, meshes, textures, Niagara, levels) against performance and memory budgets, to turn budget claims into measured evidence.
---

# Unreal asset budget review

## Steps
1. **Get the budgets.** Read the target platforms and budgets from the spec's Constraints
   (frame time per thread, GPU ms, draw calls, triangles, texture memory). If none are stated,
   propose them as ACs, and mark the review `needs-human`.
   **Done when:** each platform has numeric budgets, or there's a `needs-human` finding.
2. **Inventory the change.** List each added or changed asset with its type, path, and its
   size where it can be read (texture dimensions, LOD count, material instruction count from
   the editor's stats, Niagara emitter counts).
   **Done when:** each asset in the diff has a row. Unknown values are marked "needs capture".
3. **Require captures.** For anything that affects runtime cost, ask for a capture from the
   target hardware, or the closest available: `stat unit`, `stat gpu`, `ProfileGPU`, an Unreal
   Insights trace, or `memreport -full`. Attach the paths to the task.
   **Done when:** each budget line has a measured number, or is marked unverified.
4. **Compare.** Budget vs measured, per platform. An overrun is `major`. Being within 10% of
   the budget is `minor`, with a note.
   **Done when:** the comparison table is in the findings.
5. **Recommend levers**, in order of cost: scalability settings, LOD and culling distances,
   texture size and compression, material simplification (static switches, fewer samplers),
   Nanite adoption, and moving Blueprint per-frame logic to C++.
