# BATS test helper — loads BATS libraries and performs project-specific setup
#
# Usage (in every .bats file):
#   setup() { load test_helper; }
#
# Library resolution order:
#   1. node_modules/ (local dev via npx bats)
#   2. /usr/lib/ (CI via bats-core/bats-action)
#   3. bats_load_library (fallback, uses BATS_LIB_PATH)

# Resolve project root (two levels up from tests/bats/)
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export PROJECT_ROOT

# Load BATS helper libraries
if [ -d "${PROJECT_ROOT}/node_modules/bats-support" ]; then
    # Development mode: load from local node_modules
    load "${PROJECT_ROOT}/node_modules/bats-support/load"
    load "${PROJECT_ROOT}/node_modules/bats-assert/load"
    load "${PROJECT_ROOT}/node_modules/bats-file/load"
elif [ -d "/usr/lib/bats-support" ]; then
    # CI mode: load from system paths (BATS_LIB_PATH)
    load "/usr/lib/bats-support/load"
    load "/usr/lib/bats-assert/load"
    load "/usr/lib/bats-file/load"
else
    # Fallback: try using bats_load_library (available in BATS core)
    bats_load_library bats-support
    bats_load_library bats-assert
    bats_load_library bats-file
fi
