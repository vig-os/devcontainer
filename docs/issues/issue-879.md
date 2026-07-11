---
type: issue
state: closed
created: 2026-07-06T16:24:56Z
updated: 2026-07-08T07:54:21Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/879
comments: 1
labels: bug, priority:high, area:image, effort:medium, semver:minor
assignees: none
milestone: 0.4.1
projects: none
parent: none
children: none
synced: 2026-07-11T13:33:31.781Z
---

# [Issue 879]: [fix(image): no C/C++ toolchain — uv cannot build sdists for deps without cp314 wheels (CMake reads absent nix-store compiler from sysconfig)](https://github.com/vig-os/devkit/issues/879)

### Description

Found during 0.4.0 consumer field-validation (EXOMA/hyrr): `just sync` (uv) fails for any dependency that ships no cp314 wheel and must build from source.

Evidence (hyrr, `uv sync` in `ghcr.io/vig-os/devcontainer:0.4.0`):

```
× Failed to build `pycatima==1.981`
╰─▶ Call to `scikit_build_core.build.build_wheel` failed
    *** scikit-build-core 0.12.2 using CMake 4.3.4 (wheel)
    loading initial cache file build/cpython-314/CMakeInit.txt
    CMake Error: Could not find the compiler specified in the environment variable CXX
    CMake Error: CMAKE_CXX_COMPILER not set, after EnableLanguage
```

In a fresh 0.4.0 container: `CC`/`CXX` are unset and **no compiler exists on PATH** (`c++`, `g++`, `gcc`, `cc`, `clang++` all absent). The CXX value CMake complains about comes from the baked CPython's build-time sysconfig — a nix-store compiler path not shipped in the runtime image.

Impact is amplified by the Python 3.14 jump: the cp314 wheel ecosystem is young, so scientific consumers (pycatima here; cadquery-ocp/vtk are cp312/313-only) hit source builds far more often than under 3.13 — and every source build hard-fails.

### Possible Solution

Decide the contract and implement one of: (a) ship a working C/C++ toolchain (gcc + make + CMake already present?) wired so scikit-build-core/setuptools find it (export sane CC/CXX); (b) explicitly document "no native builds in-image — provide toolchains via the project flake" and make the shipped ci.yml/direnv-mode support that (relates to #854); (c) sanitize the baked CPython sysconfig so build backends fall back to PATH discovery instead of a dead nix-store path.

### Changelog Category

Fixed
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 07:54 AM_

Implemented in **0.4.1** (released 2026-07-08) — see the `## [0.4.1]` CHANGELOG entry. Closing as completed.

