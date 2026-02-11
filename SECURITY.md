# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |
| < latest | No       |

Only the latest released version receives security updates.
Older versions are not maintained.

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

To report a vulnerability, use
[GitHub Private Vulnerability Reporting](https://github.com/vig-os/devcontainer/security/advisories/new).

When reporting, please include:

- Description of the vulnerability
- Steps to reproduce (or proof of concept)
- Affected component (container image, CI workflow, build script, etc.)
- Potential impact assessment

## Response Timeline

| Stage | Target |
|-------|--------|
| Acknowledgement | 3 business days |
| Initial assessment | 7 business days |
| Fix or mitigation | 30 calendar days |

We will keep you informed of progress throughout.

## Scope

The following areas are in scope for security reports:

- **Supply chain:** GitHub Actions workflows and pinned dependencies
- **Container image:** Base image vulnerabilities, installed packages, permissions
- **Build tooling:** Scripts in `scripts/`, `install.sh`, `init-workspace.sh`
- **Secrets handling:** Accidental exposure of tokens, keys, or credentials
- **Workflow permissions:** Overly broad permissions in CI/CD pipelines

## Security Practices

This repository follows these security practices:

- All GitHub Actions are pinned to commit SHAs (not mutable tags)
- Dependabot monitors dependencies for known vulnerabilities
- Workflow permissions follow the principle of least privilege
- No `pull_request_target` triggers are used (prevents untrusted code execution)
- Branch protection is enforced via GitHub Enterprise

## Compliance

This project is designed to support medical device software development under
IEC 62304 and ISO 13485. Security practices align with configuration management
and risk management requirements of these standards.
