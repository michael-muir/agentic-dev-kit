# Unreal technical-art review checklist

## Naming and structure
- [ ] Asset names use the project's prefixes (BP_, M_, MI_, MF_, T_, SM_, SK_, ABP_, NS_, WBP_ …). Gate step: `unreal-technical-artist:asset-naming`.
- [ ] Assets live in feature folders, not dumped in `Content/` root. There are no spaces or non-ASCII characters in paths.
- [ ] Redirectors are fixed up after moves or renames.
- [ ] Binary assets are tracked by Git LFS (or the project's VCS), as `.gitattributes` says.

## Materials and shaders
- [ ] Material instances are used for variations. Master materials are few, and parameterised.
- [ ] Shader permutations are kept low (static switches and usage flags are checked).
- [ ] Instruction count and texture samplers are within budget for the target platform.
- [ ] Translucency and masked materials are justified, with overdraw considered.

## Meshes, LOD and Nanite
- [ ] Nanite is enabled where appropriate (opaque, high-poly). Fallback meshes are sized for non-Nanite paths.
- [ ] Non-Nanite meshes have LODs and screen sizes that make sense. Collision is simple, where possible.
- [ ] Skeletal meshes have LODs, and bone counts within the platform budget.

## Textures
- [ ] Sizes are powers of two, and within budget. Compression settings match usage (normal maps, masks, UI).
- [ ] sRGB is off for data textures (masks, normals, ORM). Mip generation is appropriate.
- [ ] Texture groups and streaming are set. There are no uncompressed textures without a reason.

## Effects (Niagara)
- [ ] Particle counts and bounds are set. GPU vs CPU simulation is chosen deliberately.
- [ ] Scalability and culling are set up (distance, significance, effect types).

## Blueprint / C++ boundary
- [ ] Heavy per-frame logic is in C++. Blueprints orchestrate content.
- [ ] Blueprint Tick is used only when needed. Timers and events are preferred.
- [ ] Hard references that pull large assets into memory are avoided (soft references, asset manager).

## Budgets
- [ ] Frame-time budget (game thread, draw, GPU) per platform is stated in the spec, and backed by a capture.
- [ ] Memory budget (textures, meshes) is checked with `memreport`, or the Size Map.
