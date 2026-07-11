---
type: issue
state: closed
created: 2026-03-27T11:51:44Z
updated: 2026-07-08T08:13:47Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devkit/issues/468
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:20.025Z
---

# [Issue 468]: [feat(remote): auto-detect GPU and configure passthrough in devc-remote.sh](https://github.com/vig-os/devkit/issues/468)

## Summary

`devc-remote.sh` should detect GPU availability on the remote host during preflight and auto-configure GPU passthrough in the compose stack. Currently GPU setup is fully manual.

## Parent

- #70 (remote devcontainer orchestration)

## Problem

Projects like `duplet_patients_analysis` (JAX, PyMC) need GPU access. The user must manually add GPU config to `docker-compose.local.yaml` — error-prone and runtime-dependent (podman CDI vs docker `deploy.resources`).

## Detection (preflight)

Add GPU detection to the existing remote preflight heredoc:

```bash
# GPU detection
if command -v nvidia-smi &>/dev/null; then
    GPU_AVAILABLE=1
    GPU_NAME=$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)
    GPU_MEM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1)
    # Check NVIDIA Container Toolkit
    if command -v nvidia-ctk &>/dev/null; then
        NVIDIA_CTK=1
        # Check CDI spec (podman >= 4.1)
        CDI_AVAILABLE=$(nvidia-ctk cdi list 2>/dev/null | grep -c nvidia || echo 0)
    fi
fi
```

## Injection (compose config)

GPU config varies by runtime:

### Podman with CDI (preferred, modern)

```yaml
services:
  devcontainer:
    devices:
      - nvidia.com/gpu=all
```

Requires: `nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml` (one-time setup, can be part of `--bootstrap`).

### Podman without CDI (legacy)

```yaml
services:
  devcontainer:
    security_opt:
      - label=disable
    hooks:
      prestart:
        - path: /usr/bin/nvidia-container-toolkit
```

### Docker Compose

```yaml
services:
  devcontainer:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## Proposed UX

### Auto-detect + prompt

```
$ ./scripts/devc-remote.sh ksb-meatgrinder:/path/to/project
ℹ  GPU detected: NVIDIA T400 4GB (nvidia-container-toolkit available)
ℹ  Enable GPU passthrough? [Y/n]
✓  GPU passthrough configured (CDI: nvidia.com/gpu=all)
```

### Flags

```bash
--gpu           # Enable GPU passthrough (auto-detect method)
--gpu=all       # All GPUs
--gpu=0         # Specific GPU index
--no-gpu        # Explicitly disable (skip detection)
```

### Where to inject

GPU config should go into `docker-compose.local.yaml` (personal/machine-specific, not committed). Same injection pattern as Tailscale key injection.

For projects that *always* need GPU, they can add it to `docker-compose.project.yaml` (team-shared, committed).

## Bootstrap integration

`--bootstrap` should:
1. Detect NVIDIA toolkit
2. Generate CDI spec if missing: `sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`
3. Report GPU status

## Acceptance Criteria

- [ ] GPU detection in remote preflight (nvidia-smi + nvidia-ctk + CDI)
- [ ] Auto-configure compose GPU based on runtime (podman CDI / podman legacy / docker)
- [ ] `--gpu` / `--no-gpu` flags
- [ ] CDI spec generation in `--bootstrap`
- [ ] Inject GPU config into `docker-compose.local.yaml`
- [ ] Support `docker-compose.project.yaml` for always-GPU projects
- [ ] Report GPU info in preflight output
- [ ] Tests (mock nvidia-smi / nvidia-ctk responses)

## Context

- ksb-meatgrinder: NVIDIA T400 4GB, `nvidia-container-toolkit` installed, podman with `crun`
- duplet_patients_analysis: JAX + PyMC (GPU-accelerated Bayesian inference)

## Related

- #70 (parent: remote devcontainer orchestration)
- #467 (auto-scaffold and image resolution)
- #464 (secure secret resolution)
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 08:13 AM_

Closing as part of an agreed backlog cleanup (with @gerchowl). The remote-devcontainer / `devc-remote` / Tailscale initiative predates the Nix + Claude-native migration (#625) and has had no activity since Feb–Mar 2026. If remote provisioning is wanted again it will be re-planned from scratch after the devkit rename (#781). Reopen/refile if revived.

