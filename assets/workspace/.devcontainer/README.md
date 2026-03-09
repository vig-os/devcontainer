# Devcontainer Reference

This folder contains everything VS Code needs to launch the
[vigOS development container](https://github.com/vig-os/devcontainer) inside your project.

- **Version**: This is an unreleased development version

## Lifecycle scripts

1. `.devcontainer/scripts/initialize.sh` – host-side hook that runs before VS Code builds the container.
   - `.devcontainer/scripts/copy-host-user-conf.sh` – copies host git/SSH/GitHub CLI config into `.devcontainer/.conf/`.
2. `.devcontainer/scripts/post-create.sh` – container-side hook that runs when the container is created for the first time.
Add your custom setup commands here to install any dependencies or tools needed for your project.
3. `.devcontainer/scripts/post-attach.sh` – container-side hook that is run every time you launch your project:
   - `scripts/init-git.sh` to initialize or reuse the project repo
   - `scripts/setup-git-conf.sh` to wire up GitHub authentication, commit signing, and allowed signers
   - `scripts/init-precommit.sh` to install the pre-commit hooks that live under `.githooks/`

You rarely need to run these manually; VS Code executes them automatically via `initializeCommand`, `postCreateCommand`, and `postAttachCommand`.
If you do re-run them, make sure to use the same working directory that VS Code would (`project/.devcontainer` on the host
or `/workspace/<project>/.devcontainer` inside the container).

## Mounts and multi-root workspaces

This devcontainer supports mounting additional folders/projects using Docker Compose override files.

1. **Copy the example file:**

   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

2. **Edit the file and uncomment the mounts you need:**

   ```yaml
   version: '3.8'

   services:
     devcontainer:
       volumes:
         - ../other-project:/workspace/other-project:cached
         - ~/shared-libs:/workspace/shared:cached
   ```

Paths to other mounts can be absolute or relative to the main project folder.
   You can also specify read-only mount with `ro` instead of `cached`.
   Your settings will remain local since `docker-compose.override.yml` is git-ignored.

1. **Rebuild the devcontainer:**
   In VS Code: `Cmd/Ctrl+Shift+P` → "Dev Containers: Rebuild Container"

2. **Accessing mounted folders:**
   Mounted folders are accessible from the terminal in `/workspace/`:

   ```bash
   # List all workspace folders
   ls -la /workspace/

   # Access mounted project
   cd /workspace/other-project
   ```

3. **Configure VS Code workspace (optional):**
   To browse and edit mounted folders from VS Code's Explorer, copy the workspace example:

   ```bash
   cp workspace.code-workspace.example workspace.code-workspace
   ```

   Then customize the `folders` array in `workspace.code-workspace` to include any mounted
   projects you want to see in the editor. The file is git-ignored, so your personal
   configuration stays local.

## Tailscale SSH

Connect to the devcontainer over Tailscale SSH instead of the devcontainer protocol.
This enables tools like Cursor GUI to execute shell commands inside the container via SSH remote.

### Prerequisites

1. A [Tailscale](https://tailscale.com/) account with SSH enabled in your tailnet ACLs.
2. An auth key (ephemeral + reusable recommended) from
   [Tailscale Admin → Settings → Keys](https://login.tailscale.com/admin/settings/keys).

### Setup

1. Add the auth key to your local compose override (git-ignored):

   ```yaml
   # .devcontainer/docker-compose.local.yaml
   services:
     devcontainer:
       environment:
         - TAILSCALE_AUTHKEY=tskey-auth-XXXX
         # Optional: override the auto-generated hostname
         # - TAILSCALE_HOSTNAME=myproject-devc-mybox
   ```

2. Rebuild the devcontainer (`Cmd/Ctrl+Shift+P` → "Dev Containers: Rebuild Container").

3. Tailscale installs on first create (~10 s) and connects on every start.
   The container appears in your tailnet as `<project>-devc-<hostname>`.

4. Connect via SSH from Cursor or any SSH client:

   ```bash
   ssh root@<tailscale-hostname>
   ```

### Tailscale ACL configuration

Your tailnet must allow SSH access. Add a rule like this to your
[ACL policy](https://login.tailscale.com/admin/acls):

```json
{
  "ssh": [
    {
      "action": "accept",
      "src": ["autogroup:members"],
      "dst": ["autogroup:self"],
      "users": ["root", "autogroup:nonroot"]
    }
  ]
}
```

### How it works

- `setup-tailscale.sh install` runs during `postCreateCommand` — installs Tailscale if `TAILSCALE_AUTHKEY` is set.
- `setup-tailscale.sh start` runs during `postStartCommand` — starts `tailscaled` (userspace networking, no `/dev/net/tun` needed) and authenticates.
- When `TAILSCALE_AUTHKEY` is unset, both hooks are silent no-ops.

## Updating the template

If you synchronize with a newer release of the vigOS devcontainer image,
re-run `init-workspace.sh --force` from the image to refresh this folder.
Commit your project changes first: the force flag overwrites files in
`.devcontainer/`, `.githooks/`, and docs such as this README.
