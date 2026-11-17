---
name: release-process
description: Use when preparing a release, to choose the semantic version from the merged changes, convert the Unreleased changelog into a dated version section, bump every version field consistently, write release notes, and hand the tag to a human.
---

# Release process

## Steps
1. **Collect the changes.** List the PRs merged since the last tag
   (`git log <last-tag>..origin/main --merges --oneline`, or the first-parent history for
   squash merges), and read the `## Unreleased` changelog section.
   **Done when:** every merged PR maps to a changelog entry, and missing entries have been added.
2. **Choose the version** (Semantic Versioning):
   | The release contains | Bump |
   |---|---|
   | any **Breaking** entry (a removed or changed public API, file format or config, or behaviour callers rely on) | MAJOR (or MINOR while `0.x`) |
   | new backwards-compatible capability (Added) | MINOR |
   | only fixes, docs, performance or internal changes | PATCH |
   Pre-releases use `-rc.N`, `-beta.N`.
   **Done when:** the version and the reason are written in the handoff.
3. **Bump every version field** the project uses, together: `VERSION`, `package.json`
   (and its lockfile, via `npm version --no-git-tag-version`), `Cargo.toml` (and `Cargo.lock`),
   `pyproject.toml`, `*.csproj` / `Directory.Build.props` `<Version>`, `*.rockspec`, and
   `*.uplugin` `VersionName`.
   **Done when:** a search for the old version string finds only history (the changelog and old release notes).
4. **Date the changelog.** Rename `## Unreleased` to `## X.Y.Z — YYYY-MM-DD`, start a new empty
   `## Unreleased`, and update the compare links if the file uses them.
   **Done when:** the changelog has the new section, and an empty Unreleased.
5. **Write the release notes** at `docs/releases/vX.Y.Z.md`: highlights first, then breaking
   changes with migration steps, then the full list grouped as in the changelog, with links to PRs and specs.
   **Done when:** a user upgrading can tell from the notes alone what to do.
6. **Verify.** The gate passes on the release branch, the build artifacts build, and the
   version printed by the built artifact (`--version`, package metadata) is the new one.
   **Done when:** the commands and outputs are in the handoff.
7. **Hand over the tag.** After the release PR merges, give the human the annotated-tag
   commands for the merge commit. Publishing to registries or stores follows the project's
   documented steps, and is always started by the human.

## Notes
- Never retag a published version. Fix forward with a new PATCH release.
- A release that includes a `one-way-door` change needs the human to confirm the rollback
  plan in the release PR.
