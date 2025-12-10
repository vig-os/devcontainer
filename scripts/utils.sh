#!/usr/bin/env bash
# scripts/utils.sh
# Cross-platform utility functions for build scripts

# Detect OS type
detect_os() {
    case "$(uname -s)" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        *)          echo "unknown";;
    esac
}

# Cross-platform sed in-place editing
# Usage: sed_inplace "s/pattern/replacement/g" file
sed_inplace() {
    local pattern="$1"
    local file="$2"

    if sed --version >/dev/null 2>&1; then
        # GNU sed (Linux)
        sed -i "$pattern" "$file"
    else
        # BSD sed (macOS)
        sed -i '' "$pattern" "$file"
    fi
}

# Cross-platform timeout command
# Usage: run_with_timeout <seconds> <command...>
run_with_timeout() {
    local timeout_sec="$1"
    shift

    if command -v timeout >/dev/null 2>&1; then
        # GNU coreutils (Linux)
        timeout "$timeout_sec" "$@"
    elif command -v gtimeout >/dev/null 2>&1; then
        # GNU coreutils via brew (macOS)
        gtimeout "$timeout_sec" "$@"
    else
        # Fallback using bash background process (macOS/BSD)
        ( "$@" ) &
        local pid=$!
        ( sleep "$timeout_sec" && kill -TERM $pid 2>/dev/null ) &
        local watcher=$!
        if wait $pid 2>/dev/null; then
            kill -TERM $watcher 2>/dev/null
            return 0
        else
            return 1
        fi
    fi
}

# Cross-platform date formatting (ISO 8601)
# Usage: get_iso_date
get_iso_date() {
    if date --version >/dev/null 2>&1; then
        # GNU date (Linux)
        date -u +"%Y-%m-%dT%H:%M:%SZ"
    else
        # BSD date (macOS)
        date -u +"%Y-%m-%dT%H:%M:%SZ"
    fi
}

# Detect sed type for debugging
get_sed_type() {
    if sed --version >/dev/null 2>&1; then
        echo "GNU"
    else
        echo "BSD"
    fi
}
