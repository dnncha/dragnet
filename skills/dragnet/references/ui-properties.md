# Property-based UI exploration

How to get the most out of a UI property tester such as [Bombadil](https://github.com/antithesishq/bombadil) (manual: <https://antithesishq.github.io/bombadil/>). A spec exports properties (`always`, `eventually(...).within`, `next`) over values read from the page (`extract`) and action generators (`actions`, `weighted`, `.when`, `.filter`, `.map`, `flatMap`). The tool clicks, types, scrolls and navigates on its own and checks every property on every state it reaches.

Examples assume Bombadil 0.8 or later. On 0.7.x, `--output-path` names a directory with `trace.jsonl` inside it, and there is no `--chrome-variant`, `bombadil trace` or `--coverage-symbols`.

## The value comes from search effort, not from the gate run

A 10 to 30 second `test` from one page is a smoke check: it reaches shallow states only. The deep, multi-step bugs this technique exists for need long runs, many runs, and runs that start somewhere interesting. Split the work into two tiers:

| Tier | Command | Purpose |
|---|---|---|
| gate | `bombadil browser test --headless --exit-on-violation --time-limit 30s ...` per surface | Catch a broken property on today's change in minutes |
| nightly or background | `bombadil browser fuzz --headless --chrome-variant headless-shell --swarm --parallelism N --time-limit-fuzz 1h --time-limit-run 3m --output-path runs/run.bin <origin> spec.ts` | Find the bugs that need many steps, then shrink each one |

- `--swarm` switches a random subset of action generators off in each run. It is the cheapest way to reach states that a uniform random walk almost never hits, because it stops common actions (scroll, back) from drowning out rare sequences.
- `--chrome-variant headless-shell` renders frame by frame and gives up to four times the throughput of full Chrome. Use it for fuzz campaigns; keep full Chrome for a run whose screenshots someone will read.
- Run campaigns on build machines, not the developer laptop, following the environment's compute routing. Give the campaign a fixed time budget and report the number of runs and states explored as numbers, never as a gate-failing limit.

## Every violation is shrunk before anyone reads it

1. A run or campaign exits non-zero and writes a trace per run.
2. Shrink it with the same flags as the original run: `bombadil browser shrink --headless --trace runs/run-3.bin --output-path shrunk.bin <same flags> <origin> spec.ts`. Shrink runs calibration first, because outside a deterministic hypervisor a replay may not hit the bug again.
3. Attach `bombadil trace shrunk.bin` (state index, action, URL, violations), `bombadil trace shrunk.bin --screenshots shots/` and the reproduce command (`bombadil browser test <same flags> --reproduce shrunk.bin <origin> spec.ts`). `bombadil browser inspect shrunk.bin` opens the state-by-state view for a person.
4. Turn the shrunk trace into a regression: a fixture page that violates the property (below) or a short example test for the exact sequence. Then run the four moves on it.

A violation that will not reproduce after calibration still counts. Fix what the trace shows; do not discard it as flaky.

## Measure what the exploration reaches

Add `--coverage-symbols blocks.jsonl` (the file must not exist yet). It maps covered block ids to script, function and line. Compare the blocks hit across a campaign with the app's routes and handlers. Code a campaign never reaches is a hole in the exploration, not in the properties. Close it by:

- seeding realistic data so the surface exists (signed-in accounts, a basket with items, a merchant with orders) and starting runs from those URLs with `--cookie`;
- weighting rare but important actions up (`weighted([[10, submitForm], [1, scroll]])`);
- adding domain actions with `actions(() => [...])` that type valid values into the right fields, so forms get past validation;
- gating actions on state with `.when(() => ...)` so the walk does useful things on each screen.

## Properties worth writing

Start with the defaults, then turn written rules into properties. A property is the UI form of a sweep: it checks every state the walk reaches, so new pages are covered without new tests.

- **Crash and error signals:** export `noUncaughtExceptions` and `noUnhandledPromiseRejections` from `@antithesishq/bombadil/browser/defaults/properties`, plus no failed same-origin requests and never falling to an error boundary.
- **Leaks:** `noResourceLeak` from `@antithesishq/bombadil/browser/extras/resources` on `dom_nodes` and `js_event_listeners`; these are clearer signals than heap size, which moves with garbage collection. Set the growth limit far above normal behaviour (hundreds of nodes per second, not a number fitted to today's reading) and use `inspect` to look at the metric before choosing it.
- **Product rules:** totals add up, no negative balances, sample data is labelled as sample, no pre-checked consent, no fabricated urgency, money never wraps across lines.
- **Design and accessibility rules:** controls and dialogs have names, invalid fields describe their error, nothing overflows the viewport, Escape closes dialogs (`next` plus `eventually(...).within`).
- **Temporal guarantees:** an error eventually disappears, a loading state eventually resolves, a submitted form eventually shows a result. Use `eventually(...).within(n, "seconds")` with a generous window.

Each extractor names its offenders with a locator (id, href, test id or nearest labelled container) so the violation is one step from the fix.

## Prove each property can fail

A property that has never been seen to fail may check nothing: the extractor can return the wrong element, or the guard condition can be false everywhere. Keep a fault suite: a tiny local server that serves one broken fixture page per property and one clean page, runs the spec against each, and fails unless each broken page violates exactly its property and the clean page violates none. Run it in the gate. When a campaign finds a new bug, add its shape as a fixture.

## Keep the harness honest

Driver faults are not product failures. Treat them separately so agents do not learn that red means nothing.

- **Always export a fallback action.** If every generator is gated with `.when`, some states have no action and the run dies with `no actions available`. Export `actions(() => ["Wait"])` with a low weight, or a back or reload action, so every state has a move.
- **Classify exits.** A property violation is a product failure. A driver error (CDP timeouts such as `Page.captureScreenshot` or `CSS.enable`, `failed to launch`, `connection closed`) is an infrastructure loss: retry that surface once and report it as no verdict if it fails again.
- **Pin the boundary.** Start from a local server with a seeded throwaway database and fake payment, email and storage endpoints. Use `--allow-url` to keep the walk on the surface under test. When the page needs network fencing, run `bombadil browser test-external --remote-debugger <url>` against a browser the harness controls (for example a Playwright context that routes or blocks every request) and assert afterwards that the walk stayed in that context.
- **Stable browser flags.** `--disable-dev-shm-usage`, `--disable-gpu`, `--force-prefers-reduced-motion` and a host resolver rule that maps everything but the local server to nothing remove most environment noise. `--chrome-virtual-time-policy` speeds up timer-heavy apps.
- **Clean up evidence.** Traces with screenshots are large. Write them under the job's own temporary directory, keep only failing traces, and delete the rest when the run ends. A RAM-backed `/tmp` on a build machine fills with them otherwise.
- **Pin the tool version** in the lockfile, and read the release notes before upgrading: trace formats and output paths have changed between 0.x releases.

## Where it sits in the net

- Inner loop: the fault suite for the property you are editing, and the pure functions behind each extractor.
- Gate: one short `test` per key surface and viewport, `--exit-on-violation`, driver errors retried once.
- Nightly or background: a `fuzz --swarm` campaign with coverage symbols, every violation shrunk and filed with its trace.
- Escape log: when a person or a later tier finds a UI bug, ask which property would have caught it and whether the walk could reach that state. Add the property, or the seed data and actions that reach the state, or both.
