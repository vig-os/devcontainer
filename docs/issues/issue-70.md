---
type: issue
state: open
created: 2026-02-18T01:45:43Z
updated: 2026-02-22T09:22:29Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/70
comments: 2
labels: feature, priority:low, area:workspace, effort:large, semver:minor
assignees: gerchowl
milestone: Backlog
projects: none
relationship: none
synced: 2026-02-23T04:30:08.741Z
---

# [Issue 70]: [[FEATURE] Remote devcontainer orchestration via just recipe](https://github.com/vig-os/devcontainer/issues/70)

### Description

Add a `just` recipe (e.g. `just devc-remote <ssh-host>`) that orchestrates starting a devcontainer on a remote host and connecting Cursor/VS Code to it **in a single command**. This enables a workflow where developers can spin up their devcontainer on a powerful remote machine from their local terminal.

### Problem Statement

Currently, starting a devcontainer on a remote host requires multiple manual steps:
1. SSH into the remote host
2. Clone/update the repository
3. Check if podman/docker is available and start the container via compose
4. Open Cursor with `--remote ssh-remote+host /path/to/project`
5. Reopen in Container from within Cursor

This is tedious and error-prone. A single `just` command should handle the full orchestration.

### Proposed Solution

A `just` recipe (or small shell script invoked by `just`) in `justfile.base` that:

1. **SSHs into the specified remote host** and runs pre-flight checks (see Pre-flight Checks below)
2. **Clones the repo** if a target path is specified (defaults to `~/`), or skips if already present
3. **Starts the devcontainer** via `compose up -d` on the remote host, with container state detection (see below)
4. **Opens Cursor** directly into the remote devcontainer using the **nested authority CLI syntax** (see below)

Example usage:
```bash
just devc-remote myserver
just devc-remote user@host --path /opt/projects/myrepo
just devc-remote myserver --clone git@github.com:org/repo.git
```

### Cursor Nested Authority CLI (Key Finding)

Cursor supports opening a devcontainer on a remote SSH host in a **single CLI command** using nested authorities:

```bash
cursor --folder-uri "vscode-remote://dev-container+${DC_HEX}@ssh-remote+${SSH_SPEC}/${container_workspace}"
```

**Dev container spec** (hex-encoded JSON):
```json
{
  "settingType": "config",
  "workspacePath": "/home/user/repo",
  "devcontainerPath": "/home/user/repo/.devcontainer/devcontainer.json"
}
```

**SSH spec** — two variants:
- **Simple** (host from `~/.ssh/config`): `@ssh-remote+loginnode`
- **Full** (hex-encoded JSON): `@ssh-remote+${SSH_HEX}` where `{"hostName":"user@1.2.3.4 -p 22"}`

This eliminates the previously assumed two-step flow. No manual "Reopen in Container" is needed.

### Pre-flight Checks

The recipe must validate the following before proceeding, with clear error messages on failure:

#### Local (before SSH)
| Check | Failure mode | Error message |
|-------|-------------|---------------|
| `cursor` or `code` CLI exists | CLI not in PATH | "Neither cursor nor code CLI found. Install Cursor or VS Code and enable the shell command." |
| SSH host is reachable | DNS failure, network timeout, auth failure | "Cannot connect to <host>. Check your SSH config and network." |
| SSH key/agent available | No key loaded, agent not running | "SSH authentication failed for <host>. Ensure your SSH key is loaded (ssh-add -l)." |

