# vigos.git — org git environment (#821).
#
# Identity and signing are OPTIONS with null defaults: the module writes
# nothing it was not told (a fresh host must never fail its first commit
# because a signing key does not exist yet). Key minting and forge
# registration are runbook steps (docs/home, #826) — per-user × host keys,
# never copied, so a signature identifies the machine it was made on.
{
  config,
  lib,
  ...
}:
let
  cfg = config.vigos.git;
in
{
  options.vigos.git = {
    enable = lib.mkEnableOption "the vigOS git environment (git+delta, gh, lazygit)";
    userName = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = "Git author/committer name; nothing is written when null.";
    };
    userEmail = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      description = "Git author/committer email; nothing is written when null.";
    };
    signingKeyPath = lib.mkOption {
      type = lib.types.nullOr lib.types.str;
      default = null;
      example = "~/.ssh/id_ed25519_signing.pub";
      description = ''
        Path to the per-user x host SSH signing key. SSH-format commit
        signing activates only when set; null (the default) writes no
        signing configuration at all.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    programs = {
      git = lib.mkMerge [
        {
          enable = lib.mkDefault true;
          delta.enable = lib.mkDefault true;
        }
        (lib.mkIf (cfg.userName != null) { userName = lib.mkDefault cfg.userName; })
        (lib.mkIf (cfg.userEmail != null) { userEmail = lib.mkDefault cfg.userEmail; })
        (lib.mkIf (cfg.signingKeyPath != null) {
          signing = {
            key = lib.mkDefault cfg.signingKeyPath;
            format = lib.mkDefault "ssh";
            signByDefault = lib.mkDefault true;
          };
        })
      ];

      gh = {
        enable = lib.mkDefault true;
        settings.git_protocol = lib.mkDefault "ssh";
      };

      lazygit.enable = lib.mkDefault true;
    };
  };
}
