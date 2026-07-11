---
type: issue
state: closed
created: 2026-07-07T09:47:45Z
updated: 2026-07-08T11:27:33Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/892
comments: 1
labels: bug, priority:medium, area:workspace
assignees: none
milestone: 0.5
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:28.666Z
---

# [Issue 892]: [fix(workspace): template sync recipe uses --all-extras --all-groups, breaking repos with platform-limited optional extras](https://github.com/vig-os/devkit/issues/892)

### Description

Found during 0.4.0 consumer field-validation (EXOMA/hyrr) and scoped out of #877 (see PR #891 discussion).

The 0.4.0 scaffold template changed the `sync` recipe semantics from plain `uv sync` to `uv sync --all-extras --all-groups`. Repos that deliberately quarantine platform-limited dependencies in optional extras now fail `just sync`: hyrr's `geometry` extra ships cp312/313-only wheels (cadquery-ocp/vtk), so forcing `--all-extras` on the cp314 image makes an otherwise-healthy sync hard-fail.

Note the interaction with #877/#891: the upgrade-time repair appends the current template recipe verbatim, so upgraded consumers inherit these semantics too.

### Possible Solution

Pick one: (a) revert the template default to plain `uv sync` and let teams opt into extras locally; (b) keep the default but document an override pattern in the template comments (consumer redefines `sync` in justfile.project — customized recipes win); (c) parameterize (`sync *ARGS`) with conservative defaults.

### Changelog Category

Fixed

Refs: #877
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 11:27 AM_

Closed by #924 

