---
type: issue
state: open
created: 2026-03-27T11:29:46Z
updated: 2026-03-27T11:29:46Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/467
comments: 0
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-03-28T04:26:12.663Z
---

# [Issue 467]: [feat(remote): auto-scaffold .devcontainer and smart image resolution](https://github.com/vig-os/devcontainer/issues/467)

## Summary

`devc-remote.sh` should handle the full lifecycle from "bare repo on GitHub" to "running devcontainer on remote" with zero manual setup. Currently it errors when `.devcontainer/` is missing and has no image resolution logic.

## Parent

- #70 (remote devcontainer orchestration)

## Use Cases

| # | Source | Has `.devcontainer/`? | What should happen |
|---|--------|----------------------|-------------------|
| 1 | `gh:org/repo`, not local | **No** | Clone → auto-scaffold `.devcontainer/` → resolve image → compose up |
| 2 | `gh:org/repo`, not local | **Yes** | Clone → resolve image → compose up |
| 3 | Local repo | Maybe | Push → clone/fetch on remote → (scaffold if needed) → resolve image → compose up |

## Design: Auto-Scaffold

When `devc-remote.sh` detects no `.devcontainer/` in the target repo:

1. Run `init-workspace.sh` from the devcontainer image on the remote
2. Use the bootstrapped dev image if available, otherwise pull `:latest` from GHCR
3. Continue with normal compose-up flow

```bash
# In preflight, instead of erroring:
if [[ "${DEVCONTAINER_EXISTS:-0}" != "1" ]]; then
    log_info "No .devcontainer/ found — scaffolding from devcontainer image..."
    # Resolve which image to use for scaffolding
    scaffold_image=$(resolve_scaffold_image)
    ssh "$SSH_HOST" "$RUNTIME run --rm -v '$REMOTE_PATH:/workspace' \
        $scaffold_image /root/assets/init-workspace.sh"
fi
```

## Design: Smart Image Resolution

The scaffolded (or existing) `devcontainer.json` / `docker-compose.yml` references an image tag. The remote needs to resolve that image.

### Resolution chain

```
1. Image already exists locally on remote?
   YES → compose up (fast path)
   NO  ↓
2. Is it a released tag (latest, semver)?
   YES → podman pull ghcr.io/vig-os/devcontainer:<tag> → compose up
   NO  ↓
3. Is it a dev/unreleased tag?
   Is devcontainer repo bootstrapped on remote?
   YES → rebuild from source → compose up
   NO  → error with actionable message:
         "Image :dev not in registry. Run: devc-remote.sh --bootstrap <host>"
```

### Tag semantics

| Tag | Source | Needs bootstrap? |
|-----|--------|-----------------|
| `latest` | GHCR registry | No — just `podman pull` |
| `0.3.1` (semver) | GHCR registry | No — just `podman pull` |
| `dev` | Local build | **Yes** — needs devcontainer repo + `scripts/build.sh` |
| custom | Depends | Resolved by trying pull first, then build |

### Scaffold tag selection

When `init-workspace.sh` scaffolds a new `.devcontainer/`:

| Context | Default tag | Rationale |
|---------|-------------|-----------|
| `--bootstrap` was run | `dev` | User explicitly set up dev builds |
| No bootstrap, GHCR accessible | `latest` | Zero setup, just pull |
| `--image-tag <tag>` flag | User-specified | Override for any case |

## Examples

```bash
# Use case 1: bare repo, no devcontainer, released image (zero bootstrap)
./scripts/devc-remote.sh ksb-meatgrinder gh:MorePET/duplet_patients_analysis
# → clone → scaffold with :latest → pull image → compose up

# Use case 1b: bare repo, bleeding edge (needs bootstrap)
./scripts/devc-remote.sh ksb-meatgrinder gh:MorePET/duplet_patients_analysis --image-tag dev
# → clone → scaffold with :dev → use bootstrapped image → compose up

# Use case 2: repo with existing devcontainer
./scripts/devc-remote.sh ksb-meatgrinder gh:vig-os/fd5
# → clone → .devcontainer exists → read tag from compose → pull/use → compose up

# Use case 3: local repo to remote
just remote-devc ksb-meatgrinder
# → push → clone on remote → (scaffold if needed) → compose up
```

## Acceptance Criteria

- [ ] `devc-remote.sh` auto-scaffolds `.devcontainer/` when missing (via `init-workspace.sh`)
- [ ] `--image-tag <tag>` flag to override scaffold/image tag
- [ ] Image resolution chain: local → pull → build → error
- [ ] Default to `:latest` (released) when no bootstrap present
- [ ] Default to `:dev` when bootstrap is present
- [ ] `init-workspace.sh` respects tag override via env or flag
- [ ] Works for all three use cases (gh: without devcontainer, gh: with devcontainer, local repo)
- [ ] Error messages guide user to correct action (bootstrap vs pull)
- [ ] Tests for scaffold + resolution logic

## Related

- #70 (parent: remote devcontainer orchestration)
- #464 (secure secret resolution)
- #465 (SSH key security enforcement)
