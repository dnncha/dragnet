---
name: dragnet
description: dragnet builds the feedback net (types, lint, assertions, tests, fuzzing, sanitizers, production signals) that lets coding agents catch their own mistakes early. It fixes every defect the net catches, then turns each one into a class-level guard that makes the same kind of bug impossible or catches it within seconds of the edit. Invoke it yourself, mid-task, the moment a bug surfaces later than it should have - a user, reviewer or late gate found what an earlier check could have, the same kind of fix recurs, or debugging took far longer than the fix. Also use when choosing a testing strategy, when the test loop is slow or flaky, or when asked what the tests cover.
---

# dragnet

## North star

**Fastest honest feedback on every change.** An agent improves only as fast as its signals tell it it is wrong. Every check in a project is a feedback signal, rated on four things:

- **Early:** fires at the earliest tier that can see the bug (`edit` → `inner` → `gate` → `nightly` → `production` → `human`).
- **Fast:** seconds in the inner loop, minutes at the gate.
- **Honest:** deterministic. A flaky signal is a lying signal, and agents believe it.
- **Precise:** the failure names the file, line, input and expected-vs-actual, so the fix is one step away.

The **net** is the whole set of signals. A **hole** is a risk no signal covers. An **escape** is a bug that got through the net. A **catch** is a defect a signal found, whether an old signal or one dragnet just added.

Every catch and every escape goes through the same four moves, in order:

1. **Fix it.** The defect, and every sibling with the same cause, is fixed in this session. A net that finds bugs and leaves them in place has only written a report.
2. **Kill the class.** Ask what else breaks the same way, and climb the prevention ladder in [references/escapes.md](references/escapes.md) as high as it goes. The goal is a codebase where the class cannot be written: a type, a deleted API or a lint rule beats any test.
3. **Catch it in seconds.** Whatever guard you add runs at the earliest tier that can see it, ideally the compiler or the inner loop, and fails with a message that points at the line. Measure time-to-red and push it down.
4. **Prove and log it.** The guard goes red on the broken code and on a planted sibling, green on the fix, and the row lands in `NET.md`.

A type beats a test, a test beats a review, a review beats a user report.

## Quick mode: an escape mid-task

Use this when you invoked dragnet yourself in the middle of other work because something surfaced late. It takes minutes. Then return to the task.

1. **Name it** in one line: what broke, how it was found, and which earlier tier could have seen it (use [references/catch-map.md](references/catch-map.md)).
2. **Fix it and its siblings.** Search for the same cause (the old pattern, the same call, the same assumption) across the codebase and fix every instance in this change. Fix tests that assert the buggy behaviour.
3. **Kill the class.** Climb the prevention ladder in [references/escapes.md](references/escapes.md) from the top: make it unrepresentable, delete the dangerous API, or ban it with a rule. Drop to an assertion or a test only when every rung above is impossible here, and write down why in the log row.
4. **Make it fast.** The guard must fire in the editor, the compiler or the inner-loop command, in seconds. If it can only run at the gate, also add a fast slice to the inner loop.
5. **Prove it.** Restore the bug, or plant a fresh instance of the class in a new spot: the guard goes red with a message that names the file and line, then green on the fix.
6. **Log it** in `NET.md` (create it from [references/net-template.md](references/net-template.md) if missing), including the rung reached and the time-to-red. If the log shows the same class three times, the class is still open: schedule a full run on it.

Done when the defect and its siblings are fixed, the class guard is proven on both the original bug and a planted sibling, and the row is logged.

## Branches

Do every step for a new or unfamiliar project. Otherwise start at the step for your branch, then finish with steps 6 and 7.

| Situation | Start at |
|---|---|
| Mid-task escape you noticed yourself | Quick mode |
| New project, or no strategy yet | 1 |
| A bug escaped or tests missed a regression | 4 |
| The loop or gate is too slow or flaky | 5 |
| "What do our tests actually cover?" | 3 |

## Steps

### 1. Recon the net

Run `scripts/recon.sh <repo> [days]`. It lists languages, the test files and signals it detects, gate commands, escape-like commits, fix hotspots and fixes that shipped without a test. Read the project's own agent and verification docs that recon lists (AGENTS.md, CLAUDE.md, a testing roadmap, DESIGN.md) before proposing anything: build on the net the team already chose, and respect its release rules and compute routing. Then run each loop command yourself and record its wall time, pass/fail and whether it reruns clean. Run heavy suites where the environment says heavy work goes.

Done when every existing signal is listed with its command, tier, measured time and honest/flaky status.

### 2. Name the risk surfaces

List where this project can hurt users. Look for parsers and file formats, money and auth, persistence and migrations, concurrency and async, external APIs, UI flows, performance-sensitive paths, platform spread, and AI-generated output. Weight each by recon's fix hotspots: code that keeps getting fixed is where the next bug is. Written rules count as risk surfaces too: every rule in a design, style or product doc that no check enforces is a hole waiting for an escape.

Done when each surface has file paths and a likelihood × impact rating.

### 3. Map the net and find holes

