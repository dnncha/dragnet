# dragnet

An agent skill that builds a project's feedback net, so coding agents catch their own mistakes fast.

An agent improves only as fast as its signals tell it it's wrong. Strict types, lint rules, assertions, tests, fuzzers, sanitizers and production alerts are all feedback. dragnet picks the right ones for a project, puts each at the earliest tier that can see the bug, and makes every failure precise enough to fix in one step.

**North star: the fastest honest feedback on every change.**

## What it does

1. **Recon.** `scripts/recon.sh` lists a repo's languages, tests, type and lint strictness, gate commands, escaped bugs, fix hotspots, and fixes that shipped without a test.
2. **Risk surfaces.** Names where the project can hurt users, weighted by where bugs keep landing.
3. **Net map.** Marks each risk as covered, late or a hole. Coverage here means risk × signal, with mutation testing to check that tests actually assert something.
4. **Escape analysis.** Every bug that got through, and every defect a new signal catches, is fixed along with its siblings. Then its whole class gets a guard from the top of a prevention ladder: make it impossible with a type, delete the dangerous API, ban it with a lint rule, or sweep the surface, before falling back to assertions, properties and regression tests. Each guard runs at the fastest tier it can, so the next instance fails within seconds of the edit, and is proven red on the old code and on a planted sibling.
5. **Tight loop.** One inner-loop command and one gate command, with flakes fixed or quarantined and slow suites moved to nightly runs.
6. **NET.md.** A short file at the repo root that tells every future agent session how the net works. `scripts/netcheck.py` runs in the gate and fails when a signal has no trigger (a suite that only runs by hand) or an escape's guard sits below the lint-rule rung without a written reason.
7. **Close holes now.** Each new signal is proven by injecting the bug it targets and watching it fail. Whatever it catches in today's code gets fixed in the same session, not baselined.

It ships with a catalog of 50 techniques: tier, speed, setup cost, strengths, gaps, signal quality, what covers each gap, and tools for JS/TS, Python, Swift, Rust, Go and the JVM. It also has a catch map from 17 bug classes to the signals that catch them, earliest first.

## Install

Any agent that reads skills (Claude Code, Codex, Cursor and others):

```sh
npx skills add dnncha/dragnet
```

Claude Code plugin:

```text
/plugin marketplace add dnncha/dragnet
/plugin install dragnet@dragnet
```

By hand:

```sh
git clone https://github.com/dnncha/dragnet ~/dragnet
ln -s ~/dragnet/skills/dragnet ~/.claude/skills/dragnet
```

## Use

```text
/dragnet
/dragnet a user hit a crash when importing an empty CSV
/dragnet our test suite takes 12 minutes, make the loop tight
/dragnet what do our tests actually cover?
```

The full field guide is at [notchbird.com/testing](https://notchbird.com/testing/).

## Layout

```text
skills/dragnet/SKILL.md                 the procedure
skills/dragnet/scripts/recon.sh         repo scan
skills/dragnet/scripts/bombadil-campaign.mjs  Bombadil fuzz, shrink and coverage runner
skills/dragnet/references/catalog.md    50 techniques (generated)
skills/dragnet/references/catch-map.md  bug class → signals (generated)
skills/dragnet/references/escapes.md    escape analysis
skills/dragnet/references/loop.md       faster, honest, precise signals
skills/dragnet/references/net-template.md
skills/dragnet/references/ui-properties.md  UI property exploration with Bombadil
data/catalog.json                       source data
tools/build.py                          regenerates the generated references
```

Edit `data/catalog.json`, then run `python3 tools/build.py`.

Made by [Notchbird](https://notchbird.com), a Mac notch app for Claude Code and Codex. MIT licensed.
