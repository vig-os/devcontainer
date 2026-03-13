---
type: issue
state: closed
created: 2026-01-29T08:14:26Z
updated: 2026-02-03T13:06:05Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/34
comments: 0
labels: feature
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:38.920Z
---

# [Issue 34]: [[FEATURE] Rename virtual environment upon container creation](https://github.com/vig-os/devcontainer/issues/34)

### Description

The virtual environment in a fresh devcontainer is named `template-project` instead of the project name.

### Problem Statement

Aesthetics mainly

### Proposed Solution

The renaming must happen during first initialization of the container, since the `venv` is stored in the image. I have been using the following line in `post-create.sh`:
``` bash
# Set venv prompt
sed -i 's/template-project/{{SHORT_NAME}}/g' /root/assets/workspace/.venv/bin/activate
```

### Alternatives Considered

_No response_

### Additional Context

_No response_

### Impact

_No response_
