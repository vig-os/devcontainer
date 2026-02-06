#!/usr/bin/env bash
# Prepare release branch for testing and validation
# Usage: ./scripts/prepare-release.sh X.Y.Z [--dry-run]
#
# This script prepares a release branch for testing and validation:
# - Creates release branch from dev
# - Validates semantic version format
# - Prepares CHANGELOG structure (WITHOUT setting release date)
# - Creates placeholder QMS baseline
# - Creates standardized commit and draft PR to main
#
# After testing/validation, run finalize-release.sh to complete the release.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
Prepare Release Branch Script

USAGE:
    ./scripts/prepare-release.sh X.Y.Z [--dry-run]

ARGUMENTS:
    X.Y.Z        Semantic version (e.g., 0.3.0, 1.0.0)

OPTIONS:
    --dry-run    Show what would be done without executing

EXAMPLES:
    ./scripts/prepare-release.sh 0.3.0
    ./scripts/prepare-release.sh 1.0.0 --dry-run

NOTE:
    This prepares the release but does NOT set the release date.
    After testing, run: ./scripts/finalize-release.sh X.Y.Z
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

info "Preparing release branch for version $VERSION"
info "NOTE: Release date will be set when finalized"

# Work in current directory (allow tests to pass in their own repos)
# If running from scripts/, we'll still have correct paths via $SCRIPT_DIR

# Validation checks
info "Running validation checks..."

# Check if on dev branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "dev" ]; then
    err "Must be on dev branch (currently on: $CURRENT_BRANCH)"
    echo "Run: git checkout dev"
    exit 1
fi

# Check for uncommitted changes
if ! git diff --quiet || ! git diff --cached --quiet; then
    err "Uncommitted changes detected"
    echo "Please commit or stash changes before creating release"
    git status --short
    exit 1
fi

# Check if branch is up to date (if origin exists)
if git remote | grep -q "^origin$"; then
    git fetch origin dev 2>/dev/null || warn "Could not fetch from origin"
    if git rev-parse origin/dev >/dev/null 2>&1; then
        LOCAL=$(git rev-parse dev)
        REMOTE=$(git rev-parse origin/dev)
        if [ "$LOCAL" != "$REMOTE" ]; then
            err "Local dev branch is not up to date with origin/dev"
            echo "Run: git pull origin dev"
            exit 1
        fi
    fi
else
    info "No origin remote configured (OK for testing)"
fi

# Check if release branch already exists
if git show-ref --verify --quiet "refs/heads/$RELEASE_BRANCH"; then
    err "Release branch already exists locally: $RELEASE_BRANCH"
    exit 1
fi

if git remote | grep -q "^origin$"; then
    if git show-ref --verify --quiet "refs/remotes/origin/$RELEASE_BRANCH"; then
        err "Release branch already exists on remote: $RELEASE_BRANCH"
        exit 1
    fi
fi

# Check for Unreleased entries in CHANGELOG
if ! grep -q "## Unreleased" CHANGELOG.md; then
    err "No Unreleased section found in CHANGELOG.md"
    exit 1
fi

# Check if Unreleased section has content
if ! sed -n '/## Unreleased/,/## \[/p' CHANGELOG.md | grep -q "^-"; then
    warn "Unreleased section appears empty in CHANGELOG.md"
    echo "Continue anyway? (y/n)"
    read -r response
    if [ "$response" != "y" ]; then
        echo "Aborted"
        exit 1
    fi
fi

success "All validation checks passed"

if [ "$DRY_RUN" = true ]; then
    info "DRY RUN MODE - No changes will be made"
    echo ""
    echo "Would perform the following actions:"
    echo "  1. Create branch: $RELEASE_BRANCH"
    echo "  2. Prepare CHANGELOG.md (Unreleased → $VERSION, NO date yet)"
    echo "  3. Create placeholder QMS baseline"
    echo "  4. Commit changes"
    echo "  5. Push branch to origin"
    echo "  6. Create draft PR to main"
    echo ""
    echo "After testing, run: ./scripts/finalize-release.sh $VERSION"
    exit 0
fi

# Create release branch
info "Creating release branch: $RELEASE_BRANCH"
git checkout -b "$RELEASE_BRANCH"

# Prepare CHANGELOG (without release date, clean up empty sections)
info "Preparing CHANGELOG.md structure..."
if ! python3 "$SCRIPT_DIR/prepare-changelog.py" "$VERSION" CHANGELOG.md; then
    err "Failed to prepare CHANGELOG"
    exit 1
fi

# Skip documentation regeneration - will be done at finalize
info "Skipping documentation generation (will be done at finalization)"

# Create placeholder QMS baseline
info "Creating placeholder QMS baseline..."
mkdir -p docs/baselines

cat > "docs/baselines/baseline-v$VERSION.md" <<EOF
# Release Baseline v$VERSION

**Status:** DRAFT - Release in preparation
**Release Date:** TBD (will be set by finalize-release.sh)
**Git Tag:** Not yet created
**Git SHA:** $(git rev-parse HEAD)

## Configuration Identification

- Version: $VERSION
- Base Branch: dev
- Release Branch: $RELEASE_BRANCH

## Status

This release is in preparation and testing phase.

## Next Steps

1. Test the release thoroughly
2. Fix any issues found
3. When ready, run: ./scripts/finalize-release.sh $VERSION

The finalize script will:
- Set the actual release date
- Generate complete QMS baseline documentation
- Update all version references
- Create git tag
- Trigger CI/CD pipeline
EOF

# Create commit
info "Creating release preparation commit..."
git add CHANGELOG.md 2>/dev/null || true
git add docs/baselines/ 2>/dev/null || true

git commit -m "$(cat <<EOF
chore: prepare release $VERSION

- Prepare CHANGELOG.md structure for version $VERSION
- Create placeholder QMS baseline
- Release date TBD (set during finalization)

Next: Test release, then run finalize-release.sh

Refs: #48
EOF
)"

success "Release branch prepared successfully"

# Push branch (if origin exists)
if git remote | grep -q "^origin$"; then
    info "Pushing release branch to origin..."
    git push -u origin "$RELEASE_BRANCH"
else
    info "No origin remote - skipping push (OK for testing)"
fi

# Create draft PR (if gh CLI available and origin exists)
if git remote | grep -q "^origin$" && command -v gh &> /dev/null; then
    info "Creating draft PR to main..."
    PR_BODY="## Release $VERSION

This PR prepares release $VERSION for merge to main.

### Release Date
$RELEASE_DATE

### Testing Checklist
- [ ] All tests pass (\`just test\`)
- [ ] Manual testing complete
- [ ] No critical bugs found
- [ ] Ready for release

### When Ready to Release
Run: \`./scripts/finalize-release.sh $VERSION\`

This will:
- Set release date in CHANGELOG
- Generate complete QMS baseline
- Update all documentation
- Create commit and push
- Tag will trigger CI/CD automatically

### Related
- Release automation: #48
"

    PR_URL=$(gh pr create \
        --base main \
        --head "$RELEASE_BRANCH" \
        --title "Release v$VERSION" \
        --body "$PR_BODY" \
        --draft)
    success "Draft PR created: $PR_URL"
else
    info "Skipping PR creation (no origin remote or gh CLI)"
fi

echo ""
success "Release branch created successfully!"
echo ""
echo "Next steps:"
echo "  1. Review changes: git log dev..$RELEASE_BRANCH"
echo "  2. Run tests: just test"
echo "  3. Review draft PR and mark as ready when tests pass"
echo "  4. Merge PR to main"
echo "  5. Run: ./scripts/finalize-release.sh $VERSION"
