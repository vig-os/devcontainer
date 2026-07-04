# vigos.sesh — one-keypress project sessions with a standard tmux layout
# (#824). Parameterized port of the maintainer's proven setup: the hardcoded
# project list became the `sessions` option, the window set became
# `layout.windows` with devTools-only defaults.
#
# Packages: sesh and the two generated scripts ship from here — sesh is NOT
# in devTools, so this does not duplicate vigos.packages.
{
  config,
  lib,
  pkgs,
  ...
}:
let
  cfg = config.vigos.sesh;

  windowFlags = w: "-n ${lib.escapeShellArg w.name} -c \"$PWD\"";

  # Build the standard layout: window 1 hosts the first entry (its command
  # runs in place with a shell fallback so the window survives quitting the
  # TUI); the rest are created detached, commands typed via send-keys against
  # captured window ids (stable even if names collide or auto-rename).
  seshLayout = pkgs.writeShellApplication {
    name = "sesh-layout";
    runtimeInputs = [ pkgs.tmux ];
    text = ''
      sess=$(tmux display-message -p '#S')

      # Idempotent guard: re-running (or a restored session that already has
      # the first window's name) must not duplicate windows.
      if tmux list-windows -t "$sess" -F '#{window_name}' | grep -qx ${lib.escapeShellArg (lib.head cfg.layout.windows).name}; then
        tmux select-window -t "$sess:${(lib.head cfg.layout.windows).name}" || true
        exit 0
      fi

      tmux rename-window -t "$sess:1" ${lib.escapeShellArg (lib.head cfg.layout.windows).name}
      ${lib.concatMapStringsSep "\n" (
        w:
        if w.command != null then
          ''
            wid=$(tmux new-window -d -P -F '#{window_id}' -t "$sess:" ${windowFlags w})
            tmux send-keys -t "$wid" ${lib.escapeShellArg w.command} Enter
          ''
        else
          ''tmux new-window -d -t "$sess:" ${windowFlags w}''
      ) (lib.tail cfg.layout.windows)}
      tmux select-window -t "$sess:1"
      ${lib.optionalString ((lib.head cfg.layout.windows).command != null) ''
        ${(lib.head cfg.layout.windows).command} || true
      ''}
      exec "''${SHELL:-bash}"
    '';
  };

  # Curated-seeds picker: fzf over the sessions list (plus live tmux
  # sessions), in sesh.toml order. Bind it where you like — tmux gets a
  # popup bind below; a desktop key is personal-config territory.
  seshPicker = pkgs.writeShellApplication {
    name = "sesh-picker";
    runtimeInputs = with pkgs; [
      sesh
      fzf
      zoxide
      tmux
    ];
    text = ''
      selected=$(sesh list -c -d -H -i | fzf --ansi --no-sort --prompt='project> ' --height=100%) || exit 0
      [ -z "$selected" ] && exit 0
      exec sesh connect "$selected"
    '';
  };

  windowModule = lib.types.submodule {
    options = {
      name = lib.mkOption {
        type = lib.types.str;
        description = "tmux window name.";
      };
      command = lib.mkOption {
        type = lib.types.nullOr lib.types.str;
        default = null;
        description = "Command launched in the window (null = plain shell).";
      };
    };
  };

  sessionModule = lib.types.submodule {
    options = {
      name = lib.mkOption {
        type = lib.types.str;
        example = "vigOS · devcontainer";
        description = "Picker label; use a 'Group · project' prefix to cluster the list.";
      };
      path = lib.mkOption {
        type = lib.types.str;
        description = "Project directory the session starts in.";
      };
    };
  };

  sessionToml = s: ''
    [[session]]
    name = "${s.name}"
    path = "${s.path}"
  '';
in
{
  options.vigos.sesh = {
    enable = lib.mkEnableOption "sesh project sessions with the standard tmux layout";
    sessions = lib.mkOption {
      type = lib.types.listOf sessionModule;
      default = [ ];
      description = "Curated project seeds shown by sesh-picker, in order.";
    };
    layout.windows = lib.mkOption {
      type = lib.types.listOf windowModule;
      default = [
        {
          name = "edit";
          command = "nvim .";
        }
        {
          name = "git";
          command = "lazygit";
        }
        { name = "shell"; }
        # A plain shell on purpose: no agent session/API call fires on
        # connect — type `claude` when wanted (worktrees for parallel runs).
        { name = "claude"; }
      ];
      description = "Standard window set for every new session; the first entry owns window 1.";
    };
  };

  config = lib.mkIf cfg.enable {
    home = {
      packages = [
        pkgs.sesh
        seshLayout
        seshPicker
      ];
      file.".config/sesh/sesh.toml".text = ''
        [default_session]
        startup_command = "sesh-layout"

        ${lib.concatMapStringsSep "\n" sessionToml cfg.sessions}
      '';
    };

    # prefix+o pops the picker inside tmux (merges with vigos.multiplexer).
    programs.tmux.extraConfig = lib.mkAfter ''
      bind o display-popup -E "sesh-picker"
    '';
  };
}
