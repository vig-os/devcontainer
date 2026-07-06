---
type: issue
state: open
created: 2026-06-24T12:53:46Z
updated: 2026-06-24T12:53:46Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/685
comments: 0
labels: bug, priority:high, area:workspace, semver:patch
assignees: none
milestone: none
projects: none
parent: 625
children: none
synced: 2026-06-26T06:17:57.194Z
---

# [Issue 685]: [[BUG] just build fails: missing containers policy.json when podman comes from the dev-shell (NixOS)](https://github.com/vig-os/devcontainer/issues/685)

## Description

On a NixOS host that gets `podman` from the **flake dev-shell** (rather than from the system `virtualisation.containers`/`virtualisation.podman` NixOS module), `just build` fails at the `podman load` step because no container-signature `policy.json` exists at `~/.config/containers/policy.json` or `/etc/containers/policy.json`.

The NixOS `virtualisation.containers` module is what normally installs `/etc/containers/policy.json`. A user who provisions podman purely via the dev-shell (the intended #625 onboarding path) never gets that file, so `podman` cannot load any image.

The onboarding gap: `scripts/init.sh`'s advisory host check (`scripts/init.sh:229`) uses `podman info`, which does **not** require `policy.json`. So `just init` reports the runtime as working (green), and the failure only surfaces later at `just build`.

## Steps to Reproduce

1. On a NixOS host **without** `virtualisation.containers.enable`/`virtualisation.podman.enable`, with no `~/.config/containers/policy.json` and no `/etc/containers/policy.json`.
2. Enter the dev-shell (`direnv allow` / `nix develop`) so `podman` comes from the flake.
3. Run `just build`.

## Expected Behavior

`just build` completes: the image builds and loads into podman. Onboarding (`just init`) either ensures a usable `policy.json` exists or warns clearly that one is required before `just build`.

## Actual Behavior

`nix build .#devcontainerImage` succeeds, but `podman load -i result` fails:

```
Error: payload does not match any of the supported image formats:
 * oci: no policy.json file found at any of the following: "~/.config/containers/policy.json", "/etc/containers/policy.json"
 * oci-archive: ...
 * docker-archive: ...
 * dir: ...
error: recipe `build` failed with exit code 125
```

## Environment

- **OS**: NixOS
- **Container Runtime**: Podman 5.8.2 (from the flake dev-shell, `/nix/store/...-podman-5.8.2`)
- **Image Version/Tag**: `.#devcontainerImage` (`just build`)
- **Architecture**: x86_64

## Root cause

podman's containers/image library requires a signature-verification `policy.json`; there is **no env-var override** and `podman load` exposes **no `--signature-policy` flag** in this build — the file must exist at one of the two lookup paths.

## Suggested fix

In `scripts/init.sh`'s advisory host-checks block (around `scripts/init.sh:226-238`): detect a missing `policy.json` at both lookup locations and create the user-level `~/.config/containers/policy.json` with the standard permissive default (idempotent), or guide the user. Document the requirement in `docs/NIX.md`.

Standard permissive default (same content the NixOS module / `containers-common` installs):

```json
{ "default": [ { "type": "insecureAcceptAnything" } ] }
```

### Workaround

```bash
mkdir -p ~/.config/containers
printf '{ "default": [ { "type": "insecureAcceptAnything" } ] }\n' > ~/.config/containers/policy.json
```

Refs: #625

