# vigos.cli — modern-unix CLI configuration (#821).
#
# CONFIGURATION ONLY: packages ship solely via vigos.packages (the devTools
# SSoT) — this module never adds home.packages. The HM programs.* modules
# used here install their package attribute as a side effect; those resolve
# from this module's pkgs (self-pkgs in the flake's homeConfigurations), the
# same derivations devTools carries, so the union stays one store path per
# tool.
{
  config,
  lib,
  ...
}:
{
  options.vigos.cli.enable = lib.mkEnableOption "the vigOS modern-unix CLI configuration (config only; packages ship via vigos.packages)";

  config = lib.mkIf config.vigos.cli.enable {
    programs = {
      bat.enable = lib.mkDefault true;
      eza = {
        enable = lib.mkDefault true;
        git = lib.mkDefault true;
      };
      fzf.enable = lib.mkDefault true;
      ripgrep.enable = lib.mkDefault true;
      fd.enable = lib.mkDefault true;
    };
  };
}
