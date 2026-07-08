# vigos.shell — the org shell environment (#821).
#
# Bash AND zsh (macOS default) under one switch: colleagues keep their login
# shell, integrations land in both. Every scalar is mkDefault so a personal
# config overrides with a bare assignment (ADR override policy).
#
# secretsEnv (opt-in, default off): exports each file under
# ~/.config/vigos/secrets/<NAME> (the ADR resident-credentials interface) as
# an environment variable. NAME must match [A-Z_][A-Z0-9_]*; the trailing
# newline is stripped (command substitution); sourcing is idempotent via a
# guard variable and runs from both profile and rc files. systemd user
# services and non-interactive SSH commands are out of scope v1.
{
  config,
  lib,
  ...
}:
let
  cfg = config.vigos.shell;

  secretsHook = ''
    # vigos.shell.secretsEnv — resident-credentials interface (vig-os/devcontainer#821)
    if [ -z "''${VIGOS_SECRETS_LOADED:-}" ] && [ -d "${cfg.secretsEnv.dir}" ]; then
      for _vigos_secret in "${cfg.secretsEnv.dir}"/*; do
        [ -f "$_vigos_secret" ] || continue
        _vigos_name="$(basename "$_vigos_secret")"
        if printf '%s' "$_vigos_name" | grep -Eq '^[A-Z_][A-Z0-9_]*$'; then
          export "$_vigos_name=$(cat "$_vigos_secret")"
        fi
      done
      unset _vigos_secret _vigos_name
      export VIGOS_SECRETS_LOADED=1
    fi
  '';
in
{
  options.vigos.shell = {
    enable = lib.mkEnableOption "the vigOS shell environment (bash+zsh, starship, atuin, zoxide)";
    secretsEnv = {
      enable = lib.mkEnableOption "exporting ~/.config/vigos/secrets/<NAME> files as environment variables";
      dir = lib.mkOption {
        type = lib.types.str;
        default = "${config.home.homeDirectory}/.config/vigos/secrets";
        description = "Directory holding one file per secret (mode 0600), named like the target environment variable.";
      };
    };
  };

  config = lib.mkIf cfg.enable {
    programs = {
      bash = {
        enable = lib.mkDefault true;
        initExtra = lib.mkIf cfg.secretsEnv.enable secretsHook;
        profileExtra = lib.mkIf cfg.secretsEnv.enable secretsHook;
      };

      zsh = {
        enable = lib.mkDefault true;
        initContent = lib.mkIf cfg.secretsEnv.enable secretsHook;
        profileExtra = lib.mkIf cfg.secretsEnv.enable secretsHook;
      };

      # Prompt, history, and directory jumping — each ships its own bash/zsh
      # integration toggle, defaulting to on when the shells are enabled.
      starship.enable = lib.mkDefault true;
      atuin.enable = lib.mkDefault true;
      zoxide.enable = lib.mkDefault true;
    };
  };
}
