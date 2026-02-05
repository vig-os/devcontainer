---
type: issue
state: open
created: 2026-02-05T07:46:56Z
updated: 2026-02-05T07:47:24Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/43
comments: 0
labels: bug
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-05T07:47:40.728Z
---

# [Issue 43]: [[BUG] pip-licenses not installed in fresh workspace](https://github.com/vig-os/devcontainer/issues/43)

### Description

`pip-licenses` is not installed in a fresh workspace, leading to `pre-commit` failure

### Steps to Reproduce

1. Initialize fresh workspace
2. Set up user conf
3. Launch VS Code as a dev-container
4. Run `pre-commit`

### Expected Behavior

No errors

### Actual Behavior

1. Initial workspace
```bash
carlosvigo@vigolaptop:~/Documents/vigOS/test_project$ podman run -it --rm -v "./:/workspace"      ghcr.io/vig-os/devcontainer:dev /root/assets/init-workspace.sh
Enter a short name for your project (letters/numbers only, e.g. my_proj): test-project
Project short name set to: test_project
Enter the name of your organization, e.g. 'vigOS': vigOS
Organization name set to: vigOS
Initializing workspace from template...
Copying files from /root/assets/workspace to /workspace...
Warning: rsync not available, preserved files may be overwritten
Replacing placeholders in files...
Using build-time manifest (13 files)
Renaming src/template_project to src/test_project...
Setting executable permissions on shell scripts and hooks...
Workspace initialized successfully!

You can now start developing in your workspace.
```

2. Set up user conf
```bash
carlosvigo@vigolaptop:~/Documents/vigOS/test_project$ ./.devcontainer/scripts/copy-host-user-conf.sh 
Copied SSH public key from /home/carlosvigo/.ssh/id_ed25519_github.pub to ./.devcontainer/scripts/../.conf
Copied allowed-signers file from /home/carlosvigo/.config/git/allowed-signers to ./.devcontainer/scripts/../.conf
Generated valid .gitconfig at ./.devcontainer/scripts/../.conf/.gitconfig from effective config in current directory
Copied GitHub CLI config from /home/carlosvigo/.config/gh to ./.devcontainer/scripts/../.conf/gh
Exported GitHub CLI token to ./.devcontainer/scripts/../.conf/.gh_token
```

3. Launch VS Code as a dev-container
```bash
Running the initializeCommand from devcontainer.json...

Initializing devcontainer setup...
Copied SSH public key from /home/carlosvigo/.ssh/id_ed25519_github.pub to /home/carlosvigo/Documents/vigOS/test_project/.devcontainer/scripts/../.conf
Copied allowed-signers file from /home/carlosvigo/.config/git/allowed-signers to /home/carlosvigo/Documents/vigOS/test_project/.devcontainer/scripts/../.conf
Generated valid .gitconfig at /home/carlosvigo/Documents/vigOS/test_project/.devcontainer/scripts/../.conf/.gitconfig from effective config in current directory
Copied GitHub CLI config from /home/carlosvigo/.config/gh to /home/carlosvigo/Documents/vigOS/test_project/.devcontainer/scripts/../.conf/gh
Exported GitHub CLI token to /home/carlosvigo/Documents/vigOS/test_project/.devcontainer/scripts/../.conf/.gh_token
Detected: Podman rootless (Linux)
Configuring socket path: /run/user/1000/podman/podman.sock
Socket configuration complete (written to .env)
Initialization complete

>>>> Executing external compose provider "/usr/libexec/docker/cli-plugins/docker-compose". Please refer to the documentation for details. <<<<

>>>> Executing external compose provider "/usr/libexec/docker/cli-plugins/docker-compose". Please refer to the documentation for details. <<<<

[+] Running 1/1
 ✔ Container test_project_devcontainer-devcontainer-1  Started             2.8s 
Running the postCreateCommand from devcontainer.json...

Running post-create setup...
Syncing Python dependencies...
Resolved 119 packages in 424ms
Audited 115 packages in 17ms
Post-create setup complete
Running the postStartCommand from devcontainer.json...

Running the postAttachCommand from devcontainer.json...

Running post-attach setup...
Checking git repository status...
No git repository found, initializing...
Initialized empty Git repository in /workspace/test_project/.git/
Git repository initialized with main branch
Setting up git configuration...
Applying git configuration from /workspace/test_project/.devcontainer/.conf/.gitconfig...
Applying SSH public key from /workspace/test_project/.devcontainer/.conf/id_ed25519_github.pub...
SSH public key installed at /root/.ssh/id_ed25519_github.pub
Applying allowed-signers file from /workspace/test_project/.devcontainer/.conf/allowed-signers...
Allowed-signers file installed at /root/.config/git/allowed-signers
Verifying SSH agent socket for git signing...
Looking for signing key: SHA256:hYyNbKU/0AYqau9PS9I0tQzjkp1tAEO6qJIfWz01YCQ (SSH Key for GitHub authentication (ED25519))
Current SSH_AUTH_SOCK: /tmp/cursor-remote-ssh-53b7cce0-e0dd-4e4a-b6a8-8b60f4c05dba.sock
✓ Git signing key is accessible in SSH agent
256 SHA256:hYyNbKU/0AYqau9PS9I0tQzjkp1tAEO6qJIfWz01YCQ SSH Key for EXOMA GitHub authentication (ED25519)
Applying GitHub CLI config from /workspace/test_project/.devcontainer/.conf/gh...
GitHub CLI config installed at /root/.config/gh
Authenticating GitHub CLI...
^[[13;1R^[[13;1R^[]11;rgb:1414/1414/1414^[\^[]11;rgb:1414/1414/1414^[\^[]11;rgb:1414/1414/1414^[\^[[13;1R^[[13;1R^[[13;1R^[]11;rgb:1414/1414/1414^[\^[]11;rgb:1414/1414/1414^[\^[]11;rgb:1414/1414/1414^[\^[[13;17R^[[13;17R^[[13;17R^[]11;rgb:1414/1414/1414^[\^[]11;rgb:1414/1414/1414^[\^[]11;rgb:1414/1414/1414^[\^[[13;17R^[[13;17R^[[13;17RGitHub CLI authenticated successfully
Status output: github.com
  ✓ Logged in to github.com account c-vigo (/root/.config/gh/hosts.yml)
  - Active account: true
  - Git operations protocol: https
  - Token: gho_************************************
  - Token scopes: 'admin:public_key', 'gist', 'read:org', 'repo'
Token file removed for security
Setting up git hooks...
Git hooks configured to use .githooks directory
Commit message template configured (.gitmessage)
Setting up pre-commit hooks (this may take a few minutes)...
Pre-commit hooks installed successfully
Post-attach setup complete


Terminal is finished. Press any key to close the terminal.
```

