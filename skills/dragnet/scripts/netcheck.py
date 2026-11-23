#!/usr/bin/env python3
import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

RUNG_NAMES = {
    1: "impossible",
    2: "deleted path",
    3: "rule",
    4: "sweep",
    5: "assertion",
    6: "property or fuzz",
    7: "regression test",
    8: "production",
}
CLASS_KILLING = {1, 2, 3, 4}
UNWIRED = re.compile(r"\b(by hand|manual(ly)?|not scheduled|unscheduled|on demand|ad hoc|when someone remembers|occasional(ly)?)\b", re.I)
SCHEDULED_TIERS = re.compile(r"^(nightly|weekly|daily|hourly|occasional|on demand|bench|scheduled|canary)", re.I)
WIRED_TRIGGERS = re.compile(
    r"\b(compiler|editor|save|hook|pre-commit|commit|inner|gate|merge|ci|release|deploy|scheduled|cron|launchd|live|alert|human|per release|every change)\b",
    re.I,
)


def cells(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in re.split(r"(?<!\\)\|", body)]


def tables(text):
    heading = ""
    rows = []
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("#"):
            if rows:
                yield heading, rows
                rows = []
            heading = line.lstrip("#").strip()
            continue
        if line.lstrip().startswith("|"):
            rows.append((number, cells(line)))
        elif rows:
            yield heading, rows
            rows = []
    if rows:
        yield heading, rows


def split_table(rows):
    header = [h.lower() for h in rows[0][1]]
    body = [(n, r) for n, r in rows[1:] if not all(set(c) <= set("-: ") for c in r)]
    return header, body


def column(header, *names):
    for i, h in enumerate(header):
        if any(h == n or h.startswith(n) for n in names):
            return i
    return None


def check(path):
    text = Path(path).read_text()
    errors = []
    signals = []
    escapes = []
    saw_signals = saw_escapes = False
    for heading, rows in tables(text):
        h = heading.lower()
        header, body = split_table(rows)
        if "signal" in h or h.startswith("commands") or h == "signals":
            saw_signals = True
            tier_i = column(header, "tier")
            runs_i = column(header, "runs")
            name_i = column(header, "signal", "command")
            if runs_i is None:
                errors.append((rows[0][0], f"signals table under '{heading}' has no 'Runs' column naming what triggers each signal"))
                continue
            for n, r in body:
                tier = r[tier_i] if tier_i is not None and tier_i < len(r) else ""
                runs = r[runs_i] if runs_i < len(r) else ""
                name = r[name_i] if name_i is not None and name_i < len(r) else ""
                signals.append({"line": n, "tier": tier, "runs": runs, "signal": name})
                label = (name or tier)[:70]
                if tier.lower().startswith("human"):
                    continue
                if not runs:
                    errors.append((n, f"signal '{label}' has an empty Runs cell"))
                elif UNWIRED.search(runs):
                    errors.append((n, f"signal '{label}' is written but not wired: Runs says '{runs[:60]}'. Schedule it, put it in the gate, or move it to Holes"))
                elif SCHEDULED_TIERS.match(tier) and not re.match(r"scheduled\b.{3,}", runs, re.I):
                    errors.append((n, f"signal '{label}' is tier '{tier}' but Runs does not say 'scheduled: <where, when>'"))
                elif not WIRED_TRIGGERS.search(runs):
                    errors.append((n, f"signal '{label}' Runs cell '{runs[:60]}' names no trigger (hook, inner, gate, release, scheduled, live)"))
        if "escape" in h:
            saw_escapes = True
            rung_i = column(header, "rung")
            class_i = column(header, "class", "bug class")
            if rung_i is None:
                errors.append((rows[0][0], f"escape log under '{heading}' has no 'Rung' column"))
                continue
            for n, r in body:
                cell = r[rung_i] if rung_i < len(r) else ""
                cls = r[class_i] if class_i is not None and class_i < len(r) else ""
                m = re.match(r"\s*([1-8])\b", cell)
                if not m:
                    errors.append((n, f"escape row has no rung number 1-8 (got '{cell[:40]}')"))
                    continue
                rung = int(m.group(1))
                escapes.append({"line": n, "rung": rung, "class": cls, "cell": cell})
                if rung not in CLASS_KILLING and not re.search(r"above:\s*\S.{10,}", cell, re.I):
                    errors.append((n, f"escape guarded at rung {rung} ({RUNG_NAMES[rung]}) without 'above: <why rungs 1-4 are impossible here>'"))
    if not saw_signals:
        errors.append((0, "no signals table found"))
    if not saw_escapes:
        errors.append((0, "no escape log found"))
    return signals, escapes, errors


def class_key(text):
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def report(path, as_json):
    signals, escapes, errors = check(path)
    rungs = Counter(e["rung"] for e in escapes)
    killed = sum(rungs[r] for r in CLASS_KILLING)
    by_class = defaultdict(list)
    for e in escapes:
        if e["class"]:
            by_class[class_key(e["class"])].append(e)
    open_classes = [
        {"class": rows[0]["class"], "rows": [r["line"] for r in rows], "best_rung": min(r["rung"] for r in rows)}
        for rows in by_class.values()
        if len(rows) >= 2 and min(r["rung"] for r in rows) not in CLASS_KILLING
    ]
    summary = {
        "file": str(path),
        "signals": len(signals),
        "escapes": len(escapes),
        "rungs": {str(k): rungs[k] for k in sorted(rungs)},
        "class_killing": killed,
        "open_classes": open_classes,
        "errors": [{"line": n, "message": m} for n, m in errors],
    }
    if as_json:
        print(json.dumps(summary, indent=2))
        return summary
    print(f"{path}: {len(signals)} signals, {len(escapes)} escapes")
    if escapes:
        hist = ", ".join(f"{k} {RUNG_NAMES[k]}: {rungs[k]}" for k in sorted(rungs))
        print(f"  rungs: {hist}")
        print(f"  class-killing guards (rungs 1-4): {killed} of {len(escapes)}")
    for c in open_classes:
        print(f"  open class (recurs, no class-killing guard): '{c['class'][:70]}' rows at lines {c['rows']}, best rung {c['best_rung']}")
    for n, m in errors:
        print(f"{path}:{n}: {m}")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Check a NET.md: every signal wired to a trigger, every escape guard on a named rung with a reason when it is below rung 4.")
    parser.add_argument("paths", nargs="*", default=["NET.md"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    failed = False
    for p in args.paths:
        if report(p, args.json)["errors"]:
            failed = True
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
