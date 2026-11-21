# NET.md template

Copy this layout to `NET.md` at the repository root and fill it in. Keep it short, and keep it current: update it on every escape.

```markdown
# Feedback net

Inner loop: `<one command, typical time>`
Gate: `<one command, typical time>`
Nightly: `<command or schedule>`

## Signals by tier

| Tier | Signal | Command | Time | Status |
|---|---|---|---|---|
| edit | Strict types | `...` | 4 s | honest |
| inner | Unit tests | `...` | 9 s | honest |
| gate | Integration tests | `...` | 2 min | 1 quarantined: <name, reason> |
| nightly | Fuzz parser | `...` | 1 h | honest |
| production | Error tracking | Sentry project <name> | live | |

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

Rung is the prevention ladder in dragnet's escapes.md: 1 impossible, 2 deleted path, 3 rule, 4 sweep, 5 assertion, 6 property or fuzz, 7 regression test, 8 production. Proved means red on the pre-fix code and on a planted sibling.
```
