---
type: issue
state: closed
created: 2026-03-27T10:34:16Z
updated: 2026-07-08T08:13:43Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devkit/issues/465
comments: 1
labels: none
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:20.770Z
---

# [Issue 465]: [feat(security): enforce SSH key security policy in devc-remote](https://github.com/vig-os/devkit/issues/465)

## Summary

Supply chain attacks (e.g. LiteLLM) scrape SSH keys and secrets from compromised machines. Unpassphrased SSH private keys are immediately usable by attackers. `devc-remote.sh` should enforce a configurable security policy on SSH keys before connecting, and the team's dev environment should provide FIDO2-capable SSH by default.

## Problem

Unpassphrased SSH private keys are equivalent to plaintext passwords on disk. Any process with file read access (malicious dependency, compromised tool, supply chain attack) can exfiltrate and immediately use them.

Detection is trivial: `ssh-keygen -y -P "" -f <key>` succeeds if a key has no passphrase.

## Cross-Platform SSH Security

### What stops scraped secrets from being usable

| Protection | Scrape the file | Brute-forceable? |
|-----------|----------------|-----------------|
| SSH key + passphrase (ed25519, bcrypt KDF `-a 100`) | Encrypted blob | Infeasible with strong passphrase |
| SSH key on YubiKey / FIDO2 | Nothing to scrape — key never leaves hardware | N/A |
| macOS Keychain (Secure Enclave) | Encrypted blob, needs biometric | Tied to hardware |
| age-encrypted files (X25519) | Encrypted blob | Infeasible — Curve25519 |
| Plain env var / unencrypted key | **Game over** | N/A |

### Platform authenticator reality

| Platform | FIDO2 SSH (`ed25519-sk`) | Auth gesture | External device? |
|----------|-------------------------|-------------|-----------------|
| macOS | YubiKey only (Secure Enclave can't act as FIDO2 for SSH) | Touch the key | Yes |
| macOS | Passphrased key + `ssh-agent` + `UseKeychain` | Touch ID to unlock agent | **No** |
| Linux | YubiKey | Touch the key | Yes |
| Linux | `tpm2-fido` (emulates FIDO2 via TPM2 chip) | PIN / fingerprint (PAM) | **No** |

### Pragmatic recommendation (no external hardware needed)

Passphrased ed25519 keys + ssh-agent + ControlMaster = one Touch ID / password prompt per session, keys encrypted at rest, nothing usable if scraped.

## Nix Home Manager Config (implemented)

Added to `dotfiles/home/common.nix`:

```nix
home.packages = [ pkgs.openssh ]; # FIDO2-capable (libfido2 built in)

programs.ssh = {
  enable = true;
  addKeysToAgent = "yes";
  controlMaster = "auto";
  controlPath = "~/.ssh/cm-%r@%h:%p";
  controlPersist = "10m";
  extraOptionOverrides.SecurityKeyProvider = "internal";
};
```

macOS-specific in `darwin.nix`:
```nix
programs.ssh.extraOptionOverrides.UseKeychain = "yes";
```

This gives:
- **nixpkgs openssh** with `libfido2` linked (`withFIDO = true` by default)
- **ControlMaster** — one auth per host, reused for 10 min (solves multi-touch problem for `devc-remote.sh`)
- **AddKeysToAgent** — passphrase cached in agent after first use
- **UseKeychain** (macOS) — Touch ID unlocks passphrased keys
- **SecurityKeyProvider = internal** — builtin libfido2 for `ed25519-sk` keys

## Proposed: Client-Side Enforcement in `devc-remote.sh`

### `check_ssh_key_security()` pre-flight

```bash
check_ssh_key_security() {
    local host="$1"
    local key
    key=$(ssh -G "$host" | awk '/^identityfile / {print $2}' | head -1)
    key="${key/#\~/$HOME}"

    # FIDO2 hardware key — always OK
    if [[ -f "${key}.pub" ]] && grep -qE 'sk-ssh-ed25519|sk-ecdsa' "${key}.pub"; then
        return 0
    fi

    # Check for passphrase
    if ssh-keygen -y -P "" -f "$key" &>/dev/null 2>&1; then
        log_error "SSH key $key has NO passphrase — refusing to connect."
        log_error "Fix: ssh-keygen -p -f $key -a 100"
        return 1
    fi
}
```

### Configurable policy levels

In `~/.config/devc-remote/config.yaml`:

```yaml
ssh_key_policy: strict  # warn | strict | fido2-only
```

| Policy | Unpassphrased | Passphrased | FIDO2/YubiKey |
|--------|:---:|:---:|:---:|
| `warn` | Warning | OK | OK |
| `strict` (default) | **Blocked** | OK | OK |
| `fido2-only` | **Blocked** | **Blocked** | OK |

### Remediation guidance

```
✗  SSH key ~/.ssh/id_ed25519_ksb has NO passphrase — refusing to connect.

   To add a passphrase to your existing key (key itself doesn't change):
     ssh-keygen -p -f ~/.ssh/id_ed25519_ksb -a 100

   To generate a FIDO2 hardware key (YubiKey):
     ssh-keygen -t ed25519-sk -f ~/.ssh/id_ed25519_ksb

   To use ssh-agent with confirmation (Touch ID per use):
     ssh-add -c ~/.ssh/id_ed25519_ksb          # Linux
     ssh-add --apple-use-keychain -c ~/.ssh/id_ed25519_ksb  # macOS

   To downgrade policy (not recommended):
     Set ssh_key_policy: warn in ~/.config/devc-remote/config.yaml
```

### Server-side enforcement (optional, documented)

For hosts where hardware keys should be mandatory:

```
# /etc/ssh/sshd_config.d/fido2-only.conf
PubkeyAcceptedAlgorithms sk-ssh-ed25519@openssh.com,sk-ecdsa-sha2-nistp256@openssh.com
```

## Acceptance Criteria

- [x] Add `openssh` (FIDO2-capable) to `dotfiles/home/common.nix`
- [x] Add `programs.ssh` config with ControlMaster, AddKeysToAgent, SecurityKeyProvider
- [x] Add macOS `UseKeychain` in `darwin.nix`
- [ ] `check_ssh_key_security()` pre-flight in `devc-remote.sh`
- [ ] Resolve which key is used for target host via `ssh -G <host>`
- [ ] Detect: no passphrase, passphrase, FIDO2/hardware
- [ ] Configurable policy: `warn` / `strict` / `fido2-only`
- [ ] Actionable remediation messages with exact commands
- [ ] Document `ssh-add -c` and macOS Touch ID agent integration
- [ ] Document server-side `PubkeyAcceptedAlgorithms` for FIDO2-only hosts
- [ ] Document `tpm2-fido` for Linux users without YubiKey
- [ ] Tests (mock ssh-keygen responses)

## Related

- #464 (secure secret resolution — complementary)
- #70 (parent: remote devcontainer orchestration)
---

# [Comment #1]() by [c-vigo]()

_Posted on July 8, 2026 at 08:13 AM_

Closing as part of an agreed backlog cleanup (with @gerchowl). The remote-devcontainer / `devc-remote` / Tailscale initiative predates the Nix + Claude-native migration (#625) and has had no activity since Feb–Mar 2026. If remote provisioning is wanted again it will be re-planned from scratch after the devkit rename (#781). Reopen/refile if revived.

