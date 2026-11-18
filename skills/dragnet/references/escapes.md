# Escape analysis

An escape is any bug that got further than it should have: past the editor, past the inner loop, past the gate, or all the way to a user. Each escape is evidence about a hole in the net. Treat it as a gift: it tells you exactly which signal is missing.

## Gather escapes

Pull from every source that exists:

- `scripts/recon.sh` sections "Escapes", "Hotspots" and "Fixes that shipped without a test change".
- Failed gate or CI runs, and tests that went red and then passed on retry.
- Crash reports, error tracker issues, support messages, review comments that found a bug.
- The failure the user just described.

## Analyse each escape

Fill one row per escape in NET.md's escape log:

| Field | Question |
|---|---|
| Symptom | What did someone see? |
| Root cause | What was actually wrong, in one line? |
| Bug class | Which class in catch-map.md? |
| Caught by | Which signal caught it, and at which tier? (user, review, gate, nobody) |
| Earliest signal | Walk the class's row in catch-map.md from the top. Which is the first signal that could have caught it? |
| Added | The signal you added, with its file path. |
| Proved | Seen red on the pre-fix code? (yes/no) |
| Class fix | The signal that now catches the whole class, if any. |

## Pick the earliest signal

Walk the bug class's row top-down and take the first signal that could have caught it:

1. **Make it unrepresentable.** Change a type so the bad state cannot compile: an enum instead of a string, a non-optional field, a newtype for IDs or units, a parsed type at the boundary. This catches the whole class forever at the `edit` tier.
2. **Make it a rule.** If the bug matches a pattern (a banned API, a missing `await`, an unchecked cast), add a lint rule or a Semgrep rule.
3. **Make it loud.** Add an assertion or precondition where the state first goes wrong.
4. **Make it a property.** If the bug came from an input nobody imagined, write the invariant as a property test and keep the failing input as an example.
5. **Make it a test.** Write the smallest test at the lowest seam that reproduces it: unit before integration before end-to-end.
6. **Make it observable.** If no pre-production signal can see it, add a production signal: an alert, a synthetic check or a canary metric.

## Prove the signal

Check out the pre-fix code, or revert the fix in a scratch commit, and run the new signal. It must go red with a message that points at the cause. If it passes on the broken code, it does not catch this bug. Strengthen it until it does.

## Find the class

After the specific escape is covered, ask what else breaks the same way:

- Search the codebase for the same pattern (grep, Semgrep, the type's other uses).
- If three or more escapes share a bug class or a hotspot file, the net has a structural hole there. Add the class-level signal: a stricter type, a property suite, a fuzz target, a contract test, or a redesign that removes the hazard.

## Feed production back

Every production error that reaches a human becomes a failing test before the fix lands. Keep fuzz crashes and property counterexamples as named regression examples. The net only ever gets tighter.
