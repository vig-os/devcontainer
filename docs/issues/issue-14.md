---
type: issue
state: closed
created: 2025-12-11T16:56:20Z
updated: 2026-01-06T15:43:28Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/14
comments: 0
labels: none
assignees: none
milestone: 0.2
projects: none
relationship: none
synced: 2026-02-18T08:56:42.984Z
---

# [Issue 14]: [install python tools via pyproject.toml and not specifics in containerfile](https://github.com/vig-os/devcontainer/issues/14)

using 
```
uv sync --system
```
in containerfile to install pyproject.toml

use case during dev to add other packages is
```
uv add <package>
uv sync --system
```
this removes .venv 

moreover, check if pre-commits can be made slimmer by using system packages instead of their own venvs

<!-- Edit the body of your new issue then click the ✓ "Create Issue" button in the top right of the editor. The first line will be the issue title. Assignees and Labels follow after a blank line. Leave an empty line before beginning the body of the issue. -->
