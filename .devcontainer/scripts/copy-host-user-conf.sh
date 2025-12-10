#!/usr/bin/env bash
set -euo pipefail

# Check if we're running inside the dev container
if [ "${IN_CONTAINER:-}" = "true" ]; then
	echo "This script must be run outside the container"
	exit 1
fi

# CONF directory for storing user configuration
CONF_DIR="$(dirname "$0")/../.conf"
mkdir -p "$CONF_DIR"

# Copy SSH public key from host to container
HOST_SSH_PUBKEY="$HOME/.ssh/id_ed25519_github.pub"
if [ -f "$HOST_SSH_PUBKEY" ]; then
	cp "$HOST_SSH_PUBKEY" "$CONF_DIR/id_ed25519_github.pub"
	echo "Copied SSH public key from $HOST_SSH_PUBKEY to $CONF_DIR"
else
	echo "Warning: No SSH public key found at $HOST_SSH_PUBKEY"
	echo "Git commit signing may not work without this file"
fi

# Copy allowed-signers file from host to container
HOST_ALLOWED_SIGNERS_FILE="$HOME/.config/git/allowed-signers"
if [ -f "$HOST_ALLOWED_SIGNERS_FILE" ]; then
	cp "$HOST_ALLOWED_SIGNERS_FILE" "$CONF_DIR/allowed-signers"
	echo "Copied allowed-signers file from $HOST_ALLOWED_SIGNERS_FILE to $CONF_DIR"
else
	echo "Warning: No allowed-signers file found at $HOST_ALLOWED_SIGNERS_FILE"
	echo "Git signature verification may not work without this file"
fi

# Generate a valid .gitconfig from effective config in current directory
GITCONFIG_OUT="$CONF_DIR/.gitconfig"
GITCONFIG_GLOBAL="$CONF_DIR/.gitconfig.global"
git config --list --global --include >"$GITCONFIG_GLOBAL"

# Parse key-value pairs and reconstruct .gitconfig with correct section/subsection syntax
awk -F= '
  function print_section(section, subsection) {
    if (section != "") {
      if (subsection != "") {
        print "[" section " \"" subsection "\"]"
      } else {
        print "[" section "]"
      }
    }
  }
  {
    key = $1
    val = $2
    if (key ~ /^includeif\./) next
    split(key, arr, ".")
    section = arr[1]
    # Handle subsection (e.g., filter.lfs.clean, gpg.ssh.allowedsignersfile, diff.lfs.textconv)
    # Any 3+ part key (section.subsection.key) becomes [section "subsection"] with key = value
    if (length(arr) > 2) {
      subsection = arr[2]
      subkey = arr[3]
      # Handle all subsection cases generically
      if (section != last_section || subsection != last_subsection) {
        if (last_section != "") print ""
        print_section(section, subsection)
        last_section = section
        last_subsection = subsection
      }
      print "    " subkey " = " val
      next
    }
    # Handle normal section.key
    subsection = ""
    if (section != last_section || subsection != last_subsection) {
      if (last_section != "") print ""
      print_section(section, subsection)
      last_section = section
      last_subsection = subsection
    }
    # Remove section. from key
    subkey = substr(key, length(section) + 2)
    print "    " subkey " = " val
  }
' "$GITCONFIG_GLOBAL" >"$GITCONFIG_OUT"

echo "Generated valid .gitconfig at $GITCONFIG_OUT from effective config in current directory"

# Copy GitHub CLI config from host to container (for settings, aliases, etc.)
HOST_GITHUB_CLI_CONFIG_DIR="$HOME/.config/gh"
if [ -d "$HOST_GITHUB_CLI_CONFIG_DIR" ]; then
	mkdir -p "$CONF_DIR/gh"
	cp -r "$HOST_GITHUB_CLI_CONFIG_DIR"/* "$CONF_DIR/gh/" 2>/dev/null || true
	echo "Copied GitHub CLI config from $HOST_GITHUB_CLI_CONFIG_DIR to $CONF_DIR/gh"
else
	echo "Warning: No GitHub CLI config directory found at $HOST_GITHUB_CLI_CONFIG_DIR"
	echo "GitHub CLI settings and aliases may not be available in the container"
fi

# Export GitHub CLI token from keyring to container
# This happens every time we connect to ensure the token is fresh
GH_TOKEN_FILE="$CONF_DIR/.gh_token"
if command -v gh >/dev/null 2>&1; then
	if gh auth status >/dev/null 2>&1; then
		# Export token from keyring
		gh auth token >"$GH_TOKEN_FILE" 2>/dev/null || {
			echo "Warning: Failed to export GitHub CLI token from keyring"
			echo "GitHub CLI authentication may not work in the container"
		}
		if [ -f "$GH_TOKEN_FILE" ] && [ -s "$GH_TOKEN_FILE" ]; then
			echo "Exported GitHub CLI token to $GH_TOKEN_FILE"
		fi
	else
		echo "Warning: GitHub CLI is not authenticated on host"
		echo "Run 'gh auth login' on the host to enable GitHub CLI in the container"
	fi
else
	echo "Warning: GitHub CLI (gh) is not installed on host"
	echo "GitHub CLI authentication will not be available in the container"
fi
