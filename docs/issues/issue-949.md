---
type: issue
state: closed
created: 2026-07-09T06:04:04Z
updated: 2026-07-09T13:05:01Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/949
comments: 0
labels: bug, priority:high, area:workspace, semver:patch
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:18.349Z
---

# [Issue 949]: [fix(workspace): upgrade preview report is blank on the Nix image (find misses store symlinks)](https://github.com/vig-os/devkit/issues/949)

## Summary

The upgrade file report (`--preview` and the interactive `--force` confirmation) added in #886 shows **empty OVERWRITTEN / ADDED / PRESERVED sections on the Nix-built image**, so it tells a consumer *"No existing files would be overwritten. No new files would be added."* immediately before an upgrade that actually rewrites the managed scaffold. This defeats the reviewable-upgrade safety net #886 exists to provide.

Found during local `0.5.0-rc2` validation against real consumers (see PR #938 comment). Verified on `talys`: `--preview` reports nothing, a real `--force` rewrites ~21 tracked files.

## Root cause

`assets/init-workspace.sh:534` classifies template files with:

```sh
done < <(find "$TEMPLATE_DIR" -type f ! -path "*/.git/*" -print0)
```

On the Nix image the baked template `/root/assets/workspace` is a tree of **symlinks into the nix store** (the read-only-symlink layout the script itself documents near the `rsync -avL` copy). `find … -type f` does **not** match symlinks, so the loop iterates zero files and every classification bucket (OVERWRITTEN/ADDED/PRESERVED) stays empty. The real copy uses `rsync -avL`, which dereferences the links and works — so only the *report* is blind. The `DELETED` (mode-prune) section is unaffected because it scans the workspace, not the template.

Evidence from the `0.5.0-rc2` image:

```
find    /root/assets/workspace -type f  →    0
find -L /root/assets/workspace -type f  → 1872
find    /root/assets/workspace -type l  →  998
```

## Expected vs actual

- **Expected:** `--preview` on an already-scaffolded consumer lists the managed files that would be overwritten and any newly added files.
- **Actual:** every run reports "No existing files would be overwritten / No new files would be added" regardless of tree state.

## Fix

Make the classifier follow symlinks — `find -L "$TEMPLATE_DIR" -type f …` — matching the `rsync -avL` copy semantics. Single-site change (line 534 is the only `find` over `$TEMPLATE_DIR`).

## Acceptance criteria (TDD)

- A host-runnable test (e.g. in `tests/bats/init.bats`, overriding `TEMPLATE_DIR`/`WORKSPACE_DIR`) that seeds a **symlinked** template file already present in the workspace, runs `init-workspace.sh --preview --force`, and asserts the file appears in the OVERWRITTEN section. This test must **fail** on current `main`/`release` and **pass** after the fix.
- No regression to the DELETED/PRESERVED reporting or the actual copy/prune behaviour.

