# Catch map

Generated from `data/catalog.json`. For each bug class, the signals that catch it, earliest and cheapest first. When a bug escapes, fix it first, then climb the prevention ladder in escapes.md. Use this row to pick the fastest signal for the rungs that need one: start at the top and take the first the project can afford.

## logic

wrong result from correct-looking code

1. **Linting and static analysis** (edit, instant): Always. Turn each escaped bug class that a pattern can catch into a custom rule.
2. **Assertions and design by contract** (inner, instant): Core data structures, state machines, money, anything with an invariant you can state.
3. **Parameterized and table-driven tests** (inner, instant): Any function with a clear input-to-output mapping.
4. **Unit tests** (inner, instant): Pure logic, parsers, formatters, calculations, state transitions.
5. **Component tests** (inner, seconds): UI components with state, modules with several collaborators.
6. **Metamorphic tests** (inner, seconds): Ranking, search, recommendations, numerical code, LLM pipelines.
7. **Property-based tests** (inner, seconds): Parsers, serializers, encoders, math, data structures, anything with a round-trip.
8. **Differential tests** (gate, seconds): Refactors, rewrites, ports to a new language, fast paths against slow reference code.
9. **Model-based and stateful tests** (gate, seconds): Caches, editors, sync engines, state machines, anything with history.
10. **LLM evals** (gate, minutes): Any feature whose output comes from a model.
11. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
12. **Model checking** (nightly, minutes): Protocols, distributed algorithms, locking schemes, sync logic.
13. **Code review** (human, manual): Every change worth keeping.
14. **Formal verification** (human, manual): Crypto, consensus, compilers, safety-critical kernels.

## edge

edge cases: empty, huge, unicode, negative, boundary values

1. **Assertions and design by contract** (inner, instant): Core data structures, state machines, money, anything with an invariant you can state.
2. **Boundary value and equivalence partitioning** (inner, instant): Ranges, limits, pagination, dates, money, string lengths.
3. **Parameterized and table-driven tests** (inner, instant): Any function with a clear input-to-output mapping.
4. **Unit tests** (inner, instant): Pure logic, parsers, formatters, calculations, state transitions.
5. **Property-based tests** (inner, seconds): Parsers, serializers, encoders, math, data structures, anything with a round-trip.
6. **Combinatorial and pairwise tests** (gate, seconds): Feature flags, settings screens, build matrices, option-heavy CLIs.
7. **Differential tests** (gate, seconds): Refactors, rewrites, ports to a new language, fast paths against slow reference code.
8. **Fuzzing** (nightly, hours): Untrusted input: file formats, network protocols, parsers, decoders.
9. **Symbolic and concolic execution** (nightly, hours): Small, critical functions with complex branching.
10. **Exploratory testing** (human, manual): After any user-visible change, before a release.
11. **Formal verification** (human, manual): Crypto, consensus, compilers, safety-critical kernels.

## types

null, undefined, wrong shape, wrong type

1. **Linting and static analysis** (edit, instant): Always. Turn each escaped bug class that a pattern can catch into a custom rule.
2. **Strict type checking** (edit, instant): Always. Turn on the strictest mode the language offers and ban escape hatches in new code.
3. **Schema validation at boundaries** (inner, instant): Any input crossing a process, network or trust boundary.

## crash

crashes, panics, hangs, memory corruption

1. **Property-based tests** (inner, seconds): Parsers, serializers, encoders, math, data structures, anything with a round-trip.
2. **Sanitizers** (gate, seconds): Any native, unsafe or concurrent code. Run the existing suite under them.
3. **Smoke tests** (gate, seconds): After every build and every deploy.
4. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
5. **Fuzzing** (nightly, hours): Untrusted input: file formats, network protocols, parsers, decoders.
6. **Symbolic and concolic execution** (nightly, hours): Small, critical functions with complex branching.
7. **Observability and error tracking** (production, continuous): Every shipped product.
8. **Formal verification** (human, manual): Crypto, consensus, compilers, safety-critical kernels.

## wiring

components wired wrong, config, dependency injection, routes

