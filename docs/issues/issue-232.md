---
type: issue
state: closed
created: 2026-03-06T20:51:21Z
updated: 2026-07-08T08:13:21Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devkit/issues/232
comments: 2
labels: feature, area:workspace, effort:large, semver:minor
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:23.701Z
---

# [Issue 232]: [[FEATURE] End-to-end remote devcontainer provisioning via Tailscale SSH](https://github.com/vig-os/devkit/issues/232)

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
---

# [Comment #1]() by [c-vigo]()

_Posted on July 7, 2026 at 09:33 AM_

@gerchowl — backlog-consolidation proposal for the whole remote-devcontainer family, from the post-0.4.0 triage (2026-07-07).

**Proposal:** keep **this issue (#232)** and **#70** as the two surviving trackers, and close the satellites below as consolidated-into-#232/#70. The family is dormant since Feb–Mar, and all of it pre-dates the Nix cutover — remote provisioning wants a fresh design against the 0.4.0 world (Nix image, direnv-mode workspaces #854, capability shells #884) and the upcoming devkit rename (#781, 1.0), so the fine-grained satellites would need re-speccing anyway. Their bodies stay linked from here, nothing is lost.

**Satellites proposed for closure:**
- #152 (devc-remote.sh orchestrator), #235 (--bootstrap), #236 (gh:org/repo:branch clone), #246 (local-to-remote handoff)
- #230 (Tailscale auth key injection), #85 (Tailscale in-container SSH), #231 (cursor-remote/code-remote wrappers)
- #464 (secret resolution), #465 (SSH key policy), #467 (auto-scaffold + image resolution), #468 (GPU passthrough)
- #209 (offline degradation — c-vigo's, already closed with the same rationale)

**Stale PR:** #166 (implements #70, branch `feature/70-remote-devc-orchestration`, open since February) — certain to conflict with the 0.4.0 scaffold; propose closing the PR, work restarts from #70 when the family is re-planned.

**Branches to prune with the closures** (no other open PRs attached):
- `feature/70-remote-devc-orchestration` (after closing PR #166)
- `feature/85-tailscale-in-container`
- `feature/246-remote-devc-handoff`

If you'd rather keep any satellite alive, just say which — the rest close on your ack.

---

# [Comment #2]() by [c-vigo]()

_Posted on July 8, 2026 at 08:13 AM_

Closing as part of an agreed backlog cleanup (with @gerchowl). The remote-devcontainer / `devc-remote` / Tailscale initiative predates the Nix + Claude-native migration (#625) and has had no activity since Feb–Mar 2026. If remote provisioning is wanted again it will be re-planned from scratch after the devkit rename (#781). Reopen/refile if revived.

