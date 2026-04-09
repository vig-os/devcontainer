# Tailscale SSH for Devcontainers

Design document for opt-in Tailscale SSH access to vigOS devcontainers.
Prototyped in `vig-os/fd5`, upstreamed here.

Refs: #208

## Problem

Cursor GUI connected to a devcontainer via the devcontainer protocol cannot
execute shell commands through the AI agent. The agent's shell tool fails to
route commands into the container's remote execution context. This is a Cursor
IDE limitation, not a container or project issue.

VS Code's devcontainer protocol works fine. Cursor's CLI/terminal mode also
works. Only Cursor GUI + devcontainer protocol is broken.

## Solution

Run Tailscale inside the devcontainer with SSH enabled. Connect Cursor via
SSH remote (`ssh root@<hostname>`) instead of the devcontainer protocol.
No jump hosts, no port forwarding — direct mesh access over the tailnet.

## Architecture decisions

| Decision | Choice | Rationale |
|---|---|---|
| Networking mode | `--tun=userspace-networking` | No `/dev/net/tun` device needed. Tailscale SSH is handled by the daemon directly, not through the TUN interface. Works in any container runtime without extra device mounts. |
| SSH server | Tailscale SSH (`--ssh`) | No need to install/configure openssh-server. Auth is handled by Tailscale ACLs. |
| Auth mechanism | `TAILSCALE_AUTHKEY` env var | Passed via `docker-compose.local.yaml` (git-ignored). Recommended: reusable + ephemeral keys so stale containers auto-expire. |
| Opt-in strategy | No-op when `TAILSCALE_AUTHKEY` is unset | Install is skipped in post-create, start is skipped in post-start. Zero impact on users who don't set the key. |
| Install method | `curl -fsSL https://tailscale.com/install.sh \| sh` | Official installer, idempotent. Runs once in post-create. |
| Daemon lifecycle | `setsid tailscaled ... &` in `postStartCommand` | `setsid` detaches the daemon from the shell process group so it survives when `postStartCommand` exits. Without `setsid`, the daemon dies with the parent shell. |
| State persistence | `/var/lib/tailscale/tailscaled.state` | Inside the container volume. Lost on container recreate, which is fine with ephemeral auth keys (re-registers automatically). |
| Hostname | `TAILSCALE_HOSTNAME` env var, default `<project>-devc-<server>` | Disambiguates same repo on different machines. Project name is parsed from `devcontainer.json`'s `name` field. Override via env var. |

## Lifecycle hook placement

| Hook | Script | Tailscale action |
|------|--------|-----------------|
| `postCreateCommand` | `post-create.sh` | `setup-tailscale.sh install` — installs binary once |
| `postStartCommand` | `post-start.sh` | `setup-tailscale.sh start` — starts daemon + connects |

`postStartCommand` runs on every container start (create + restart), **before**
the IDE attaches. This is critical — `postAttachCommand` runs in a transient
shell tied to the IDE session, and background processes started there die when
the shell exits.

## Files

| File | Role |
|------|------|
| `assets/workspace/.devcontainer/scripts/setup-tailscale.sh` | Single script with `install` and `start` subcommands |
| `assets/workspace/.devcontainer/scripts/post-create.sh` | Calls `setup-tailscale.sh install` |
| `assets/workspace/.devcontainer/scripts/post-start.sh` | Calls `setup-tailscale.sh start` |
| `assets/workspace/.devcontainer/docker-compose.local.yaml` | Commented example for `TAILSCALE_AUTHKEY` |
| `assets/workspace/.devcontainer/README.md` | User-facing setup instructions |

## User setup

### 1. Configure Tailscale SSH ACLs

