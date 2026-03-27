---
type: issue
state: closed
created: 2026-03-11T07:35:26Z
updated: 2026-03-11T09:23:34Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/254
comments: 0
labels: bug
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-03-12T07:59:30.725Z
---

# [Issue 254]: [[BUG] just without arguments runs lint instead of listing recipes](https://github.com/vig-os/devcontainer/issues/254)

### Description

Running `just` without arguments should display the list of available recipes (via the `default` recipe), but instead it runs the `lint` recipe (`uv run ruff check .`).

### Steps to Reproduce

1. Run `just` with no arguments in the project root

### Expected Behavior

`just` displays the list of available recipes (equivalent to `just --list --unsorted`), as defined by the `default` recipe in the justfile.

### Actual Behavior

`just` runs the `lint` recipe (`uv run ruff check .`) because `lint` is the first recipe in the file and `just` uses the first recipe as its default.

### Environment

- **OS**: Linux 6.17.0-14-generic
- **just**: system-installed

### Additional Context

The `default` recipe exists at line 37 of the justfile, but the `lint` recipe at line 11 comes first. In `just`, the first recipe in the file is the one that runs when invoked without arguments. The `lint` / `format` / `precommit` quality recipes were likely added above `default` at some point, breaking this behavior.

### Possible Solution

Move the `default` recipe (and optionally the entire "INFO" section) above the "CODE QUALITY" section so it becomes the first recipe in the file.

### Changelog Category

Fixed

- [ ] TDD compliance (see .cursor/rules/tdd.mdc)
