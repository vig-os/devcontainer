---
type: issue
state: closed
created: 2026-02-09T09:45:26Z
updated: 2026-02-13T08:05:48Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/49
comments: 0
labels: bug
assignees: c-vigo
milestone: none
projects: none
relationship: none
synced: 2026-02-18T08:56:35.644Z
---

# [Issue 49]: [[BUG] just-lsp crashes due to non-ASCII characters in justfiles](https://github.com/vig-os/devcontainer/issues/49)

## Description

The just-lsp (Just Language Server) repeatedly crashes when parsing justfiles containing non-ASCII UTF-8 characters, specifically box-drawing characters (═, ─) and emojis (✓, ✅, ✨, ❌, ⚠️, 🧹, 🔪, 🗑️).

The crash occurs with a panic in the `ropey` library due to byte range alignment issues with multi-byte UTF-8 characters:

```
thread 'main' panicked at ropey-1.6.1/src/rope.rs:973:23:
byte_slice(): Byte range does not align with char boundaries: range 238..242
```

This causes the language server to crash and restart repeatedly (5 times in 3 minutes), eventually failing completely and disabling LSP features for justfiles.

## Steps to Reproduce

1. Create or open a justfile containing non-ASCII characters (box-drawing characters or emojis)
2. Open the file in an editor with just-lsp enabled (e.g., VSCode, Cursor)
3. Observe the language server crash logs in the output panel
4. Watch the server repeatedly restart and crash until it gives up

## Expected Behavior

The just-lsp should either:
- Gracefully handle UTF-8 multi-byte characters in justfiles
- Provide a clear error message about unsupported characters
- Continue functioning despite the presence of these characters

## Actual Behavior

- just-lsp crashes immediately when parsing justfiles with non-ASCII characters
- The server enters a crash-restart loop
- After 5 crashes in 3 minutes, the server stops restarting entirely
- LSP features (syntax highlighting, completion, diagnostics) become unavailable
- Error logs show byte alignment panic in ropey library

## Environment

- **OS**: Linux 6.14.0-37-generic
- **Editor**: Cursor / VSCode with just-lsp extension
- **just-lsp version**: Uses ropey-1.6.1
- **Affected files**: All justfiles in the project (6 files total)
  - `justfile`
  - `justfile.base`
  - `justfile.podman`
  - `assets/workspace/justfile`
  - `assets/workspace/.devcontainer/justfile.base`
  - `assets/workspace/justfile.project`

## Additional Context

### Error Log Sample

```
[2026-02-09T08:29:34Z INFO  just_lsp::server] Starting just language server...
[Info  - 9:29:34 AM] just-lsp initialized

thread 'main' (3395964) panicked at /home/runner/.cargo/registry/src/index.crates.io-1949cf8c6b5b557f/ropey-1.6.1/src/rope.rs:973:23:
byte_slice(): Byte range does not align with char boundaries: range 238..242
note: run with `RUST_BACKTRACE=1` environment variable to display a backtrace
[Error - 9:52:12 AM] Server process exited with code 101.
[Info  - 9:52:12 AM] Connection to server got closed. Server will restart.

[... repeated 5 times ...]

[Error - 10:11:54 AM] The Just Language Server server crashed 5 times in the last 3 minutes. The server will not be restarted.
```

### Non-ASCII Characters Found

The following non-ASCII characters were present in the justfiles:

**Box-drawing characters (headers/separators):**
- `═` (U+2550, 3 bytes: 0xE2 0x95 0x90) - Double horizontal line
- `─` (U+2500, 3 bytes: 0xE2 0x94 0x80) - Single horizontal line

**Emojis (user feedback messages):**
- `✓` (U+2713) - Checkmark
- `✅` (U+2705) - White checkmark in green box
- `✨` (U+2728) - Sparkles
- `❌` (U+274C) - Cross mark
- `⚠️` (U+26A0) - Warning sign
- `🧹` (U+1F9F9) - Broom
- `🔪` (U+1F52A) - Knife
- `🗑️` (U+1F5D1) - Wastebasket

These were used for visual formatting in comments and echo statements.

## Possible Solution

Replace all non-ASCII characters with ASCII equivalents across all justfiles:

**Proposed Replacements:**
- `═` → `=` (equals sign)
- `─` → `-` (hyphen)
- `✓` / `✅` → `[OK]` or `(OK)`
- `❌` → `[ERROR]` or `(ERROR)`
- `⚠️` → `[!]` or `(WARNING)`
- `✨` → `[*]` or descriptive text
- `🧹` / `🔪` / `🗑️` → descriptive text (e.g., "Cleaning", "Removing")

This would maintain readability while ensuring compatibility with just-lsp.

**Alternative Solutions:**
1. Report the bug upstream to just-lsp project and wait for a fix
2. Temporarily disable just-lsp until a fix is available
3. Use a different LSP or editor that handles UTF-8 better

**Long-term Preventive Measures:**
1. **Documentation**: Add coding standards specifying ASCII-only characters in justfiles
2. **Linting**: Implement a pre-commit hook or linter rule to detect non-ASCII characters in justfiles
3. **Template Updates**: Ensure all justfile templates use ASCII-only characters
4. **CI Validation**: Add a CI check to validate justfiles contain only ASCII characters

## Related Files

- `justfile` (root)
- `justfile.base`
- `justfile.podman`
- `assets/workspace/justfile`
- `assets/workspace/.devcontainer/justfile.base`
- `assets/workspace/justfile.project`

All justfiles need to be updated to remove non-ASCII characters.

## Priority

**Medium** - This issue:
- Completely breaks LSP functionality for justfiles
- Prevents syntax highlighting, autocompletion, and error detection
- Impacts all developers working with justfiles
- Is not immediately obvious to developers (silent crash)
- Blocks productivity until resolved

