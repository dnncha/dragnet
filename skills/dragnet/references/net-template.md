# NET.md template

Copy this layout to `NET.md` at the repository root and fill it in. Keep it short, and keep it current: update it on every escape.

```markdown
# Feedback net

Inner loop: `<one command, typical time>`
Gate: `<one command, typical time>`
Scheduled: `<command>` (<scheduler, cadence, where red goes>)

## Signals by tier

| Tier | Signal | Command | Runs | Time | Status |
|---|---|---|---|---|---|
| edit | Strict types | `...` | compiler, inner, gate | 4 s | honest |
| inner | Unit tests | `...` | inner, gate | 9 s | honest |
| gate | Integration tests | `...` | gate | 2 min | 1 quarantined: <name, reason> |
| nightly | Fuzz parser | `...` | scheduled: cron on the build machine, 03:00 daily, red opens an issue | 1 h | honest |
| weekly | Mutation testing of the money core | `...` | scheduled: launchd, Sunday 04:00, red opens an issue | 20 min | 84% killed on <date> |
| production | Error tracking | Sentry project <name> | live | live | |

## Risk surfaces

| Surface | Paths | Risk (L×I) | Covered by | Status |
|---|---|---|---|---|
| Payment webhook | `src/billing/` | high × high | integration, schema | late: no contract test |
| Markdown parser | `src/md/` | med × med | unit | hole: no property or fuzz |

## Holes, ranked

1. <hole> → <signal to add> (tier, est. cost)
2. ...

## Escape log

| Date | Symptom | Root cause | Class | Caught by | Fixed (+siblings) | Class guard | Rung | Time to red | Proved |
|---|---|---|---|---|---|---|---|---|---|

Runs names what triggers each signal: `compiler`, `hook`, `inner`, `gate`, `release`, `live`, or `scheduled: <scheduler, cadence, where red goes>`. "By hand" is not a trigger; such a signal belongs in Holes until something runs it.

Rung is the prevention ladder in dragnet's escapes.md: 1 impossible, 2 deleted path, 3 rule, 4 sweep, 5 assertion, 6 property or fuzz, 7 regression test, 8 production. Write the number first, then the name, and for 5 to 8 add `above:` with why rungs 1 to 4 are impossible here, for example `7 regression test; above: one call site, value comes from the network`. Proved means red on the pre-fix code and on a planted sibling.

Check it with `python3 tools/netcheck.py NET.md` (copied from dragnet's `scripts/netcheck.py`), and run that in the gate.
```
