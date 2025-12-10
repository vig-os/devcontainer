# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

### Changed

### Removed

### Fixed

- SSH commit signing: Changed `user.signingkey` from file path to email identifier to support SSH agent forwarding.
  Git now uses the SSH agent for signing by looking up the email in allowed-signers and matching with the agent key.
- Fixed `gpg.ssh.allowedSignersFile` path to use container path instead of host path after copying git configuration.
- Automatically add git user email to allowed-signers file during setup to ensure commits can be signed and verified.

### Security
