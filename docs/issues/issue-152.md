---
type: issue
state: open
created: 2026-02-22T09:20:59Z
updated: 2026-02-22T09:53:29Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/152
comments: 3
labels: feature, area:workspace, effort:medium, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-23T04:30:08.054Z
---

# [Issue 152]: [[FEATURE] devc-remote.sh — bash orchestrator for remote devcontainer](https://github.com/vig-os/devcontainer/issues/152)

### Description

Create `scripts/devc-remote.sh` — the main bash script that orchestrates starting a devcontainer on a remote host via SSH. This script handles everything except URI construction (which is in the Python helper, sibling sub-issue).

### Problem Statement

Part of #70. The remote devcontainer orchestration requires a bash script that handles SSH connectivity, pre-flight checks, container state detection, and compose lifecycle management. This is the core orchestration logic.

### Proposed Solution

A single bash script with the following functions:

- `parse_args()` — `<ssh-host>` (required), `--path <remote-path>` (optional, default `~/`), `--help`
- `detect_editor_cli()` — prefer `cursor`, fall back to `code`
- `check_ssh()` — `ssh -o ConnectTimeout=5 -o BatchMode=yes <host> true`
- `remote_preflight()` — single SSH heredoc call batching all remote checks: runtime detection (podman > docker), compose availability, repo path exists, `.devcontainer/` exists, disk space, OS type. Returns structured key=value output.
- `remote_compose_up()` — container state detection (6-state matrix from #70), `compose up -d`, health poll (30s timeout, 5s interval, log tail on failure)
- `open_editor()` — calls Python URI helper (`devc_remote_uri.py`), then `$EDITOR_CLI --folder-uri "$URI"`
- Logging follows `scripts/init.sh` patterns (`log_info`, `log_success`, `log_warning`, `log_error`)
- `set -euo pipefail` throughout

#### Container state matrix

| State | Action |
|-------|--------|
| Running, healthy | Skip compose up, open editor |
| Running, unhealthy/restarting | `compose restart`, health poll, open editor |
| Exited/stopped | `compose up -d`, health poll, open editor |
| Not found | `compose up -d`, health poll, open editor |
| Running, config changed | `compose up -d` (detects changes), open editor |
| Running, image updated | `compose up -d` (detects image change), open editor |

#### Pre-flight checks

**Local:**
- `cursor` or `code` CLI in PATH
- SSH host reachable + auth works

**Remote (single SSH session):**
- Container runtime exists (podman > docker)
- Compose plugin available
- Repo path exists
- `.devcontainer/` directory exists in repo
- Disk space ≥ 2GB (warn if low)
- OS detection (warn if macOS)

### Files

- Create: `scripts/devc-remote.sh`
- Create: `tests/bats/devc-remote.bats`

### Testing Strategy

BATS unit tests with mocked commands:
- Argument parsing: missing host, `--path` handling, `--help`, unknown flags
- `detect_editor_cli()`: cursor found, code found, neither found
- `check_ssh()`: success, connection failure, auth failure
- Remote pre-flight: parse structured output for each check
- Container state matrix: mock `compose ps` JSON for each of 6 states
- Health poll: mock healthy start, mock timeout, mock immediate exit

Verify: `npx bats tests/bats/devc-remote.bats`

### Alternatives Considered

- Python for the full script: rejected — bash is more natural for SSH/compose orchestration
- Multiple SSH calls for pre-flight: rejected — single heredoc call avoids connection overhead

### Impact

- New file, no changes to existing behavior
- Backward compatible
- Can be worked in parallel with the sibling Python URI sub-issue

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 22, 2026 at 09:41 AM_

## Design

### Overview

`scripts/devc-remote.sh` is the bash orchestrator for starting a devcontainer on a remote host via SSH. It handles SSH connectivity, pre-flight checks, container state detection, and compose lifecycle. URI construction is delegated to a Python helper (sibling sub-issue).

### Architecture

```
main()
  → parse_args()           # <ssh-host> (required), --path (optional, default ~/), --help
  → detect_editor_cli()     # cursor > code, fail if neither
  → check_ssh()            # ssh -o ConnectTimeout=5 -o BatchMode=yes <host> true
  → remote_preflight()     # single SSH heredoc, structured key=value output
  → remote_compose_up()    # 6-state matrix → compose up/restart, health poll
  → open_editor()          # call Python URI helper, then $EDITOR_CLI --folder-uri "$URI"
```

### Components

**parse_args()**
- Positional: `<ssh-host>` (required)
- Optional: `--path <remote-path>` (default `~/`)
- Flag: `--help` → show usage, exit 0
- Unknown flags → log_error, exit 1
- Missing host → log_error, exit 1

**detect_editor_cli()**
- Prefer `cursor`, fall back to `code`
- Store in `EDITOR_CLI`
- If neither in PATH → log_error "Neither cursor nor code CLI found...", exit 1

**check_ssh()**
- `ssh -o ConnectTimeout=5 -o BatchMode=yes "$SSH_HOST" true`
- On failure → log_error "Cannot connect to <host>...", exit 1

**remote_preflight()**
- Single SSH heredoc batching all checks
- Output: structured `KEY=value` lines (one per check)
- Checks: runtime (podman>docker), compose, repo path, .devcontainer/, disk ≥2GB, OS (warn if macOS)
- Parse output into vars; fail with clear message on any required check failure

**remote_compose_up()**
- 6-state matrix (from issue body): running+healthy → skip; unhealthy/restarting → restart; exited/not found/config changed/image updated → compose up -d
- Health poll: 30s timeout, 5s interval; on timeout/failure → log tail 20 lines, exit 1

**open_editor()**
- Call Python URI helper: `scripts/devc_remote_uri.py --ssh-host "$SSH_HOST" --path "$REMOTE_PATH"` (interface TBD by sibling issue)
- Capture URI from stdout
- Execute: `"$EDITOR_CLI" --folder-uri "$URI"`

### Logging

Reuse `init.sh` patterns: `log_info`, `log_success`, `log_warning`, `log_error` (color-coded, same format). No `log_debug` unless needed.

### Error Handling

- `set -euo pipefail` throughout
- All failures exit with non-zero and clear user-facing message
- No silent failures

### Python URI Helper Interface (stub for this issue)

Until sibling issue implements `devc_remote_uri.py`, the script will call a stub that:
- Accepts `--ssh-host` and `--path`
- Returns a placeholder URI on stdout (or fails if stub not yet created)
- Enables testing of the orchestration flow; URI correctness is sibling scope

### Testing Strategy

BATS unit tests with mocked commands (`PATH` manipulation, stub scripts):
- Argument parsing: missing host, --path, --help, unknown flags
- detect_editor_cli: cursor found, code found, neither found
- check_ssh: success, connection failure (mock ssh)
- remote_preflight: parse structured output for each check
- Container state matrix: mock `compose ps` JSON for each of 6 states
- Health poll: mock healthy start, timeout, immediate exit

Verify: `npx bats tests/bats/devc-remote.bats`

---

# [Comment #2]() by [gerchowl]()

_Posted on February 22, 2026 at 09:41 AM_

## Implementation Plan

Issue: #152
Branch: feature/152-devc-remote-sh

### Tasks

- [x] Task 1: Create devc-remote.sh skeleton with set -euo pipefail, log_info/log_success/log_warning/log_error (from init.sh), empty function stubs — `scripts/devc-remote.sh` — verify: `grep -E "set -euo pipefail|log_info|parse_args" scripts/devc-remote.sh`
- [x] Task 2: BATS tests for script structure and parse_args (missing host, --help, --path, unknown flag) — `tests/bats/devc-remote.bats` — verify: `npx bats tests/bats/devc-remote.bats` (Task 2 tests may fail until Task 3)
- [x] Task 3: Implement parse_args() — `scripts/devc-remote.sh` — verify: `npx bats tests/bats/devc-remote.bats` (parse_args tests pass)
- [x] Task 4: BATS tests for detect_editor_cli (cursor found, code found, neither) — `tests/bats/devc-remote.bats` — verify: tests fail
- [x] Task 5: Implement detect_editor_cli() — `scripts/devc-remote.sh` — verify: detect_editor_cli tests pass
- [x] Task 6: BATS tests for check_ssh (success, failure via mock) — `tests/bats/devc-remote.bats` — verify: tests fail
- [x] Task 7: Implement check_ssh() — `scripts/devc-remote.sh` — verify: check_ssh tests pass
- [x] Task 8: BATS tests for remote_preflight (parse structured KEY=value output) — `tests/bats/devc-remote.bats` — verify: tests fail
- [x] Task 9: Implement remote_preflight() — `scripts/devc-remote.sh` — verify: remote_preflight tests pass
- [x] Task 10: BATS tests for remote_compose_up (6-state matrix via mock compose ps JSON) — `tests/bats/devc-remote.bats` — verify: tests fail
- [x] Task 11: Implement remote_compose_up() — `scripts/devc-remote.sh` — verify: remote_compose_up tests pass
- [x] Task 12: Create Python URI stub (scripts/devc_remote_uri.py) + BATS tests for open_editor — `scripts/devc_remote_uri.py`, `tests/bats/devc-remote.bats` — verify: tests fail
- [x] Task 13: Implement open_editor() and main() wiring — `scripts/devc-remote.sh` — verify: `npx bats tests/bats/devc-remote.bats` (all pass)

---

# [Comment #3]() by [gerchowl]()

_Posted on February 22, 2026 at 09:53 AM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (13 tasks)
- Execute: all tasks done
- Verify: BATS tests pass, lint pass (precommit hadolint skipped — Docker daemon not running locally)
- PR: https://github.com/vig-os/devcontainer/pull/156
- CI: PR Title Check pass (full CI runs on dev/release/main targets; this PR targets feature/70-remote-devc-orchestration)

