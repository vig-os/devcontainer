---
type: issue
state: closed
created: 2025-12-10T10:46:49Z
updated: 2026-01-06T15:43:27Z
author: irenecortinovis
author_url: https://github.com/irenecortinovis
url: https://github.com/vig-os/devcontainer/issues/13
comments: 2
labels: feature
assignees: c-vigo
milestone: 0.2
projects: none
relationship: none
synced: 2026-02-18T08:56:43.358Z
---

# [Issue 13]: [VS Code settings possibly using uv virtual environment Python interpreter](https://github.com/vig-os/devcontainer/issues/13)

To be discussed: eg.
`"python.defaultInterpreterPath": "/usr/local/bin/python",
`
--> `"python.defaultInterpreterPath": "/workspace/exopet/.venv/bin/python",`
---

# [Comment #1]() by [c-vigo]()

_Posted on December 10, 2025 at 01:02 PM_

Why would you want a virtual environment when you can use the devcontainer one?

---

# [Comment #2]() by [irenecortinovis]()

_Posted on December 12, 2025 at 10:29 AM_

Need to add this line to the container file: 
`export UV_PROJECT_ENVIRONMENT=/usr/local/` 
(else uv sync creates a virtual environment), and re-publish the image 

Also need to make `PROJECT_ROOT` available in `post-create.sh ` (add `PROJECT_ROOT="/workspace/exopet"`)

---
With this setup, one can then use a project with a `pyproject.toml` file and `uv.lock` file, and install dependencies from `myproject.toml` in the `post-create.sh` by setting:
```
# Install dependencies from pyproject.toml   
cd $PROJECT_ROOT
uv sync
```

and while in the container, one can add any new package by doing 
```
uv add <package>
uv sync
```


