#!/usr/bin/env bash
set -eo pipefail

# Check if gh CLI is available and authenticated
if ! command -v gh >/dev/null 2>&1; then
  echo "⚠️  GitHub CLI (gh) not found. Skipping sync."
  exit 0
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "⚠️  GitHub CLI not authenticated. Skipping sync."
  echo "   Run 'gh auth login' to enable GitHub data sync."
  exit 0
fi

# Check if jq is available
if ! command -v jq >/dev/null 2>&1; then
  echo "⚠️  jq not found. Skipping sync."
  exit 0
fi

# Create directories
mkdir -p .github_data/issues
mkdir -p .github_data/prs

echo "📥 Checking for new/updated issues..."
updated_count=0
gh issue list --state all --json number,updatedAt 2>/dev/null | jq -r '.[] | "\(.number)|\(.updatedAt)"' 2>/dev/null | while IFS='|' read -r num updated || [ -n "${num:-}" ]; do
  # Skip if num or updated is empty
  if [[ -z "${num:-}" ]] || [[ -z "${updated:-}" ]]; then
    continue
  fi

  file=".github_data/issues/${num}.md"

  # Fetch if file doesn't exist or check if we should update
  if [[ ! -f "$file" ]]; then
    echo "  ✓ Issue #${num} (new)"
    { gh issue view "$num" 2>/dev/null | sed 's/[[:space:]]*$//'; echo ""; } > "$file" || true
    ((updated_count++)) || true
  else
    # Get file modification time and compare (simple check: if file is old, update)
    file_time=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null || echo "0")
    github_time=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$updated" +%s 2>/dev/null || date -d "$updated" +%s 2>/dev/null || echo "0")

    if [[ "${github_time:-0}" -gt "${file_time:-0}" ]]; then
      echo "  ✓ Issue #${num} (updated)"
      { gh issue view "$num" 2>/dev/null | sed 's/[[:space:]]*$//'; echo ""; } > "$file" || true
      ((updated_count++)) || true
    fi
  fi
done

echo "📥 Checking for new/updated PRs..."
gh pr list --state all --json number,updatedAt 2>/dev/null | jq -r '.[] | "\(.number)|\(.updatedAt)"' 2>/dev/null | while IFS='|' read -r num updated || [ -n "${num:-}" ]; do
  # Skip if num or updated is empty
  if [[ -z "${num:-}" ]] || [[ -z "${updated:-}" ]]; then
    continue
  fi

  file=".github_data/prs/${num}.md"

  if [[ ! -f "$file" ]]; then
    echo "  ✓ PR #${num} (new)"
    { gh pr view "$num" 2>/dev/null | sed 's/[[:space:]]*$//'; echo ""; } > "$file" || true
    ((updated_count++)) || true
  else
    file_time=$(stat -f %m "$file" 2>/dev/null || stat -c %Y "$file" 2>/dev/null || echo "0")
    github_time=$(date -j -f "%Y-%m-%dT%H:%M:%SZ" "$updated" +%s 2>/dev/null || date -d "$updated" +%s 2>/dev/null || echo "0")

    if [[ "${github_time:-0}" -gt "${file_time:-0}" ]]; then
      echo "  ✓ PR #${num} (updated)"
      { gh pr view "$num" 2>/dev/null | sed 's/[[:space:]]*$//'; echo ""; } > "$file" || true
      ((updated_count++)) || true
    fi
  fi
done

echo "✅ Sync complete! (Only fetched new/updated items)"
