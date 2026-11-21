#!/usr/bin/env python3
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT / "data" / "catalog.json").read_text())
REFS = ROOT / "skills" / "dragnet" / "references"
SPEED_ORDER = ["instant", "seconds", "minutes", "hours", "continuous", "manual"]
TIER_ORDER = ["edit", "inner", "gate", "nightly", "production", "human"]
ECOSYSTEMS = [("js", "JS/TS"), ("python", "Python"), ("swift", "Swift"), ("rust", "Rust"), ("go", "Go"),
              ("jvm", "JVM"), ("c", "C/C++"), ("mobile", "Mobile"), ("binary", "Binaries"), ("any", "Any")]
BY_ID = {t["id"]: t for t in DATA["techniques"]}


def rank(t):
    return TIER_ORDER.index(t["tier"]), SPEED_ORDER.index(t["speed"]), t["name"]


def tools_line(t):
    parts = [f"{label}: {t['tools'][key]}" for key, label in ECOSYSTEMS if key in t["tools"]]
    return " · ".join(parts)


def catalog():
    out = [
        "# Technique catalog",
        "",
        "Generated from `data/catalog.json`. Each entry is a feedback signal. Judge it by when it fires (tier), how fast it runs (speed), what it catches, and how precisely its failure points at the fix.",
        "",
        "Tiers: " + "; ".join(f"`{k}` {v}" for k, v in DATA["tiers"].items()) + ".",
        "",
        "## Index",
        "",
        "| Technique | Tier | Speed | Setup | Catches |",
        "|---|---|---|---|---|",
    ]
    for t in sorted(DATA["techniques"], key=rank):
        out.append(f"| [{t['name']}](#{t['id']}) | {t['tier']} | {t['speed']} | {t['setup']} | {', '.join(t['catches']) or 'measures the net'} |")
    for group, title in DATA["groups"].items():
        members = [t for t in DATA["techniques"] if t["group"] == group]
        if not members:
            continue
        out += ["", f"## {title}"]
        for t in members:
            covers = ", ".join(f"[{BY_ID[c]['name']}](#{c})" for c in t["cover_gaps_with"])
            out += [
                "",
                f'<a id="{t["id"]}"></a>',
                f"### {t['name']}",
                "",
                t["what"],
                "",
                f"- **Tier / speed / setup:** {t['tier']} · {t['speed']} · {t['setup']}",
                f"- **Catches:** {', '.join(t['catches']) or 'nothing directly; it measures how strong the other signals are'}",
                f"- **Strengths:** {t['strengths']}",
                f"- **Gaps:** {t['gaps']}",
                f"- **Signal quality:** {t['signal']}",
                f"- **Use when:** {t['use_when']}",
                f"- **Covers its gaps:** {covers}",
                f"- **Tools:** {tools_line(t)}",
            ]
    return "\n".join(out) + "\n"


def catch_map():
    out = [
        "# Catch map",
        "",
        "Generated from `data/catalog.json`. For each bug class, the signals that catch it, earliest and cheapest first. When a bug escapes, fix it first, then climb the prevention ladder in escapes.md. Use this row to pick the fastest signal for the rungs that need one: start at the top and take the first the project can afford.",
        "",
    ]
    for cls, desc in DATA["bug_classes"].items():
        ts = sorted((t for t in DATA["techniques"] if cls in t["catches"]), key=rank)
        out += [f"## {cls}", "", desc, ""]
        out += [f"{i}. **{t['name']}** ({t['tier']}, {t['speed']}): {t['use_when']}" for i, t in enumerate(ts, 1)]
        out.append("")
    return "\n".join(out)


def main():
    REFS.mkdir(parents=True, exist_ok=True)
    (REFS / "catalog.md").write_text(catalog())
    (REFS / "catch-map.md").write_text(catch_map())
    print(f"{len(DATA['techniques'])} techniques, {len(DATA['bug_classes'])} bug classes")


if __name__ == "__main__":
    main()