#### Remote (over SSH)
| Check | Failure mode | Error message |
|-------|-------------|---------------|
| Container runtime exists | Neither podman nor docker installed | "No container runtime found on <host>. Install podman or docker." |
| Compose plugin available | `podman compose` / `docker compose` missing | "Compose not available on <host>. Install docker-compose or podman-compose." |
| Git is available | Git not installed (only if --clone used) | "Git not found on <host>. Install git to use --clone." |
| Repo path exists or --clone provided | Path missing, no clone URL | "Repository not found at <path> on <host>. Use --clone <url> to clone it." |
| Disk space sufficient | Disk full | "Low disk space on <host> (<available>). At least 2GB recommended." |
| `.devcontainer/` exists in repo | Missing devcontainer config | "No .devcontainer/ found in <path>. Is this a devcontainer-enabled project?" |
| Compose files are valid | YAML parse error | "Invalid compose configuration: <error>. Check .devcontainer/docker-compose*.yaml" |
| Container image pullable | Registry auth failure, image not found | "Cannot pull devcontainer image. Check registry access on <host>." |
| Port conflicts | Ports already bound | "Port <port> already in use on <host>. Stop the conflicting service or use a different port." |

### Implementation Detail: Container State Detection

Before running `compose up`, the recipe must detect and handle existing container state on the remote host. Docker compose scopes containers by project name (derived from directory name), so multiple repos in different directories are naturally isolated.

#### Detection flow

```
SSH into remote host
  → cd <repo_path>
    → compose ps --format json (scoped to project via -f flags)
      → Parse state of "devcontainer" service
        → running + healthy  → SKIP compose up, open Cursor
        → running + unhealthy/restarting → compose restart, health poll, open Cursor
        → exited/stopped → compose up -d, health poll, open Cursor
        → not found → compose up -d, health poll, open Cursor
```

#### Container state matrix

| # | State | Cause | Action | User message |
|---|-------|-------|--------|-------------|
| 1 | Running, healthy | Previous `devc-remote` or manual compose up | Skip compose up | "Devcontainer already running on <host>. Opening..." |
| 2 | Running, unhealthy/restarting | Container crashed, compose restart-looping | `compose restart devcontainer`, health poll | "Devcontainer unhealthy, restarting..." |
| 3 | Exited/stopped | Manual `compose stop` or unrecoverable crash | `compose up -d`, health poll | "Devcontainer was stopped. Starting..." |
| 4 | Not found | First run, or `compose down` was used | `compose up -d`, health poll | "Starting devcontainer on <host>..." |
| 5 | Running, config changed | User edited compose files since last up | `compose up -d` (detects changes, recreates) | "Devcontainer config changed. Recreating..." |
| 6 | Running, image updated | Image tag changed or new image pulled | `compose up -d` (detects image change, recreates) | "Image updated. Recreating devcontainer..." |

**Detecting config/image changes (cases 5 & 6):** `compose up -d` inherently handles these — it compares the running state to the desired state and recreates only what changed. No custom detection needed; compose's own output indicates whether it recreated or left the service as-is.

#### Health poll after compose up

After any `compose up -d` or `compose restart`, poll the container state before opening Cursor:

```bash
MAX_WAIT=30
INTERVAL=5
for i in $(seq 1 $((MAX_WAIT / INTERVAL))); do
  STATE=$(compose ps --format json | jq -r '.[] | select(.Service=="devcontainer") | .State')
  case "$STATE" in
    running) break ;;
    exited|dead)
      echo "[ERROR] Devcontainer failed to start. Last 20 log lines:"
      compose logs --tail 20 devcontainer
      exit 1
      ;;
  esac
  [ "$i" -eq $((MAX_WAIT / INTERVAL)) ] && {
    echo "[ERROR] Devcontainer did not become healthy within ${MAX_WAIT}s"
    compose logs --tail 20 devcontainer
    exit 1
  }
  sleep "$INTERVAL"
done
```

#### Edge cases in state detection

| Scenario | Behavior |
|----------|----------|
| Container name collision (different repo, same dir name) | Compose project is scoped by the `-f` file paths, so this is safe. Different repos in different directories get different project names. |
| Same repo cloned twice to different paths | Each path gets its own compose project — independent containers. No collision. |
| Multiple users running devc-remote to same host+repo | Compose project is shared. Second user's `compose up -d` is a no-op if config hasn't changed. Both get the same container — this is fine for shared dev servers. |
| `--force` flag (future) | Could add `--force` to always `compose down && compose up -d`, bypassing state detection. Not in v1 scope. |

