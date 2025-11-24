#!/usr/bin/env bash
# Restore template folder from backup
# Usage: restore_template.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

TEMPLATE_BACKUP=".template.backup"

if [ -d "$TEMPLATE_BACKUP" ]; then
	echo "Restoring template folder from backup..."
	if ! { rm -rf template && mv "$TEMPLATE_BACKUP" template; }; then
		echo "⚠️  Failed to restore template"
		exit 1
	fi
	echo "✓ Restored template folder"
else
	echo "⚠️  No backup found at $TEMPLATE_BACKUP, skipping restore"
fi