1. **Strict type checking** (edit, instant): Always. Turn on the strictest mode the language offers and ban escape hatches in new code.
2. **Component tests** (inner, seconds): UI components with state, modules with several collaborators.
3. **Combinatorial and pairwise tests** (gate, seconds): Feature flags, settings screens, build matrices, option-heavy CLIs.
4. **Integration tests** (gate, seconds): Anything that talks to storage or another process.
5. **Smoke tests** (gate, seconds): After every build and every deploy.
6. **End-to-end tests** (gate, minutes): A handful of revenue-critical or signup-critical paths only.
7. **Canary and progressive rollout** (production, continuous): Any service with enough traffic to compare.
8. **Synthetic monitoring** (production, continuous): Signup, checkout, login and health endpoints.

## contract

API or schema breaks between services, clients or versions

1. **Strict type checking** (edit, instant): Always. Turn on the strictest mode the language offers and ban escape hatches in new code.
2. **Schema validation at boundaries** (inner, instant): Any input crossing a process, network or trust boundary.
3. **Contract tests** (gate, seconds): Separately deployed services, mobile apps against a backend, public APIs.
4. **Integration tests** (gate, seconds): Anything that talks to storage or another process.
5. **Shadow traffic and replay** (production, continuous): Rewrites of request-handling services.

## data

migrations, persistence, serialization, data loss

1. **Assertions and design by contract** (inner, instant): Core data structures, state machines, money, anything with an invariant you can state.
2. **Schema validation at boundaries** (inner, instant): Any input crossing a process, network or trust boundary.
3. **Property-based tests** (inner, seconds): Parsers, serializers, encoders, math, data structures, anything with a round-trip.
4. **Integration tests** (gate, seconds): Anything that talks to storage or another process.
5. **Model-based and stateful tests** (gate, seconds): Caches, editors, sync engines, state machines, anything with history.
6. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
7. **Deterministic simulation** (nightly, minutes): Databases, sync engines, distributed systems, anything with retries and timeouts.

## ui

broken flows, wrong UI state, dead buttons

1. **Component tests** (inner, seconds): UI components with state, modules with several collaborators.
2. **End-to-end tests** (gate, minutes): A handful of revenue-critical or signup-critical paths only.
3. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
4. **Exploratory testing** (human, manual): After any user-visible change, before a release.

## visual

layout, styling and rendering breakage

1. **Localization and pseudo-localization** (gate, minutes): Any app with, or planning, translations.
2. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
3. **Visual regression tests** (gate, minutes): Design systems, marketing pages, any UI an agent edits often.
4. **Exploratory testing** (human, manual): After any user-visible change, before a release.

## perf

slowness, memory growth, resource exhaustion

1. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.
2. **Benchmarks and performance regression tests** (nightly, minutes): Hot loops, startup time, rendering, audio, anything users feel.
3. **Load, stress, spike and soak tests** (nightly, hours): Before launches, pricing changes or anything expecting a traffic jump.
4. **Canary and progressive rollout** (production, continuous): Any service with enough traffic to compare.
5. **Observability and error tracking** (production, continuous): Every shipped product.
6. **Shadow traffic and replay** (production, continuous): Rewrites of request-handling services.

## concurrency

races, deadlocks, ordering bugs

1. **Linting and static analysis** (edit, instant): Always. Turn each escaped bug class that a pattern can catch into a custom rule.
2. **Assertions and design by contract** (inner, instant): Core data structures, state machines, money, anything with an invariant you can state.
3. **Concurrency and interleaving tests** (gate, seconds): Shared mutable state, actors, locks, async pipelines, lock-free code.
4. **Model-based and stateful tests** (gate, seconds): Caches, editors, sync engines, state machines, anything with history.
5. **Sanitizers** (gate, seconds): Any native, unsafe or concurrent code. Run the existing suite under them.
6. **Deterministic simulation** (nightly, minutes): Databases, sync engines, distributed systems, anything with retries and timeouts.
7. **Flaky test detection** (nightly, minutes): As soon as any test has failed and then passed on retry.
8. **Model checking** (nightly, minutes): Protocols, distributed algorithms, locking schemes, sync logic.
9. **Load, stress, spike and soak tests** (nightly, hours): Before launches, pricing changes or anything expecting a traffic jump.

## security

vulnerabilities, leaked secrets, unsafe dependencies

