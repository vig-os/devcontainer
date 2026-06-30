# Production images with `nix2container`

The devcontainer image is built with `dockerTools.buildLayeredImage` (see
`flake.nix`). For **production / runtime images in downstream packages**, use
**`nix2container`** instead — it gives finer layer control and much faster
push/pull than `dockerTools`, while still deriving from the **same pinned
`nixpkgs`** as the shared toolchain (so dev and prod never drift).

This keeps two builders for two jobs:

| Image | Builder | Contents |
|-------|---------|----------|
| **devcontainer** (this repo) | `dockerTools.buildLayeredImage` | full dev toolchain + Nix |
| **production** (your package) | `nix2container` | your app + its runtime closure only |

## Pattern

A complete, copy-pasteable example lives in
[`examples/nix2container-production/`](../examples/nix2container-production/flake.nix).
The essentials:

```nix
inputs = {
  vigos.url = "github:vig-os/devcontainer";   # shared toolchain SSoT
  nixpkgs.follows = "vigos/nixpkgs";           # same pinned nixpkgs as dev
  nix2container.url = "github:nlewo/nix2container";
  nix2container.inputs.nixpkgs.follows = "nixpkgs";
};
# ...
n2c = nix2container.packages.${system}.nix2container;
packages.productionImage = n2c.buildImage {
  name = "ghcr.io/your-org/your-app";
  tag = "latest";
  copyToRoot = [ app pkgs.cacert ];            # app + runtime deps ONLY
  config.Cmd = [ "${app}/bin/hello" ];
};
```

Build and push:

```bash
nix build .#productionImage
./result/bin/... copy-to docker://ghcr.io/your-org/your-app:latest   # nix2container skopeo helper
```

## Why follow `vigos/nixpkgs`

`nixpkgs.follows = "vigos/nixpkgs"` resolves the production image against the
*same* pinned revision the dev shell uses, so a CVE fixed by advancing the
toolchain pin (see [`CONTAINER_SECURITY.md`](CONTAINER_SECURITY.md)) lands in
production too, through the same Renovate-driven bump.

> The example references the published `github:vig-os/devcontainer` flake
> outputs (`lib`, `overlays.default`), so a full `nix build` of it works once
> the Nix toolchain migration (#625) is published to the default branch.
