#!/usr/bin/env bash
# Finalize a release: set date, create tag
# Usage: ./scripts/finalize-release.sh X.Y.Z [--dry-run]
#
# This script finalizes a release that was prepared by prepare-release.sh:
# - Verifies release branch and PR status
# - Sets the actual release date in CHANGELOG
# - Creates annotated git tag
# - Triggers sync-issues workflow for PR documentation
#
# Prerequisites:
#   - Must be on release/X.Y.Z branch (created by prepare-release.sh)
#   - CHANGELOG must have ## [X.Y.Z] - TBD entry
#   - CI checks should have passed
#   - PR should be reviewed and approved

set -euo pipefail

# Colors for output
if [ -t 1 ]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED='' GREEN='' YELLOW='' BLUE='' NC=''
fi

err() { echo -e "${RED}error${NC}: $1" >&2; }
info() { echo -e "${BLUE}info${NC}: $1"; }
warn() { echo -e "${YELLOW}warn${NC}: $1"; }
success() { echo -e "${GREEN}success${NC}: $1"; }

usage() {
    cat <<'EOF'
Finalize Release Script

USAGE:
    ./scripts/finalize-release.sh X.Y.Z [--dry-run]

ARGUMENTS:
    X.Y.Z        Semantic version (e.g., 0.3.0, 1.0.0)

OPTIONS:
    --dry-run    Show what would be done without executing

EXAMPLES:
    ./scripts/finalize-release.sh 0.3.0
    ./scripts/finalize-release.sh 1.0.0 --dry-run

PREREQUISITES:
    - Must be on release/X.Y.Z branch (created by prepare-release.sh)
    - CHANGELOG must have ## [X.Y.Z] - TBD entry
    - CI checks should have passed
    - PR should be reviewed and approved
    - GitHub CLI (gh) and origin remote must be configured
EOF
}

# Parse arguments
VERSION=""
DRY_RUN=false

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        -*)
            err "Unknown option: $1"
            usage
            exit 1
            ;;
        *)
            if [ -z "$VERSION" ]; then
                VERSION="$1"
            else
                err "Too many arguments"
                usage
                exit 1
            fi
            shift
            ;;
    esac
done

if [ -z "$VERSION" ]; then
    err "Version argument required"
    usage
    exit 1
fi

# Validate semantic version format
if ! echo "$VERSION" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+$'; then
    err "Invalid version format '$VERSION'"
    echo "Version must follow semantic versioning format: MAJOR.MINOR.PATCH (e.g., 1.2.3)"
    exit 1
fi

RELEASE_BRANCH="release/$VERSION"
RELEASE_DATE="$(date +%Y-%m-%d)"
TAG_NAME="v$VERSION"

info "Finalizing release $VERSION"

# ═══════════════════════════════════════════════════════════════════════════════
# Validation Phase
# ═══════════════════════════════════════════════════════════════════════════════

info "Running validation checks..."

# Check if on correct release branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "$RELEASE_BRANCH" ]; then
    err "Must be on $RELEASE_BRANCH branch (currently on: $CURRENT_BRANCH)"
    echo "Run: git checkout $RELEASE_BRANCH"
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    err "Uncommitted changes detected"
    echo "Please commit or stash changes before finalizing release"
    git status --short
    exit 1
fi

# Verify CHANGELOG has the TBD entry for this version
if ! grep -q "## \[$VERSION\] - TBD" CHANGELOG.md; then
    err "CHANGELOG.md does not contain '## [$VERSION] - TBD'"
    echo "Was prepare-release.sh run for version $VERSION?"
    exit 1
fi

# Check if tag already exists
if git tag -l "$TAG_NAME" | grep -q "^$TAG_NAME$"; then
    err "Tag $TAG_NAME already exists"
    echo "Delete it first if re-releasing: git tag -d $TAG_NAME && git push origin :refs/tags/$TAG_NAME"
    exit 1
fi

# ── PR and CI checks (required for production releases) ──

HAS_REMOTE=false
HAS_GH=false
PR_NUMBER=""

if git remote | grep -q "^origin$"; then
    HAS_REMOTE=true
fi

if command -v gh &> /dev/null; then
    HAS_GH=true
fi

# In dry-run mode, skip GitHub validation but use placeholder values
if [ "$DRY_RUN" = true ]; then
    info "Dry-run mode: skipping GitHub/PR validation"
    PR_NUMBER="999"  # Placeholder for dry-run output
