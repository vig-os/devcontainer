#!/usr/bin/env bash
# In-container Nix runtime smoke test (#675).
#
# Runs INSIDE the Nix-built devcontainer image to prove that the baked Nix
# toolchain (`nix`, `direnv`, `nix-direnv` — see flake.nix `imageTools`, #634)
# is not merely *present* but actually *functional* at runtime. The portable
# testinfra suite (tests/test_image.py, #635) only asserts tool presence, so a
# regression that left `nix`/`direnv` on PATH but broken would pass it; this
# script closes that gap.
#
# Every check is self-contained and network-free (no flake input fetch, no
# substituter round-trip), so it is fast and deterministic in CI and fails iff
# the in-container runtime is genuinely broken.
#
# Usage (from the workflow, against the loaded image):
#   podman run --rm <image> bash /root/assets/../scripts/nix_runtime_smoke.sh
# In CI the repo's scripts/ dir is bind-mounted at /smoke and this is run as
#   podman run --rm -v "$PWD/scripts":/smoke:ro <image> bash /smoke/nix_runtime_smoke.sh

set -euo pipefail

echo "== In-container Nix runtime smoke test (#675) =="

# 1) The Nix binary itself runs (dynamic linker, store access, self-test).
echo "-- nix --version"
nix --version

# 2) direnv runs.
echo "-- direnv version"
direnv version

# 3) The Nix evaluator actually evaluates with the experimental features the
#    live closure must enable. `--version` does not exercise evaluation; this
#    does, so a broken evaluator / missing experimental-features fails here.
echo "-- nix eval (evaluator + nix-command/flakes)"
result="$(nix eval --extra-experimental-features 'nix-command flakes' --expr '1 + 1')"
if [ "${result}" != "2" ]; then
	echo "::error::nix eval returned '${result}', expected '2' — evaluator is broken"
	exit 1
fi
echo "nix eval '1 + 1' = ${result}"

# 4) direnv's allow + exec runtime path works end-to-end. We use a trivial
#    non-flake .envrc (a plain export) so this proves direnv's own runtime —
#    load, allow, hook, exec — without depending on a network flake fetch.
echo "-- direnv allow + direnv exec"
work="$(mktemp -d)"
cd "${work}"
printf 'export VIGOS_SMOKE_OK=1\n' >.envrc
# direnv keys its allow-list on $HOME/.config/direnv; HOME is /root in the image.
direnv allow .
# Single quotes are intentional: VIGOS_SMOKE_OK must be expanded by the inner
# shell `direnv exec` spawns (with .envrc loaded), not by this outer shell.
# shellcheck disable=SC2016
got="$(direnv exec . sh -c 'printf %s "${VIGOS_SMOKE_OK:-}"')"
if [ "${got}" != "1" ]; then
	echo "::error::direnv exec did not load .envrc (got '${got}') — direnv runtime is broken"
	exit 1
fi
echo "direnv exec loaded .envrc (VIGOS_SMOKE_OK=${got})"

echo "== All in-container Nix runtime smoke checks passed =="
