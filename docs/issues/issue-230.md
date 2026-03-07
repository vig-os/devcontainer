---
type: issue
state: open
created: 2026-03-06T20:44:19Z
updated: 2026-03-06T20:51:27Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/230
comments: 0
labels: feature, area:workspace, effort:medium, semver:minor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:37.824Z
---

# [Issue 230]: [[FEATURE] Tailscale auth key injection in devc-remote.sh](https://github.com/vig-os/devcontainer/issues/230)

## Summary

Extend `devc-remote.sh` to automatically generate and inject a Tailscale ephemeral auth key into the remote container's `docker-compose.local.yaml` before `compose up`. This enables the container to join the tailnet without manual key setup on the remote host.

## Context

- `devc-remote.sh` (#152) handles remote devcontainer orchestration
- Tailscale SSH (#208) requires `TAILSCALE_AUTHKEY` in `docker-compose.local.yaml`
- Currently, the auth key must be manually placed on the remote host
- With this feature, local OAuth credentials generate a per-session ephemeral key that gets injected into the remote automatically

## Design

### Prerequisites (local machine)

- `TS_CLIENT_ID` and `TS_CLIENT_SECRET` environment variables (from Tailscale OAuth client with `auth_keys` scope and `tag:devcontainer`)
- `curl` and `jq` available

### Flow

1. After `remote_preflight`, before `remote_compose_up`
2. Check if `TS_CLIENT_ID` is set locally — if not, skip (opt-in, like everything Tailscale)
3. Generate an OAuth access token from `api.tailscale.com/api/v2/oauth/token`
4. Create an ephemeral (non-reusable) auth key via `api.tailscale.com/api/v2/tailnet/-/keys` with `tag:devcontainer`
5. Inject `TAILSCALE_AUTHKEY=<key>` into the remote `docker-compose.local.yaml` via SSH
6. Proceed with `compose up` — container installs Tailscale and joins tailnet
7. Output the Tailscale hostname for downstream use (IDE wrappers, direct SSH)

### Constraints

- OAuth client must have `tag:devcontainer` — ACLs must allow SSH to tagged devices
- Key is ephemeral: container removal auto-cleans the tailnet node
- Non-reusable: one key per container session, not shared across rebuilds
- `docker-compose.local.yaml` is git-ignored, safe to write

### Scope boundary

This issue covers only the infra side — key generation + injection + container on tailnet. IDE-specific connection (Cursor, VS Code) is a separate concern (see linked issue).

## Depends on

- #208 (Tailscale SSH in workspace template)
- #152 (devc-remote.sh orchestrator)

## References

- [Tailscale OAuth clients](https://tailscale.com/kb/1215/oauth-clients)
- [Tailscale API — create key](https://tailscale.com/kb/1101/api)
- Design doc: `docs/designs/tailscale-ssh.md`