1. **Linting and static analysis** (edit, instant): Always. Turn each escaped bug class that a pattern can catch into a custom rule.
2. **Schema validation at boundaries** (inner, instant): Any input crossing a process, network or trust boundary.
3. **Dependency and secret scanning** (gate, seconds): Every repo.
4. **Sanitizers** (gate, seconds): Any native, unsafe or concurrent code. Run the existing suite under them.
5. **Security static analysis (SAST)** (gate, seconds): Anything handling user input, auth or money.
6. **Dynamic security scanning (DAST)** (nightly, hours): Public web apps and APIs.
7. **Fuzzing** (nightly, hours): Untrusted input: file formats, network protocols, parsers, decoders.
8. **Symbolic and concolic execution** (nightly, hours): Small, critical functions with complex branching.
9. **Code review** (human, manual): Every change worth keeping.
10. **Penetration testing** (human, manual): Before handling money, health data or enterprise customers.

## a11y

accessibility failures

1. **Linting and static analysis** (edit, instant): Always. Turn each escaped bug class that a pattern can catch into a custom rule.
2. **Accessibility checks** (gate, seconds): Every user interface.
3. **Property-based UI exploration** (gate, minutes): Any web or terminal UI an agent edits often: forms, checkout, dashboards, multi-step flows. A short run at the gate, long swarm fuzz campaigns nightly.

## platform

works on one OS, browser, device or locale only

1. **Combinatorial and pairwise tests** (gate, seconds): Feature flags, settings screens, build matrices, option-heavy CLIs.
2. **Localization and pseudo-localization** (gate, minutes): Any app with, or planning, translations.
3. **Compatibility and cross-platform tests** (nightly, minutes): Shipping to several browsers, OS versions or devices.
4. **Canary and progressive rollout** (production, continuous): Any service with enough traffic to compare.
5. **Observability and error tracking** (production, continuous): Every shipped product.

## resilience

bad behaviour when dependencies fail or slow down

1. **Chaos and fault injection** (nightly, minutes): Services with dependencies, offline-capable apps, payment flows.
2. **Deterministic simulation** (nightly, minutes): Databases, sync engines, distributed systems, anything with retries and timeouts.
3. **Model checking** (nightly, minutes): Protocols, distributed algorithms, locking schemes, sync logic.
4. **Load, stress, spike and soak tests** (nightly, hours): Before launches, pricing changes or anything expecting a traffic jump.
5. **Observability and error tracking** (production, continuous): Every shipped product.
6. **Synthetic monitoring** (production, continuous): Signup, checkout, login and health endpoints.

## requirements

built the wrong thing, confusing UX

1. **Acceptance tests** (gate, minutes): Before starting a feature: write the acceptance check first.
2. **End-to-end tests** (gate, minutes): A handful of revenue-critical or signup-critical paths only.
3. **LLM evals** (gate, minutes): Any feature whose output comes from a model.
4. **A/B and beta testing** (production, continuous): Product decisions, pricing, onboarding.
5. **Code review** (human, manual): Every change worth keeping.
6. **Exploratory testing** (human, manual): After any user-visible change, before a release.
7. **Usability testing** (human, manual): New flows, onboarding, anything with drop-off.

## regression

something that used to work broke

1. **Strict type checking** (edit, instant): Always. Turn on the strictest mode the language offers and ban escape hatches in new code.
2. **Parameterized and table-driven tests** (inner, instant): Any function with a clear input-to-output mapping.
3. **Snapshot and characterization tests** (inner, instant): Before refactoring legacy code, for CLI output, generated code, serialized formats.
4. **Unit tests** (inner, instant): Pure logic, parsers, formatters, calculations, state transitions.
5. **Differential tests** (gate, seconds): Refactors, rewrites, ports to a new language, fast paths against slow reference code.
6. **Integration tests** (gate, seconds): Anything that talks to storage or another process.
7. **End-to-end tests** (gate, minutes): A handful of revenue-critical or signup-critical paths only.
8. **LLM evals** (gate, minutes): Any feature whose output comes from a model.
9. **Visual regression tests** (gate, minutes): Design systems, marketing pages, any UI an agent edits often.
10. **Benchmarks and performance regression tests** (nightly, minutes): Hot loops, startup time, rendering, audio, anything users feel.
11. **Canary and progressive rollout** (production, continuous): Any service with enough traffic to compare.
12. **Shadow traffic and replay** (production, continuous): Rewrites of request-handling services.
13. **Synthetic monitoring** (production, continuous): Signup, checkout, login and health endpoints.
