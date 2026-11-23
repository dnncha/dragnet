# Technique catalog

Generated from `data/catalog.json`. Each entry is a feedback signal. Judge it by when it fires (tier), how fast it runs (speed), what it catches, and how precisely its failure points at the fix.

Tiers: `edit` fires while the agent edits (editor, compiler, watch mode); `inner` the agent's change loop, run after every change; `gate` the one-command gate before a commit, merge or release; `nightly` scheduled or background runs; `production` signals from the running product; `human` needs a person.

## Index

| Technique | Tier | Speed | Setup | Catches |
|---|---|---|---|---|
| [Linting and static analysis](#lint) | edit | instant | low | logic, types, concurrency, security, a11y |
| [Strict type checking](#types) | edit | instant | low | types, wiring, contract, regression |
| [Assertions and design by contract](#assertions) | inner | instant | low | logic, edge, data, concurrency |
| [Boundary value and equivalence partitioning](#boundary) | inner | instant | low | edge |
| [Parameterized and table-driven tests](#parameterized) | inner | instant | low | edge, logic, regression |
| [Schema validation at boundaries](#schema) | inner | instant | low | types, contract, data, security |
| [Snapshot and characterization tests](#snapshot) | inner | instant | low | regression |
| [Unit tests](#unit) | inner | instant | low | logic, edge, regression |
| [Component tests](#component) | inner | seconds | medium | ui, logic, wiring |
| [Metamorphic tests](#metamorphic) | inner | seconds | medium | logic |
| [Property-based tests](#property) | inner | seconds | medium | edge, logic, crash, data |
| [Accessibility checks](#a11y) | gate | seconds | low | a11y |
| [Code coverage](#coverage) | gate | seconds | low | measures the net |
| [Combinatorial and pairwise tests](#combinatorial) | gate | seconds | low | platform, wiring, edge |
| [Concurrency and interleaving tests](#concurrency) | gate | seconds | medium | concurrency |
| [Contract tests](#contract) | gate | seconds | medium | contract |
| [Dependency and secret scanning](#deps) | gate | seconds | low | security |
| [Differential tests](#differential) | gate | seconds | low | logic, regression, edge |
| [Integration tests](#integration) | gate | seconds | medium | wiring, data, contract, regression |
| [Model-based and stateful tests](#model) | gate | seconds | high | logic, data, concurrency |
| [Sanitizers](#sanitizers) | gate | seconds | low | crash, concurrency, security |
| [Security static analysis (SAST)](#sast) | gate | seconds | low | security |
| [Smoke tests](#smoke) | gate | seconds | low | wiring, crash |
| [Acceptance tests](#acceptance) | gate | minutes | medium | requirements |
| [End-to-end tests](#e2e) | gate | minutes | high | ui, wiring, regression, requirements |
| [LLM evals](#evals) | gate | minutes | medium | logic, regression, requirements |
| [Localization and pseudo-localization](#i18n) | gate | minutes | low | platform, visual |
| [Property-based UI exploration](#ui-property) | gate | minutes | medium | ui, visual, a11y, crash, logic, data, perf |
| [Visual regression tests](#visual) | gate | minutes | medium | visual, regression |
| [Benchmarks and performance regression tests](#benchmark) | nightly | minutes | medium | perf, regression |
| [Chaos and fault injection](#chaos) | nightly | minutes | high | resilience |
| [Compatibility and cross-platform tests](#compatibility) | nightly | minutes | medium | platform |
| [Deterministic simulation](#simulation) | nightly | minutes | high | concurrency, resilience, data |
| [Flaky test detection](#flaky) | nightly | minutes | low | concurrency |
| [Model checking](#model-checking) | nightly | minutes | high | concurrency, logic, resilience |
| [Dynamic security scanning (DAST)](#dast) | nightly | hours | medium | security |
| [Fuzzing](#fuzz) | nightly | hours | medium | crash, security, edge |
| [Load, stress, spike and soak tests](#load) | nightly | hours | high | perf, resilience, concurrency |
| [Mutation testing](#mutation) | nightly | hours | low | measures the net |
| [Symbolic and concolic execution](#symbolic) | nightly | hours | high | crash, edge, security |
| [A/B and beta testing](#ab) | production | continuous | medium | requirements |
| [Canary and progressive rollout](#canary) | production | continuous | medium | regression, perf, platform, wiring |
| [Observability and error tracking](#observability) | production | continuous | medium | crash, perf, resilience, platform |
| [Shadow traffic and replay](#shadow) | production | continuous | high | regression, perf, contract |
| [Synthetic monitoring](#synthetic) | production | continuous | low | wiring, regression, resilience |
| [Code review](#review) | human | manual | low | logic, requirements, security |
| [Exploratory testing](#exploratory) | human | manual | low | ui, requirements, visual, edge |
| [Formal verification](#formal) | human | manual | high | logic, edge, crash |
| [Penetration testing](#pentest) | human | manual | high | security |
| [Usability testing](#usability) | human | manual | medium | requirements |

## Static signals: catch bugs without running the code

<a id="types"></a>
### Strict type checking

The compiler or checker proves shapes, nullability and call signatures before anything runs.

- **Tier / speed / setup:** edit · instant · low
- **Catches:** types, wiring, contract, regression
- **Strengths:** Instant, exhaustive over all paths, points at file and line, and makes refactors safe for agents.
- **Gaps:** Says nothing about values, logic or behaviour, and escape hatches (any, force unwraps, casts) silently switch it off.
- **Signal quality:** Best-in-class: fastest, deterministic, exact location, readable message.
- **Use when:** Always. Turn on the strictest mode the language offers and ban escape hatches in new code.
- **Covers its gaps:** [Unit tests](#unit), [Property-based tests](#property), [Assertions and design by contract](#assertions)
- **Tools:** JS/TS: TypeScript strict, noUncheckedIndexedAccess · Python: pyright strict, mypy --strict · Swift: Swift 6 language mode, strict concurrency · Rust: the compiler · Go: the compiler, go vet · JVM: Kotlin, NullAway, Checker Framework

<a id="lint"></a>
### Linting and static analysis

Rules flag bug patterns, unsafe APIs, dead code and style drift.

- **Tier / speed / setup:** edit · instant · low
- **Catches:** logic, types, concurrency, security, a11y
- **Strengths:** Encodes past mistakes as rules, runs in milliseconds, and gives agents a precise fix hint.
- **Gaps:** Pattern-based, so it misses novel bugs, and noisy rule sets train agents to suppress warnings.
- **Signal quality:** Excellent when the rule set is curated and warnings fail the build.
- **Use when:** Always. Turn each escaped bug class that a pattern can catch into a custom rule.
- **Covers its gaps:** [Strict type checking](#types), [Unit tests](#unit), [Security static analysis (SAST)](#sast)
- **Tools:** JS/TS: ESLint, Biome, oxlint · Python: Ruff · Swift: SwiftLint · Rust: Clippy · Go: staticcheck, golangci-lint · JVM: Error Prone, detekt

<a id="assertions"></a>
### Assertions and design by contract

Preconditions, postconditions and invariants checked inside the code at runtime.

- **Tier / speed / setup:** inner · instant · low
- **Catches:** logic, edge, data, concurrency
- **Strengths:** Turns silent corruption into a loud failure at the point of the bug, and makes every other test stronger.
- **Gaps:** Only fires on paths that run, and costs a little at runtime.
- **Signal quality:** Fails exactly where state first goes wrong instead of three calls later.
- **Use when:** Core data structures, state machines, money, anything with an invariant you can state.
- **Covers its gaps:** [Property-based tests](#property), [Fuzzing](#fuzz)
- **Tools:** JS/TS: node:assert, invariant · Python: assert, icontract · Swift: precondition, assert · Rust: assert!, debug_assert! · Go: explicit panics in debug builds · JVM: Guava Preconditions

<a id="schema"></a>
### Schema validation at boundaries

Parse every external input (HTTP, files, env, LLM output) against a schema before using it.

- **Tier / speed / setup:** inner · instant · low
- **Catches:** types, contract, data, security
- **Strengths:** Extends type safety to data the compiler can't see, with clear errors at the edge.
- **Gaps:** Validates shape, not meaning, and schemas drift if they aren't the single source of truth.
- **Signal quality:** Names the exact field that is wrong.
- **Use when:** Any input crossing a process, network or trust boundary.
- **Covers its gaps:** [Contract tests](#contract), [Fuzzing](#fuzz)
- **Tools:** JS/TS: Zod, Valibot, ArkType · Python: Pydantic · Swift: Codable with strict decoding · Rust: serde with deny_unknown_fields · Go: go-playground/validator · JVM: Jackson with strict mode, JSON Schema

<a id="sast"></a>
### Security static analysis (SAST)

Scans source for injection, unsafe deserialization, weak crypto and taint flows.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** security
- **Strengths:** Runs before deploy and finds whole classes of vulnerability across the codebase.
- **Gaps:** False positives, and blind to runtime configuration and business-logic flaws.
- **Signal quality:** Good location, noisy unless rules are tuned.
- **Use when:** Anything handling user input, auth or money.
- **Covers its gaps:** [Dynamic security scanning (DAST)](#dast), [Penetration testing](#pentest)
- **Tools:** Any: Semgrep, CodeQL

## Tests by scope: examples written by hand

<a id="unit"></a>
### Unit tests

One function, class or module checked on hand-picked examples.

- **Tier / speed / setup:** inner · instant · low
- **Catches:** logic, edge, regression
- **Strengths:** Fast, precise failure location, cheap to write, and the main inner-loop signal for agents.
- **Gaps:** Only covers cases someone thought of, and heavy mocking tests the mocks instead of the code.
- **Signal quality:** Excellent when tests hit public behaviour and failure messages show expected against actual.
- **Use when:** Pure logic, parsers, formatters, calculations, state transitions.
- **Covers its gaps:** [Property-based tests](#property), [Integration tests](#integration), [Mutation testing](#mutation)
- **Tools:** JS/TS: Vitest, node:test · Python: pytest · Swift: Swift Testing, XCTest · Rust: cargo test, cargo-nextest · Go: go test · JVM: JUnit 5

<a id="parameterized"></a>
### Parameterized and table-driven tests

One test body run over many rows of inputs and expected outputs.

- **Tier / speed / setup:** inner · instant · low
- **Catches:** edge, logic, regression
- **Strengths:** Cheap breadth, and each escaped bug becomes one new row.
- **Gaps:** Still limited to the rows written down.
- **Signal quality:** Names the failing row.
- **Use when:** Any function with a clear input-to-output mapping.
- **Covers its gaps:** [Property-based tests](#property), [Boundary value and equivalence partitioning](#boundary)
- **Tools:** JS/TS: test.each · Python: pytest.mark.parametrize · Swift: @Test(arguments:) · Rust: rstest · Go: table-driven tests · JVM: @ParameterizedTest

<a id="component"></a>
### Component tests

A larger unit, such as a UI component or service module, exercised through its public interface.

- **Tier / speed / setup:** inner · seconds · medium
- **Catches:** ui, logic, wiring
- **Strengths:** Realistic behaviour without booting the whole system.
- **Gaps:** Fakes at the edges can drift from reality.
- **Signal quality:** Good, as long as queries target roles and labels rather than internals.
- **Use when:** UI components with state, modules with several collaborators.
- **Covers its gaps:** [Integration tests](#integration), [End-to-end tests](#e2e), [Visual regression tests](#visual)
- **Tools:** JS/TS: Testing Library, Storybook interaction tests · Swift: ViewInspector, view model tests · JVM: Compose UI tests

<a id="integration"></a>
### Integration tests

Real components together: code plus a real database, queue, filesystem or HTTP server.

- **Tier / speed / setup:** gate · seconds · medium
- **Catches:** wiring, data, contract, regression
- **Strengths:** Catches serialization, query, schema and configuration bugs that mocks hide.
- **Gaps:** Slower, needs setup, and failures point at a seam rather than a line.
- **Signal quality:** Good when each test owns its data and logs the failing request.
- **Use when:** Anything that talks to storage or another process.
- **Covers its gaps:** [Contract tests](#contract), [End-to-end tests](#e2e)
- **Tools:** Python: pytest with real Postgres · Go: httptest · JVM: Spring Boot test slices · Any: Testcontainers

<a id="contract"></a>
### Contract tests

Provider and consumer each verify they honour a shared API contract.

- **Tier / speed / setup:** gate · seconds · medium
- **Catches:** contract
- **Strengths:** Catches breaking API changes in seconds without a full environment.
- **Gaps:** Only as good as the contract, and blind to business logic.
- **Signal quality:** Names the field or endpoint that broke.
- **Use when:** Separately deployed services, mobile apps against a backend, public APIs.
- **Covers its gaps:** [Integration tests](#integration), [End-to-end tests](#e2e)
- **Tools:** Any: Pact, Schemathesis for OpenAPI, buf breaking for protobuf

<a id="e2e"></a>
### End-to-end tests

Real user flows driven through the UI against the running stack.

- **Tier / speed / setup:** gate · minutes · high
- **Catches:** ui, wiring, regression, requirements
- **Strengths:** Closest to what users experience, and proves the whole path works.
- **Gaps:** Slow, flaky, costly to maintain, and failures point at a screen rather than a cause.
- **Signal quality:** Weak alone: pair with traces, screenshots and logs so the agent sees why.
- **Use when:** A handful of revenue-critical or signup-critical paths only.
- **Covers its gaps:** [Integration tests](#integration), [Component tests](#component), [Property-based UI exploration](#ui-property)
- **Tools:** JS/TS: Playwright · Swift: XCUITest · JVM: Espresso · Mobile: Maestro, Detox

<a id="smoke"></a>
### Smoke tests

The build starts, the main page loads, the health endpoint answers.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** wiring, crash
- **Strengths:** Seconds to run, and catches the broken build before anything else does.
- **Gaps:** Shallow by design.
- **Signal quality:** Binary and fast.
- **Use when:** After every build and every deploy.
- **Covers its gaps:** [End-to-end tests](#e2e), [Integration tests](#integration)
- **Tools:** Any: curl script, one Playwright test, app launch check

<a id="acceptance"></a>
### Acceptance tests

Checks the software meets the stated requirement, often written as Given/When/Then.

- **Tier / speed / setup:** gate · minutes · medium
- **Catches:** requirements
- **Strengths:** Ties tests to the reason the feature exists, and gives agents an executable spec.
- **Gaps:** Late and often manual, and only as precise as the requirement.
- **Signal quality:** Good as a definition of done for an agent task.
- **Use when:** Before starting a feature: write the acceptance check first.
- **Covers its gaps:** [Usability testing](#usability), [Exploratory testing](#exploratory)
- **Tools:** Any: Cucumber, behave, plain tests named as scenarios

## Generated and oracle-free tests: more inputs than anyone would write

<a id="property"></a>
### Property-based tests

Generate many inputs and assert invariants such as round-trips, ordering and idempotence.

- **Tier / speed / setup:** inner · seconds · medium
- **Catches:** edge, logic, crash, data
- **Strengths:** Finds cases nobody imagined, and shrinks each failure to a minimal reproduction.
- **Gaps:** Properties take thought to write, and rare paths can still be missed.
- **Signal quality:** Excellent: the shrunk counterexample is the bug report.
- **Use when:** Parsers, serializers, encoders, math, data structures, anything with a round-trip.
- **Covers its gaps:** [Fuzzing](#fuzz), [Mutation testing](#mutation)
- **Tools:** JS/TS: fast-check · Python: Hypothesis · Swift: SwiftCheck · Rust: proptest · Go: rapid · JVM: jqwik

<a id="model"></a>
### Model-based and stateful tests

Random sequences of operations run against the system and a simple model, compared step by step.

- **Tier / speed / setup:** gate · seconds · high
- **Catches:** logic, data, concurrency
- **Strengths:** Finds the bug that needs five specific steps in order.
- **Gaps:** The model is real work and can share the system's misunderstanding.
- **Signal quality:** Shrinks to the shortest failing operation sequence.
- **Use when:** Caches, editors, sync engines, state machines, anything with history.
- **Covers its gaps:** [Deterministic simulation](#simulation), [Model checking](#model-checking)
- **Tools:** JS/TS: fast-check commands · Python: Hypothesis RuleBasedStateMachine · Rust: proptest-state-machine · JVM: jqwik stateful

<a id="ui-property"></a>
### Property-based UI exploration

A tool drives the real UI with generated clicks, typing, scrolling and navigation, and checks temporal properties (always, eventually within, next) on every state it reaches, including leak properties over DOM nodes, listeners and heap.

- **Tier / speed / setup:** gate · minutes · medium
- **Catches:** ui, visual, a11y, crash, logic, data, perf
- **Strengths:** Turns every design, product and accessibility rule into a check on every reachable screen, finds the bug that needs a dozen steps in an unplanned order, and shrinks the failing trace with a screenshot of each state.
- **Gaps:** Random exploration only reaches shallow states unless runs are long, seeded with realistic data and steered with weighted actions; replay is not deterministic outside a deterministic hypervisor; a property never seen to fail may be checking nothing.
- **Signal quality:** Good when every violation is shrunk and carries its trace, screenshots and the property name; poor when browser driver errors are counted as failures.
- **Use when:** Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
- **Covers its gaps:** [End-to-end tests](#e2e), [Visual regression tests](#visual), [Model-based and stateful tests](#model)
- **Tools:** JS/TS: Bombadil (@antithesishq/bombadil), Quickstrom · Any: Bombadil browser and terminal drivers

<a id="fuzz"></a>
### Fuzzing

Coverage-guided mutation of inputs, looking for crashes, hangs and sanitizer failures.

- **Tier / speed / setup:** nightly · hours · medium
- **Catches:** crash, security, edge
- **Strengths:** Finds memory bugs, parser holes and security issues that nothing else does.
- **Gaps:** Mostly finds crashes rather than wrong answers, and needs CPU time and a harness.
- **Signal quality:** Saves a crashing input that becomes a permanent regression test.
- **Use when:** Untrusted input: file formats, network protocols, parsers, decoders.
- **Covers its gaps:** [Property-based tests](#property), [Differential tests](#differential), [Property-based UI exploration](#ui-property)
- **Tools:** JS/TS: Jazzer.js · Python: Atheris · Swift: libFuzzer via -sanitize=fuzzer · Rust: cargo-fuzz · Go: go test -fuzz · JVM: Jazzer

<a id="metamorphic"></a>
### Metamorphic tests

Assert relations between outputs when there is no exact expected answer.

- **Tier / speed / setup:** inner · seconds · medium
- **Catches:** logic
- **Strengths:** Works for search, ML, simulations and compilers where no oracle exists.
- **Gaps:** Good relations are hard to find, and they only check part of correctness.
- **Signal quality:** Clear when a relation breaks, but the root cause needs digging.
- **Use when:** Ranking, search, recommendations, numerical code, LLM pipelines.
- **Covers its gaps:** [Differential tests](#differential), [LLM evals](#evals)
- **Tools:** Any: write as property tests

<a id="differential"></a>
### Differential tests

Run two implementations or two versions on the same inputs and compare outputs.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** logic, regression, edge
- **Strengths:** Needs no oracle, and is perfect for rewrites, ports and optimisations.
- **Gaps:** Both sides can share a bug.
- **Signal quality:** Shows the input and both outputs.
- **Use when:** Refactors, rewrites, ports to a new language, fast paths against slow reference code.
- **Covers its gaps:** [Property-based tests](#property), [Unit tests](#unit)
- **Tools:** Any: a property test that calls both implementations

<a id="snapshot"></a>
### Snapshot and characterization tests

Compare output to a stored known-good copy.

- **Tier / speed / setup:** inner · instant · low
- **Catches:** regression
- **Strengths:** Near-zero effort, and locks down legacy behaviour before a refactor.
- **Gaps:** Locks in bugs too, and agents and humans rubber-stamp snapshot updates.
- **Signal quality:** Shows a diff, but cannot say whether the change was intended.
- **Use when:** Before refactoring legacy code, for CLI output, generated code, serialized formats.
- **Covers its gaps:** [Unit tests](#unit), [Property-based tests](#property)
- **Tools:** JS/TS: Vitest toMatchSnapshot · Python: syrupy · Swift: swift-snapshot-testing · Rust: insta · Go: go-snaps · Any: ApprovalTests

<a id="boundary"></a>
### Boundary value and equivalence partitioning

Pick inputs at the edges and one from each class of the input space.

- **Tier / speed / setup:** inner · instant · low
- **Catches:** edge
- **Strengths:** Cheap, and targets where off-by-one bugs live.
- **Gaps:** Depends on finding the right boundaries.
- **Signal quality:** Precise.
- **Use when:** Ranges, limits, pagination, dates, money, string lengths.
- **Covers its gaps:** [Property-based tests](#property)
- **Tools:** Any: parameterized tests

<a id="combinatorial"></a>
### Combinatorial and pairwise tests

Cover every pair of configuration values instead of every combination.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** platform, wiring, edge
- **Strengths:** Shrinks large configuration matrices to a handful of runs.
- **Gaps:** Misses bugs that need three or more factors at once.
- **Signal quality:** Names the failing combination.
- **Use when:** Feature flags, settings screens, build matrices, option-heavy CLIs.
- **Covers its gaps:** [Property-based tests](#property)
- **Tools:** Any: PICT, allpairspy

## Runtime checks: memory, concurrency, performance and resilience

<a id="sanitizers"></a>
### Sanitizers

Instrumented builds that trap memory errors, undefined behaviour and data races as they happen.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** crash, concurrency, security
- **Strengths:** Turns silent corruption into a stack trace at the faulting line.
- **Gaps:** Only checks paths the tests run, and slows the build by about two to three times.
- **Signal quality:** Excellent: exact stack and access type.
- **Use when:** Any native, unsafe or concurrent code. Run the existing suite under them.
- **Covers its gaps:** [Fuzzing](#fuzz), [Concurrency and interleaving tests](#concurrency)
- **Tools:** Swift: -sanitize=address,thread,undefined · Rust: Miri, -Zsanitizer · Go: go test -race · C/C++: ASan, UBSan, TSan, MSan

<a id="concurrency"></a>
### Concurrency and interleaving tests

Explore thread and task interleavings systematically or under stress.

- **Tier / speed / setup:** gate · seconds · medium
- **Catches:** concurrency
- **Strengths:** Reproduces races that normal runs hit once a month.
- **Gaps:** Can't cover the whole interleaving space.
- **Signal quality:** Good when the tool replays the failing schedule.
- **Use when:** Shared mutable state, actors, locks, async pipelines, lock-free code.
- **Covers its gaps:** [Model checking](#model-checking), [Deterministic simulation](#simulation)
- **Tools:** Swift: TSan, strict concurrency checking · Rust: loom, shuttle · Go: go test -race -count · JVM: jcstress, Lincheck

<a id="simulation"></a>
### Deterministic simulation

Run the whole system on a fake clock, network and disk with a seeded scheduler, injecting faults.

- **Tier / speed / setup:** nightly · minutes · high
- **Catches:** concurrency, resilience, data
- **Strengths:** Every failure replays exactly from its seed, which agents can debug step by step.
- **Gaps:** Requires designing the system for injectable time, I/O and randomness.
- **Signal quality:** Best possible for distributed bugs: one seed reproduces the failure.
- **Use when:** Databases, sync engines, distributed systems, anything with retries and timeouts.
- **Covers its gaps:** [Model checking](#model-checking)
- **Tools:** Rust: madsim, turmoil · Any: Antithesis

<a id="benchmark"></a>
### Benchmarks and performance regression tests

Measure latency, throughput, allocations or frame time of hot paths and compare to a baseline.

- **Tier / speed / setup:** nightly · minutes · medium
- **Catches:** perf, regression
- **Strengths:** Catches the slow commit when it lands, not when users complain.
- **Gaps:** Noisy on shared machines, and needs a stable baseline.
- **Signal quality:** Report the number and the change, and fail only on a large, repeated regression.
- **Use when:** Hot loops, startup time, rendering, audio, anything users feel.
- **Covers its gaps:** [Load, stress, spike and soak tests](#load)
- **Tools:** JS/TS: Vitest bench, tinybench · Python: pytest-benchmark · Swift: package-benchmark, XCTest metrics · Rust: criterion, divan · Go: go test -bench · JVM: JMH

<a id="load"></a>
### Load, stress, spike and soak tests

Drive expected, extreme, sudden or sustained traffic and watch latency, errors and memory.

- **Tier / speed / setup:** nightly · hours · high
- **Catches:** perf, resilience, concurrency
- **Strengths:** Shows capacity, breaking points, leaks and autoscaling behaviour.
- **Gaps:** Synthetic traffic differs from real traffic, and environments cost money.
- **Signal quality:** Coarse: tells you that it broke, and traces tell you why.
- **Use when:** Before launches, pricing changes or anything expecting a traffic jump.
- **Covers its gaps:** [Benchmarks and performance regression tests](#benchmark), [Chaos and fault injection](#chaos), [Observability and error tracking](#observability)
- **Tools:** Any: k6, Locust, Gatling, Artillery, vegeta

<a id="chaos"></a>
### Chaos and fault injection

Kill processes, drop packets, add latency and fail dependencies on purpose.

- **Tier / speed / setup:** nightly · minutes · high
- **Catches:** resilience
- **Strengths:** Proves retries, timeouts and fallbacks actually work.
- **Gaps:** Risky without good observability, and needs a production-like environment.
- **Signal quality:** Useful only with traces and alerts in place.
- **Use when:** Services with dependencies, offline-capable apps, payment flows.
- **Covers its gaps:** [Deterministic simulation](#simulation), [Observability and error tracking](#observability)
- **Tools:** Any: Toxiproxy, Chaos Mesh, network link conditioner

## User-facing surface: UI, accessibility, platforms

<a id="visual"></a>
### Visual regression tests

Screenshot pages or components and diff them against approved baselines.

- **Tier / speed / setup:** gate · minutes · medium
- **Catches:** visual, regression
- **Strengths:** Catches CSS and layout breakage that functional tests pass straight through.
- **Gaps:** Font and anti-aliasing noise, and someone must review each diff.
- **Signal quality:** The diff image is direct evidence an agent can read.
- **Use when:** Design systems, marketing pages, any UI an agent edits often.
- **Covers its gaps:** [Accessibility checks](#a11y), [End-to-end tests](#e2e)
- **Tools:** JS/TS: Playwright toHaveScreenshot, Chromatic · Swift: swift-snapshot-testing image strategy · JVM: Paparazzi, Roborazzi

<a id="a11y"></a>
### Accessibility checks

Automated audits for roles, labels, contrast and focus, plus manual screen reader passes.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** a11y
- **Strengths:** Automated rules catch a solid share of issues for almost no effort.
- **Gaps:** Automation misses most real usability problems for disabled users.
- **Signal quality:** Precise rule, element and fix.
- **Use when:** Every user interface.
- **Covers its gaps:** [Usability testing](#usability)
- **Tools:** JS/TS: axe-core, @axe-core/playwright · Swift: performAccessibilityAudit in XCUITest · JVM: Espresso accessibility checks

<a id="compatibility"></a>
### Compatibility and cross-platform tests

Run the suite across browsers, OS versions, devices, runtimes and screen sizes.

- **Tier / speed / setup:** nightly · minutes · medium
- **Catches:** platform
- **Strengths:** Catches the bug that only exists on Safari, Linux or an older OS.
- **Gaps:** The matrix explodes, and device farms cost money.
- **Signal quality:** Names the platform.
- **Use when:** Shipping to several browsers, OS versions or devices.
- **Covers its gaps:** [Combinatorial and pairwise tests](#combinatorial)
- **Tools:** JS/TS: Playwright projects · Swift: simulator destinations · Any: BrowserStack, device farms

<a id="i18n"></a>
### Localization and pseudo-localization

Run the UI with long, accented, right-to-left text and other locales' formats.

- **Tier / speed / setup:** gate · minutes · low
- **Catches:** platform, visual
- **Strengths:** Finds truncation, hard-coded strings and date or number format bugs early.
- **Gaps:** Needs native speakers to judge translation quality.
- **Signal quality:** Visible in screenshots.
- **Use when:** Any app with, or planning, translations.
- **Covers its gaps:** [Visual regression tests](#visual)
- **Tools:** Any: pseudo-locale builds, Xcode double-length pseudolanguage

<a id="exploratory"></a>
### Exploratory testing

A person or an agent drives the real product freely, looking for anything wrong.

- **Tier / speed / setup:** human · manual · low
- **Catches:** ui, requirements, visual, edge
- **Strengths:** Finds what nobody thought to script, and agents can now do a useful first pass.
- **Gaps:** Not repeatable unless findings become tests.
- **Signal quality:** Rich but unstructured: turn each finding into an automated test.
- **Use when:** After any user-visible change, before a release.
- **Covers its gaps:** [End-to-end tests](#e2e), [Visual regression tests](#visual), [Property-based UI exploration](#ui-property)
- **Tools:** Any: agent browser or simulator control, session recording

<a id="usability"></a>
### Usability testing

Real users attempt real tasks while you watch.

- **Tier / speed / setup:** human · manual · medium
- **Catches:** requirements
- **Strengths:** Finds confusion that no assertion can.
- **Gaps:** Slow, small samples, subjective.
- **Signal quality:** Qualitative.
- **Use when:** New flows, onboarding, anything with drop-off.
- **Covers its gaps:** [A/B and beta testing](#ab)
- **Tools:** Any: moderated sessions, session replay

## Security

<a id="deps"></a>
### Dependency and secret scanning

Check dependencies against vulnerability databases and the repo for committed secrets.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** security
- **Strengths:** Automatic and cheap, and catches the leaked key before it ships.
- **Gaps:** Only known CVEs, and noisy about unreachable code.
- **Signal quality:** Names the package, version and fix.
- **Use when:** Every repo.
- **Covers its gaps:** [Security static analysis (SAST)](#sast)
- **Tools:** JS/TS: npm audit · Python: pip-audit · Rust: cargo audit · Go: govulncheck · Any: osv-scanner, gitleaks, trufflehog

<a id="dast"></a>
### Dynamic security scanning (DAST)

Attack the running app with known exploit patterns.

- **Tier / speed / setup:** nightly · hours · medium
- **Catches:** security
- **Strengths:** Finds issues that are actually exploitable in the deployed configuration.
- **Gaps:** Limited reach into authenticated or deep flows.
- **Signal quality:** Names the URL and payload.
- **Use when:** Public web apps and APIs.
- **Covers its gaps:** [Penetration testing](#pentest), [Security static analysis (SAST)](#sast)
- **Tools:** Any: OWASP ZAP, Nuclei

<a id="pentest"></a>
### Penetration testing

Skilled attackers probe the system by hand.

- **Tier / speed / setup:** human · manual · high
- **Catches:** security
- **Strengths:** Finds logic and authorization flaws that tools miss.
- **Gaps:** Expensive, a point-in-time snapshot, and only as good as the tester.
- **Signal quality:** Rich report, slow.
- **Use when:** Before handling money, health data or enterprise customers.
- **Covers its gaps:** [Dynamic security scanning (DAST)](#dast), [Security static analysis (SAST)](#sast)
- **Tools:** Any: Burp Suite

## Testing the tests

<a id="coverage"></a>
### Code coverage

Measure which lines and branches the tests execute.

- **Tier / speed / setup:** gate · seconds · low
- **Catches:** nothing directly; it measures how strong the other signals are
- **Strengths:** Cheap, and shows code no test even runs.
- **Gaps:** Executed is not checked: high coverage with weak assertions proves little, and the number is easy to game.
- **Signal quality:** A map of untested code, not a quality score.
- **Use when:** Finding untested risky code. Read it on the diff, not as a repo-wide floor.
- **Covers its gaps:** [Mutation testing](#mutation)
- **Tools:** JS/TS: vitest --coverage · Python: coverage.py · Swift: -enableCodeCoverage, llvm-cov · Rust: cargo-llvm-cov · Go: go test -cover · JVM: JaCoCo

<a id="mutation"></a>
### Mutation testing

Inject small bugs into the code and check that some test fails for each one.

- **Tier / speed / setup:** nightly · hours · low
- **Catches:** nothing directly; it measures how strong the other signals are
- **Strengths:** The honest measure of whether tests check anything, and it names the exact unchecked line.
- **Gaps:** Slow on large code, and equivalent mutants add noise.
- **Signal quality:** Each surviving mutant is a concrete missing assertion.
- **Use when:** On the riskiest modules, or only on the lines a change touched.
- **Covers its gaps:** [Property-based tests](#property)
- **Tools:** JS/TS: StrykerJS · Python: mutmut, cosmic-ray · Swift: Muter · Rust: cargo-mutants · Go: gremlins · JVM: PIT

<a id="flaky"></a>
### Flaky test detection

Rerun tests many times, in random order and in parallel, to find nondeterminism.

- **Tier / speed / setup:** nightly · minutes · low
- **Catches:** concurrency
- **Strengths:** Restores trust in the signal, which agents need more than humans do.
- **Gaps:** Finds the flake but not its cause.
- **Signal quality:** A flaky test is a lying signal: fix it or quarantine it.
- **Use when:** As soon as any test has failed and then passed on retry.
- **Covers its gaps:** [Deterministic simulation](#simulation), [Concurrency and interleaving tests](#concurrency)
- **Tools:** JS/TS: playwright --repeat-each, vitest --sequence.shuffle · Python: pytest-randomly, pytest-repeat · Rust: cargo nextest with retries · Go: go test -count=50 -shuffle=on

## Proof and exhaustive exploration

<a id="model-checking"></a>
### Model checking

Exhaustively explore every state of a design written as a formal spec.

- **Tier / speed / setup:** nightly · minutes · high
- **Catches:** concurrency, logic, resilience
- **Strengths:** Finds design bugs in protocols and concurrency before any code exists.
- **Gaps:** Checks the model, not the code, and large state spaces blow up.
- **Signal quality:** Gives the exact counterexample trace.
- **Use when:** Protocols, distributed algorithms, locking schemes, sync logic.
- **Covers its gaps:** [Deterministic simulation](#simulation), [Model-based and stateful tests](#model)
- **Tools:** Rust: Kani · Any: TLA+ (TLC, Apalache), Alloy, P

<a id="formal"></a>
### Formal verification

Machine-checked proofs that code meets a specification for every input.

- **Tier / speed / setup:** human · manual · high
- **Catches:** logic, edge, crash
- **Strengths:** A guarantee rather than a sample.
- **Gaps:** Expensive, and proves the spec, which can itself be wrong.
- **Signal quality:** Agents are getting good at closing proof obligations, which changes the cost.
- **Use when:** Crypto, consensus, compilers, safety-critical kernels.
- **Covers its gaps:** [Property-based tests](#property)
- **Tools:** Rust: Verus, Kani, Prusti · Any: Dafny, Lean, Coq

<a id="symbolic"></a>
### Symbolic and concolic execution

Solve for inputs that reach each path through the code.

- **Tier / speed / setup:** nightly · hours · high
- **Catches:** crash, edge, security
- **Strengths:** Reaches deep branches guarded by exact values that random inputs never hit.
- **Gaps:** Path explosion on large programs.
- **Signal quality:** Produces a concrete failing input.
- **Use when:** Small, critical functions with complex branching.
- **Covers its gaps:** [Fuzzing](#fuzz)
- **Tools:** Python: CrossHair · Rust: Kani · C/C++: KLEE · Binaries: angr

## Production feedback

<a id="canary"></a>
### Canary and progressive rollout

Release to a small share of users, compare health metrics, then widen.

- **Tier / speed / setup:** production · continuous · medium
- **Catches:** regression, perf, platform, wiring
- **Strengths:** Real users and real data with a small blast radius.
- **Gaps:** Some users still hit the bug, and it needs good metrics.
- **Signal quality:** Fast when error rates are wired to automatic rollback.
- **Use when:** Any service with enough traffic to compare.
- **Covers its gaps:** [Observability and error tracking](#observability)
- **Tools:** Any: feature flags, staged rollouts, TestFlight, Play staged rollout

<a id="shadow"></a>
### Shadow traffic and replay

Send copies of real requests to the new version and compare responses without serving them.

- **Tier / speed / setup:** production · continuous · high
- **Catches:** regression, perf, contract
- **Strengths:** Production realism with no user impact.
- **Gaps:** Side effects are tricky, and it doubles the infrastructure.
- **Signal quality:** Shows the request and both responses.
- **Use when:** Rewrites of request-handling services.
- **Covers its gaps:** [Differential tests](#differential)
- **Tools:** Any: GoReplay, mirrored traffic in the proxy

<a id="synthetic"></a>
### Synthetic monitoring

Scripted checks run against production on a schedule.

- **Tier / speed / setup:** production · continuous · low
- **Catches:** wiring, regression, resilience
- **Strengths:** Catches outages and broken deploys before users report them.
- **Gaps:** Only covers the scripted paths.
- **Signal quality:** Fast and binary.
- **Use when:** Signup, checkout, login and health endpoints.
- **Covers its gaps:** [Observability and error tracking](#observability)
- **Tools:** Any: Checkly, a scheduled Playwright or curl job

<a id="observability"></a>
### Observability and error tracking

Structured logs, traces, metrics and crash reports from real use.

- **Tier / speed / setup:** production · continuous · medium
- **Catches:** crash, perf, resilience, platform
- **Strengths:** Catches what no pre-production environment reproduces, with real stack traces.
- **Gaps:** Users meet the bug first.
- **Signal quality:** Feed every new production error back as a failing test.
- **Use when:** Every shipped product.
- **Covers its gaps:** [Canary and progressive rollout](#canary), [Synthetic monitoring](#synthetic)
- **Tools:** Any: Sentry, OpenTelemetry, crash reporters

<a id="ab"></a>
### A/B and beta testing

Compare variants on live users, or ship early builds to a willing group.

- **Tier / speed / setup:** production · continuous · medium
- **Catches:** requirements
- **Strengths:** Measures real behaviour and real-world environments.
- **Gaps:** Tests outcomes, not correctness, and needs traffic or testers.
- **Signal quality:** Slow, statistical.
- **Use when:** Product decisions, pricing, onboarding.
- **Covers its gaps:** [Usability testing](#usability)
- **Tools:** Any: feature flag platforms, TestFlight

## AI features

<a id="evals"></a>
### LLM evals

Score model or agent output on a fixed dataset with code checks, rubrics or model graders.

- **Tier / speed / setup:** gate · minutes · medium
- **Catches:** logic, regression, requirements
- **Strengths:** The only way to know whether a prompt or model change made an AI feature better or worse.
- **Gaps:** Graders can be wrong, datasets go stale, and scores are noisy.
- **Signal quality:** Report the per-case diff, not just the average.
- **Use when:** Any feature whose output comes from a model.
- **Covers its gaps:** [Schema validation at boundaries](#schema), [Metamorphic tests](#metamorphic)
- **Tools:** Any: promptfoo, Inspect, Braintrust, plain pytest with fixtures

## Human judgement

<a id="review"></a>
### Code review

A human or a second model reads the change.

- **Tier / speed / setup:** human · manual · low
- **Catches:** logic, requirements, security
- **Strengths:** Catches design problems, wrong assumptions and missing tests.
- **Gaps:** Inconsistent and tiring, and it misses subtle bugs.
- **Signal quality:** Strongest when the reviewer is a different model or person than the author.
- **Use when:** Every change worth keeping.
- **Covers its gaps:** [Mutation testing](#mutation), [Property-based tests](#property)
- **Tools:** Any: pull request review, cross-model review
