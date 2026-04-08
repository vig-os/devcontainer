# Sources the canonical retry() from .github/scripts/retry.sh (same as setup-env).
_retry_helper_fixture_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_retry_helper_repo_root="$(cd "${_retry_helper_fixture_dir}/../../.." && pwd)"
_retry_helper_shared_script="${_retry_helper_repo_root}/.github/scripts/retry.sh"

if [ ! -f "${_retry_helper_shared_script}" ]; then
  echo "ERROR: Shared retry helper not found: ${_retry_helper_shared_script}" >&2
  return 1
fi

# shellcheck source=/dev/null
. "${_retry_helper_shared_script}"

if ! command -v retry >/dev/null 2>&1; then
  echo "ERROR: Shared retry helper did not define retry()" >&2
  return 1
fi