4. Run `pre-commit`
```bash
root@152e2fab5b86:/workspace/test_project# source /root/assets/workspace/.venv/bin/activate
(test_project) root@152e2fab5b86:/workspace/test_project# git add .
(test_project) root@152e2fab5b86:/workspace/test_project# pre-commit 
branch-name (enforce <type>/<issue>-<summary>)...........................Passed
check for added large files..............................................Passed
check for case conflicts.................................................Passed
check json...............................................................Passed
check for merge conflicts................................................Passed
check for broken symlinks............................(no files to check)Skipped
check toml...............................................................Passed
check yaml...............................................................Passed
debug statements (python)................................................Passed
detect destroyed symlinks................................................Passed
detect private key.......................................................Passed
fix end of files.........................................................Passed
mixed line ending........................................................Passed
trim trailing whitespace.................................................Passed
ruff (legacy alias)......................................................Passed
ruff format..............................................................Passed
yamllint.................................................................Passed
shellcheck...............................................................Passed
pymarkdown...............................................................Passed
just (format justfiles)..................................................Failed
- hook id: just-fmt
- files were modified by this hook

Wrote justfile to `/workspace/test_project/justfile`

typos....................................................................Passed
pip-licenses (check dependency licenses).................................Failed
- hook id: pip-licenses
- exit code: 2

      Built test-project @ file:///workspace/test_project
Installed 1 package in 0.78ms
error: Failed to spawn: `pip-licenses`
  Caused by: No such file or directory (os error 2)
```


### Environment

- **OS**: Ubuntu 24.04
- **Container Runtime**: Podman 4.9.3
- **Image Version**: dev
- **Architecture**: AMD64

### Additional Context

#### Format `justfile`

Take this opportunity to fix `justfile` formatting for pre-commit compliance (see message above):

```ini
# ═══════════════════════════════════════════════════════════════════════════════
# MAIN JUSTFILE - Orchestrates all recipe sources
# ═══════════════════════════════════════════════════════════════════════════════

# Show available commands
[group('info')]
help:
    @just --list

# Import devcontainer-managed base recipes (replaced on upgrade)

import '.devcontainer/justfile.base'

# Import team-shared project recipes (git-tracked, preserved on upgrade)

import? 'justfile.project'

# Import personal recipes (gitignored, preserved on upgrade)

import? 'justfile.local'
```

### Possible Solution

- Add to project dependencies
- Install system-wide in `Containerfile`
