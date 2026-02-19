---
type: issue
state: open
created: 2026-02-19T06:48:57Z
updated: 2026-02-19T06:48:57Z
author: gerchowl
author_url: https://github.com/gerchowl
url: https://github.com/vig-os/devcontainer/issues/88
comments: 0
labels: chore
assignees: none
milestone: none
projects: none
relationship: none
synced: 2026-02-19T06:49:13.729Z
---

# [Issue 88]: [Update Python dependencies to address security vulnerabilities in urllib3, filelock, and virtualenv](https://github.com/vig-os/devcontainer/issues/88)

## Summary

Update vulnerable Python dependencies to their patched versions to address 6 Dependabot security alerts (3 high, 3 medium severity).

## Problem Statement

Dependabot has identified security vulnerabilities in three Python dependencies used in the devcontainer:

### High Severity (urllib3)

1. **CVE-2026-21441** (GHSA-38jv-5279-wg99)
   - **Current:** urllib3 2.5.0
   - **Fixed in:** 2.6.3
   - **Issue:** Decompression-bomb safeguards bypassed when following HTTP redirects (streaming API)
   - **Alert created:** 2026-01-26

2. **CVE-2025-66471** (GHSA-2xpw-w6gg-jr37)
   - **Current:** urllib3 2.5.0
   - **Fixed in:** 2.6.0
   - **Issue:** Streaming API improperly handles highly compressed data
   - **Alert created:** 2026-01-26

3. **CVE-2025-66418** (GHSA-gm62-xv2j-4w53)
   - **Current:** urllib3 2.5.0
   - **Fixed in:** 2.6.0
   - **Issue:** Allows unbounded number of links in decompression chain
   - **Alert created:** 2026-01-26

### Medium Severity

4. **CVE-2025-68146** (GHSA-w853-jp5j-5j7f)
   - **Package:** filelock
   - **Current:** 3.20.0
   - **Fixed in:** 3.20.1
   - **Issue:** TOCTOU race condition allowing symlink attacks during lock file creation
   - **Alert created:** 2026-01-26

5. **CVE-2026-22701** (GHSA-qmgc-5h2g-mvrw)
   - **Package:** filelock
   - **Current:** 3.20.0
   - **Fixed in:** 3.20.3
   - **Issue:** TOCTOU symlink vulnerability in SoftFileLock
   - **Alert created:** 2026-01-13

6. **CVE-2026-22702** (GHSA-597g-3phw-6986)
   - **Package:** virtualenv
   - **Current:** 20.35.4
   - **Fixed in:** 20.36.1
   - **Issue:** TOCTOU vulnerabilities in directory creation
   - **Alert created:** 2026-01-13

## Proposed Solution

Update `pyproject.toml` minimum versions and regenerate `uv.lock`:

```bash
# Update dependencies to patched versions
uv add "urllib3>=2.6.3" "filelock>=3.20.3" "virtualenv>=20.36.1"

# Or manually edit pyproject.toml and run:
uv lock --upgrade
uv sync
```

### Risk Assessment

**Impact:** Development environment only
- These packages are used in the devcontainer build/development tooling
- Not part of any production runtime (consistent with project scope)
- All vulnerabilities are TOCTOU or decompression-related attacks

**Exposure:** LOW
- Devcontainer is a development environment (untrusted code already present)
- TOCTOU attacks require local filesystem race conditions
- Decompression attacks require malicious HTTP responses

**Urgency:** MEDIUM
- No production runtime exposure
- Development environment has inherent trust model
- Updates are straightforward (no breaking changes expected)

### Testing

After updating:
- [ ] Run `uv run pytest tests/` to ensure no test regressions
- [ ] Verify container builds successfully
- [ ] Check that CI passes all checks
- [ ] Confirm Dependabot alerts are resolved

## Alternatives Considered

1. **Accept risks and document in SECURITY.md**
   - Not recommended: These have straightforward patches available
   - Unlike the BATS test dependencies (unmaintained), these packages are actively maintained

2. **Pin to older versions and add to exception register**
   - Not recommended: Defeats purpose of Dependabot monitoring
   - Better to stay current with security patches

## Additional Context

- These vulnerabilities were discovered by Dependabot on 2026-01-13 and 2026-01-26
- All three packages (urllib3, filelock, virtualenv) are transitive dependencies of core Python tooling
- Patched versions are available and widely adopted
- No breaking changes expected in minor version bumps
- **Not introduced by PR #87** - these are pre-existing on the dev branch

## Acceptance Criteria

- [ ] All 6 Dependabot alerts resolved
- [ ] `uv.lock` regenerated with patched versions
- [ ] CI passes all checks (image tests, integration tests, security scans)
- [ ] No test regressions introduced
- [ ] CHANGELOG.md updated under "Security" section if user-facing impact

## Links

- [Dependabot Alerts](https://github.com/vig-os/devcontainer/security/dependabot)
- [urllib3 GHSA-38jv-5279-wg99](https://github.com/advisories/GHSA-38jv-5279-wg99)
- [urllib3 GHSA-2xpw-w6gg-jr37](https://github.com/advisories/GHSA-2xpw-w6gg-jr37)
- [urllib3 GHSA-gm62-xv2j-4w53](https://github.com/advisories/GHSA-gm62-xv2j-4w53)
- [filelock GHSA-w853-jp5j-5j7f](https://github.com/advisories/GHSA-w853-jp5j-5j7f)
- [filelock GHSA-qmgc-5h2g-mvrw](https://github.com/advisories/GHSA-qmgc-5h2g-mvrw)
- [virtualenv GHSA-597g-3phw-6986](https://github.com/advisories/GHSA-597g-3phw-6986)
