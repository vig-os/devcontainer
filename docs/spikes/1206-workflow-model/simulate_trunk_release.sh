#!/usr/bin/env bash
# Spike (#1206, epic #1205): trunk release-topology proof.
#
# Proves that a release cut from `main` and merged back into `main` works with
# NO `dev` branch, and that the prepare-release freeze/fork logic is
# topology-correct when the base is retargeted from `dev` to `main`.
#
# This is a LOCAL git simulation only — it creates a throwaway repo, never a
# GitHub repo, and never dispatches an Action. It replays the *core* logic of
# the real managed workflows against base=`main`:
#
#   prepare-release.yml
#     - freeze + reset      (:199-240) prepare-changelog reset-version + prepare,
#                                       then commit the frozen CHANGELOG to base
#     - fork-from-base      (:242-281) create release/X.Y.Z from base's
#                                       post-freeze SHA
#     - #617 advance guard  (:250-269) assert base advanced past the pre-freeze
#                                       SHA before branching (read-after-write lag
#                                       guard; here proven identical with base=main)
#     - #590 Unreleased      (:293-297) base retains an empty `## Unreleased`
#                                       above the dated release
#   promote-release.yml
#     - merge release/* -> main (:458-466) merge the release branch back to main
#     - tag                                 publish the version tag into main history
#
# Uses the real `prepare-changelog` tool from the devkit dev shell so the freeze
# is byte-for-byte what the workflow runs. Run inside the dev shell:
#   direnv exec . docs/spikes/1206-workflow-model/simulate_trunk_release.sh
set -euo pipefail

VERSION="1.0.0"
REPO="$(mktemp -d "${TMPDIR:-/tmp}/trunk-release-sim.XXXXXX")"
trap 'rm -rf "$REPO"' EXIT

fail() { echo "ASSERT FAILED: $*" >&2; exit 1; }
pass() { echo "  ok: $*"; }

command -v prepare-changelog >/dev/null 2>&1 \
  || fail "prepare-changelog not on PATH — run inside the devkit dev shell (direnv exec .)"

cd "$REPO"

# ── Trunk repo: main is the ONLY long-lived branch (no dev) ──────────────────
git init -q -b main
git config user.name  "Spike Bot"
git config user.email "spike@example.invalid"
git config commit.gpgsign false

cat > CHANGELOG.md <<'EOF'
# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

### Added

