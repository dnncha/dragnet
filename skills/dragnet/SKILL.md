---
name: dragnet
description: "dragnet builds the feedback net that lets coding agents catch their own mistakes early: strict types, lint rules, assertions, tests, property-based testing, fuzzing, mutation testing, sanitizers and production signals. It fixes every bug the net catches, then turns each one into a class-level guard that makes the same kind of bug impossible or catches it within seconds of the edit. Bare `/dragnet` runs deep mode: a whole-project dive that hunts and fixes defects everywhere, closes the holes in test coverage, speeds up the loop and ships the result. Invoke it yourself mid-task the moment a bug surfaces later than it should have - a user, reviewer or late CI gate found what an earlier check could have, the same kind of fix recurs, or debugging took far longer than the fix. Also use for a testing strategy, regression prevention, a slow or flaky test suite, or when asked what the tests actually cover."
license: MIT
---

# dragnet

## North star

**Fastest honest feedback on every change.** An agent improves only as fast as its signals tell it it is wrong. Every check in a project is a feedback signal, rated on four things:

- **Early:** fires at the earliest tier that can see the bug (`edit` → `inner` → `gate` → `nightly` → `production` → `human`).
- **Fast:** seconds in the inner loop, minutes at the gate.
- **Honest:** deterministic. A flaky signal is a lying signal, and agents believe it.
- **Precise:** the failure names the file, line, input and expected-vs-actual, so the fix is one step away.
- **Wired:** something runs it without anyone remembering to: the compiler, a hook, the inner-loop command, the gate, the release script or a scheduler. A signal that runs "by hand" or "nightly" with no scheduler behind it is a hole with documentation.

The **net** is the whole set of signals. A **hole** is a risk no signal covers. An **escape** is a bug that got through the net. A **catch** is a defect a signal found, whether an old signal or one dragnet just added.

Every catch and every escape goes through the same four moves, in order:

1. **Fix it.** The defect, and every sibling with the same cause, is fixed in this session. A net that finds bugs and leaves them in place has only written a report.
2. **Kill the class.** Ask what else breaks the same way, and climb the prevention ladder in [references/escapes.md](references/escapes.md) as high as it goes. The goal is a codebase where the class cannot be written: a type, a deleted API or a lint rule beats any test. A test is the floor, not the default: a guard below rung 4 needs a written reason why each rung above is impossible here, and `scripts/netcheck.py` refuses the log row without one.
3. **Catch it in seconds.** Whatever guard you add runs at the earliest tier that can see it, ideally the compiler or the inner loop, and fails with a message that points at the line. Measure time-to-red and push it down.
4. **Prove and log it.** The guard goes red on the broken code and on a planted sibling, green on the fix, and the row lands in `NET.md`.

A type beats a test, a test beats a review, a review beats a user report.

## Pick the mode first

- **Deep mode:** the user fired `/dragnet` (or "run dragnet") with no arguments and nothing in the conversation names an escape, a file or a question. Go straight to deep mode below. Do not ask what they want, do not pick quick mode, and do not stop at a report.
- **Quick mode:** you invoked dragnet yourself mid-task because something surfaced late, or the arguments name one bug.
- **Branches:** the arguments or conversation name a narrower job (a slow loop, a coverage question). Use the branch table.

## Deep mode: dive the whole project and improve everything

The target is the project at the current working directory (its git root). If the working directory is a scratch folder with no project, use the repo the conversation is about; if there is none, say so in one line and stop. Load the `compute-routing` skill before any build, gate or fan-out, and follow the repo's own AGENTS.md or CLAUDE.md for gates, release rules and compute routing.

"Everything" means everything dragnet owns: every defect in the code, every hole in the net, every slow, flaky or vague signal, every unwired check, and every written rule nothing enforces. Feature work and redesigns are out of scope; a bug in a feature is in.

1. **Recon the whole history.** Run steps 1 to 3 in full, with `scripts/recon.sh <repo> <days since first commit>` so every escape-like commit is in view, not only the last 90 days. Run every existing signal at its strictest setting and record what is red.
2. **Hunt defects on every surface.** For each risk surface from step 2, read the code itself, not only its tests, looking for the bug classes in [references/catch-map.md](references/catch-map.md). Turn on every cheap strictness the stack offers (strictest compiler mode, warnings as errors, sanitizers, exhaustive lint) and run mutation testing, fuzzing and property tests on the riskiest surfaces. Fan the read-only audits out to subagents, one per surface or two, within the Mac admission limits; give each the surface's paths and the catch-map classes, and have each return defects with file, line, failing input and expected-vs-actual. Verify every reported defect yourself before fixing it.
3. **Fix every defect and kill every class.** Run each confirmed defect through the four moves. Group by class first, so one type or lint rule replaces many fixes. Then run step 4 over every escape in the whole history and re-climb every row in NET.md.
4. **Tighten and wire the loop.** Run step 5 on every tier, not only the slowest.
5. **Close every hole you can.** Run step 7 on every hole ranked in NET.md, not only the top three, in rank order. Defer a hole only when it is too large for the session, and list it in NET.md with its locator and the next step.
6. **Repeat until dry.** After each round, rerun the gate and the new signals. Anything new they catch starts another round. Stop when a round finds no new defect, or when everything left is a deferred hole.
7. **Ship.** Commit in reviewable pieces (one class or hole per commit, naming the defects it fixed), run the repo's gate, and push, merge or release following the repo's rules and the owner's standing instructions.

