# Escape analysis

An escape is any bug that got further than it should have: past the editor, past the inner loop, past the gate, or all the way to a user. A catch is a defect a signal found, including one that a newly added signal just turned up in existing code. Both are evidence about a hole in the net, and both get the same treatment: fix the defect, kill its class, make the next one show up in seconds, prove it, log it.

## Gather escapes

Pull from every source that exists:

- `scripts/recon.sh` sections "Escapes", "Hotspots" and "Fixes that shipped without a test change".
- Failed gate or CI runs, and tests that went red and then passed on retry.
- Crash reports, error tracker issues, support messages, review comments that found a bug.
- The failure the user just described.
- Failures from a signal dragnet just added. Each one is a live defect.

## Analyse each escape

Fill one row per escape in NET.md's escape log:

| Field | Question |
|---|---|
| Symptom | What did someone see? |
| Root cause | What was actually wrong, in one line? |
| Bug class | Which class in catch-map.md? Name it in the project's terms too ("money as Double", "unawaited save"). |
| Caught by | Which signal caught it, and at which tier? (user, review, gate, nobody) |
| Fixed | The fix, and how many siblings were fixed with it. |
| Class guard | The guard that now covers the whole class, with its file path. |
| Rung | Which rung of the prevention ladder the guard reached, and why the rungs above were impossible. |
| Time to red | How long after the bad edit the guard fires: compile, save, inner loop (seconds), gate (minutes). |
| Proved | Seen red on the pre-fix code and on a planted sibling? (yes/no) |

## Fix the defect first

A caught defect that is still in the code is fixed in this session, before or with its guard.

- Fix the root cause, not the symptom the report named.
- Search for siblings: the old pattern, the same call, the same assumption, the other screens or endpoints that copy it. Fix every one in the same change. Partial fixes are the most common escape of all.
- Fix tests that assert the buggy behaviour. A test that expects the wrong output locks the bug in. Note that the spec was unclear.
- Never suppress, baseline, skip or allowlist a real catch to get green. If the fix is too large for the session, list it in NET.md's holes with a greppable locator and leave the signal red or explicitly quarantined with that reason.

## Climb the prevention ladder

The goal is that this class of bug can no longer be written, and that if it somehow can, it is found seconds after the edit. Start at the top rung and take the highest one this project can support. Dropping a rung needs a reason, and the reason goes in the log row.

1. **Make it impossible.** Change the design so the bad state cannot exist: an enum instead of a string, a non-optional field, a newtype for IDs, money or units, a parsed type at the boundary, a constructor that validates, a state machine whose transitions are the only API. The compiler now rejects every future instance at the `edit` tier.
2. **Delete the dangerous path.** Remove or make private the helper, overload, default or API that let the bug in, and give one safe way to do the thing. Every old call site now fails to compile and gets fixed.
3. **Ban it with a rule.** If the bug matches a pattern (a banned API, a missing `await`, an unchecked cast, a raw SQL string, a hard-coded colour), add a lint, Semgrep, SwiftLint or ast-grep rule that runs in the editor and the inner loop, set to error.
4. **Sweep the whole surface.** If the rule is about output rather than code (tap targets, contrast, copy, every route returns JSON), write one check that walks every page, route or call site at once and names each offender with a locator. New instances get caught without anyone writing a new test.
5. **Make it loud at runtime.** Add an assertion or precondition where the state first goes wrong, so any test or dev run that reaches it fails on the spot.
6. **Generate the inputs.** If the bug came from an input nobody imagined, write the invariant as a property test or fuzz target over the whole input space, and keep the failing input as a named example.
7. **Pin the instance.** Write the smallest test at the lowest seam that reproduces it: unit before integration before end-to-end. It guards one bug and leaves the rest of the class open, so treat it as the floor.
8. **Watch production.** If nothing before production can see it, add an alert, a synthetic check or a canary metric.

Rungs 1 to 4 kill a class. Rungs 5 to 8 catch instances. Where you can, stack them: a type that makes the bug impossible plus a regression test that pins the original report.

## Make discovery hyper fast

A guard that runs only nightly finds the next instance a day late. For each guard:

- Put it at the earliest tier it can run: compiler or type checker, then editor lint, then the inner-loop command, then a pre-commit hook, then the gate.
- If it needs the gate (a sweep in a browser, a slow integration), add a fast slice to the inner loop as well: the one route, the one fixture, the pure function behind it.
- Make it run on the change, not the world: related-tests flags, the touched package, the changed files.
- Make the failure precise: file, line, offending value, expected value, and the rule's name, so the agent fixes it in one step without a search.
- Record the measured time-to-red in the log. If it is minutes, look for a rung or a tier that makes it seconds.

## Prove the signal

Check out the pre-fix code, or revert the fix in a scratch commit, and run the new signal. It must go red with a message that points at the cause. If it passes on the broken code, it does not catch this bug. Strengthen it until it does.

Then plant a sibling: write the same mistake in a different file or a different shape, and run the guard again. A guard that catches only the original line is just a regression test. Restore the code afterwards.

## Find the class

Ask what else breaks the same way, beyond the siblings you already fixed.

- Search the codebase for the same pattern (grep, Semgrep, the type's other uses), and fix what you find.
- Look at the escape log. If three or more rows share a bug class or a hotspot file, the class is still open and the net has a structural hole there. Climb higher on the ladder for that class: a stricter type, a redesign that removes the hazard, a property suite, a fuzz target or a contract test.

## Feed production back

Every production error that reaches a human becomes a failing test before the fix lands. Keep fuzz crashes and property counterexamples as named regression examples. The net only ever gets tighter.
