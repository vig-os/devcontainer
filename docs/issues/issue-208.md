---
type: issue
state: open
created: 2026-02-26T11:21:03Z
updated: 2026-02-26T19:00:35Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/208
comments: 3
labels: feature, area:image, area:workspace, effort:medium, semver:minor
assignees: gerchowl
milestone: none
projects: none
relationship: none
synced: 2026-02-27T04:19:05.199Z
---

# [Issue 208]: [[FEATURE] Add opt-in Tailscale SSH support to devcontainer workspace template](https://github.com/vig-os/devcontainer/issues/208)

### Problem

Cursor GUI connected to a devcontainer via the devcontainer protocol cannot execute shell commands through the AI agent. The agent's shell tool fails to route commands into the container's remote execution context. This is a known Cursor IDE limitation — VS Code and Cursor CLI/terminal both work fine.

The solution is to connect Cursor via SSH remote instead of the devcontainer protocol. Tailscale SSH provides this: no jump hosts, no port forwarding — direct mesh access over the tailnet.

This was prototyped in `vig-os/fd5` (see `docs/tailscale-devcontainer.md` in that repo for full design notes).

### Proposed changes

**New file: `assets/workspace/.devcontainer/scripts/setup-tailscale.sh`**

Single script with two subcommands:

- `install` — installs Tailscale via the official installer if `TAILSCALE_AUTHKEY` is set and Tailscale isn't already present. Idempotent. Called from `post-create.sh`.
- `start` — starts `tailscaled` (userspace networking, no `/dev/net/tun` needed) and calls `tailscale up --ssh --authkey=...`. Called from `post-start.sh`.

Opt-in: when `TAILSCALE_AUTHKEY` is unset, both subcommands are silent no-ops — zero impact on users who don't configure it.

Hostname defaults to `<project>-devc-<hostname -s>`, overridable via `TAILSCALE_HOSTNAME` env var.

**Modified: `assets/workspace/.devcontainer/scripts/post-create.sh`**

Add after the user-setup placeholder:

```bash
# Tailscale SSH (opt-in: no-op when TAILSCALE_AUTHKEY is unset)
"$SCRIPT_DIR/setup-tailscale.sh" install
```

`SCRIPT_DIR` resolution needs to be added to this file if not already present.

**Modified: `assets/workspace/.devcontainer/scripts/post-start.sh`** _(add if not present)_

Add after dependency sync:

```bash
# Tailscale SSH (opt-in: no-op when TAILSCALE_AUTHKEY is unset)
"$SCRIPT_DIR/setup-tailscale.sh" start
```

**Modified: `assets/workspace/.devcontainer/docker-compose.local.yaml`**

Add a commented example block:

```yaml
# Optional: Tailscale SSH for direct mesh access (e.g. Cursor GUI workaround)
#   services:
#     devcontainer:
#       environment:
#         - TAILSCALE_AUTHKEY=tskey-auth-XXXX
#         - TAILSCALE_HOSTNAME=myproject-devc-mybox  # optional
```

**Modified: `assets/workspace/.devcontainer/README.md`**

Add a "Tailscale SSH" section with quick-start instructions (key generation, env var setup, rebuild, connect).

### Architecture decisions

| Decision | Choice | Rationale |
|---|---|---|
| Networking | `--tun=userspace-networking` | No `/dev/net/tun` device needed; works in any container runtime without extra device mounts |
| SSH server | Tailscale SSH (`--ssh`) | No openssh-server needed; auth via Tailscale ACLs |
| Auth | `TAILSCALE_AUTHKEY` env var via `docker-compose.local.yaml` | Git-ignored; ephemeral + reusable keys auto-expire stale containers |
| Opt-in | No-op when env var unset | Zero impact on existing users |
| Install | `curl -fsSL https://tailscale.com/install.sh \| sh` | Official installer, idempotent; ~10s on first create |
| Hostname default | `<project>-devc-<hostname -s>` | Disambiguates same repo on multiple machines; should use project name from `init-workspace.sh` |

### Open questions / known gaps

