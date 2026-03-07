---
type: issue
state: open
created: 2026-03-06T20:51:21Z
updated: 2026-03-06T20:51:41Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/232
comments: 0
labels: feature, area:workspace, effort:large, semver:minor
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-03-07T04:05:37.233Z
---

# [Issue 232]: [[FEATURE] End-to-end remote devcontainer provisioning via Tailscale SSH](https://github.com/vig-os/devcontainer/issues/232)

## Summary

One-command flow to provision a devcontainer on a remote host and connect via Tailscale SSH. From zero (uncloned repo) to working terminal session — no manual steps.

## Target DX

```
C-SPC d → "new devc on remote" → pick host → pick repo → [automated] → SSH tab
```

Or from CLI:
```bash
devc-provision.sh sdsc --repo git@github.com:vig-os/fd5.git
# → clones, scaffolds .devcontainer, injects TS key, compose up, waits for tailnet, prints IP
```

## Sub-issues

- [ ] #208 — Tailscale SSH in workspace template (container-side plumbing)
- [ ] #230 — Tailscale auth key injection in `devc-remote.sh` (local OAuth → remote inject)
- [ ] #231 — IDE-agnostic remote connection wrappers (split infra from Cursor/VS Code)

## Architecture

```
Local machine                              Remote host
─────────────                              ───────────
devc-provision.sh <host> [repo]
  ├── devc-remote.sh --open none --yes
  │     ├── SSH connectivity check
  │     ├── Clone repo (if missing)
  │     ├── init-workspace (if no .devcontainer/)
  │     ├── Generate ephemeral TS key (OAuth API)
  │     ├── Inject key into docker-compose.local.yaml
  │     └── compose up ──────────────────► container starts
  │                                        ├── post-create: install tailscale
  │                                        └── post-start: tailscaled + tailscale up
  ├── Poll tailscale status --json
  │   until container appears on tailnet
  └── Output: tailscale hostname + IP

IDE/terminal (choose one):
  ├── WezTerm C-SPC d → ssh root@<ip>
  ├── cursor --remote ssh-remote+root@<hostname>
  ├── code --remote ssh-remote+root@<hostname>
  └── ssh root@<hostname>
```

## Prerequisites

- Tailscale OAuth client with `auth_keys` scope + `tag:devcontainer`
- `TS_CLIENT_ID` + `TS_CLIENT_SECRET` in local environment
- Tailnet ACLs allowing SSH to `tag:devcontainer` devices
- Remote host with podman/docker + compose

## Out of scope

- WezTerm keybind integration (personal dotfiles, not project code)
- JetBrains Gateway support
- Baking Tailscale into the container image (separate optimization)

## References

- Design doc: `docs/designs/tailscale-ssh.md`
- [Tailscale OAuth clients](https://tailscale.com/kb/1215/oauth-clients)
- [Tailscale API](https://tailscale.com/kb/1101/api)
