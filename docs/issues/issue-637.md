---
type: issue
state: closed
created: 2026-06-23T06:54:12Z
updated: 2026-07-01T11:19:15Z
author: c-vigo
author_url: https://github.com/c-vigo
url: https://github.com/vig-os/devkit/issues/637
comments: 1
labels: docs, area:image, security
assignees: none
milestone: none
projects: none
parent: none
children: none
synced: 2026-07-11T13:34:12.326Z
---

# [Issue 637]: [T3.1 — vulnix + SBOM CVE scanning; re-author security policy](https://github.com/vig-os/devkit/issues/637)

Tracking: #625



## Context

A Nix-built image has no apt/dpkg database, so Trivy's OS-package scanner — the basis of the
current CVE workflow and the `.trivyignore` expiry register — goes dark. This is the headline
cost of the image cutover and must be addressed *before* publishing (#639). The signal is
replaced with `vulnix` (a nixpkgs-native CVE scanner) plus SBOM-based scanning.

## Scope

**In:**
- Make **`vulnix`** the primary nightly CVE scanner.
- Keep Trivy in **CycloneDX SBOM mode** for defense-in-depth.
- Rewrite `docs/CONTAINER_SECURITY.md`: drop the apt `--only-upgrade` escape hatch; the CVE
  lever becomes "advance the nixpkgs rev".
- Rebuild the **exception register with expiry** around vulnix findings to preserve the
  IEC 62304 audit story.

**Out:**
- Renovate wiring for `flake.lock` (#638).

## Tasks

- [ ] Add a `vulnix` nightly scan job
- [ ] Emit a CycloneDX SBOM and feed Trivy in SBOM mode
- [ ] Rewrite `docs/CONTAINER_SECURITY.md`
- [ ] Rebuild the exception register with expiry around vulnix findings

## Acceptance criteria

- `vulnix` nightly runs.
- Rewritten policy + expiry register reviewed.
- **Objective gate (this is the go/no-go input for #639):** no HIGH/CRITICAL vulnix finding on
  the Nix image without a documented, expiring entry in the exception register.
- **Confidence check (not a pass/fail gate):** Trivy-vs-vulnix findings compared over a
  one-cycle overlap and the diff archived, to confirm no class of finding silently disappears
  in the scanner switch. The two scanners cover different surfaces (apt packages vs Nix store),
  so this is a documented comparison, not a numeric parity requirement.

## Dependencies

- **Depends-on:** #634.
- **Blocks:** #639.

## Files

- `.github/workflows/security-scan.yml`
- `docs/CONTAINER_SECURITY.md`
- exception register (replacement for `.trivyignore` semantics)

## Test notes

- The objective threshold (no unexcepted HIGH/CRITICAL) is the explicit gate input for #639;
  the Trivy-vs-vulnix overlap diff is archived as supporting confidence evidence.

## Related issues

- **#604** (consolidate Trivy scan categories / clean stale alerts) — its "single authoritative
  scan + document the SSoT" goal **is** this issue's outcome under vulnix/SBOM. The
  orphaned/stale-alert cleanup (the `container-image-scheduled` and stale `container-image`
  categories) should still happen so zombies aren't carried into the new system.
- **#602 / #521** (nightly HIGH/CRITICAL gate issues) — these gates re-point from Trivy-on-apt
  to vulnix; the apt-CVE surface they track changes with the Nix image. #521 (Apr) is already
  stale vs #602 (Jun). Close once the new scan passes its gate (with #642).
- **#109** (discussion: full security scan on every PR) — the category-consolidation decision
  overlaps this thread; resolve together.
- **#27** (Adopt Nix/devenv) — provides the SBOM / IEC 62304 / air-gapped framing this issue
  realizes (`nix derivation show`, `nix flake archive`).

---

# [Comment #1]() by [c-vigo]()

_Posted on July 1, 2026 at 11:19 AM_

Delivered on `dev` via the Nix-migration epic PR #670 (merged 2026-06-30) + PR #660 (commit 343234a0). Nightly `security-scan.yml` runs vulnix (primary) + Trivy CycloneDX SBOM; `vulnix_gate.py` is a blocking gate over `.vulnixignore`; `docs/CONTAINER_SECURITY.md` re-authored. (Its CVE gate feeds the #639 cutover.) Closing as complete — this stayed open only because the epic merged to `dev` (not `main`) and these T/C-track issues carry `Tracking: #625` but were never linked as GitHub sub-issues, so sync-issues auto-close never fired (tracked by #677). Refs #625.