- **`SCRIPT_DIR` in `post-create.sh`**: The upstream template doesn't currently resolve `SCRIPT_DIR` — this needs to be added alongside the hook.
- **Git commit signing over Tailscale SSH**: SSH agent forwarding doesn't work through Tailscale SSH by default. The `post-start.sh` script should warn when `TAILSCALE_AUTHKEY` is set but no SSH agent is available. The `commit.gpgsign` / `gpg.format` git config should be set in the init scripts so signing works automatically when a key is available.
- **Image baking**: Consider pre-installing Tailscale in the container image to avoid the ~10s install-on-first-create latency. Trade-off: image size vs. cold-start time.
- **ACL documentation**: Users must configure a Tailscale SSH ACL rule in their tailnet admin console before SSH connections are accepted. This should be documented.

### Acceptance Criteria

- [ ] `setup-tailscale.sh` added to workspace template scripts directory
- [ ] `post-create.sh` hooks `setup-tailscale.sh install`
- [ ] `post-start.sh` hooks `setup-tailscale.sh start`
- [ ] `docker-compose.local.yaml` template includes commented Tailscale example
- [ ] `.devcontainer/README.md` updated with Tailscale SSH quick-start section
- [ ] All hooks are no-ops when `TAILSCALE_AUTHKEY` is unset
- [ ] TDD compliance (see .cursor/rules/tdd.mdc)

### References

- Prototype: `vig-os/fd5` commit `13797db` (branch `chore/158-tailscale-ssh-devcontainer`)
- Design doc: `docs/tailscale-devcontainer.md` in `vig-os/fd5`
---

# [Comment #1]() by [gerchowl]()

_Posted on February 26, 2026 at 06:52 PM_

## Design

Issue: #208
Branch: feature/208-tailscale-ssh-support

### Overview

Add opt-in Tailscale SSH support to the devcontainer workspace template. When `TAILSCALE_AUTHKEY` is set (via `docker-compose.local.yaml`), Tailscale is installed at container creation and started on every container start. When unset, all hooks are silent no-ops — zero impact on existing users.

### Architecture

#### New file: `assets/workspace/.devcontainer/scripts/setup-tailscale.sh`

Single script with two subcommands:

