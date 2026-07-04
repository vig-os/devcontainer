# bats with its helper libraries (support/assert/file), wrapped so
# BATS_LIB_PATH can be derived from one place. Shared by the devTools list
# (nix/devtools.nix), mkProjectShell, and the image env. Refs #695, #818.
pkgs:
pkgs.bats.withLibraries (p: [
  p.bats-support
  p.bats-assert
  p.bats-file
])
