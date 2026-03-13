---
type: issue
state: closed
created: 2026-01-07T09:36:25Z
updated: 2026-02-06T10:48:25Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/24
comments: 0
labels: bug
assignees: none
milestone: 0.3
projects: none
relationship: none
synced: 2026-02-18T08:56:40.152Z
---

# [Issue 24]: [[BUG] Virtual environment prompt name](https://github.com/vig-os/devcontainer/issues/24)

### Description

The `venv` prompt keeps the name `template-project`:

```bash
root@688c2de6d0f4:/workspace/my-project# source /root/assets/workspace/.venv/bin/activate
(template-project) root@688c2de6d0f4:/workspace/my-project# 
```

### Steps to Reproduce

1. Initialize a project
2. Launch

### Expected Behavior

The `venv` prompt should be the short name of the project.

### Actual Behavior

The `venv` prompt defaults to `template-project`.

### Environment

- **OS**: Ubuntu 24.04
- **Container Runtime**: podman version 4.9.3
- **Image Version**: 0.2.0
- **Architecture**: AMD64

### Additional Context

_No response_

### Possible Solution

Edit the venv’s bin/activate and set the variable.

For example, add to `post-create.sh`:
``` bash
# Set venv prompt
sed -i 's/template-project/{{SHORT_NAME}}/g' /root/assets/workspace/.venv/bin/activate
```