For each surface, list the signals that cover it today, using the bug classes in [references/catch-map.md](references/catch-map.md). A surface whose likely bug classes have no signal, or only a late one, is a hole. Coverage means risk surfaces × signals, not a line-coverage percentage. Line coverage only shows code no test runs. To learn whether tests *check* anything, run mutation testing on the riskiest surface or on the lines a change touched. Each surviving mutant is a missing assertion.

Done when every surface is marked covered, late or hole.

### 4. Shift escapes left

Read [references/escapes.md](references/escapes.md) and run its escape analysis on each recent escape: recon's fix commits, failing CI or gate runs, bug reports, crash logs, or the failure the user just described. For each one: fix it and its siblings if it is still live, climb the prevention ladder for its whole class, wire the guard into the fastest tier that can run it, and prove it red on the old code and on a planted sibling.

Group escapes by class before you start. One type change or lint rule that kills a class beats five regression tests for its five past instances.

Done when every live defect is fixed, every escape's class has a guard at the highest rung the project allows, and each guard demonstrably fails on the pre-fix code.

### 5. Tighten the loop

Place every signal in a tier. The inner loop runs in seconds after every change. The gate is one command that runs before every commit or merge. Slow work belongs in nightly or background runs. If any tier is too slow, flaky or vague to steer an agent, apply [references/loop.md](references/loop.md). These timings are targets for the design, not gate-failing budgets. Report times as numbers and never fail a build on a limit fitted to today's measurement.

Done when the inner loop and the gate are each one documented command, and every flaky test is fixed or quarantined with a named reason.

### 6. Write NET.md

Write or update `NET.md` at the repo root from [references/net-template.md](references/net-template.md). It holds the signals by tier, the risk surfaces with their coverage, the ranked holes and the escape log. Link it from `AGENTS.md` or `CLAUDE.md` in one line so every future agent session finds the inner-loop and gate commands. Rank holes by likelihood × impact ÷ cost, and prefer the signal that fires earliest.

### 7. Close the top holes now

Implement the top one to three holes in this session. Prove each new signal works: inject the bug it targets by hand (flip a comparison, drop a check, delete a line), watch it go red with a precise message, then restore the code. A signal that has never been seen to fail is unproven.

**Fix what the new signals catch.** A new type, rule, sweep or property often goes red on today's code. Each of those failures is a real defect the old net missed. Fix every one in this session, rather than suppressing it, baselining it or loosening the signal. If a finding is a false positive, tighten the signal until it is precise, never widen an allowlist to get green. Only a fix too large for the session may be deferred, and then it is listed in NET.md's holes with its locator, never hidden behind a skip. Run each caught defect through the four moves: its class may be wider than the hole you were closing.

For a web or terminal UI, the top holes usually include rules no check enforces and multi-step flows nobody tests: write them as properties, prove each with a fault fixture, and run a fuzz campaign long enough to reach deep states, following [references/ui-properties.md](references/ui-properties.md). Fix every shrunk violation it finds.

Run the gate, then commit with the escape or hole it closes and the defects it caught in the message.

Done when each new signal has been seen to fail on an injected fault and pass on the real code, every defect it caught is fixed or listed, the gate is green, and NET.md lists what remains.

## Reference

- [references/catalog.md](references/catalog.md): every technique with tier, speed, setup cost, strengths, gaps, signal quality, when to use, what covers its gaps, and tools per ecosystem. Use it to choose between techniques.
- [references/catch-map.md](references/catch-map.md): bug class → signals, earliest first.
- [references/escapes.md](references/escapes.md): escape analysis.
- [references/loop.md](references/loop.md): making signals faster, more honest and more precise.
- [references/net-template.md](references/net-template.md): the NET.md layout.
- [references/ui-properties.md](references/ui-properties.md): property-based UI exploration with Bombadil: gate and nightly tiers, swarm fuzzing, shrinking, coverage of the walk, properties worth writing, a fault suite that proves each property, and keeping driver errors out of the verdict.

## Starting nets

For projects with no strategy yet. Adjust using step 2's risks.

- **Any project:** strictest types, curated lint as errors, unit tests on pure logic, dependency and secret scanning, one gate command.
- **Web app:** add schema validation at every boundary, integration tests against a real database, three to five Playwright paths, axe checks, visual snapshots of key pages, synthetic checks on signup and checkout, and a property-based UI spec (Bombadil) that checks the product, design and accessibility rules on every reachable screen: a short run at the gate and a nightly swarm fuzz campaign whose violations are shrunk ([references/ui-properties.md](references/ui-properties.md)).
- **iOS or macOS app:** add the Swift 6 language mode, Swift Testing for view models and stores, XCUITest for the main flows with accessibility audits, snapshot tests for key screens, TSan on the suite, crash reporting.
- **Library or parser:** add property tests for round-trips and invariants, fuzz targets for every untrusted input, differential tests against a reference, mutation testing on the core.
- **Service or API:** add contract tests per consumer, integration tests with Testcontainers, a load test before launches, fault injection on dependencies, tracing.
- **Concurrent or distributed core:** add assertions on invariants, stateful model tests, sanitizers, and deterministic simulation or a TLA+ model of the protocol.
- **AI feature:** add schema-validated model output, an eval set built from real failures, and metamorphic checks where there is no single right answer.
