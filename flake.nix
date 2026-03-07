{
  description = "eXoma devcontainer – host development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            # Build automation
            just

            # Version control & GitHub
            git
            gh

            # Python tooling
            uv

            # Node.js (bats, devcontainer CLI via npm)
            nodejs

            # Shell & JSON utilities
            jq
            tmux
            shellcheck

            # Linting
            hadolint
            taplo

            # Container runtime
            podman
          ];

          shellHook = ''
            echo "devcontainer dev environment loaded (nix)"
          '';
        };
      }
    );
}
