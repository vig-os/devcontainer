#!/usr/bin/env bash
# Spike (#1206, epic #1205): scaffold-render prototype for DEVKIT_WORKFLOW.
#
# Prototypes `render_workflow_model()` — the trunk-mode counterpart of
# `render_codeql_matrix()` (assets/init-workspace.sh:857). It rewrites a COPY of
# the scaffolded workspace from the gitflow default (dev + main + sync-main-to-dev)
# to the trunk shape (main only) using anchored sed, mirroring the locked design:
# trunk is realized entirely at scaffold time — no resolve-toolchain runtime
# wiring, no workflow twin.
#
# NOT wired into init-workspace.sh yet (that is #1208). Invoke it directly:
#   render_workflow_model <workspace_dir> <gitflow|trunk>
#
# The `sync-main-to-dev.yml` removal is a COPY-EXCLUDE at rsync time in
# production (a trunk workspace never receives the file), mirrored here by
# deleting it from the copy. Every other change is an anchored in-place edit.
#
# Anchoring rules (verified by the driver + tests):
#   - `heads/dev\b`   : word-boundary so `development`/`devkit`/`devcontainer`
#                       are never touched, and `heads/development` cannot match.
#   - `ref: dev$` / ` from dev$` : end-anchored so only the exact branch
#                       literal / step-name suffix is rewritten.
set -euo pipefail

# ── render_workflow_model: gitflow (no-op) | trunk (anchored dev->main) ───────
# $1 = workspace dir (a scaffolded tree)   $2 = workflow model
render_workflow_model() {
    local ws="$1" model="$2"

    # gitflow is the default and a pure no-op: the committed template already IS
    # the gitflow shape, so rendering must change zero bytes.
    [[ "$model" == "trunk" ]] || return 0

    local wf="$ws/.github/workflows"

    # sync-main-to-dev.yml: production excludes it from the rsync copy (a trunk
    # workspace has no such file). Mirror by removing it from the copy.
    rm -f "$wf/sync-main-to-dev.yml"

    # prepare-release.yml — retarget the release base dev -> main (#590/#617
    # logic is base-agnostic; every dev token here is a plain branch literal).
    local pr="$wf/prepare-release.yml"
    # checkout `ref: dev` (validate + prepare jobs)
    sed -i -E 's|^([[:space:]]*ref:) dev$|\1 main|' "$pr"
    # git/ref/heads/dev  AND  refs/heads/dev  (word-boundary anchored)
    sed -i -E 's|heads/dev\b|heads/main|g' "$pr"
    # step name "... from dev"
    sed -i -E 's| from dev$| from main|' "$pr"

    # ci.yml — drop `- dev` from the PR branch filter; retarget the commit-gate
    # TRUNK anchor used to exclude already-merged history on release PRs.
    local ci="$wf/ci.yml"
    sed -i '/^      - dev$/d' "$ci"
    sed -i 's|TRUNK="dev"|TRUNK="main"|' "$ci"

    # codeql.yml — drop `- dev` from the PR branch filter (push is main-only).
    sed -i '/^      - dev$/d' "$wf/codeql.yml"

    # sync-issues.yml — default target branch + `|| 'dev'` fallbacks dev -> main.
    local si="$wf/sync-issues.yml"
    sed -i -E "s|^([[:space:]]*default:) 'dev'\$|\1 'main'|" "$si"
    sed -i "s#|| 'dev'#|| 'main'#g" "$si"

    # branch-naming SKILL.md — base-branch default dev -> main. (Single-quoted
    # sed so the Markdown backticks stay literal; the `chore/sync-main-to-dev`
    # example on another line is untouched.)
    local skill="$ws/.claude/skills/branch-naming/SKILL.md"
    # shellcheck disable=SC2016  # literal Markdown backticks, not command substitution
    sed -i 's|fall back to `dev`|fall back to `main`|' "$skill"
    # shellcheck disable=SC2016  # literal Markdown backticks, not command substitution
    sed -i 's|use `dev` as|use `main` as|' "$skill"

    # .pre-commit-config.yaml — drop the `(?!dev$)` protect-clause + its comments.
    local pc="$ws/.pre-commit-config.yaml"
    sed -i 's|# Allows main, dev, and|# Allows main and|' "$pc"
    sed -i 's|main/dev are not protected|main is not protected|' "$pc"
    sed -i 's|(?!dev$)||' "$pc"
}

# Allow sourcing (tests) or direct CLI use.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    render_workflow_model "$@"
fi
