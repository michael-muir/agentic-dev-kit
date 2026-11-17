---
name: performance-review
description: Use when a change touches hot paths, data volume, latency, memory, frame time or any performance budget in the spec, to measure it against the budget and the base branch with repeatable benchmarks instead of guessing.
---

# Performance review

Opinions about speed are usually wrong. Measure, compare, and leave a benchmark behind.

## Steps
1. **Find the budgets.** Read the spec's Constraints for latency (p50/p95/p99), throughput,
   memory, allocations, start-up time, binary or bundle size, and frame time per platform.
   **Done when:** each relevant budget is listed with its number and unit, or marked missing.
2. **Find what the change makes hot.** In the diff, look for loops over unbounded input,
   nested iteration (O(n²)), per-item I/O or queries (N+1), allocation in hot loops, locks on
   hot paths, blocking calls in async code, unbounded caches or queues, and large copies.
   **Done when:** you have a list of suspect paths, each with the input size that matters.
3. **Measure the base and the head** with the stack's benchmark tool, on the same machine,
   with warm-up, several iterations and realistic input sizes (including the largest the
   spec allows).
   | Stack | Benchmark | Profile |
   |---|---|---|
   | python | pytest-benchmark, pyperf | cProfile, py-spy, tracemalloc |
   | javascript / typescript | vitest bench, tinybench | `node --cpu-prof`, Chrome DevTools |
   | rust | criterion, divan | cargo flamegraph, heaptrack |
   | go | `go test -bench -benchmem` | pprof |
   | dotnet | BenchmarkDotNet | dotnet-trace, dotnet-counters |
   | cpp | Google Benchmark, nanobench | perf, VTune, Tracy |
   | lua | os.clock loops, LuaJIT `-jp` | LuaJIT profiler |
   | Unreal | `stat unit` / `stat gpu`, automation perf tests | Unreal Insights |
   **Done when:** each suspect path has a base number and a head number, with the variance.
4. **Judge with the numbers.**
   - Over budget → `major`, or `critical` if users or safety are affected.
   - A regression of more than 10% against base on a budgeted path, even within budget → `minor`,
     with the trend noted.
   - A difference within the measurement noise → no finding. Say so.
   **Done when:** each finding cites the base, the head, the budget and the benchmark name.
5. **Leave the benchmark.** Commit the benchmarks so the measurement can be repeated. If CI
   can run them reliably, propose a gate step to the retro agent (an advisory step first).
   **Done when:** the benchmarks are committed, and their run command is in the findings.

## Notes
- Fix the input, the seed and the environment. Report the CPU, OS and build mode (always
  measure release/optimised builds).
- Microbenchmarks can mislead. Confirm a big claim with an end-to-end measurement.
