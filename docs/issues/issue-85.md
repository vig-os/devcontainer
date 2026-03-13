---
type: issue
state: open
created: 2026-02-18T21:40:17Z
updated: 2026-02-18T21:40:17Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/85
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-19T00:08:05.712Z
---

# [Issue 85]: [[FEATURE] Add Tailscale support for remote SSH access to devcontainer](https://github.com/vig-os/devcontainer/issues/85)

## Description

Add Tailscale to the devcontainer image to enable secure, private remote SSH access from any device (phone, tablet, laptop on a different network). Combined with tmux, this allows monitoring and interacting with worktree agent sessions from mobile SSH clients.

## Problem Statement

When running parallel agents via tmux + cursor-agent CLI inside the devcontainer (see #64), there's no way to connect from a mobile device or remote machine to monitor or interact with those sessions. The devcontainer is typically only accessible from the host machine. Tailscale would provide a stable, private Wireguard-based IP reachable from any device on the tailnet.

## Proposed Solution

1. **Add Tailscale to the devcontainer image** — install `tailscale` in the Containerfile.
2. **Configure SSH access** — ensure `sshd` is running and accessible over the Tailscale interface.
3. **Auth key management** — support `TS_AUTHKEY` env var for headless authentication (no browser login inside container).
4. **Justfile recipe** — `just tailscale-up` to start Tailscale and display the container's tailnet IP.
5. **Document the mobile workflow** — how to SSH in from a mobile client (e.g. Termius, Blink) and attach to tmux sessions.

## Alternatives Considered

- **Port forwarding / VS Code tunnels** — works for the host, but not for mobile clients on different networks without additional setup.
- **Cloudflare Tunnel** — similar capability but heavier, and Tailscale is more natural for peer-to-peer access.

## Additional Context

- Related: #64 (worktree/parallel agent support — provides the tmux sessions to connect to)
- Tailscale is free for personal use (up to 100 devices)
- Requires the container to run with `--cap-add=NET_ADMIN --device=/dev/net/tun` or equivalent

## Impact

- Developers who work across multiple devices benefit from seamless access to their devcontainer.
- Not a breaking change — Tailscale is opt-in (only starts when `just tailscale-up` is run or `TS_AUTHKEY` is set).

## Changelog Category

Added
