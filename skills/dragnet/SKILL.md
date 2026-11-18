---
name: dragnet
description: dragnet designs a project's feedback net (types, lint, assertions, tests, fuzzing, sanitizers, production signals) so coding agents catch their own mistakes fast. Use when choosing a testing strategy for a project, when a bug escaped to a user or got past the tests, when the test or build loop is too slow, or when asked what the tests actually cover.
---

# dragnet

## North star

**Fastest honest feedback on every change.** An agent improves only as fast as its signals tell it it is wrong. Every check in a project is a feedback signal, rated on four things:

- **Early:** fires at the earliest tier that can see the bug (`edit` → `inner` → `gate` → `nightly` → `production` → `human`).
- **Fast:** seconds in the inner loop, minutes at the gate.
- **Honest:** deterministic. A flaky signal is a lying signal, and agents believe it.
- **Precise:** the failure names the file, line, input and expected-vs-actual, so the fix is one step away.

The **net** is the whole set of signals. A **hole** is a risk no signal covers. An **escape** is a bug that got through the net. Every escape gets **shifted left**: caught next time by the earliest, cheapest signal that could have seen it. A type beats a test, a test beats a review, a review beats a user report.

## Branches

Do every step for a new or unfamiliar project. Otherwise start at the step for your branch, then finish with steps 6 and 7.

| Situation | Start at |
|---|---|
| New project, or no strategy yet | 1 |
| A bug escaped or tests missed a regression | 4 |
| The loop or gate is too slow or flaky | 5 |
| "What do our tests actually cover?" | 3 |

## Steps

### 1. Recon the net

Run `scripts/recon.sh <repo> [days]`. It lists languages, the test files and signals it detects, gate commands, escape-like commits, fix hotspots and fixes that shipped without a test. Then run each loop command yourself and record its wall time, pass/fail and whether it reruns clean.

Done when every existing signal is listed with its command, tier, measured time and honest/flaky status.

### 2. Name the risk surfaces

List where this project can hurt users. Look for parsers and file formats, money and auth, persistence and migrations, concurrency and async, external APIs, UI flows, performance-sensitive paths, platform spread, and AI-generated output. Weight each by recon's fix hotspots: code that keeps getting fixed is where the next bug is.

Done when each surface has file paths and a likelihood × impact rating.

### 3. Map the net and find holes

For each surface, list the signals that cover it today, using the bug classes in [references/catch-map.md](references/catch-map.md). A surface whose likely bug classes have no signal, or only a late one, is a hole. Coverage means risk surfaces × signals, not a line-coverage percentage. Line coverage only shows code no test runs. To learn whether tests *check* anything, run mutation testing on the riskiest surface or on the lines a change touched. Each surviving mutant is a missing assertion.

Done when every surface is marked covered, late or hole.

### 4. Shift escapes left

Read [references/escapes.md](references/escapes.md) and run its escape analysis on each recent escape: recon's fix commits, failing CI or gate runs, bug reports, crash logs, or the failure the user just described. For each one, find the earliest signal that could have caught it, add that signal so it goes red on the old code and green on the fix, then ask whether the escape is one of a class. If it is, add the signal that catches the whole class: a type, a lint rule, a property, a fuzz target or a contract.

Done when every escape has a signal that demonstrably fails on the pre-fix code.

### 5. Tighten the loop

Place every signal in a tier. The inner loop runs in seconds after every change. The gate is one command that runs before every commit or merge. Slow work belongs in nightly or background runs. If any tier is too slow, flaky or vague to steer an agent, apply [references/loop.md](references/loop.md). These timings are targets for the design, not gate-failing budgets. Report times as numbers and never fail a build on a limit fitted to today's measurement.

Done when the inner loop and the gate are each one documented command, and every flaky test is fixed or quarantined with a named reason.

### 6. Write NET.md

Write or update `NET.md` at the repo root from [references/net-template.md](references/net-template.md). It holds the signals by tier, the risk surfaces with their coverage, the ranked holes and the escape log. Link it from `AGENTS.md` or `CLAUDE.md` in one line so every future agent session finds the inner-loop and gate commands. Rank holes by likelihood × impact ÷ cost, and prefer the signal that fires earliest.

### 7. Close the top holes now

Implement the top one to three holes in this session. Prove each new signal works: inject the bug it targets by hand (flip a comparison, drop a check, delete a line), watch it go red with a precise message, then restore the code. A signal that has never been seen to fail is unproven. Run the gate, then commit with the escape or hole it closes in the message.

Done when each new signal has been seen to fail on an injected fault and pass on the real code, the gate is green, and NET.md lists what remains.

## Reference

- [references/catalog.md](references/catalog.md): every technique with tier, speed, setup cost, strengths, gaps, signal quality, when to use, what covers its gaps, and tools per ecosystem. Use it to choose between techniques.
- [references/catch-map.md](references/catch-map.md): bug class → signals, earliest first.
- [references/escapes.md](references/escapes.md): escape analysis.
- [references/loop.md](references/loop.md): making signals faster, more honest and more precise.
- [references/net-template.md](references/net-template.md): the NET.md layout.

## Starting nets

For projects with no strategy yet. Adjust using step 2's risks.

- **Any project:** strictest types, curated lint as errors, unit tests on pure logic, dependency and secret scanning, one gate command.
- **Web app:** add schema validation at every boundary, integration tests against a real database, three to five Playwright paths, axe checks, visual snapshots of key pages, synthetic checks on signup and checkout.
- **iOS or macOS app:** add the Swift 6 language mode, Swift Testing for view models and stores, XCUITest for the main flows with accessibility audits, snapshot tests for key screens, TSan on the suite, crash reporting.
- **Library or parser:** add property tests for round-trips and invariants, fuzz targets for every untrusted input, differential tests against a reference, mutation testing on the core.
- **Service or API:** add contract tests per consumer, integration tests with Testcontainers, a load test before launches, fault injection on dependencies, tracing.
- **Concurrent or distributed core:** add assertions on invariants, stateful model tests, sanitizers, and deterministic simulation or a TLA+ model of the protocol.
- **AI feature:** add schema-validated model output, an eval set built from real failures, and metamorphic checks where there is no single right answer.
