# Tightening the loop

A tight loop is one an agent can run after every change and trust completely. Work through these in order. Each section lists the moves that make a signal earlier, faster, more honest or more precise.

## One command per tier

- **Inner loop:** one command that type-checks and runs the tests near the change, in seconds. Use watch mode or a related-tests flag: `vitest related`, `pytest --lf -x`, `cargo nextest run -E 'rdeps(...)'`, `go test ./pkg/...`, `swift test --filter`.
- **Gate:** one command that runs everything a merge needs, and exits non-zero on any failure. The agent should never have to remember a sequence.
- Write both commands at the top of AGENTS.md or CLAUDE.md, and in NET.md.

## Earlier

- Move checks into the compiler: strict mode, warnings as errors, exhaustive switches, banned escape hatches in new code.
- Run the type checker and linter in the editor or language server so they fire while the agent writes.
- Validate config, environment and feature flags at startup, so a bad deploy fails in the smoke test, not on the first request.
- Turn a recurring review comment into a lint rule.
- Turn every rule in a design or style doc (tap target sizes, units, wording, colours) into a sweep that checks all pages or call sites at once, instead of one hand-written assertion per component.
- Delete the dangerous alternative. When a helper produces the wrong format or unit for the product, remove it so the compiler rejects every future use.

## Faster

- Measure first: list the slowest tests and the slowest setup steps.
- Push tests down the seams: replace an end-to-end test that checks logic with a unit test, and keep the end-to-end test for wiring only.
- Use real, fast dependencies over mocks: in-memory or containerised databases with per-test transactions or templates, local fakes for HTTP.
- Parallelise and shard: `vitest` threads, `pytest-xdist`, `cargo nextest`, `go test -p`, Playwright workers, parallel testing in Xcode.
- Cache builds and test results, and only run what the change can affect (test impact analysis, `--changed`, affected-project graphs in monorepos).
- Move slow, rarely failing suites (fuzzing, load, full mutation, device matrices) to nightly runs, and keep a fast slice of each at the gate.
- Remove sleeps and fixed waits; wait on conditions instead.
- Run heavy suites on build machines when the local machine is shared or small, following the environment's routing rules.

## Honest

- Find flakes: rerun the suite many times, in random order and in parallel.
- Fix the cause, which is usually shared state, real time, real network, ordering or randomness. Inject the clock, the random seed and the network.
- Quarantine a flake you can't fix yet, with a named reason in NET.md. Never leave it retrying silently: an agent will learn that red means nothing.
- Pin tool and dependency versions so the same commit gives the same result.
- Cut tests loose from the host. A test that reads `/etc`, a production env file or a real service, or demands one exact runtime version, fails on every other machine, and agents learn to ignore it. Inject paths and versions through parameters or environment, with fixtures.
- Wait on the page or process being ready, never on the network going idle. Dev servers and analytics keep connections open.

## Precise

- Assert on behaviour through public interfaces, with expected-vs-actual output.
- Name tests as sentences describing behaviour, so a failure reads as a bug report.
- Make end-to-end and integration failures carry their evidence: a trace, a screenshot, the request and response, the relevant log lines.
- Keep property and fuzz counterexamples shrunk and saved.
- Print the seed for anything random.
- Make every sweep name each offender by something grep can find: the href, id, test id or nearest labelled container. A list of sizes without locators costs a search per finding.
- Make error messages in the product itself say what was wrong, where, and what was expected. Agents read them too.

## Agent-specific

- Agents run the commands they can see. A signal that isn't one documented command does not exist for them.
- Agents trust green. A suite with weak assertions trains overconfidence. Mutation-test the core to find tests that pass without checking anything.
- Agents loop on noise. Warnings that never fail the build, and logs full of expected errors, waste their attention. Make the gate quiet when green.
- Agents can write tests faster than humans can. Spend that on properties, fuzz harnesses and stateful models, the techniques humans skip because they take thought.
- When an agent fixes a bug, the commit should contain the fix for every sibling and the guard that kills the class, at the fastest tier it can run. Require it in AGENTS.md.
