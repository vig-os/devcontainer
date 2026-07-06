# Nix cutover — vulnix vs Trivy scan overlap

Go/no-go evidence for the publish-cutover (#639) and the confidence check from
#637: comparing the two CVE scanners over a one-cycle overlap so we can confirm
no class of finding silently disappears when the published image moves from the
Debian/apt build (Trivy OS-package scan) to the Nix build (vulnix).

## Method

- **Baseline:** `nixos-26.05` (rev `34268251`, 2026-06-22), bumped from the
  year-old `nixos-25.05` as the primary CVE lever (see `CONTAINER_SECURITY.md`).
- **vulnix** (primary gate) scans the image package closure —
  `nix build .#devcontainerImageEnv` then `vulnix --closure`. Matches the Nix
  store derivations by name + upstream version against NVD.
- **Trivy** (defence in depth) scans the built image —
  `trivy image --input <devcontainerImage tar>`. Detects bundled binaries and
  language dependencies (e.g. Go stdlib inside `gh`/`podman`/`runc`) and flags
  their CVEs.
- Snapshot date: **2026-06-23**. HIGH/CRITICAL = CVSS v3 ≥ 7.0.

## Results (26.05 baseline)

| Scanner | HIGH/CRITICAL (unique) | Disposition |
|---------|------------------------|-------------|
| **vulnix** | 27 | All triaged in `.vulnixignore` (gate green) |
| **Trivy** | 14 | Awareness / defence-in-depth (non-gating) |
| **Overlap (both)** | **0** | — |

- The bump cut the surface for **both** scanners: vulnix **83 → 27** unique
  HIGH/CRITICAL, Trivy HIGH **244 → 14**.
- **Zero overlap.** The two scanners flag completely disjoint CVE sets because
  they examine different surfaces: vulnix sees Nix-store packages (glibc,
  openssl, perl, …); Trivy sees vendored/bundled components inside binaries (Go
  stdlib, npm/Go modules). Neither is redundant — together they widen coverage,
  and **no class of finding disappears** in the Debian→Nix scanner switch
  (Trivy's OS-package surface is replaced by vulnix's store surface; Trivy's
  bundled-binary surface is retained).

## vulnix residual (27, all excepted in `.vulnixignore`)

- **Not applicable — CPE mismatch (4):** `shellcheck` CVE-2021-28794 (the VS Code
  *extension*, not the binary) and three `git` CVEs that are *Jenkins Git-plugin*
  advisories.
- **Accepted recent CVEs (23):** `glibc`, `openssl`, `perl`, `zlib`, `sqlite`,
  `ldns`, `libmicrohttpd` — version-matched against current-stable nixpkgs; low
  exploitability in an interactive single-user dev container; remediation is
  advancing the pinned `nixpkgs` rev as fixes land (#638). 3-month re-review.

## Trivy residual (14 HIGH, non-gating)

Bundled-binary CVEs (predominantly Go stdlib inside Go-based tools). Not gated by
`vulnix-gate` (Trivy is the SBOM / defence-in-depth view); they shrink as the
pinned `nixpkgs` rev advances. The nightly `scan-nix-image` job keeps emitting
the CycloneDX SBOM + this comparison so the set is tracked each cycle.

## Verdict

- **vulnix gate: GREEN** after the 26.05 bump + triage (`vulnix-gate` exits 0).
- **Confidence check: satisfied** — disjoint surfaces documented; no finding
  class lost in the scanner switch.
- **Publish remains PAUSED.** This batch stages the cutover (gate green +
  blocking, release pipeline able to build the Nix image) but does not run a
  release / promote `:latest`. That deliberate trigger — and a final review of
  the CRITICAL acceptances above — is left to a maintainer.