Done when every confirmed defect is fixed, every escape class has its highest guard proven red on a planted sibling, every signal has a trigger, the gate is green, NET.md is current with only deferred holes left, and the work has shipped. Report in a few lines: defects fixed (count and the worst three), classes killed, holes closed, inner-loop and gate times before and after, and the deferred holes.

## Quick mode: an escape mid-task

Use this when you invoked dragnet yourself in the middle of other work because something surfaced late. It takes minutes. Then return to the task.

1. **Name it** in one line: what broke, how it was found, and which earlier tier could have seen it (use [references/catch-map.md](references/catch-map.md)).
2. **Fix it and its siblings.** Search for the same cause (the old pattern, the same call, the same assumption) across the codebase and fix every instance in this change. Fix tests that assert the buggy behaviour.
3. **Kill the class.** Climb the prevention ladder in [references/escapes.md](references/escapes.md) from the top, before writing any test. Name the type that would make it unrepresentable, the API you would delete, and the lint or ast-grep rule that would ban it; build the first one that works. The promotion table in escapes.md lists the usual way up for common classes. Drop to an assertion or a test only when you can say in one line why each of rungs 1 to 4 is impossible here, and that line goes in the log row as `above: ...`. "A test was quicker" is not a reason.
4. **Make it fast.** The guard must fire in the editor, the compiler or the inner-loop command, in seconds. If it can only run at the gate, also add a fast slice to the inner loop.
5. **Prove it.** Restore the bug, or plant a fresh instance of the class in a new spot: the guard goes red with a message that names the file and line, then green on the fix.
6. **Log it** in `NET.md` (create it from [references/net-template.md](references/net-template.md) if missing), including the rung reached and the time-to-red, then run `scripts/netcheck.py NET.md`. It fails on a row with no rung, a rung with no guard behind it (`7 none yet`), or below rung 4 with no `above:` reason, lists guards never proved red, and lists every open class: a class logged twice with no guard at rungs 1 to 4. An open class is the next thing to fix, in this session if the guard is small.

Done when the defect and its siblings are fixed, the class guard is proven on both the original bug and a planted sibling, and the row is logged.

## Branches

Do every step for a new or unfamiliar project. Otherwise start at the step for your branch, then finish with steps 6 and 7.

| Situation | Start at |
|---|---|
| Fired bare, no context | Deep mode |
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

Then re-climb the old log. Run `scripts/netcheck.py NET.md`: for each open class, and each row whose `above:` reason no longer holds (the project gained a lint engine, a schema library, a stricter compiler mode), build the higher guard now, prove it on a planted sibling, and update the row's rung. Old rows are not settled just because they were logged.

Done when every live defect is fixed, every escape's class has a guard at the highest rung the project allows, each guard demonstrably fails on the pre-fix code, and netcheck reports no open class you could close this session.

### 5. Tighten the loop

Place every signal in a tier. The inner loop runs in seconds after every change. The gate is one command that runs before every commit or merge. Slow work belongs in nightly or background runs. If any tier is too slow, flaky or vague to steer an agent, apply [references/loop.md](references/loop.md). These timings are targets for the design, not gate-failing budgets. Report times as numbers and never fail a build on a limit fitted to today's measurement.

Then wire every signal. Each row in NET.md's signals table names its trigger in a `Runs` column: `compiler`, `hook`, `inner`, `gate`, `release`, `live`, or `scheduled: <scheduler>, <cadence>`. Slow suites (mutation testing, long fuzz and property runs, full browser matrices, model checking at depth, real-data benchmarks) go to a real scheduler: cron, launchd, a CI schedule, or the build machines the environment already uses, with a red run reaching a person or an issue tracker. Mutation testing on the riskiest surface is scheduled at least weekly, and a fast slice (mutants on the lines a change touched) runs at the gate where the tool supports it. A signal nobody wires moves to Holes; it does not stay in the signals table looking covered.

Done when the inner loop and the gate are each one documented command, every flaky test is fixed or quarantined with a named reason, and every signal has a trigger.

### 6. Write NET.md

Write or update `NET.md` at the repo root from [references/net-template.md](references/net-template.md). It holds the signals by tier, the risk surfaces with their coverage, the ranked holes and the escape log. Link it from `AGENTS.md` or `CLAUDE.md` in one line so every future agent session finds the inner-loop and gate commands. If a NET.md already exists in an older layout (no `Runs` column on signals, or no `Rung` and `Proved` columns on the escape log), netcheck reports it as 0 signals and 0 escapes: migrate it in place, filling each new cell from the evidence rather than guessing, before adding rows. Rank holes by likelihood × impact ÷ cost, and prefer the signal that fires earliest. Copy `scripts/netcheck.py` into the repo (for example `tools/netcheck.py`) and run it in the gate, so a NET.md row with no trigger or no rung fails the merge.

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
- `scripts/netcheck.py`: checks a NET.md. Every signal names its trigger, every escape names a real guard and its rung with a reason when below 4. It lists deferred climbs, unproved guards and recurring classes with no class-killing guard, and says how to migrate an older layout.
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
