{
  description = "Example: a nix2container production image derived from the vigOS toolchain SSoT.";

  # Production/runtime images for downstream packages are built with
  # `nix2container` (better layering + push performance than dockerTools),
  # NOT the devcontainer's buildLayeredImage. They still follow the same pinned
  # nixpkgs as the shared toolchain (vigos), so dev and prod agree on versions.
  inputs = {
    vigos.url = "github:vig-os/devcontainer";
    nixpkgs.follows = "vigos/nixpkgs";
    flake-utils.follows = "vigos/flake-utils";
    nix2container.url = "github:nlewo/nix2container";
    nix2container.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs =
    {
      self,
      vigos,
      nixpkgs,
      flake-utils,
      nix2container,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ vigos.overlays.default ];
        };
        n2c = nix2container.packages.${system}.nix2container;

        # Replace with your built application. A minimal runtime closure — the
        # app and its runtime deps only, NOT the dev toolchain — is the point:
        # production images stay small while sharing the pinned nixpkgs.
        app = pkgs.hello;
      in
      {
        packages.productionImage = n2c.buildImage {
          name = "ghcr.io/your-org/your-app";
          tag = "latest";
          copyToRoot = [
            app
            pkgs.cacert
          ];
          config = {
            Cmd = [ "${app}/bin/hello" ];
            Env = [ "SSL_CERT_FILE=${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt" ];
          };
        };
      }
    );
}
