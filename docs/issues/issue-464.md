---
type: issue
state: open
created: 2026-03-27T10:29:33Z
updated: 2026-03-27T10:30:15Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/464
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:13.166Z
---

# [Issue 464]: [feat(remote): secure secret resolution for devc-remote.sh](https://github.com/vig-os/devcontainer/issues/464)

## Summary

`devc-remote.sh` currently requires secrets (`CLAUDE_CODE_OAUTH_TOKEN`, `TS_CLIENT_ID`, `TS_CLIENT_SECRET`) as plain environment variables. This is insecure (visible in shell history, process lists, `.zshenv`) and requires manual `claude setup-token` + copy-paste.

The script should resolve secrets automatically via a fallback chain with secure storage backends.

## Problem

1. **No auto-extraction** — user must manually run `claude setup-token`, copy the OAT, and set an env var
2. **No secure storage** — tokens sit in plain text env vars or dotfiles
3. **Applies to all secrets** — Claude Code OAuth, Tailscale client ID/secret all have the same problem

## Proposed Design

### `resolve_secret()` fallback chain

```bash
resolve_secret() {
    local name="$1"
    # 1. Env var (explicit override, backwards-compatible)
    # 2. OS keychain:
    #    - macOS: security find-generic-password (triggers Touch ID)
    #    - Linux desktop: secret-tool lookup (GNOME Keyring / KDE Wallet via libsecret)
    # 3. Bitwarden CLI (bw get password) — prompts for master password
    # 4. age-encrypted file (~/.config/devc-remote/secrets.age)
    #    - Uses SSH keys as identity (no extra key management)
    #    - Best fallback for headless Linux / SSH servers
    # 5. Fail with actionable error message
}
```

### Backend detection (auto)

| Platform | Primary | Fallback 1 | Fallback 2 |
|----------|---------|------------|------------|
| macOS | `security` (Keychain, Touch ID) | `bw` CLI | `age` file |
| Linux (desktop) | `secret-tool` (GNOME Keyring / KDE Wallet) | `bw` CLI | `age` file |
| Linux (headless) | `bw` CLI | `age` file | — |
| Any | env var override | always works | — |

### Secret storage

After first `claude setup-token`, offer to store the token in the best available backend:

- **macOS keychain** — `security add-generic-password -s "devc-remote" -a "<name>" -w`
  - Triggers Touch ID / biometric on read
- **Linux `secret-tool`** — `secret-tool store --label "devc-remote/<name>" service devc-remote name <name>`
  - Integrates with GNOME Keyring / KDE Wallet (unlocked with login session)
- **Bitwarden CLI** — `bw create item` in a "devc-remote" folder
  - `bw unlock` prompts for master password
- **`age`-encrypted file** — `age -r <pubkey> -o ~/.config/devc-remote/secrets.age`
  - Uses SSH keys as identity (`age -d -i ~/.ssh/id_ed25519`)
  - No daemon, no GUI, works over SSH — ideal for headless servers
  - Available in nixpkgs (`pkgs.age`)

### Secrets covered

| Secret | Current | Proposed |
|--------|---------|----------|
| `CLAUDE_CODE_OAUTH_TOKEN` | env var | keychain / secret-tool / bw / age / env var |
| `TS_CLIENT_ID` | env var | keychain / secret-tool / bw / age / env var |
| `TS_CLIENT_SECRET` | env var | keychain / secret-tool / bw / age / env var |
| `GHCR_TOKEN` | `gh auth token` | already OK (gh handles its own auth) |

### UX flow (first time)

```
$ ./scripts/devc-remote.sh --open ssh myserver
ℹ  Claude Code OAuth token not found.
ℹ  Run 'claude setup-token' to generate one, then re-run this command.
    The token will be stored in your macOS keychain (Touch ID protected).
```

### UX flow (subsequent runs, macOS)

```
$ ./scripts/devc-remote.sh --open ssh myserver
🔐 [Touch ID prompt]
✓  Claude Code auth forwarded
✓  Tailscale key injected
```

### UX flow (headless Linux with age)

```
$ ./scripts/devc-remote.sh --open ssh myserver
🔐 Decrypting secrets with ~/.ssh/id_ed25519...
✓  Claude Code auth forwarded
✓  Tailscale key injected
```

## Acceptance Criteria

- [ ] `resolve_secret()` function with env → keychain/secret-tool → bw → age fallback chain
- [ ] `--store-secret <name>` subcommand to save a secret to the preferred backend
- [ ] Auto-detect backend: keychain (macOS), secret-tool (Linux desktop), bw, age, in order
- [ ] All three secret types migrated to use `resolve_secret()`
- [ ] Backwards-compatible: plain env vars still work as first-priority override
- [ ] `age` fallback for headless environments using SSH keys as identity
- [ ] Tests for fallback chain (mock keychain/secret-tool/bw/age)

## Related

- #70 (parent: remote devcontainer orchestration)
- `setup-claude.sh` — consumes `CLAUDE_CODE_OAUTH_TOKEN` in container
- `setup-tailscale.sh` — consumes `TAILSCALE_AUTHKEY` in container
