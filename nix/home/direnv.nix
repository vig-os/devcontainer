# vigos.direnv — direnv + nix-direnv (#821).
#
# The org's per-project activation layer (ADR-nix-devenv-strategy axis 1):
# `use flake` in a repo's .envrc activates its mkProjectShell dev-shell,
# GC-rooted so re-entry is instant. Shell integrations follow the enabled
# shells automatically.
{
  config,
  lib,
  ...
}:
{
  options.vigos.direnv.enable = lib.mkEnableOption "direnv + nix-direnv integration";

  config = lib.mkIf config.vigos.direnv.enable {
    programs.direnv = {
      enable = lib.mkDefault true;
      nix-direnv.enable = lib.mkDefault true;
    };
  };
}
