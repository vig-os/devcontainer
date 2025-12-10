#!/bin/bash
# Initialize workspace by copying template files
# Usage: init-workspace [--force]

set -euo pipefail

TEMPLATE_DIR="/root/assets/workspace"
WORKSPACE_DIR="/workspace"
FORCE=false

# Check if running in interactive mode
if [[ ! -t 0 ]]; then
    echo "Error: This script requires an interactive terminal." >&2
    echo "" >&2
    echo "Please run with the -it flags:" >&2
    echo "  podman run -it --rm -v \"./:/workspace\" ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh" >&2
    echo "  docker run -it --rm -v \"./:/workspace\" ghcr.io/vig-os/devcontainer:latest /root/assets/init-workspace.sh" >&2
    exit 1
fi

# Parse arguments
for arg in "$@"; do
    case "$arg" in
        --force)
            FORCE=true
            ;;
        *)
            echo "Unknown option: $arg" >&2
            echo "Usage: init-workspace [--force]" >&2
            exit 1
            ;;
    esac
done

# Check if template directory exists
if [[ ! -d "$TEMPLATE_DIR" ]]; then
    echo "Error: Template directory not found at $TEMPLATE_DIR" >&2
    exit 1
fi

# Function to check if workspace is effectively empty
is_workspace_empty() {
    # Count non-hidden files and directories (excluding .git)
    local count
    count=$(find "$WORKSPACE_DIR" -mindepth 1 -maxdepth 1 \
        ! -name '.git' ! -name '.*' 2>/dev/null | wc -l)

    # Also check for .git only (common case)
    if [[ -d "$WORKSPACE_DIR/.git" ]] && [[ $count -eq 0 ]]; then
        return 0  # Empty except for .git
    fi

    [[ $count -eq 0 ]]
}

# Check if workspace has content
if ! is_workspace_empty && [[ "$FORCE" != "true" ]]; then
    echo "Error: Workspace is not empty. Use --force to overwrite existing files." >&2
    echo "Current workspace contents:" >&2
    find "$WORKSPACE_DIR" -maxdepth 1 -mindepth 1 -exec ls -ld {} \; 2>/dev/null | head -10 >&2
    exit 1
fi

# Ask user for short project name
read -rp "Enter a short name for your project (letters/numbers only, e.g. my_proj): " SHORT_NAME
if [[ -z "$SHORT_NAME" ]]; then
    echo "Error: Short project name is required" >&2
    exit 1
fi

# Sanitize: replace hyphens and spaces with underscore; lowercase; remove other special chars
SHORT_NAME=$(echo "$SHORT_NAME" | tr '[:upper:]' '[:lower:]' | sed 's/[ -]/_/g' | sed 's/[^a-z0-9_]/_/g')
echo "Project short name set to: $SHORT_NAME"

# Ask user for organization name
read -rp "Enter the name of your organization, e.g. 'vigOS': " ORG_NAME
if [[ -z "$ORG_NAME" ]]; then
    echo "Error: Organization name is required" >&2
    exit 1
fi
echo "Organization name set to: $ORG_NAME"

# Warn if forcing (prompt user) - show which files would be overwritten
if [[ "$FORCE" == "true" ]]; then
    echo ""
    echo "Checking for files that would be overwritten..."
    
    # Find files that exist in both template and workspace
    CONFLICTS=()
    while IFS= read -r -d '' template_file; do
        # Get relative path from template directory
        rel_path="${template_file#$TEMPLATE_DIR/}"
        workspace_file="$WORKSPACE_DIR/$rel_path"
        
        if [[ -e "$workspace_file" ]]; then
            CONFLICTS+=("$rel_path")
        fi
    done < <(find "$TEMPLATE_DIR" -type f ! -path "*/.git/*" -print0)
    
    if [[ ${#CONFLICTS[@]} -eq 0 ]]; then
        echo "No existing files would be overwritten."
    else
        echo ""
        echo "The following ${#CONFLICTS[@]} file(s) will be OVERWRITTEN:"
        echo "─────────────────────────────────────────────────────────────"
        for conflict in "${CONFLICTS[@]}"; do
            echo "  ⚠  $conflict"
        done
        echo "─────────────────────────────────────────────────────────────"
        echo ""
    fi
    
    read -rp "Continue with --force? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Copy template contents to workspace
echo "Initializing workspace from template..."
echo "Copying files from $TEMPLATE_DIR to $WORKSPACE_DIR..."

# Use rsync if available, otherwise cp
if command -v rsync &> /dev/null; then
    rsync -av --exclude='.git' "$TEMPLATE_DIR/" "$WORKSPACE_DIR/"
else
    # Fallback to cp with proper handling
    cp -r "$TEMPLATE_DIR"/* "$WORKSPACE_DIR/" 2>/dev/null || true
    cp -r "$TEMPLATE_DIR"/.[!.]* "$WORKSPACE_DIR/" 2>/dev/null || true
fi

# Replace placeholders in all files (recursively, excluding .git)
echo "Replacing placeholders in files..."
# Use a more efficient approach: only process files that contain placeholders
# and combine both replacements in a single sed pass
find "$WORKSPACE_DIR" -type f ! -path "*/.git/*" -print0 | while IFS= read -r -d '' file; do
    if grep -q 'devcontainer\|vigOS' "$file" 2>/dev/null; then
        sed -i "s/devcontainer/${SHORT_NAME}/g; s/vigOS/${ORG_NAME}/g" "$file"
    fi
done

# Restore executable permissions on shell scripts and hooks (must be after sed -i)
echo "Setting executable permissions on shell scripts and hooks..."
find "$WORKSPACE_DIR" -type f -name "*.sh" -exec chmod +x {} \;
find "$WORKSPACE_DIR/.githooks" -type f -exec chmod +x {} \; 2>/dev/null || true


echo "Workspace initialized successfully!"
echo ""
echo "You can now start developing in your workspace."