- **\`install\`** — Installs Tailscale via the official installer (\`curl -fsSL https://tailscale.com/install.sh | sh\`). Idempotent: skips if Tailscale is already installed. No-op when \`TAILSCALE_AUTHKEY\` is unset.
- **\`start\`** — Starts \`tailscaled\` in userspace networking mode (\`--tun=userspace-networking\`, no \`/dev/net/tun\` needed) and runs \`tailscale up --ssh --authkey=...\`. No-op when \`TAILSCALE_AUTHKEY\` is unset.

Hostname defaults to \`\${SHORT_NAME}-devc-\$(hostname -s)\`, overridable via \`TAILSCALE_HOSTNAME\` env var. Since \`SHORT_NAME\` isn't available at runtime in the workspace template (it's replaced during init), we'll read the project name from \`devcontainer.json\`'s \`name\` field (which contains \`<project>-devc\` after init). We strip the \`-devc\` suffix and use that as the project prefix. Fallback: \`devc\`.

#### Modified: `assets/workspace/.devcontainer/scripts/post-create.sh`

Add call to \`setup-tailscale.sh install\` after the user-setup placeholder section. The file already has \`SCRIPT_DIR\` defined, so no additional resolution needed.

#### Modified: `assets/workspace/.devcontainer/scripts/post-start.sh`

Add \`SCRIPT_DIR\` resolution (not yet present) and call to \`setup-tailscale.sh start\` after dependency sync.

#### Modified: `assets/workspace/.devcontainer/docker-compose.local.yaml`

Add a commented example block showing how to set \`TAILSCALE_AUTHKEY\` and \`TAILSCALE_HOSTNAME\`.

#### Modified: `assets/workspace/.devcontainer/README.md`

Add a \"Tailscale SSH\" section with quick-start instructions: key generation, env var setup, rebuild, connect, ACL configuration.

### Design Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Networking | \`--tun=userspace-networking\` | No \`/dev/net/tun\` device needed; works in any container runtime |
| SSH server | Tailscale SSH (\`--ssh\`) | No openssh-server needed; auth via Tailscale ACLs |
| Auth | \`TAILSCALE_AUTHKEY\` env var via \`docker-compose.local.yaml\` | Git-ignored; ephemeral keys auto-expire stale containers |
| Opt-in | No-op when env var unset | Zero impact on existing users |
| Install method | Official \`curl\` installer | Idempotent; ~10s on first create |
| Hostname | \`<project>-devc-<hostname -s>\` | Disambiguates same repo on multiple machines |
| Project name | Parsed from \`devcontainer.json\` \`name\` field | Available after init; no extra env var needed |

### Error Handling

- \`setup-tailscale.sh install\`: If the installer fails, the script exits non-zero (fails the post-create hook). This is intentional — a partial install would be confusing.
- \`setup-tailscale.sh start\`: If \`tailscaled\` or \`tailscale up\` fails, the script logs a warning but does **not** exit non-zero. The container should still be usable via the devcontainer protocol even if Tailscale fails to start.
- Invalid subcommand: prints usage and exits 1.

### Testing Strategy

**BATS tests** (\`tests/bats/setup-tailscale.bats\`):
- Script structure: executable, shebang, strict mode
- \`install\` subcommand: no-op when \`TAILSCALE_AUTHKEY\` is unset
- \`start\` subcommand: no-op when \`TAILSCALE_AUTHKEY\` is unset
- Invalid subcommand: exits with error
- No subcommand: exits with error

**Existing integration tests** (\`test_integration.py\`) are session-scoped and verify script presence/executability. The \`setup-tailscale.sh\` script will be picked up by \`TestDevContainerScripts\` automatically once added to the manifest.

**No live Tailscale tests**: Testing actual Tailscale install/start requires network access and a valid authkey. These are not suitable for CI. The BATS tests cover the opt-in gate logic (the most important behavior).

### Files Changed

1. **New**: \`assets/workspace/.devcontainer/scripts/setup-tailscale.sh\`
2. **Modified**: \`assets/workspace/.devcontainer/scripts/post-create.sh\`
3. **Modified**: \`assets/workspace/.devcontainer/scripts/post-start.sh\`
4. **Modified**: \`assets/workspace/.devcontainer/docker-compose.local.yaml\`
5. **Modified**: \`assets/workspace/.devcontainer/README.md\`
6. **New**: \`tests/bats/setup-tailscale.bats\`
7. **Modified**: \`CHANGELOG.md\` (unreleased section)
8. **Modified**: \`scripts/sync_manifest.py\` or manifest file (to include new script in sync)

---

# [Comment #2]() by [gerchowl]()

_Posted on February 26, 2026 at 06:52 PM_

## Implementation Plan

Issue: #208
Branch: feature/208-tailscale-ssh-support

### Tasks

- [x] Task 1: Create `setup-tailscale.sh` with install and start subcommands — `assets/workspace/.devcontainer/scripts/setup-tailscale.sh` — verify: `npx bats tests/bats/setup-tailscale.bats`
- [x] Task 2: Add BATS tests for `setup-tailscale.sh` — `tests/bats/setup-tailscale.bats` — verify: `npx bats tests/bats/setup-tailscale.bats`
- [x] Task 3: Hook `setup-tailscale.sh install` into `post-create.sh` — `assets/workspace/.devcontainer/scripts/post-create.sh` — verify: `grep 'setup-tailscale.sh install' assets/workspace/.devcontainer/scripts/post-create.sh`
- [x] Task 4: Hook `setup-tailscale.sh start` into `post-start.sh` — `assets/workspace/.devcontainer/scripts/post-start.sh` — verify: `grep 'setup-tailscale.sh start' assets/workspace/.devcontainer/scripts/post-start.sh`
- [x] Task 5: Add commented Tailscale example to `docker-compose.local.yaml` — `assets/workspace/.devcontainer/docker-compose.local.yaml` — verify: `grep 'TAILSCALE_AUTHKEY' assets/workspace/.devcontainer/docker-compose.local.yaml`
- [x] Task 6: Add Tailscale SSH section to `README.md` — `assets/workspace/.devcontainer/README.md` — verify: `grep 'Tailscale SSH' assets/workspace/.devcontainer/README.md`
- [x] Task 7: Update `CHANGELOG.md` with unreleased entry — `CHANGELOG.md` — verify: `grep 'Tailscale SSH' CHANGELOG.md`

---

# [Comment #3]() by [gerchowl]()

_Posted on February 26, 2026 at 07:00 PM_

## Autonomous Run Complete

- Design: posted
- Plan: posted (7 tasks)
- Execute: all tasks done
- Verify: all checks pass
- PR: https://github.com/vig-os/devcontainer/pull/211
- CI: all checks pass

