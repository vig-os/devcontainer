---
type: issue
state: open
created: 2026-02-06T07:38:17Z
updated: 2026-02-06T07:38:17Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/44
comments: 0
labels: feature
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-06T07:38:36.670Z
---

# [Issue 44]: [[FEATURE] Update just LSP extension](https://github.com/vig-os/devcontainer/issues/44)

## [FEATURE] Update just LSP extension

#### Description

Update the VS Code extension for just (justfile) syntax highlighting and language support. The currently configured extension `promptexecution.justlang-lsp` in the devcontainer configuration may be outdated or no longer available/maintained.

#### Problem Statement

In `assets/workspace/.devcontainer/devcontainer.json` (lines 17-18), the extension list includes:

```json
"GitHub.vscode-pull-request-github",
"nefrob.vscode-just-syntax"
```

The `nefrob.vscode-just-syntax` extension no longer exists or is deprecated, which may cause:
- Extension installation failures when starting the devcontainer
- Missing just/justfile syntax highlighting
- No LSP features (go-to-definition, hover, etc.) for justfiles

#### Proposed Solution

Replace `nefrob.vscode-just-syntax` with a current, actively maintained just extension. Candidates:
- `skellock.just` — Just syntax highlighting
- `kokakiwi.vscode-just` — Just language support (syntax + more)

Update the extension ID in:
- `assets/workspace/.devcontainer/devcontainer.json`
- Any other devcontainer.json files in the repo if applicable

#### Alternatives Considered

- Keep the current extension and hope it still installs (fragile)
- Remove just extension entirely (loses justfile support)

#### Additional Context

- Extension marketplace link (current): https://marketplace.visualstudio.com/items?itemName=nefrob.vscode-just-syntax (check if still available)
- Possible replacement: https://marketplace.visualstudio.com/items?itemName=skellock.just

#### Impact

- **Who benefits:** All developers using the devcontainer template with justfiles
- **Breaking change:** No — just an extension swap; existing workflows unaffected

