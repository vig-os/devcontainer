#!/bin/bash
# Sync workspace templates from repo root to assets/workspace/
#
# This script copies Cursor rules/commands, GitHub templates, and supporting
# files from the repo root into assets/workspace/, applying generalizations
# to make them suitable for downstream projects.
#
# Ground truth lives in repo root (where files are active/tested).
# Output in assets/workspace/ is generated and should not be manually edited.

set -euo pipefail

# Colors for output
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_DEST="$REPO_ROOT/assets/workspace"

echo -e "${BLUE}Syncing workspace templates from repo root...${NC}"
echo ""

# Check for untracked files in source directories
# Warns but does not fail - developer decides whether to stage or ignore
check_untracked_files() {
    local dir="$1"
    local untracked=()

    if [[ -d "$dir" ]]; then
        while IFS= read -r -d '' file; do
            if ! git ls-files --error-unmatch "$file" &>/dev/null; then
                untracked+=("$file")
            fi
        done < <(find "$dir" -type f -print0 2>/dev/null)
    fi

    if [[ ${#untracked[@]} -gt 0 ]]; then
        echo -e "${YELLOW}⚠ Untracked source files detected (not yet in git):${NC}"
        for file in "${untracked[@]}"; do
            echo -e "    ${file#"$REPO_ROOT"/}"
        done
        echo -e "  ${YELLOW}Run 'git add' on these files, then re-run sync.${NC}"
        echo ""
    fi
}

# Check all source directories for untracked files
check_untracked_files "$REPO_ROOT/.cursor"
check_untracked_files "$REPO_ROOT/.github/ISSUE_TEMPLATE"

# ===============================================================================
# DIRECTORY COPIES (rsync --delete)
# ===============================================================================

echo "Copying directories with rsync..."

# .cursor/rules/
mkdir -p "$WORKSPACE_DEST/.cursor/rules"
rsync -a --delete \
    "$REPO_ROOT/.cursor/rules/" \
    "$WORKSPACE_DEST/.cursor/rules/"
echo "  ✓ .cursor/rules/ → assets/workspace/.cursor/rules/"

# .cursor/commands/
mkdir -p "$WORKSPACE_DEST/.cursor/commands"
rsync -a --delete \
    "$REPO_ROOT/.cursor/commands/" \
    "$WORKSPACE_DEST/.cursor/commands/"
echo "  ✓ .cursor/commands/ → assets/workspace/.cursor/commands/"

# .github/ISSUE_TEMPLATE/
mkdir -p "$WORKSPACE_DEST/.github/ISSUE_TEMPLATE"
rsync -a --delete \
    "$REPO_ROOT/.github/ISSUE_TEMPLATE/" \
    "$WORKSPACE_DEST/.github/ISSUE_TEMPLATE/"
echo "  ✓ .github/ISSUE_TEMPLATE/ → assets/workspace/.github/ISSUE_TEMPLATE/"

echo ""

# ===============================================================================
# EXPLICIT FILE COPIES
# ===============================================================================

echo "Copying individual files..."

mkdir -p "$WORKSPACE_DEST/.github"

cp "$REPO_ROOT/.github/pull_request_template.md" \
   "$WORKSPACE_DEST/.github/pull_request_template.md"
echo "  ✓ .github/pull_request_template.md"

cp "$REPO_ROOT/.github/dependabot.yml" \
   "$WORKSPACE_DEST/.github/dependabot.yml"
echo "  ✓ .github/dependabot.yml"

cp "$REPO_ROOT/.pre-commit-config.yaml" \
   "$WORKSPACE_DEST/.pre-commit-config.yaml"
echo "  ✓ .pre-commit-config.yaml"

cp "$REPO_ROOT/.gitmessage" \
   "$WORKSPACE_DEST/.gitmessage"
echo "  ✓ .gitmessage"

echo ""

# ===============================================================================
# POST-COPY TRANSFORMATIONS
# ===============================================================================

echo "Applying transformations..."

# .cursor/rules/commit-messages.mdc - Remove line with doc link
# Use grep -v (inverse match) to remove the line
grep -v 'Full reference: \[docs/COMMIT_MESSAGE_STANDARD.md\]' \
    "$WORKSPACE_DEST/.cursor/rules/commit-messages.mdc" > "$WORKSPACE_DEST/.cursor/rules/commit-messages.mdc.tmp" && \
    mv "$WORKSPACE_DEST/.cursor/rules/commit-messages.mdc.tmp" "$WORKSPACE_DEST/.cursor/rules/commit-messages.mdc"
echo "  ✓ commit-messages.mdc: removed doc link"

# .cursor/commands/tdd.md - Generalize test recipes (cross-platform using Python)
uv run python "$REPO_ROOT/scripts/utils.py" sed 's|just test-image|just test|g' \
    "$WORKSPACE_DEST/.cursor/commands/tdd.md"
uv run python "$REPO_ROOT/scripts/utils.py" sed 's|just test-integration|just test-cov|g' \
    "$WORKSPACE_DEST/.cursor/commands/tdd.md"
uv run python "$REPO_ROOT/scripts/utils.py" sed 's|just test-utils|just test-pytest|g' \
    "$WORKSPACE_DEST/.cursor/commands/tdd.md"
echo "  ✓ tdd.md: generalized test recipes"

# .cursor/commands/verify.md - Generalize test recipes
uv run python "$REPO_ROOT/scripts/utils.py" sed 's|just test-image|just test|g' \
    "$WORKSPACE_DEST/.cursor/commands/verify.md"
echo "  ✓ verify.md: generalized test recipes"

# .github/dependabot.yml - Remove Docker ecosystem section and ensure single final newline
# Delete from "  # Docker" comment through the end of that section, remove trailing blank lines
awk '/^  # Docker/,/^$/{next} 1' "$WORKSPACE_DEST/.github/dependabot.yml" | \
    # Remove all trailing blank lines except keep one final newline
    sed -e :a -e '/^\n*$/{ $d; N; ba' -e '}' > "$WORKSPACE_DEST/.github/dependabot.yml.tmp" && \
    mv "$WORKSPACE_DEST/.github/dependabot.yml.tmp" "$WORKSPACE_DEST/.github/dependabot.yml"
echo "  ✓ dependabot.yml: removed Docker ecosystem"

# .pre-commit-config.yaml - Multiple transforms
# 1. Remove generate-docs hook block (from "id: generate-docs" through "pass_filenames: false" plus blank line)
awk '
    /id: generate-docs/ { skip=1 }
    skip && /pass_filenames: false/ { getline; next }
    !skip { print }
    skip && /^$/ { skip=0; next }
' "$WORKSPACE_DEST/.pre-commit-config.yaml" > "$WORKSPACE_DEST/.pre-commit-config.yaml.tmp" && \
    mv "$WORKSPACE_DEST/.pre-commit-config.yaml.tmp" "$WORKSPACE_DEST/.pre-commit-config.yaml"

# 2. Replace Bandit paths (cross-platform using Python)
uv run python "$REPO_ROOT/scripts/utils.py" sed \
    's|bandit -r packages/vig-utils/src/ scripts/ assets/workspace/|bandit -r src/|g' \
    "$WORKSPACE_DEST/.pre-commit-config.yaml"

# 3. Comment out validate-commit-msg args (replace with documented examples)
# Use awk to find the section and replace the args block
awk '
    /id: validate-commit-msg/ { in_section=1; print; next }
    in_section && /args: \[/ {
        in_args=1
        print "        # Optional: customize commit types, scopes, or refs-optional types via CLI arguments."
        print "        # By default, scopes are not enforced. Set --scopes to require specific scopes."
        print "        # Examples (choose one args line):"
        print "        #   args: [\"--types\", \"feat,fix,docs,chore\"]"
        print "        #   args: [\"--scopes\", \"api,cli,utils\"]"
        print "        #   args: [\"--refs-optional-types\", \"chore\"]"
        print "        #   args: [\"--types\", \"feat,fix,docs\", \"--scopes\", \"api,cli,utils\", \"--refs-optional-types\", \"chore\"]"
        next
    }
    in_args && /\]/ { in_args=0; next }
    in_args { next }
    in_section && /^$/ { in_section=0 }
    { print }
' "$WORKSPACE_DEST/.pre-commit-config.yaml" > "$WORKSPACE_DEST/.pre-commit-config.yaml.tmp" && \
    mv "$WORKSPACE_DEST/.pre-commit-config.yaml.tmp" "$WORKSPACE_DEST/.pre-commit-config.yaml"

echo "  ✓ .pre-commit-config.yaml: removed generate-docs, generalized Bandit paths, commented validate-commit-msg args"

echo ""
echo -e "${GREEN}✓ Workspace sync complete${NC}"
echo ""
echo "Generated files in assets/workspace/:"
echo "  - .cursor/rules/ (4 files)"
echo "  - .cursor/commands/ (15 files)"
echo "  - .github/ISSUE_TEMPLATE/ (3 files)"
echo "  - .github/pull_request_template.md"
echo "  - .github/dependabot.yml"
echo "  - .pre-commit-config.yaml"
echo "  - .gitmessage"