### Failure Modes & Edge Cases

| Scenario | Expected behavior |
|----------|------------------|
| SSH connection drops mid-operation | Partial state left on remote. Recipe must be idempotent — re-running detects existing state and resumes. Compose up is already idempotent. Clone skips if directory exists. |
| Container already running (various states) | See Container State Detection section above. |
| Repo exists but is on wrong branch | Don't touch the branch. Warn: "Repo exists at <path> on branch <branch>." |
| Container runtime is rootless podman | Must work — test both rootless and rootful. Rootless podman uses `$XDG_RUNTIME_DIR/podman/podman.sock`. |
| Remote host is macOS (not Linux) | podman runs in a VM on macOS — compose paths differ. Detect OS via `uname` and warn if unsupported. |
| `~/.ssh/config` uses ProxyJump or bastion | Cursor's `ssh-remote` authority supports full SSH config, including proxy jumps. Test with multi-hop. |
| Multiple devcontainer services in compose | Recipe assumes service name `devcontainer` (from template). Fail clearly if service not found in compose ps output. |
| Compose up succeeds but container exits immediately | Health poll catches this within 30s. Reports last 20 log lines for debugging. |
| User interrupts with Ctrl+C | Trap SIGINT/SIGTERM. If mid-compose-up, let compose finish (it's idempotent). If mid-clone, warn about partial clone. |
| Remote host has no internet (air-gapped) | Image must be pre-loaded. Pre-flight check for image pullability will catch this. Suggest `podman load` as workaround. |
| SSH agent forwarding needed for private repo clone | Recipe should forward the SSH agent (`ssh -A`) when `--clone` is used with an SSH URL. |

### Implementation Detail: Script Architecture

The recipe should be a thin `just` wrapper calling a shell script for complex logic:

```
justfile.base
  └── devc-remote recipe → calls assets/scripts/devc-remote.sh

devc-remote.sh structure:
  ├── parse_args()          — host, --path, --clone, --clone-to
  ├── detect_editor_cli()   — cursor > code, store in $EDITOR_CLI
  ├── check_ssh()           — connectivity + auth test
  ├── remote_preflight()    — single SSH session, runs all remote checks
  │   ├── detect_runtime()  — podman > docker, store in $COMPOSE_CMD
  │   ├── check_git()       — only if --clone
  │   ├── check_repo()      — exists? has .devcontainer/?
  │   └── check_disk()      — df, warn if < 2GB
  ├── remote_clone()        — git clone (if --clone), with SSH agent forwarding
  ├── remote_compose_up()   — container state detection + compose up + health poll
  ├── build_cursor_uri()    — hex encode specs, assemble nested authority URI
  └── open_editor()         — $EDITOR_CLI --folder-uri "$URI"
```

Key design decisions:
- **Single SSH session for pre-flight**: Batch all remote checks into one `ssh` call to avoid repeated connection overhead.
- **Idempotent by design**: Every step checks existing state before acting. Safe to re-run.
- **No dependencies on remote host beyond runtime + git**: No `just`, `jq`, or other tools assumed on remote. Use basic shell + compose JSON output.
- **`set -euo pipefail`**: Strict error handling throughout.

### Implementation Detail: Cursor URI Construction

The hex encoding and URI assembly must be exact. Here's the construction logic:

```bash
build_cursor_uri() {
  local workspace_path="$1"    # e.g. /home/user/myrepo
  local ssh_host="$2"          # e.g. myserver or user@host
  local container_workspace    # e.g. /workspace/myrepo (from devcontainer.json)

  # Read workspaceFolder from devcontainer.json on remote
  container_workspace=$(ssh "$ssh_host" \
    "grep -o '\"workspaceFolder\"[[:space:]]*:[[:space:]]*\"[^\"]*\"' \
     ${workspace_path}/.devcontainer/devcontainer.json" \
    | sed 's/.*: *"//;s/"//')

  # Build devcontainer spec
  local dc_conf
  dc_conf=$(printf '{"settingType":"config","workspacePath":"%s","devcontainerPath":"%s/.devcontainer/devcontainer.json"}' \
    "$workspace_path" "$workspace_path")

  # Hex encode
  local dc_hex
  dc_hex=$(printf '%s' "$dc_conf" | od -A n -t x1 | tr -d '[\n\t ]')

  # Build URI — simple variant (host from SSH config)
  printf 'vscode-remote://dev-container+%s@ssh-remote+%s%s' \
    "$dc_hex" "$ssh_host" "$container_workspace"
}
```

For hosts not in SSH config, the full variant adds hex-encoded SSH spec:
```bash
local ssh_conf
ssh_conf=$(printf '{"hostName":"%s"}' "$ssh_host")
local ssh_hex
ssh_hex=$(printf '%s' "$ssh_conf" | od -A n -t x1 | tr -d '[\n\t ]')
# URI becomes: dev-container+${dc_hex}@ssh-remote+${ssh_hex}/${container_workspace}
```

### Testing Strategy

#### Unit tests (BATS — shell script analysis)
- Script structure validation (`set -euo pipefail`, error handling, signal traps)
- Argument parsing (`host`, `--path`, `--clone`, `--clone-to`)
- Hex encoding correctness — given known JSON input, assert exact hex output
- URI assembly — given known specs, assert exact `--folder-uri` output
- Container state matrix — each state maps to correct action
- Error message formatting for each pre-flight failure

#### Integration tests — local simulation (pytest, no remote host)
Reuse existing patterns from `conftest.py`:

| Test | Approach |
|------|----------|
| URI construction end-to-end | Call `build_cursor_uri()` with known inputs, assert exact output matches Cursor docs examples. |
| Pre-flight check functions | Mock SSH commands via a stub script, test each check returns correct pass/fail with correct exit code. |
| Compose file resolution | Given a workspace path, verify the recipe generates correct `-f` flags for all three compose files. |
| Idempotency | Run the remote setup logic twice against a local container. Verify second run detects "running" state and skips compose up. |
| Error messages | Trigger each failure mode, assert user-facing message matches spec. |
| Container state detection | For each of the 6 states in the matrix, mock `compose ps` output and verify correct action is taken. |
| Health poll timeout | Mock a container that never becomes healthy. Verify timeout fires at 30s with log output. |

#### Integration tests — SSH loopback (pytest + sshd sidecar)
Spin up a **sidecar container running sshd** to simulate a remote host:

```yaml
services:
  test-remote-host:
    image: linuxserver/openssh-server:latest
    environment:
      - PUBLIC_KEY_FILE=/config/.ssh/authorized_keys
    volumes:
      - ./test-keys/id_ed25519.pub:/config/.ssh/authorized_keys:ro
    ports:
      - "2222:2222"
```

| Test | Approach |
|------|----------|
| SSH connectivity pre-flight | Connect to sshd sidecar on port 2222. Verify check passes. |
| SSH auth failure | Connect with wrong key. Verify check fails with correct message. |
| Remote runtime detection | sshd sidecar has podman/docker installed (or mock binaries). Verify detection picks correct runtime. |
| No runtime installed | sshd sidecar with neither podman nor docker. Verify error message. |
| Clone + compose up | Clone a test repo into sidecar, run compose up, verify container starts via `compose ps`. |
| Container state detection (live) | Start container, verify "already running" detection. Stop container, verify "stopped" detection. |
| Full URI generation | After remote setup, verify the generated `cursor --folder-uri` command is syntactically valid (parse the URI, decode hex, validate JSON). |
| Idempotency (live) | Run devc-remote twice against sshd sidecar. Verify second run is a no-op for compose. |
| SSH drop simulation | Kill sshd mid-compose-up. Re-run. Verify recovery. |
| Disk space check | Fill sidecar's `/tmp`. Verify disk space warning triggers. |

This follows the existing `devcontainer_with_sidecar` fixture pattern from `conftest.py`.

#### CI considerations
- **GitHub Actions runners** (ubuntu-22.04) support running sshd containers as sidecars
- No multi-machine CI needed — the sshd sidecar simulates a remote host on the same runner
- Existing `test-integration` job structure can host these tests
- Session-scoped fixture for the sshd sidecar (expensive to set up, reuse across tests)
- Clean up sidecar containers after test session (existing `PYTEST_AUTO_CLEANUP` pattern)
- Generate ephemeral SSH keypair in CI (no secrets needed)

#### Manual / smoke testing
- Test with a real remote host (developer's own server) — not automatable in CI, documented in test plan
- Test with ProxyJump / bastion hosts
- Test Cursor actually opens and connects (requires human verification)
- Test with rootless podman on remote
- Test with macOS remote (expected: warn unsupported)

### Alternatives Considered

- **Manual SSH + compose**: Current approach — works but requires many steps.
- **VS Code Remote SSH + "Reopen in Container"**: GUI-only workflow, not scriptable.
- **`devcontainer` CLI over SSH**: Requires `@devcontainers/cli` installed on the remote host (extra dependency).
- **Cursor tunnels (`cursor tunnel`)**: Requires the Cursor CLI on the remote host and a different auth flow.

### Additional Context

- Depends on issue #71 (local justfile.base recipes) for the shared `up`/`down`/compose patterns
- Cursor CLI docs confirm nested `dev-container+...@ssh-remote+...` authority works for single-command remote devcontainer opening
- The recipe should auto-detect `cursor` vs `code` CLI (prefer cursor, fall back to code)
- Existing test infrastructure (sidecar pattern, SSH agent forwarding, pexpect) provides a solid foundation
- No `jq` or `just` assumed on the remote host — only basic shell, git, and a container runtime

### Impact

- Benefits developers working with remote build/dev machines (GPU servers, cloud VMs, CI runners)
- Backward compatible — new recipe, no changes to existing behavior
- Requires SSH access configured on the host (uses `~/.ssh/config`)

### Changelog Category

Added
---

# [Comment #1]() by [gerchowl]()

_Posted on February 21, 2026 at 11:57 PM_

## Design

### Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dependency on #71 | **Decoupled** — #71 is implemented (PR #151), not yet merged. #70 proceeds independently; shared compose patterns are simple enough (runtime detection, compose file flags) that remote SSH execution reimplements them. Verify consistency when #71 merges. | No code-level coupling — only pattern consistency |
| Phased delivery | **Yes** — 3 sub-issues for v1, follow-ups for `--clone`, signal traps, etc. | Effort:large; incremental delivery reduces risk |
| Script language | **Hybrid** — bash orchestrator + Python URI helper | Bash is natural for SSH/compose; Python is cleaner for JSON/hex encoding |
| File placement | Canonical files in repo root (`scripts/`), synced to `assets/workspace/.devcontainer/scripts/` via manifest | Follows existing pattern (cf. `justfile.gh`, `scripts/gh_issues.py`) |
| Recipe location | `assets/workspace/.devcontainer/justfile.base` | Works in both this repo and deployed workspaces |

### Architecture

```
just devc-remote <ssh-host> [--path <remote-repo-path>]
  └── .devcontainer/scripts/devc-remote.sh
        ├── detect_editor_cli()        → cursor > code (local)
        ├── check_ssh()                → connectivity + auth (local)
        ├── remote_preflight()         → single SSH call batching all remote checks
        │   ├── detect runtime         → podman > docker
        │   ├── check compose          → podman compose / docker compose
        │   ├── check repo path        → exists? has .devcontainer/?
        │   └── check disk space       → warn if < 2GB
        ├── remote_compose_up()        → container state detection + compose up + health poll
        └── python3 devc_remote_uri.py → hex encode + build URI → $EDITOR_CLI --folder-uri
```

**Key design choices:**
- **Single SSH session for remote pre-flight** — heredoc-based `ssh <host> bash -s` batching all checks to avoid repeated connection overhead.
- **No remote dependencies** beyond shell, git, container runtime — Python helper runs locally.
- **Idempotent by design** — every step checks existing state before acting. Safe to re-run.
- Compose patterns (runtime detection, file flags) are consistent with #71 but reimplemented for remote SSH context.

### File Layout

| File | Purpose |
|------|---------|
| `scripts/devc-remote.sh` | Main bash orchestrator (SSH, pre-flight, compose, open editor) |
| `scripts/devc_remote_uri.py` | Python helper: hex encoding + Cursor URI construction |
| `assets/workspace/.devcontainer/justfile.base` | `devc-remote` recipe (thin wrapper) |
| `scripts/sync_manifest.py` | New entries to sync both scripts into `assets/workspace/` |

### Sub-Issue Decomposition (v1)

#### Sub-issue A: Script scaffold + pre-flight checks
- `devc-remote.sh` with `parse_args()`, `usage()`, `set -euo pipefail`
- Arguments: `<ssh-host>` (required), `--path <remote-repo-path>` (optional, default `~/`)
- Local pre-flight: `detect_editor_cli()` (cursor > code), `check_ssh()` (connectivity + auth via `ssh -o BatchMode=yes`)
- Remote pre-flight: single SSH call returning structured key=value output (runtime, repo_exists, devcontainer_exists, disk_gb, os_type)
- BATS tests: argument parsing, pre-flight checks with mocked commands

#### Sub-issue B: Container state + compose + URI construction
- Container state detection from `compose ps --format json` (6-state matrix from issue spec)
- Health polling: 30s timeout, 5s interval, log tail on failure
- `devc_remote_uri.py`: `hex_encode()`, `build_uri()` with CLI interface
- Pytest unit tests for URI construction (known inputs → exact outputs)
- BATS tests for state detection (mocked compose output for each state)

#### Sub-issue C: End-to-end wiring
- `justfile.base` recipe: `devc-remote host *args`
- Manifest entries for both scripts
- Smoke/integration test (script runs `--help` successfully)
- Defer full SSH loopback sidecar tests to follow-up issue

### Follow-Up Issues (post-v1)
- `--clone <url>` flag for remote repo cloning (+ SSH agent forwarding with `ssh -A`)
- Signal trapping (`trap` for SIGINT/SIGTERM)
- macOS remote host detection + warning
- ProxyJump / bastion host testing
- `--force` flag (always `compose down && compose up -d`)
- Full SSH loopback integration tests (sshd sidecar in CI)

### Testing Strategy (v1)

| Layer | Tool | Coverage |
|-------|------|----------|
| Argument parsing, pre-flight, state matrix | BATS | Mocked commands, no SSH needed |
| Hex encoding, URI assembly | Pytest | Pure functions, known input/output |
| Smoke test | Pytest or BATS | `devc-remote.sh --help` exits 0 |
| End-to-end (deferred) | Pytest + sshd sidecar | Full SSH loopback, follow-up issue |

---

# [Comment #2]() by [gerchowl]()

_Posted on February 22, 2026 at 09:22 AM_

## Implementation Plan

Issue: #70
Branch: `feature/70-remote-devc-orchestration`

### Structure

Two parallel sub-issues, then wiring on the parent branch:

| Sub-issue | Scope | Parallelism |
|-----------|-------|-------------|
| #152 — `devc-remote.sh` bash orchestrator | Script scaffold, pre-flight checks, container state detection, compose up, health poll, BATS tests | Parallel with #153 |
| #153 — `devc_remote_uri.py` Python URI helper | Hex encoding, URI construction, CLI interface, pytest tests | Parallel with #152 |
| #70 (final phase) | Just recipe, manifest entries, wiring, smoke test | Sequential after #152 + #153 merge |

### Sub-issue #152 Tasks — `devc-remote.sh`

- [ ] Test: BATS tests for argument parsing (missing host, `--path`, `--help`, unknown flags) — `tests/bats/devc-remote.bats` — verify: `npx bats tests/bats/devc-remote.bats`
- [ ] Impl: `parse_args()` + `usage()` + `set -euo pipefail` scaffold — `scripts/devc-remote.sh` — verify: BATS pass
- [ ] Test: BATS tests for `detect_editor_cli()` (cursor found, code found, neither) — `tests/bats/devc-remote.bats` — verify: BATS pass
- [ ] Impl: `detect_editor_cli()` — `scripts/devc-remote.sh` — verify: BATS pass
- [ ] Test: BATS tests for `check_ssh()` (success, connection fail, auth fail) — `tests/bats/devc-remote.bats` — verify: BATS pass
- [ ] Impl: `check_ssh()` — `scripts/devc-remote.sh` — verify: BATS pass
- [ ] Test: BATS tests for `remote_preflight()` structured output parsing — `tests/bats/devc-remote.bats` — verify: BATS pass
- [ ] Impl: `remote_preflight()` — single SSH heredoc returning key=value output — `scripts/devc-remote.sh` — verify: BATS pass
- [ ] Test: BATS tests for container state matrix (6 states → correct actions, mocked `compose ps`) — `tests/bats/devc-remote.bats` — verify: BATS pass
- [ ] Impl: `remote_compose_up()` — state detection + compose up + health poll — `scripts/devc-remote.sh` — verify: BATS pass
- [ ] Impl: `open_editor()` — call `devc_remote_uri.py`, then `$EDITOR_CLI --folder-uri` — `scripts/devc-remote.sh` — verify: BATS pass
- [ ] Wire: main function connecting all stages — `scripts/devc-remote.sh` — verify: `bash scripts/devc-remote.sh --help` exits 0

### Sub-issue #153 Tasks — `devc_remote_uri.py`

- [ ] Test: pytest for `hex_encode()` — known inputs → exact hex output — `tests/test_devc_remote_uri.py` — verify: `uv run pytest tests/test_devc_remote_uri.py -v`
- [ ] Impl: `hex_encode()` — `scripts/devc_remote_uri.py` — verify: pytest pass
- [ ] Test: pytest for `build_uri()` — known inputs → exact URI — `tests/test_devc_remote_uri.py` — verify: pytest pass
- [ ] Impl: `build_uri()` — `scripts/devc_remote_uri.py` — verify: pytest pass
- [ ] Test: pytest for CLI interface — subprocess call, verify stdout — `tests/test_devc_remote_uri.py` — verify: pytest pass
- [ ] Impl: CLI `__main__` block with argparse — `scripts/devc_remote_uri.py` — verify: pytest pass
- [ ] Test: edge cases — special chars in paths, empty strings, missing args — `tests/test_devc_remote_uri.py` — verify: pytest pass

### #70 Wiring Tasks (after #152 + #153 merge)

- [ ] Add `devc-remote` recipe to `assets/workspace/.devcontainer/justfile.base` — verify: `just --list` shows recipe
- [ ] Add manifest entries for both scripts to `scripts/sync_manifest.py` — verify: `uv run python scripts/sync_manifest.py list` shows entries
- [ ] Run manifest sync — verify: files in `assets/workspace/.devcontainer/scripts/`
- [ ] Smoke test: `bash scripts/devc-remote.sh --help` exits 0 with usage output
- [ ] Update CHANGELOG.md Unreleased section

