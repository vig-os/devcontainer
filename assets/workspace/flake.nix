{
  description = "Project development environment (vigOS toolchain).";

  # Downstream repos consume the shared toolchain as a flake INPUT, so updating
  # the dev environment means bumping that input — it never overwrites your
  # files. To update: `nix flake update vigos`.
  inputs = {
    # The shared vigOS toolchain (single source of truth).
    # This scaffold deliberately FLOATS on the default branch so a fresh
    # project works before its first pin. Once you depend on stability
    # (especially the vigos.* home-manager module options), pin a release
    # tag instead and bump deliberately:
    #   vigos.url = "github:vig-os/devcontainer?ref=<tag>";
    # Policy: docs/NIX.md "Home-manager modules - versioning & release policy".
    vigos.url = "github:vig-os/devcontainer";
    # Follow vigos's pinned nixpkgs + flake-utils so your tools match the
    # toolchain exactly (one resolved nixpkgs, no drift).
    nixpkgs.follows = "vigos/nixpkgs";
    flake-utils.follows = "vigos/flake-utils";
  };

  outputs =
    {
      self,
      vigos,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ vigos.overlays.default ];
          config.allowUnfree = true;
        };

        # ────────────────────────────────────────────────────────────────────
        # Your project tools go here. This block is YOURS: a dev-environment
        # update never overwrites it (scaffold-once / never-overwrite, the same
        # guarantee as justfile.project and docker-compose.project.yaml).
        #
        #   extraPackages = pkgs: [
        #     pkgs.postgresql_16
        #     pkgs.ffmpeg
        #   ];
        # ────────────────────────────────────────────────────────────────────
        extraPackages = pkgs: [
          # add project tools here
        ];
      in
      {
        # The dev shell = the shared vigOS toolchain + your extras.
        # `direnv allow` (via .envrc) or `nix develop` enters it.
        devShells.default = vigos.lib.mkProjectShell {
          inherit pkgs;
          extraPackages = extraPackages pkgs;
        };

        # Opt-in local dev services (#795): a daemonless process-compose stack
        # (Postgres, SeaweedFS/S3, Redis, …) with service versions from the
        # pinned vigos nixpkgs — no Docker/Podman daemon, no extra flake
        # inputs. Uncomment, then `nix run .#services` (or enable the
        # `services` recipe in justfile.project); service state lands in
        # ./data — add it to .gitignore.
        #
        #   packages.services = vigos.lib.mkProjectServices {
        #     inherit pkgs;
        #     modules = [ { services.postgres."db".enable = true; } ];
        #   };

        # Future (upstream, opt-in): vigos may expose modular language shells —
        # e.g. `vigos.devShells.${system}.{cpp,geant4,dataAnalysis}` — that you
        # select without changing this scaffold. Out of scope today.
      }
    );
}
