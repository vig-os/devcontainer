#!/usr/bin/env bash
# Backup template folder and replace {{IMAGE_TAG}} with version
# Usage: backup_template.sh <version>

set -e

VERSION="${1:-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

TEMPLATE_BACKUP=".template.backup"

if [ -d template ]; then
	echo "Backing up template folder..."
	cp -r template "$TEMPLATE_BACKUP" || { echo "❌ Failed to backup template"; exit 1; }
	echo "Replacing {{IMAGE_TAG}} with $VERSION in template files..."
	find template -type f -exec sed -i.tmp "s|{{IMAGE_TAG}}|$VERSION|g" {} \; 2>/dev/null || true
	find template -name "*.tmp" -delete 2>/dev/null || true
else
	TEMPLATE_BACKUP=""
fi