else
    # PR validation is mandatory for actual releases
    if [ "$HAS_REMOTE" = false ]; then
        err "No origin remote configured"
        echo "Production releases require a GitHub remote"
        exit 1
    fi

    if [ "$HAS_GH" = false ]; then
        err "GitHub CLI (gh) not installed"
        echo "Production releases require gh CLI. Install: https://cli.github.com"
        exit 1
    fi

    info "Checking PR and CI status..."

    # Find the PR for this release branch
    PR_JSON=$(gh pr list --head "$RELEASE_BRANCH" --base main --json number,isDraft,reviewDecision --limit 1 2>/dev/null || echo "[]")
    PR_COUNT=$(echo "$PR_JSON" | uv run python -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")

    if [ "$PR_COUNT" != "1" ]; then
        if [ "$PR_COUNT" = "0" ]; then
            err "No PR found from $RELEASE_BRANCH to main"
            echo "Production releases must have a PR. Create one first:"
            echo "  gh pr create --base main --head $RELEASE_BRANCH"
        else
            err "Multiple PRs found from $RELEASE_BRANCH to main (found: $PR_COUNT)"
            echo "There must be exactly one open PR. Review existing PRs:"
            echo "  gh pr list --head $RELEASE_BRANCH --base main"
        fi
        exit 1
    fi

    PR_NUMBER=$(echo "$PR_JSON" | uv run python -c "import sys,json; print(json.load(sys.stdin)[0]['number'])" 2>/dev/null || echo "")
    IS_DRAFT=$(echo "$PR_JSON" | uv run python -c "import sys,json; print(json.load(sys.stdin)[0]['isDraft'])" 2>/dev/null || echo "")
    REVIEW_DECISION=$(echo "$PR_JSON" | uv run python -c "import sys,json; print(json.load(sys.stdin)[0]['reviewDecision'])" 2>/dev/null || echo "")

    info "Found PR #$PR_NUMBER"

    # Check draft status
    if [ "$IS_DRAFT" = "True" ]; then
        warn "PR #$PR_NUMBER is still a draft"
        warn "Consider marking it ready: gh pr ready $PR_NUMBER"
    else
        success "PR #$PR_NUMBER is ready for review"
    fi

    # Check review status
    if [ "$REVIEW_DECISION" = "APPROVED" ]; then
        success "PR #$PR_NUMBER has been approved"
    else
        warn "PR #$PR_NUMBER review status: ${REVIEW_DECISION:-none}"
        warn "Consider getting approval before finalizing"
    fi

    # Check CI status
    CI_STATUS=$(gh pr checks "$PR_NUMBER" --json bucket --jq '.[].bucket' 2>/dev/null || echo "")
    if echo "$CI_STATUS" | grep -q "fail"; then
        warn "Some CI checks have failed on PR #$PR_NUMBER"
        warn "Review: gh pr checks $PR_NUMBER"
    elif [ -n "$CI_STATUS" ]; then
        success "CI checks status verified"
    fi
fi

success "All validation checks passed"

# ═══════════════════════════════════════════════════════════════════════════════
# Dry-run Mode
# ═══════════════════════════════════════════════════════════════════════════════

if [ "$DRY_RUN" = true ]; then
    info "DRY RUN MODE - No changes will be made"
    echo ""
    echo "Would perform the following actions:"
    echo ""
    echo "1. Set release date in CHANGELOG.md:"
    echo "   uv run python scripts/prepare-changelog.py finalize \"$VERSION\" \"$RELEASE_DATE\""
    echo ""
    echo "2. Commit finalization changes:"
    echo "   git add CHANGELOG.md"
    echo "   git commit -m \"chore: finalize release $VERSION"
    echo ""
    echo "Set release date to $RELEASE_DATE in CHANGELOG.md"
    echo ""
    echo "Refs: #$PR_NUMBER\""
    echo ""
    echo "3. Push release branch:"
    echo "   git push origin \"$RELEASE_BRANCH\""
    echo ""
    echo "4. Trigger sync-issues workflow:"
    echo "   gh workflow run sync-issues.yml -f \"target-branch=$RELEASE_BRANCH\""
    echo "   (wait for completion and pull changes)"
    echo ""
    echo "5. Create annotated tag:"
    echo "   git tag -s \"$TAG_NAME\" -m \"Release $VERSION\""
    echo ""
    echo "6. Push tag:"
    echo "   git push origin \"$TAG_NAME\""
    echo ""
    echo "7. Verify release workflow triggers"
    echo ""
    echo "Current state:"
    echo "  Branch: $CURRENT_BRANCH"
    echo "  Version: $VERSION"
    echo "  Release date: $RELEASE_DATE"
    echo "  Tag: $TAG_NAME"
    if [ -n "$PR_NUMBER" ]; then
        echo "  PR: #$PR_NUMBER"
    fi
    exit 0
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Action Phase
# ═══════════════════════════════════════════════════════════════════════════════

# Step 1: Set release date in CHANGELOG
info "Setting release date in CHANGELOG.md..."
uv run python scripts/prepare-changelog.py finalize "$VERSION" "$RELEASE_DATE" || {
    err "Failed to set release date in CHANGELOG.md"
    exit 1
}
success "Set release date: $RELEASE_DATE"

# Step 2: Commit finalization changes
info "Creating finalization commit..."
git add CHANGELOG.md 2>/dev/null || true

# Use PR number (validated above)
git commit -m "$(cat <<EOF
chore: finalize release $VERSION

Set release date to $RELEASE_DATE in CHANGELOG.md

Refs: #$PR_NUMBER
EOF
)"

