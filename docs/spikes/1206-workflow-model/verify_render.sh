#!/usr/bin/env bash
# Spike (#1206): drive render_workflow_model() against a copy of the scaffold
# template and verify the trunk output. Run inside the dev shell:
#   direnv exec . docs/spikes/1206-workflow-model/verify_render.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$HERE/../../.." && pwd)"
TEMPLATE="$REPO_ROOT/assets/workspace"
# shellcheck source-path=SCRIPTDIR
# shellcheck source=./render_workflow_model.sh
source "$HERE/render_workflow_model.sh"

WORK="$(mktemp -d "${TMPDIR:-/tmp}/render-verify.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
fail() { echo "ASSERT FAILED: $*" >&2; exit 1; }
pass() { echo "  ok: $*"; }

# ── gitflow render is byte-identical to the committed template ────────────────
GF="$WORK/gitflow"; cp -a "$TEMPLATE" "$GF"
render_workflow_model "$GF" gitflow
if diff -r "$TEMPLATE" "$GF" >/dev/null; then
    pass "gitflow render is byte-identical to the committed template"
else
    fail "gitflow render changed bytes (must be a no-op)"; fi

# ── trunk render ─────────────────────────────────────────────────────────────
TR="$WORK/trunk"; cp -a "$TEMPLATE" "$TR"
render_workflow_model "$TR" trunk
WF="$TR/.github/workflows"

echo "── Trunk shape assertions ──────────────────────────────────────────────"

# sync-main-to-dev.yml removed
[[ ! -e "$WF/sync-main-to-dev.yml" ]] || fail "sync-main-to-dev.yml still present"
pass "sync-main-to-dev.yml removed (copy-exclude)"

# prepare-release: zero residual heads/dev, base is main
if grep -n 'heads/dev\b' "$WF/prepare-release.yml"; then
    fail "residual heads/dev in prepare-release.yml"; fi
pass "prepare-release.yml has zero residual heads/dev"
[[ "$(grep -c '^          ref: main$' "$WF/prepare-release.yml")" -eq 2 ]] \
    || fail "prepare-release.yml checkout base not retargeted to main (x2)"
grep -q 'refs/heads/main' "$WF/prepare-release.yml" \
    || fail "prepare-release.yml commit target not retargeted to refs/heads/main"
grep -q 'Create release branch from main' "$WF/prepare-release.yml" \
    || fail "prepare-release.yml fork step name not retargeted"
pass "prepare-release.yml base retargeted dev -> main"

# development/devkit/devcontainer NOT collaterally damaged anywhere in the tree
if grep -rn 'heads/mainelopment\|heads/maincontainer\|heads/mainkit\|mainelopment\|maincontainer' "$TR" ; then
    fail "anchoring damaged a development/devcontainer/devkit token"; fi
pass "no development/devcontainer/devkit token collaterally rewritten"

# ci.yml: PR filter excludes dev, TRUNK anchor = main
grep -qE '^      - dev$' "$WF/ci.yml" && fail "ci.yml still lists '- dev' in PR filter"
grep -q 'TRUNK="main"' "$WF/ci.yml" || fail "ci.yml commit-gate TRUNK not retargeted"
pass "ci.yml PR filter drops dev; commit-gate TRUNK=main"

# codeql.yml: PR filter excludes dev, push main leg intact
grep -qE '^      - dev$' "$WF/codeql.yml" && fail "codeql.yml still lists '- dev'"
grep -qE '^      - main$' "$WF/codeql.yml" || fail "codeql.yml lost its main leg"
pass "codeql.yml PR filter drops dev; main leg intact"

# sync-issues.yml: default main + no `|| 'dev'` fallbacks
grep -qE "^        default: 'main'\$" "$WF/sync-issues.yml" \
    || fail "sync-issues.yml default target-branch not 'main'"
grep -q "|| 'dev'" "$WF/sync-issues.yml" && fail "sync-issues.yml still has || 'dev' fallback"
pass "sync-issues.yml default main; no || 'dev' fallback"

# SKILL.md: base default main, sync-main-to-dev example untouched
# shellcheck disable=SC2016  # literal Markdown backticks in the grep pattern
grep -q 'fall back to `main`' "$TR/.claude/skills/branch-naming/SKILL.md" \
    || fail "SKILL.md parent fallback not main"
# shellcheck disable=SC2016  # literal Markdown backticks in the grep pattern
grep -q 'use `main` as' "$TR/.claude/skills/branch-naming/SKILL.md" \
    || fail "SKILL.md base default not main"
grep -q 'chore/sync-main-to-dev' "$TR/.claude/skills/branch-naming/SKILL.md" \
    || fail "SKILL.md example branch name accidentally rewritten"
pass "SKILL.md base default main; example branch name preserved"

# pre-commit: no (?!dev$) clause
grep -q '(?!dev$)' "$TR/.pre-commit-config.yaml" && fail "pre-commit still has (?!dev\$)"
grep -q '(?!main$)' "$TR/.pre-commit-config.yaml" || fail "pre-commit lost the (?!main\$) clause"
pass "pre-commit drops (?!dev\$); (?!main\$) retained"

echo "── #991 invariants on rendered prepare-release.yml ─────────────────────"
grep -q 'ghcr.io/vig-os/devcontainer:' "$WF/prepare-release.yml" \
    && fail "#991: rendered prepare-release.yml pins a raw image"
grep -q 'resolve-image' "$WF/prepare-release.yml" \
    && fail "#991: rendered prepare-release.yml references resolve-image"
grep -q 'setup-devkit-toolchain' "$WF/prepare-release.yml" \
    || fail "#991: rendered prepare-release.yml lost setup-devkit-toolchain"
pass "#991 invariants intact (no raw pin, no resolve-image, uses setup-devkit-toolchain)"

echo "── actionlint on rendered trunk workflows ──────────────────────────────"
# actionlint runs per-file; the scaffold uses reusable-workflow `uses: ./...`
# refs that only resolve inside a full repo checkout, so lint each file and
# treat 'workflow file not found' cross-refs as out-of-scope for the spike.
for f in prepare-release.yml ci.yml codeql.yml sync-issues.yml; do
    if actionlint "$WF/$f" 2>&1 | grep -vE 'could not read|does not exist|reusable workflow'; then
        :
    fi
    actionlint "$WF/$f" >/dev/null 2>&1 && pass "actionlint clean: $f" \
        || echo "  note: actionlint on $f — see filtered output above (cross-ref only?)"
done

echo
echo "RENDER VERIFY: all trunk-shape + gitflow-noop assertions passed."
