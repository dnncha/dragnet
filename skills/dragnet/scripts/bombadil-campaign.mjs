import { spawn } from "node:child_process";
import { createReadStream, existsSync } from "node:fs";
import { mkdir, readdir, rm, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { createInterface } from "node:readline";

export const driverFailure = /driver error|timed out waiting for response|failed to launch|connection closed|failed to locate/i;

function collect(binary, args, { env = process.env } = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(binary, args, { env, stdio: ["ignore", "pipe", "pipe"] });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => (stdout += chunk));
    child.stderr.on("data", (chunk) => (stderr += chunk));
    child.once("error", reject);
    child.once("exit", (code, signal) => resolve({ code: signal ? 1 : code, stdout, stderr }));
  });
}

function redacted(args) {
  return args.map((arg, index) => (args[index - 1] === "--cookie" ? `'${arg.split("=")[0]}=<redacted>'` : arg.includes(" ") ? `'${arg}'` : arg));
}

export async function traceStates(binary, tracePath) {
  if (!existsSync(tracePath)) return [];
  const { stdout } = await collect(binary, ["trace", "--json", tracePath]);
  return stdout
    .split("\n")
    .filter((line) => line.startsWith("{"))
    .map((line) => JSON.parse(line));
}

function snapshotsIn(value) {
  if (!value || typeof value !== "object") return [];
  if (Array.isArray(value.snapshots)) return value.snapshots;
  for (const child of Object.values(value)) {
    const found = snapshotsIn(child);
    if (found.length) return found;
  }
  return [];
}

export function violationsInStates(states) {
  const found = new Map();
  for (const entry of states) {
    for (const violation of entry.metadata?.violations ?? entry.violations ?? []) {
      if (found.has(violation.name)) continue;
      found.set(violation.name, {
        name: violation.name,
        url: entry.metadata?.state?.url ?? entry.state?.url ?? "unknown url",
        index: entry.index,
        snapshots: snapshotsIn(violation.violation)
      });
    }
  }
  return [...found.values()];
}

function actionOf(entry) {
  const action = entry.metadata?.action ?? entry.action;
  if (!action) return "(initial state)";
  const [kind, detail] = typeof action === "string" ? [action, null] : Object.entries(action)[0];
  const target = detail?.fingerprint ? ` ${JSON.stringify(detail.fingerprint)}` : detail && typeof detail !== "object" ? ` ${detail}` : "";
  return `${kind}${target}`;
}

async function coverageReport(blocksPath, states) {
  if (!existsSync(blocksPath)) return null;
  const blocks = new Map();
  const lines = createInterface({ input: createReadStream(blocksPath) });
  for await (const line of lines) {
    if (!line.startsWith("{")) continue;
    const block = JSON.parse(line);
    blocks.set(block.id, block);
  }
  const hit = new Set();
  for (const entry of states) for (const id of entry.metadata?.state?.branches ?? entry.state?.branches ?? []) hit.add(Array.isArray(id) ? id[0] : id);
  const byScript = new Map();
  for (const [id, block] of blocks) {
    const script = block.script.replace(/^https?:\/\/[^/]+/, "");
    const row = byScript.get(script) ?? { script, total: 0, hit: 0, unreached: new Set() };
    row.total += 1;
    if (hit.has(id)) row.hit += 1;
    else if (block.function && block.function !== "<top>") row.unreached.add(`${block.function}:${block.line}`);
    byScript.set(script, row);
  }
  const vendor = /node_modules|turbopack|webpack|hmr-client|next-devtools|react-dom|react-server-dom/;
  const rows = [...byScript.values()].filter((row) => !vendor.test(row.script)).sort((a, b) => b.total - b.hit - (a.total - a.hit));
  return { blocks: blocks.size, hit: [...blocks.keys()].filter((id) => hit.has(id)).length, rows };
}

const localHosts = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);

export function assertAllowedOrigin(origin, allowedHosts = []) {
  const { hostname } = new URL(origin);
  if (localHosts.has(hostname) || hostname.endsWith(".localhost") || allowedHosts.includes(hostname)) return;
  throw new Error(`bombadil campaign refuses origin ${origin}: fuzz a local or staging build you own, and name its host in allowedHosts`);
}

