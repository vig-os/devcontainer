---
type: issue
state: open
created: 2025-12-16T10:54:31Z
updated: 2025-12-18T09:19:52Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/17
comments: 1
labels: none
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-01-09T16:17:33.552Z
---

# [Issue 17]: [discuss: Python base image vs uv-managed Python](https://github.com/vig-os/devcontainer/issues/17)

## Question for Discussion

@c-vigo - Would like to discuss the tradeoffs of our current approach vs an alternative.

## Current Approach

We use `python:3.12-slim-trixie` as our base image, which includes Python pre-installed:

```dockerfile
FROM python:3.12-slim-trixie
```

Then we install tools via `uv pip install --system` and create venvs with `uv sync`.

## Alternative Approach

Start with a slimmer base image (e.g., `debian:trixie-slim`) and let uv manage Python entirely:

```dockerfile
FROM debian:trixie-slim

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# uv downloads and manages Python
RUN uv python install 3.12
```

## Comparison

| Aspect | python:3.12-slim-trixie | debian + uv-managed Python |
|--------|-------------------------|---------------------------|
| Base image size | ~150MB | ~75MB |
| Python management | System package | uv managed |
| Version flexibility | Fixed to image tag | Easy to change via uv |
| Build complexity | Simple | Slightly more complex |
| Python location | /usr/local/bin/python | ~/.local/share/uv/python |
| Consistency | Debian Python build | Astral's Python builds |

## Questions to Discuss

1. **Size**: Is the ~75MB difference significant for our use case?
2. **Flexibility**: Do we need easy Python version switching?
3. **Consistency**: Is using Debian's Python build important for compatibility?
4. **Maintenance**: Which approach is easier to maintain long-term?
5. **uv ecosystem**: Should we go all-in on uv's Python management?

## Current Issue

If we keep the Python base image but use `uv sync`, we need to configure:
```toml
[tool.uv]
python-preference = "only-system"
```

Otherwise uv might download Python again (~100MB wasted).

## Related

- Issue #16 (pre-commit cache optimization)
- Recent work on pre-building venvs during container build
---

# [Comment #1]() by [gerchowl]()

_Posted on December 18, 2025 at 09:19 AM_

works like this fine, no real advantage 

