---
type: issue
state: closed
created: 2026-07-15T07:29:46Z
updated: 2026-07-15T08:29:52Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/1099
comments: 2
labels: bug, priority:medium, area:workspace, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: 1096
children: none
synced: 2026-07-15T11:04:52.410Z
---

# [Issue 1099]: [[BUG] Managed .yamllint / .pymarkdown (+ .pymarkdown.config.md) silently clobber consumer lint config on upgrade (same class as #878/#913)](https://github.com/vig-os/devkit/issues/1099)

## Summary

`.yamllint` and `.pymarkdown.config.md` are **fully-managed** scaffold files
(`init-workspace.sh` overwrites them on every `--force`, carrying the
*"regenerated on upgrade; local edits are lost"* banner), yet they are lint
**configs a consumer legitimately customizes** with repo-specific `ignore:`
globs, rule disables, and domain exceptions. On upgrade those edits are silently
destroyed and the hook then flags legitimate content — the exact failure that
**`.pre-commit-config.yaml` (#878)** and **`.typos.toml` (#913)** were fixed for
by promoting them to `PRESERVE_FILES`.

The same reasoning was never applied to `.yamllint` / `.pymarkdown.config.md`.
This is the class-A generalization identified in the epic (#1096): a managed
full-overwrite file with no durable consumer seam.

## Mechanism

- `assets/workspace/.yamllint` and `assets/workspace/.pymarkdown.config.md` are
  copied by the template and NOT listed in `PRESERVE_FILES` (init-workspace.sh),
  so `rsync` overwrites any consumer edits on `install.sh --force`.
- A consumer who adds a repo-specific yamllint `ignore:` (generated YAML, vendored
  manifests) or a pymarkdown rule disable (domain docs) loses it on the next
  upgrade; the hook then fails on files/rules it must not touch — identical to the
  #878/#913 symptom.

## Suggested fix

Mirror the **`.typos.toml` (#913)** promotion exactly for both files:

1. Add `".yamllint"` and `".pymarkdown.config.md"` to `PRESERVE_FILES` in
   `assets/init-workspace.sh`.
2. Add the `*_PREEXISTED` capture + `print_preserved_template_diff` call so the
   upgrade still surfaces template evolution against the preserved file (as
   `.typos.toml` / `.pre-commit-config.yaml` do).
3. The banner transform derives managed-vs-preserved text from `PRESERVE_FILES`
   (`tests/test_transforms.py`), so both files must render the **preserved**
   banner after promotion — verify no managed banner leaks.
4. Tests: extend `tests/bats/init-workspace.bats` (preserve-on-upgrade cases,
   mirroring the `.typos.toml`/pyproject preserve tests) and
   `tests/test_transforms.py` (preserved-banner coverage).

## Scope / non-goals

Only these two lint-config files. The broader "managed base + consumer fragment"
convention for files that cannot be whole-file preserved (root `.gitignore`) is
tracked separately in #1092. Editor/config files with a milder, lower-frequency
version of this concern (`.vscode/settings.json`, `.devcontainer/devcontainer.json`,
`SECURITY.md`) are observations in #1096, not in scope here.

Refs: #1096

---

# [Comment #1]() by [c-vigo]()

_Posted on July 15, 2026 at 07:47 AM_

Correction (scope): the file a consumer actually customizes for markdown-lint rules is **`.pymarkdown`** (the JSON config pymarkdown reads — `md012`/`md013`/`md036` etc.), not just `.pymarkdown.config.md` (its human-readable companion). `.pymarkdown` is comment-less JSON so it carries no managed banner (it is in `_BANNER_SKIP`), which is why the original triage keyed on the banner missed it. The correct fix preserves **`.pymarkdown`** — precedent: `renovate.json` is already a preserved, banner-skip-listed JSON in `PRESERVE_FILES`. `.pymarkdown.config.md` is preserved too so the config+doc stay a consumer-owned pair. `.yamllint` is unchanged (it is the real yamllint config).

---

# [Comment #2]() by [c-vigo]()

_Posted on July 15, 2026 at 08:29 AM_

Fixed by #1102 (merged to `dev`, commit `23dd89a7`; ships in the next release). Shipped: promoted **`.pymarkdown`** (the JSON config pymarkdown reads), **`.yamllint`**, and the **`.pymarkdown.config.md`** doc companion to `PRESERVE_FILES` — mirroring the `.typos.toml` (#913) change set — so consumer lint-rule exceptions survive `install.sh --force`. `.pymarkdown` stays un-bannered in `_BANNER_SKIP` like the already-preserved `renovate.json`. Part of #1096.

