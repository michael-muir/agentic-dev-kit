# Testing the kit

Run this smoke test after changing scripts, agents or skills. It installs the kit into a
throwaway repo, checks that the generated files are produced, and confirms the built-in gate
checks catch what they should.

```bash
python adapters/build.py --check
python docs/smoke_test.py
```

`smoke_test.py` creates a throwaway repo in the system temp folder
(`agentic-dev-kit-smoke/`) and checks the following:

1. A fresh install with `--stacks python --domains aerospace-engineer,unreal-technical-artist
   --tools claude,copilot,cursor,gemini,generic` produces AGENTS.md, CLAUDE.md, GEMINI.md, the
   registry, and the agent and skill files for every tool.
2. `--update` keeps state files and hand-edited project notes, and refreshes the managed block.
3. An approved spec with an AC no test names fails `builtin:trace`. Adding the test makes it pass.
4. `lock-tests` locks the AC test. Editing it fails `builtin:test-lock`, and re-locking passes.
5. A leftover debug tag fails `builtin:debug-tags`, and a fake key fails `builtin:secrets`.
6. Standards packs: configs are copied without overwriting existing files,
   `CODING_STANDARDS.md` is generated with one section per pack plus Project rules,
   `--update` keeps Project rules, a pack step `replaces` its profile step, and conflicting
   packs, or packs for unselected stacks, are rejected.

7. Role scopes: an implementer commit touching a lock file fails `builtin:scope`, a
   test-designer's passes, unknown roles fail, and human commits are left alone. Claude deny
   rules and CODEOWNERS are generated.
8. Runner: with a scripted fake engine (`docs/fake_agent.py`), `loop` runs test-designer →
   implementer → verifier → integrator, then stops at review. Every step commits with its
   trailer and passes the scope check. `plan` warns when independent roles share an engine.
   The optional files are generated: dependabot, review workflow, devcontainer, `.prettierignore`.

9. Cost controls: the default `track` mode records a Spend row. `enforce` blocks a task at
   its cost limit, at the review-round limit, and at the daily limit. `warn` continues.
   `off` records nothing. `--ignore-budgets` runs once and is recorded. Codex-style usage
   events are summed and priced.

It prints `SMOKE OK` and exits 0 on success.

## Fixtures: the real tools

`fixtures/<stack>/` holds a tiny sample project per stack. `fixture_test.py` installs the
kit into a copy, with no pack or a chosen pack, and runs `gate.py run --stage ci` with the
real tools:

```bash
python fixtures/fixture_test.py --stack dotnet --standards dotnet-stylecop
```

The kit's CI (`.github/workflows/kit-ci.yml`) runs every stack × pack combination on Linux,
and the smoke test on Windows and Linux.
