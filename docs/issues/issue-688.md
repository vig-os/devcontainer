---
type: issue
state: open
created: 2026-06-24T14:08:12Z
updated: 2026-06-24T14:08:12Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devcontainer/issues/688
comments: 0
labels: bug, priority:medium, area:ci, effort:small, semver:patch
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-06-26T06:17:56.526Z
---

# [Issue 688]: [[BUG] allowed-signers test rejects valid ECDSA SSH keys](https://github.com/vig-os/devcontainer/issues/688)

## Description

`TestHostGitSignatureSetup::test_allowed_signers_file_exists` asserts that the git allowed-signers file contains either `ssh-ed25519` or `ssh-rsa`. It does **not** accept ECDSA keys (`ecdsa-sha2-nistp256`, `ecdsa-sha2-nistp384`, `ecdsa-sha2-nistp521`), which are valid SSH key types fully supported by OpenSSH for commit signing. A user whose allowed-signers file legitimately uses ECDSA keys gets a spurious test failure.

This is a **test-assertion bug** (too-narrow key-type allowlist), not a defect in the workspace setup.

## Steps to Reproduce

1. Configure `gpg.ssh.allowedSignersFile` to point at a file whose entries use ECDSA keys, e.g.:
   ```
   carlos.vigo@exoma.ch ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTIt...
   ```
2. Run `just test` (or `pytest tests/test_integration.py::TestHostGitSignatureSetup::test_allowed_signers_file_exists`).

## Expected Behavior

The test recognizes any valid SSH signing key type — including ECDSA — and passes.

## Actual Behavior

```
tests/test_integration.py:176: in test_allowed_signers_file_exists
    assert "ssh-ed25519" in content or "ssh-rsa" in content, (
E   AssertionError: Allowed signers file doesn't appear to contain SSH public keys
```

The file in question does contain valid public keys — they are just `ecdsa-sha2-nistp256` entries, which the assertion does not look for.

## Environment

- **OS**: NixOS 26.05 (Yarara)
- **Image Version/Tag**: `dev` (`just build`)
- **Architecture**: x86_64

## Root cause

`tests/test_integration.py:176` hard-codes only two of OpenSSH's supported key-type prefixes:

```python
assert "ssh-ed25519" in content or "ssh-rsa" in content, (
    "Allowed signers file doesn't appear to contain SSH public keys"
)
```

OpenSSH also accepts `ecdsa-sha2-nistp{256,384,521}` (and `sk-*` security-key variants) for signing.

## Suggested fix

Broaden the assertion to accept all valid SSH public-key type tokens, e.g. check for the presence of any known prefix:

```python
key_types = ("ssh-ed25519", "ssh-rsa", "ecdsa-sha2-nistp",
             "sk-ssh-ed25519@openssh.com", "sk-ecdsa-sha2-nistp256@openssh.com")
assert any(k in content for k in key_types), (
    "Allowed signers file doesn't appear to contain SSH public keys"
)
```

## Changelog Category

Fixed

