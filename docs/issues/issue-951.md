---
type: issue
state: closed
created: 2026-07-09T08:47:29Z
updated: 2026-07-09T13:05:02Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/951
comments: 0
labels: bug, priority:medium, area:workspace, semver:patch
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:17.965Z
---

# [Issue 951]: [fix(workspace): upgrade file report over-reports ADDED (find walk misses rsync's .venv exclude)](https://github.com/vig-os/devkit/issues/951)

## Summary

The upgrade file report (`--preview` and interactive `--force`) massively **over-reports the ADDED section**: ~1763 of ~1867 listed entries are phantom `.venv/.../site-packages/*` files that the actual upgrade never writes. Surfaced during `0.5.0-rc3` consumer validation (all four consumers + a controlled repo showed it).

This is a direct side-effect of the #949 fix. That fix changed the report classifier to `find -L` so it would follow the Nix image's store-symlink template (correctly fixing the previously-blank OVERWRITTEN section). But `find -L` now also follows the baked template's `.venv` symlink tree.

## Root cause

`assets/init-workspace.sh:534` (the report classifier):

```sh
done < <(find -L "$TEMPLATE_DIR" -type f ! -path "*/.git/*" -print0)
```

It excludes only `.git`, whereas the real copy excludes more (`assets/init-workspace.sh:669` and `:717`):

```sh
rsync -avL --delete --exclude='.git' --exclude='.venv' --exclude='docs/issues/' --exclude='docs/pull-requests/' "$TEMPLATE_DIR/" "$WORKSPACE_DIR/"
```

The image template `/root/assets/workspace` carries a `.venv`, so the report walk enumerates it while the copy skips it. Verified in the `0.5.0-rc3` image:

```
find    /root/assets/workspace -type f                 →    0   (pre-#949, symlinks missed)
find -L /root/assets/workspace -type f                 → 1872
find -L /root/assets/workspace -type f -path '*/.venv/*'   → 1763   (phantom ADDED)
find -L /root/assets/workspace -type f ! -path '*/.venv/*' ! -path '*/.git/*' → 109   (real)
```

## Impact

**Report-only — no data risk.** The real `--force` upgrade uses the rsync excludes, so no `.venv`/site-packages is ever written to a consumer (verified: absent from every upgraded tree). The safety-critical OVERWRITTEN section is accurate. But the ADDED list is unusable (inflated ~18×), undermining the #886 preview feature.

## Fix

Mirror the copy's static excludes in the report `find`:

```sh
done < <(find -L "$TEMPLATE_DIR" -type f \
    ! -path "*/.git/*" ! -path "*/.venv/*" \
    ! -path "*/docs/issues/*" ! -path "*/docs/pull-requests/*" -print0)
```

(`.venv` is the one that actually leaks today; `docs/issues/`/`docs/pull-requests/` are added for parity with the rsync copy so future template changes can't leak them either.)

## Acceptance criteria (TDD)

- Extend the bats coverage in `tests/bats/init-workspace.bats`: a **symlinked `.venv/...` file** placed under `TEMPLATE_DIR` must NOT appear in the ADDED section, while a real symlinked template file still does. Fails before the fix, passes after.
- No change to the OVERWRITTEN/PRESERVED/DELETED behaviour (the #949 tests must still pass).

Relates to #949.