The tailnet's ACL policy must allow SSH access. In the
[Tailscale admin console](https://login.tailscale.com/admin/acls/file), add:

```jsonc
"ssh": [
  {
    "action": "accept",
    "src":    ["autogroup:member"],
    "dst":    ["autogroup:self"],
    "users":  ["root", "autogroup:nonroot"]
  }
]
```

### 2. Generate a Tailscale auth key

Generate at https://login.tailscale.com/admin/settings/keys
(Reusable + Ephemeral recommended).

### 3. Configure the devcontainer

Edit `.devcontainer/docker-compose.local.yaml`:

```yaml
services:
  devcontainer:
    environment:
      - TAILSCALE_AUTHKEY=tskey-auth-XXXX
      - TAILSCALE_HOSTNAME=myproject-devc-mybox  # optional
```

### 4. Rebuild

Rebuild the devcontainer. Post-create installs Tailscale (~10s on first build).
Post-start connects to the tailnet on every start.

### 5. Connect

```bash
ssh root@<tailscale-hostname>
```

For Cursor, use "Remote - SSH" to connect to `root@<hostname>`. On first
connection, authenticate the Cursor remote server:

```bash
cursor tunnel --accept-server-license-terms --name <hostname>
```

## Programmatic auth key generation

Instead of manual key creation in the admin console, auth keys can be generated
via the Tailscale API using an OAuth client. This enables fully automated setup.

### Setup

1. Create an OAuth client in the [admin console](https://login.tailscale.com/admin/settings/oauth)
   with scope `auth_keys` (write) and tag(s) like `tag:devcontainer`.
2. Store `TS_CLIENT_ID` and `TS_CLIENT_SECRET` per-user (keychain, vault, `.env.local`).

### Key generation flow

```bash
# 1. Get an OAuth access token
TOKEN=$(curl -s -d "client_id=$TS_CLIENT_ID" \
  -d "client_secret=$TS_CLIENT_SECRET" \
  "https://api.tailscale.com/api/v2/oauth/token" | jq -r .access_token)

# 2. Create an ephemeral + reusable auth key
AUTH_KEY=$(curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "capabilities": {
      "devices": {
        "create": {
          "reusable": true,
          "ephemeral": true,
          "tags": ["tag:devcontainer"]
        }
      }
    }
  }' \
  "https://api.tailscale.com/api/v2/tailnet/-/keys" | jq -r .key)
```

### Integration point

`initialize.sh` (host-side, before container build) could:
1. Check if `TAILSCALE_AUTHKEY` is already set in `docker-compose.local.yaml`
2. If not, check for `TS_CLIENT_ID` + `TS_CLIENT_SECRET` in environment
3. Generate an ephemeral key via the API
4. Inject it into `docker-compose.local.yaml`

This is a future enhancement — the current implementation requires manual key
configuration, which is sufficient for the initial release.

## Known gap: git commit signing over Tailscale SSH

When connecting via Tailscale SSH (instead of the devcontainer protocol),
**git commit signing does not work out of the box**.

The devcontainer image sets `user.signingkey` to an SSH public key
(`/root/.ssh/id_ed25519_github.pub`), but two things are missing:

1. **The private key is not present.** Only the `.pub` file exists inside the
   container. The private key lives on the host and is normally forwarded via
   SSH agent forwarding — but Tailscale SSH doesn't forward the host's SSH
   agent into the container session.

2. **Git signing config is incomplete.** The following settings are not set:

   ```gitconfig
   [commit]
       gpgsign = true
   [gpg]
       format = ssh
   [gpg "ssh"]
       allowedSignersFile = <path>   # needed for verification only
   ```

### Workarounds

- **Forward the SSH agent manually.** SSH into the container with `ssh -A root@<hostname>`
  so the agent is available. Then set the missing git config:

  ```bash
  git config --global commit.gpgsign true
  git config --global gpg.format ssh
  ```

- **Copy the private key into the container.** Mount or copy the signing key
  via `docker-compose.local.yaml` volume mount. Less secure (key at rest in
  container).

- **Use a container-local signing key.** Generate a key inside the container,
  register it with GitHub, and configure git to use it.

### Future fix

The `setup-tailscale.sh start` script should detect whether an SSH agent is
available and, if not, print a warning that commit signing will not work. The
git signing config (`commit.gpgsign`, `gpg.format`) should be set alongside
`user.signingkey` in the devcontainer image or init script so that signing
works automatically when the key is available.

## Future considerations

- **Bake Tailscale into the container image** to avoid the ~10s install latency
  on first create. Trade-off: image size (~30MB) vs. cold-start time.
- **Hostname templating** via `init-workspace.sh` — the `{{SHORT_NAME}}`
  placeholder could feed the default hostname.
- **`docker-compose.local.yaml` template** — include commented Tailscale
  example in the template that `init-workspace.sh` generates.
- **Tailscale ACL documentation** — ship a recommended ACL snippet in the
  devcontainer README or docs.
- **Programmatic key generation** — integrate OAuth-based key generation into
  `initialize.sh` for zero-touch setup (see section above).