success "Committed finalization changes"

# Step 3: Push release branch
info "Pushing release branch to origin..."
git push origin "$RELEASE_BRANCH"
success "Pushed release branch"

# Step 4: Trigger sync-issues workflow and wait for completion
info "Triggering sync-issues workflow..."
if gh workflow run sync-issues.yml -f "target-branch=$RELEASE_BRANCH" 2>/dev/null; then
    success "Triggered sync-issues workflow"

    # Wait for workflow to start and complete
    info "Waiting for sync-issues to complete (timeout: 120s)..."
    TIMEOUT=120
    ELAPSED=0
    INTERVAL=10

    sleep 5  # Give workflow time to register
    ELAPSED=5

    while [ $ELAPSED -lt $TIMEOUT ]; do
        # Get the most recent run of sync-issues on our branch
        RUN_STATUS=$(gh run list --workflow sync-issues.yml --limit 1 --json status,conclusion --jq '.[0].status' 2>/dev/null || echo "unknown")

        if [ "$RUN_STATUS" = "completed" ]; then
            RUN_CONCLUSION=$(gh run list --workflow sync-issues.yml --limit 1 --json conclusion --jq '.[0].conclusion' 2>/dev/null || echo "unknown")
            if [ "$RUN_CONCLUSION" = "success" ]; then
                success "sync-issues workflow completed successfully"
            else
                warn "sync-issues workflow completed with status: $RUN_CONCLUSION"
            fi
            break
        fi

        sleep "$INTERVAL"
        ELAPSED=$((ELAPSED + INTERVAL))
        info "Still waiting... (${ELAPSED}s / ${TIMEOUT}s)"
    done

    if [ $ELAPSED -ge $TIMEOUT ]; then
        warn "Timed out waiting for sync-issues workflow"
        warn "Check status: gh run list --workflow sync-issues.yml"
    fi

    # Pull any changes from the workflow (PR docs)
    info "Pulling changes from sync-issues workflow..."
    if git pull origin "$RELEASE_BRANCH" --no-edit 2>/dev/null; then
        # Check if new files arrived
        if ! git diff --quiet HEAD~1 2>/dev/null; then
            info "New PR documentation files detected"
        fi
    fi
else
    err "Failed to trigger sync-issues workflow"
    echo "Check GitHub Actions access."
    exit 1
fi

# Step 5: Create signed annotated tag
info "Creating signed annotated tag: $TAG_NAME"
git tag -s "$TAG_NAME" -m "Release $VERSION"
success "Created tag: $TAG_NAME"

# Step 6: Push tag
info "Pushing tag to origin..."
git push origin "$TAG_NAME"
success "Pushed tag: $TAG_NAME"

# Step 7: Verify publish workflow triggered
info "Waiting for publish workflow to trigger (timeout: 60s)..."
PUBLISH_TIMEOUT=60
PUBLISH_ELAPSED=0
PUBLISH_INTERVAL=10

sleep 5  # Give workflow time to register
PUBLISH_ELAPSED=5

PUBLISH_TRIGGERED=false
while [ $PUBLISH_ELAPSED -lt $PUBLISH_TIMEOUT ]; do
    # Check for recent release workflow runs triggered by tag push
    RECENT_RUN=$(gh run list --workflow release.yml --limit 5 --json event,status,headBranch --jq ".[] | select(.event == \"push\" or .event == \"workflow_dispatch\")" 2>/dev/null || echo "")

    if [ -n "$RECENT_RUN" ]; then
        success "Release workflow triggered successfully"
        info "Monitor progress: gh run list --workflow release.yml"
        PUBLISH_TRIGGERED=true
        break
    fi

    sleep "$PUBLISH_INTERVAL"
    PUBLISH_ELAPSED=$((PUBLISH_ELAPSED + PUBLISH_INTERVAL))
    info "Still waiting for workflow... (${PUBLISH_ELAPSED}s / ${PUBLISH_TIMEOUT}s)"
done

if [ "$PUBLISH_TRIGGERED" = false ]; then
    warn "Timed out waiting for release workflow to trigger"
    warn "Verify manually: gh run list --workflow release.yml"
    warn "The workflow should start automatically from the tag push"
fi

# ═══════════════════════════════════════════════════════════════════════════════
# Summary
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
success "Release $VERSION finalized successfully!"
echo ""
echo "Next steps:"
if [ -n "$PR_NUMBER" ]; then
    echo "  1. Merge PR #$PR_NUMBER: https://github.com/vig-os/devcontainer/pull/$PR_NUMBER"
else
    echo "  1. Merge the release PR to main"
fi
echo "  2. Tag $TAG_NAME will trigger release workflow automatically"
echo "  3. Monitor release: gh run list --workflow release.yml"
echo ""
echo "After merge to main:"
echo "  4. Merge main back to dev: git checkout dev && git merge main && git push origin dev"
echo "  5. Reset CHANGELOG: just reset-changelog"
