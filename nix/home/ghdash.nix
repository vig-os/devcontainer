# vigos.ghdash — gh-dash PR/issue dashboard (#824). Parameterized port: the
# hardcoded personal repo filters became `repoFilters`; the CPU-tuning
# lessons (lean scoped sections, capped closed lists) are the defaults.
# Reuses the gh login; the gh-dash package rides this module (not devTools).
{
  config,
  lib,
  ...
}:
let
  cfg = config.vigos.ghdash;

  scope = if cfg.repoFilters == [ ] then "involves:@me" else lib.concatStringsSep " " cfg.repoFilters;

  sections = [
    {
      title = "Involved";
      filters = "is:open involves:@me ${scope}";
    }
    {
      title = "Open";
      filters = "is:open ${scope}";
    }
    {
      title = "Recently closed";
      filters = "is:closed ${scope} sort:updated-desc";
      limit = 10;
    }
  ];
in
{
  options.vigos.ghdash = {
    enable = lib.mkEnableOption "the gh-dash PR/issue dashboard";
    repoFilters = lib.mkOption {
      type = lib.types.listOf lib.types.str;
      default = [ ];
      example = [ "repo:vig-os/devcontainer" ];
      description = ''
        GitHub search scope for the generated sections (e.g. repo:/org:
        qualifiers). Empty = everything involving you. Scoping to the repos
        you work in keeps each idle dashboard cheap.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    programs.gh-dash = {
      enable = lib.mkDefault true;
      settings = {
        prSections = lib.mkDefault sections;
        issuesSections = lib.mkDefault sections;
        defaults.refetchIntervalMinutes = lib.mkDefault 10;
      };
    };
  };
}
