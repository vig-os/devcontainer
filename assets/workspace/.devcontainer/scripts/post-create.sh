#!/bin/bash
# Managed by vigOS devkit — regenerated on upgrade; local edits are lost.
# Customize in justfile.project. Bugs / missing tools: https://github.com/vig-os/devkit/issues

# Post-create script - runs once when container is created for the first time.
# This script is called from postCreateCommand in devcontainer.json.
#
# All one-time setup belongs here:
#   - Git repo init, config, hooks
#   - SSH key + allowed-signers placement
#   - GitHub CLI config + authentication
#   - Pre-commit hook installation
#   - Dependency sync (via just)

set -euo pipefail

echo "Running post-create setup..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PROJECT_ROOT="/workspace/{{SHORT_NAME}}"

if [ ! -d "$PROJECT_ROOT" ]; then
    echo "Error: Project directory $PROJECT_ROOT does not exist"
    exit 1
fi

# One-time setup: git repo, config, hooks, gh auth
"$SCRIPT_DIR/init-git.sh"
"$SCRIPT_DIR/setup-git-conf.sh"
"$SCRIPT_DIR/setup-gh-repo.sh"
"$SCRIPT_DIR/init-precommit.sh"

# Sync dependencies (fast if nothing changed from pre-built venv)
echo "Syncing dependencies..."
just --justfile "$PROJECT_ROOT/justfile" --working-directory "$PROJECT_ROOT" sync

# Set the venv prompt to the project name. Runs after `just sync` because the
# Nix image populates /root/assets/workspace/.venv at this stage rather than
# baking it at image-build time (the Debian image baked a venv whose prompt was
# the literal "template-project"). `uv` writes the prompt as the basename of the
# venv's parent dir, so rewrite the VIRTUAL_ENV_PROMPT assignment directly
# instead of substituting a fixed string. Guarded so a missing activate script
# never aborts post-create.
venv_activate="/root/assets/workspace/.venv/bin/activate"
if [ -f "$venv_activate" ]; then
    sed -i -E 's/^([[:space:]]*VIRTUAL_ENV_PROMPT=)"[^"]*"/\1"{{SHORT_NAME}}"/' "$venv_activate"
fi

# User specific setup
# Add your custom setup commands here to install any dependencies or tools needed for your project

echo "Post-create setup complete"

# --- vigOS resident credentials (vig-os/devcontainer#546, #823) ------------
# Export ~/.config/vigos/secrets/<NAME> files (mounted ro from the host) as
# env vars at shell startup. Same semantics as vigos.shell.secretsEnv.
if [ -d /root/.config/vigos/secrets ] && ! grep -q VIGOS_SECRETS_LOADED /root/.bashrc 2>/dev/null; then
  cat >> /root/.bashrc <<'VIGOS_SECRETS'
if [ -z "${VIGOS_SECRETS_LOADED:-}" ] && [ -d "$HOME/.config/vigos/secrets" ]; then
  for _vigos_secret in "$HOME/.config/vigos/secrets"/*; do
    [ -f "$_vigos_secret" ] || continue
    _vigos_name="$(basename "$_vigos_secret")"
    if printf '%s' "$_vigos_name" | grep -Eq '^[A-Z_][A-Z0-9_]*$'; then
      export "$_vigos_name=$(cat "$_vigos_secret")"
    fi
  done
  unset _vigos_secret _vigos_name
  export VIGOS_SECRETS_LOADED=1
fi
VIGOS_SECRETS
fi
