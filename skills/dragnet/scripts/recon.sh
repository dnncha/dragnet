#!/usr/bin/env bash
set -u

repo="${1:-.}"
days="${2:-90}"
cd "$repo" || { echo "dragnet recon: cannot enter $repo" >&2; exit 2; }

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  files() { git ls-files; }
  in_git=1
else
  files() { find . -type f -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/.build/*' -not -path '*/target/*' | sed 's|^\./||'; }
  in_git=0
fi

all="$(files)"
has() { printf '%s\n' "$all" | grep -Eq "$1"; }
count() { printf '%s\n' "$all" | grep -Ec "$1" || true; }
grep_files() { local pattern="$1"; shift; printf '%s\n' "$all" | grep -E "$pattern" | head -400 | tr '\n' '\0' | xargs -0 grep -l -E "$@" 2>/dev/null | wc -l | tr -d ' '; }
section() { printf '\n## %s\n' "$1"; }
line() { printf -- '- %s\n' "$1"; }

echo "# dragnet recon: $(basename "$(pwd)")"
echo "path: $(pwd)"
[ "$in_git" = 1 ] && echo "head: $(git rev-parse --short HEAD 2>/dev/null) on $(git branch --show-current 2>/dev/null)"

section "Languages (tracked files)"
for pair in "TypeScript:\.(ts|tsx)$" "JavaScript:\.(js|jsx|mjs|cjs)$" "Python:\.py$" "Swift:\.swift$" "Rust:\.rs$" "Go:\.go$" "Kotlin:\.kt$" "Java:\.java$" "C/C++:\.(c|cc|cpp|h|hpp)$" "Ruby:\.rb$"; do
  n=$(count "${pair#*:}")
  [ "$n" -gt 0 ] && line "${pair%%:*}: $n files"
done

section "Test files"
tests=$(count '(^|/)(tests?|__tests__|spec|Tests|e2e|UITests)/|[._-](test|spec)\.[a-z]+$|_test\.(go|py)$|^test_.*\.py$|/test_[^/]*\.py$|Tests?\.swift$')
src=$(count '\.(ts|tsx|js|jsx|py|swift|rs|go|kt|java|c|cc|cpp|rb)$')
line "test-looking files: $tests of $src source files"
has '(^|/)e2e/|\.e2e\.|playwright\.config|cypress\.config|UITests/|\.maestro/' && line "end-to-end suite present"
has '(^|/)fuzz/|fuzz_targets/|FuzzTarget' && line "fuzz targets present"
has '__snapshots__/|\.snap$|/snapshots/|__Snapshots__/' && line "snapshot files present"
has '\.tla$|\.als$|\.dfy$|\.lean$' && line "formal specs present (TLA+, Alloy, Dafny or Lean)"
has '(^|/)evals?/|promptfooconfig' && line "LLM eval suite present"
has '(^|/)bench(es|marks?)?/|_bench\.|\.bench\.' && line "benchmarks present"

section "Signals detected"
if [ -f package.json ]; then
  for dep in typescript vitest jest mocha @playwright/test cypress fast-check @stryker-mutator/core eslint @biomejs/biome oxlint zod valibot @axe-core/playwright storybook c8 @vitest/coverage-v8 k6 @pact-foundation/pact jazzer.js; do
    grep -q "\"$dep\"" package.json && line "npm: $dep"
  done
fi
for f in tsconfig.json tsconfig.base.json; do
  [ -f "$f" ] && { grep -Eq '"strict"[[:space:]]*:[[:space:]]*true' "$f" && line "$f: strict on" || line "$f: strict NOT on"; }
done
for f in pyproject.toml setup.cfg requirements.txt requirements-dev.txt; do
  [ -f "$f" ] || continue
  for dep in pytest hypothesis mypy pyright ruff mutmut atheris coverage pydantic schemathesis pytest-randomly syrupy crosshair; do
    grep -qi "$dep" "$f" && line "$f: $dep"
  done
done
[ -f pyrightconfig.json ] && line "pyrightconfig.json present"
if [ -f Package.swift ]; then
  line "SwiftPM package"
  grep -q 'swift-snapshot-testing' Package.swift && line "swift-snapshot-testing"
  grep -Eq 'swiftLanguageMode|swiftLanguageVersions|StrictConcurrency' Package.swift && line "Swift language mode or strict concurrency set"
fi
has '\.xcodeproj/|\.xcworkspace/' && line "Xcode project"
[ "$(grep_files '\.swift$' 'import Testing')" -gt 0 ] && line "Swift Testing in use"
[ "$(grep_files '\.swift$' 'import XCTest')" -gt 0 ] && line "XCTest in use"
if [ -f Cargo.toml ]; then
  for dep in proptest quickcheck insta criterion divan loom shuttle rstest; do
    grep -q "^$dep\|^\[.*\]$dep\| $dep " Cargo.toml 2>/dev/null; grep -q "$dep" Cargo.toml && line "cargo: $dep"
  done
fi
if [ -f go.mod ]; then
  [ "$(grep_files '_test\.go$' 'func Fuzz')" -gt 0 ] && line "Go native fuzz tests"
  [ "$(grep_files '_test\.go$' 'func Benchmark')" -gt 0 ] && line "Go benchmarks"
  grep -q 'pgregory.net/rapid' go.mod && line "rapid property tests"
fi
for f in .swiftlint.yml .eslintrc .eslintrc.js .eslintrc.json eslint.config.js eslint.config.mjs biome.json ruff.toml .golangci.yml clippy.toml .semgrep.yml .gitleaks.toml; do
  [ -f "$f" ] && line "lint config: $f"
done
[ "$(grep_files '\.(ts|tsx)$' ': any\b|as any\b|@ts-ignore')" -gt 0 ] && line "TypeScript escape hatches (any, @ts-ignore) in $(grep_files '\.(ts|tsx)$' ': any\b|as any\b|@ts-ignore') files"
[ "$(grep_files '\.py$' 'type: ignore')" -gt 0 ] && line "Python type: ignore in $(grep_files '\.py$' 'type: ignore') files"
[ "$(grep_files '\.swift$' '[a-zA-Z)\]]!\.|try!|as!')" -gt 0 ] && line "Swift force unwraps or try! in $(grep_files '\.swift$' '[a-zA-Z)\]]!\.|try!|as!') files"

section "Gate and loop commands"
if [ -f package.json ]; then
  python3 - <<'PY' 2>/dev/null
import json
s = json.load(open("package.json")).get("scripts", {})
for k, v in s.items():
    if any(w in k for w in ("test", "check", "lint", "type", "gate", "verify", "e2e", "ci", "build")):
        print(f"- npm run {k}: {v}")
PY
fi
for f in Makefile justfile Justfile Taskfile.yml; do
  [ -f "$f" ] && grep -E '^[a-zA-Z0-9_-]+:' "$f" | cut -d: -f1 | grep -Ei 'test|check|lint|gate|verify|ci|fuzz|bench' | sed "s|^|- $f target: |"
done
printf '%s\n' "$all" | grep -Ei '(^|/)scripts?/[^/]*gate[^/]*$' | head -5 | sed 's|^|- gate script: |'
printf '%s\n' "$all" | grep -Ei '^scripts?/[^/]*(check|test|verify|ci)[^/]*$' | grep -vi gate | head -10 | sed 's|^|- script: |'
printf '%s\n' "$all" | grep -E '^\.github/workflows/|^\.gitlab-ci|^\.circleci/|^ci_scripts/|^\.buildkite/' | head -10 | sed 's|^|- hosted CI file: |'
[ -f .pre-commit-config.yaml ] && line "pre-commit hooks configured"
printf '%s\n' "$all" | grep -Eq '^\.husky/|^lefthook\.yml' && line "git hooks configured"
for f in AGENTS.md CLAUDE.md .cursorrules NET.md TESTING.md; do
  [ -f "$f" ] && line "agent or testing doc: $f"
done

if [ "$in_git" = 1 ]; then
  section "Escapes in the last $days days (fix, revert, hotfix commits)"
  since="$days days ago"
  total=$(git log --since="$since" --oneline 2>/dev/null | wc -l | tr -d ' ')
  fixes=$(git log --since="$since" -i -E --grep='^(fix|hotfix|revert|bug)|\bfix(es|ed)?\b|regression|broke|crash' --oneline 2>/dev/null | wc -l | tr -d ' ')
  line "$fixes fix-like commits of $total"
  git log --since="$since" -i -E --grep='^(fix|hotfix|revert|bug)|\bfix(es|ed)?\b|regression|broke|crash' --format='  %h %s' 2>/dev/null | head -25
  section "Hotspots: files most touched by fix-like commits"
  git log --since="$since" -i -E --grep='^(fix|hotfix|revert|bug)|\bfix(es|ed)?\b|regression|broke|crash' --name-only --format= 2>/dev/null \
    | grep -Ev '(^|/)(tests?|__tests__|Tests|spec)/|[._-](test|spec)\.|_test\.|\.lock$|\.md$|^$' \
    | sort | uniq -c | sort -rn | head -15 | sed 's|^ *||;s|^|- |'
  section "Fixes that shipped without a test change"
  git log --since="$since" -i -E --grep='^(fix|hotfix|bug)|\bfix(es|ed)?\b|regression|crash' --format='%h' 2>/dev/null | head -60 | while read -r sha; do
    changed=$(git show --name-only --format= "$sha" 2>/dev/null)
    printf '%s\n' "$changed" | grep -Eq '(^|/)(tests?|__tests__|Tests|spec|e2e)/|[._-](test|spec)\.|_test\.|Tests?\.swift$' || git log -1 --format='- %h %s' "$sha"
  done | head -20
fi

section "Next"
echo "Time each loop command above, then follow SKILL.md step 2."
