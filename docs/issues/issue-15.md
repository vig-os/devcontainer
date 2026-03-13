---
type: issue
state: closed
created: 2025-12-15T07:39:16Z
updated: 2026-01-30T15:17:25Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/15
comments: 0
labels: bug
assignees: c-vigo
milestone: 0.2
projects: none
relationship: none
synced: 2026-02-18T08:56:42.566Z
---

# [Issue 15]: [[BUG] docker-compose.override.yml is not picked up](https://github.com/vig-os/devcontainer/issues/15)

### Description

The file `docker-compose.override.yml` is not picked up.

### Steps to Reproduce

1. Create  `docker-compose.override.yml` and mount any other local folder.
2. Rebuild devcontainer
3. Launch and try to access mounted folder

### Expected Behavior

Folder should be mounted

### Actual Behavior

File `docker-compose.override.yml` is never read.

### Environment

- Ubuntu 24.04
- AMD64
- Image version 0.1

### Additional Context

_No response_

### Possible Solution

1. Modify `devcontainer.json`
```yaml
...
    "dockerComposeFile": [
        "docker-compose.yml",
        "docker-compose.override.yml"
    ],
...
```

2. Create an empty `docker-compose.override.yml`, otherwise container start-up will fail.