export async function runCampaign({
  binary,
  origin,
  specification,
  directory,
  fuzzTime = "4m",
  runTime = "90s",
  parallelism = 2,
  chromeVariant = "full",
  env = process.env,
  flags = [],
  keepPassingTraces = false,
  allowedHosts = [],
  disposableContainer = false,
  log = console.log
}) {
  assertAllowedOrigin(origin, allowedHosts);
  await mkdir(directory, { recursive: true });
  const shared = ["--headless", ...(disposableContainer ? ["--no-sandbox"] : []), "--chrome-variant", chromeVariant, ...flags];
  const started = Date.now();
  const fuzz = await collect(
    binary,
    [
      "browser",
      "fuzz",
      ...shared,
      "--swarm",
      "--parallelism",
      String(parallelism),
      "--time-limit-fuzz",
      fuzzTime,
      "--time-limit-run",
      runTime,
      "--output-path",
      join(directory, "run.bin"),
      "--coverage-symbols",
      join(directory, "blocks.jsonl"),
      origin,
      specification
    ],
    { env }
  );
  await writeFile(join(directory, "fuzz.log"), fuzz.stdout + fuzz.stderr);
  const traces = (await readdir(directory)).filter((name) => /^run-\d+\.bin$/.test(name)).sort((a, b) => Number(a.match(/\d+/)[0]) - Number(b.match(/\d+/)[0]));
  const allStates = [];
  const firstRunFor = new Map();
  let statesExplored = 0;
  for (const name of traces) {
    const states = await traceStates(binary, join(directory, name));
    statesExplored += states.length;
    allStates.push(...states);
    const violations = violationsInStates(states);
    for (const violation of violations) if (!firstRunFor.has(violation.name)) firstRunFor.set(violation.name, { trace: name, states: states.length, violation });
    if (!violations.length && !keepPassingTraces) await rm(join(directory, name), { force: true });
  }
  const coverage = await coverageReport(join(directory, "blocks.jsonl"), allStates);
  const fuzzOutput = fuzz.stdout + fuzz.stderr;
  const driverError = ![0, 2].includes(fuzz.code) || (!traces.length && driverFailure.test(fuzzOutput));
  const errorTail = driverError ? fuzzOutput.split("\n").filter((line) => line.trim() && !line.includes(" WARN ")).slice(-3).join(" / ").slice(0, 600) : "";
  const findings = [];
  for (const [property, found] of firstRunFor) {
    const shrunk = join(directory, `shrunk-${property}.bin`);
    const shrink = await collect(
      binary,
      ["browser", "shrink", ...shared, "--trace", join(directory, found.trace), "--property", property, "--output-path", shrunk, "--output-path-overwrite", origin, specification],
      { env }
    );
    await writeFile(join(directory, `shrink-${property}.log`), shrink.stdout + shrink.stderr);
    const finalTrace = existsSync(shrunk) ? shrunk : join(directory, found.trace);
    const steps = await traceStates(binary, finalTrace);
    const shots = join(directory, `screens-${property}`);
    await mkdir(shots, { recursive: true });
    await collect(binary, ["trace", finalTrace, "--screenshots", shots]);
    findings.push({
      property,
      url: found.violation.url,
      originalStates: found.states,
      shrunk: existsSync(shrunk),
      steps: steps.map(actionOf),
      snapshots: found.violation.snapshots,
      trace: finalTrace,
      screenshots: shots,
      reproduce: `${binary} browser test ${redacted(shared).join(" ")} --reproduce ${finalTrace} '${origin}' ${specification}`
    });
  }
  const summary = {
    origin,
    seconds: Math.round((Date.now() - started) / 1000),
    runs: traces.length,
    statesExplored,
    fuzzExit: fuzz.code,
    driverError,
    errorTail,
    coverage: coverage && { blocks: coverage.blocks, hit: coverage.hit },
    findings
  };
  await writeFile(join(directory, "summary.json"), JSON.stringify(summary, null, 2));
  const report = [
    `# Bombadil campaign: ${origin}`,
    "",
    `${summary.runs} runs, ${summary.statesExplored} states, ${summary.seconds} s, fuzz exit ${summary.fuzzExit}${driverError ? ` (no verdict: ${errorTail})` : ""}.`,
    coverage ? `Coverage: ${coverage.hit} of ${coverage.blocks} instrumented blocks reached.` : "Coverage: no symbols written.",
    "",
    ...findings.flatMap((finding) => [
      `## ${finding.property}`,
      "",
      `At ${finding.url}. ${finding.shrunk ? `Shrunk from ${finding.originalStates} states to ${finding.steps.length}` : `Not shrunk (${finding.originalStates} states)`}:`,
      "",
      ...finding.steps.map((step, index) => `${index}. ${step}`),
      "",
      ...finding.snapshots.slice(0, 6).map((snapshot) => `- ${snapshot.name ?? "value"} = ${JSON.stringify(snapshot.value).slice(0, 400)}`),
      "",
      `Trace: ${finding.trace}`,
      `Screenshots: ${finding.screenshots}`,
      `Reproduce: ${finding.reproduce}`,
      ""
    ]),
    ...(coverage
      ? [
          "## Least reached app scripts",
          "",
          "| Script | Reached | Blocks | Some unreached functions |",
          "|---|---|---|---|",
          ...coverage.rows.slice(0, 15).map((row) => `| ${row.script.slice(-80)} | ${row.hit} | ${row.total} | ${[...row.unreached].slice(0, 5).join(", ")} |`)
        ]
      : [])
  ].join("\n");
  await writeFile(join(directory, "report.md"), report + "\n");
  log(
    `${findings.length ? "FAIL " : driverError ? "ERROR" : "ok   "} ${origin}: ${summary.runs} runs, ${summary.statesExplored} states, ${coverage ? `${coverage.hit}/${coverage.blocks} blocks, ` : ""}${findings.length} properties violated${findings.length ? ` (${findings.map((finding) => `${finding.property} in ${finding.steps.length} steps`).join(", ")})` : ""}${driverError ? `; fuzz exit ${fuzz.code}, no verdict: ${errorTail}` : ""}; report ${join(directory, "report.md")}`
  );
  return summary;
}
