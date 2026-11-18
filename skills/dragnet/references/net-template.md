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

| Date | Symptom | Root cause | Class | Caught by | Earliest signal | Added | Proved | Class fix |
|---|---|---|---|---|---|---|---|---|
```
