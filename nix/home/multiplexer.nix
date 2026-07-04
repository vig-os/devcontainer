# vigos.multiplexer — org tmux configuration (#821).
#
# Config only where possible; the tmux binary itself also ships via
# vigos.packages (devTools). programs.tmux hard-requires a package for its
# plugin/wrapper plumbing — it comes from this module's pkgs (self-pkgs in
# the flake's own homeConfigurations), matching the devTools version, so no
# second copy appears in practice. extraConfig stays open for personal
# keybindings.
{
  config,
  lib,
  ...
}:
{
  options.vigos.multiplexer.enable = lib.mkEnableOption "the vigOS tmux configuration";

  config = lib.mkIf config.vigos.multiplexer.enable {
    programs.tmux = {
      enable = lib.mkDefault true;
      # vi keys and a sane scrollback are org defaults; everything is
      # mkDefault so a personal config overrides with a bare assignment.
      keyMode = lib.mkDefault "vi";
      historyLimit = lib.mkDefault 100000;
      mouse = lib.mkDefault true;
      escapeTime = lib.mkDefault 10;
      baseIndex = lib.mkDefault 1;
    };
  };
}
