# retry() — keep in sync with .github/actions/setup-env/action.yml (heredoc body)
# and .github/workflows/sync-main-to-dev.yml (embedded copy).
retry() {
  local retries=3
  local backoff=1
  local max_backoff=60
  local rc=1

  while [ "$#" -gt 0 ]; do
    case "$1" in
      --retries)
        retries="$2"
        shift 2
        ;;
      --backoff)
        backoff="$2"
        shift 2
        ;;
      --max-backoff)
        max_backoff="$2"
        shift 2
        ;;
      --)
        shift
        break
        ;;
      *)
        echo "ERROR: Unknown retry option '$1'"
        return 2
        ;;
    esac
  done

  if [ "$#" -eq 0 ]; then
    echo "ERROR: retry requires a command after '--'"
    return 2
  fi

  local attempt=1
  local current_backoff="$backoff"
  while [ "$attempt" -le "$retries" ]; do
    "$@" && return 0
    rc=$?
    if [ "$attempt" -lt "$retries" ]; then
      local wait="$current_backoff"
      if [ "$wait" -gt "$max_backoff" ]; then
        wait="$max_backoff"
      fi
      echo "Retry $attempt/$retries failed (exit $rc), waiting ${wait}s..."
      sleep "$wait"
      current_backoff=$((current_backoff * 2))
    fi
    attempt=$((attempt + 1))
  done

  echo "ERROR: Command failed after $retries attempts: $*"
  return "$rc"
}