- **Trunk workflow model** ([#1205](https://example/1205))
  - A per-consumer `DEVKIT_WORKFLOW` knob selecting `gitflow` or `trunk`.

### Fixed

- **Freeze idempotency** ([#612](https://example/612))
EOF

git add CHANGELOG.md
git commit -qm "chore: seed changelog with populated Unreleased"

# The frozen-content fingerprint we expect to survive into [1.0.0].
FROZEN_MARKER="Trunk workflow model"

# ── prepare-release: capture pre-freeze base SHA (the #617 anchor) ───────────
# Real workflow reads git/ref/heads/dev; here the base is `main`.
PREPARE_START_SHA="$(git rev-parse main)"
echo "prepare-release base = main  (pre-freeze SHA ${PREPARE_START_SHA:0:12})"

# ── prepare-release: freeze + reset (:199-240) ───────────────────────────────
# reset-version is a no-op here (heading is TBD/absent) but mirrors the workflow
# exactly; prepare moves Unreleased -> [1.0.0] - TBD and recreates empty Unreleased.
prepare-changelog reset-version "$VERSION" CHANGELOG.md
prepare-changelog prepare "$VERSION" CHANGELOG.md
git add CHANGELOG.md
# Real workflow commits this to the base branch via commit-action; base=main here.
git commit -qm "chore: freeze changelog for release ${VERSION}"
POST_FREEZE_SHA="$(git rev-parse main)"
echo "froze changelog on main    (post-freeze SHA ${POST_FREEZE_SHA:0:12})"

# ── prepare-release: #617 advance guard (:250-269) ───────────────────────────
# The workflow loops until the base ref advances past PREPARE_START_SHA before
# branching, guarding read-after-write lag. The guard predicate is base-agnostic:
# it compares two SHAs of the SAME base branch. Retargeting dev->main changes only
# WHICH ref is read, not the comparison — so the logic is identical.
[ "$POST_FREEZE_SHA" != "$PREPARE_START_SHA" ] \
  || fail "#617 guard: base (main) did not advance past pre-freeze SHA"
pass "#617 advance guard holds with base=main (post-freeze != pre-freeze)"

# ── prepare-release: fork release branch from base's post-freeze SHA (:242-281)
RELEASE_BRANCH="release/${VERSION}"
git branch "$RELEASE_BRANCH" "$POST_FREEZE_SHA"
echo "cut ${RELEASE_BRANCH} from main@${POST_FREEZE_SHA:0:12}"

# Between fork and promote, main keeps developing (trunk: features land on main).
git commit -q --allow-empty -m "feat: post-freeze work continues on main"

# ── promote-release: merge release/* -> main + tag (:458-466) ────────────────
# Real workflow merges the release PR into main via `gh pr merge --merge` (a
# merge commit), then the release pipeline tags the version. Simulate with a
# no-ff merge + annotated tag.
git checkout -q main
git merge --no-ff -q "$RELEASE_BRANCH" -m "chore: release ${VERSION}"
git tag -a "$VERSION" -m "Release ${VERSION}"
echo "merged ${RELEASE_BRANCH} into main and tagged ${VERSION}"

echo
echo "── Assertions ──────────────────────────────────────────────────────────"

# 1. Tag 1.0.0 exists and points into main's history.
git rev-parse -q --verify "refs/tags/${VERSION}" >/dev/null \
  || fail "tag ${VERSION} does not exist"
git merge-base --is-ancestor "$VERSION" main \
  || fail "tag ${VERSION} is not reachable from main"
pass "tag ${VERSION} exists and is an ancestor of main"

# 2. `## Unreleased` is present on main (#590 preservation).
git show "main:CHANGELOG.md" | grep -q '^## Unreleased$' \
  || fail "main lost its '## Unreleased' section"
pass "main retains an empty '## Unreleased' section (#590)"

# 3. No `dev` branch was ever created.
! git show-ref --verify --quiet refs/heads/dev \
  || fail "a 'dev' branch exists — trunk topology must have none"
[ "$(git for-each-ref --format='%(refname:short)' refs/heads/ | sort | tr '\n' ' ')" \
  = "main release/1.0.0 " ] \
  || fail "unexpected branch set: $(git for-each-ref --format='%(refname:short)' refs/heads/)"
pass "no 'dev' branch exists (only main + release/1.0.0)"

# 4. The dated [1.0.0] section carries the frozen Unreleased content.
git show "main:CHANGELOG.md" | grep -qE "^## \[${VERSION//./\\.}\]" \
  || fail "main CHANGELOG missing dated [${VERSION}] heading"
awk -v ver="[${VERSION}]" '
  $0 ~ ("^## \\" ver) {inver=1; next}
  /^## \[/ && inver {inver=0}
  inver {print}
' <(git show "main:CHANGELOG.md") | grep -q "$FROZEN_MARKER" \
  || fail "frozen content ('${FROZEN_MARKER}') not found under [${VERSION}]"
pass "the [${VERSION}] section carries the frozen content"

# 5. Unreleased is empty of the frozen entry (it moved down, not duplicated).
awk '
  /^## Unreleased$/ {inunrel=1; next}
  /^## \[/ && inunrel {inunrel=0}
  inunrel {print}
' <(git show "main:CHANGELOG.md") | grep -q "$FROZEN_MARKER" \
  && fail "frozen content still present under Unreleased (freeze did not move it)"
pass "the new Unreleased no longer carries the frozen entry (moved, not copied)"

echo
echo "TRUNK RELEASE TOPOLOGY: all assertions passed (no dev branch involved)."
