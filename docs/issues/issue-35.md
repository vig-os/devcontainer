---
type: issue
state: closed
created: 2026-01-29T08:19:47Z
updated: 2026-02-17T12:01:26Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/35
comments: 0
labels: feature
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:38.581Z
---

# [Issue 35]: [[FEATURE] Execute user configuration script within install.sh pipeline](https://github.com/vig-os/devcontainer/issues/35)

### Description

Execute `{{PROJECT_FOLDER}}/.devcontainer/scripts/copy-host-user-conf.sh` during `curl install.sh` pipeline.

### Problem Statement

Simplifies user experience and warns of `git` issues already during installation phase.

### Proposed Solution

- Add script to pipeline with proper output check-up.
- Add an option to only run this script, e.g. if it fails and you want to re-execute.

### Alternatives Considered

_No response_

### Additional Context

_No response_

### Impact

_No response_
