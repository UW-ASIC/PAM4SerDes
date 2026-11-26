# The smallest shell that can check the Verilog-A design: VerA, ngspice, make, python.
# .github/workflows/analog.yaml runs `make -C analog/PAM4SerDes/build/sim check` in it, so
# CI does not build the whole EDA shell. Same pins as shell.nix.
#
#   nix-shell .flows/env/va.nix --run "make -C analog/PAM4SerDes/build/sim check"
{
  pkgs ?
    import (builtins.fetchTarball "https://github.com/NixOS/nixpkgs/archive/nixos-25.11.tar.gz")
      { },
}:
let
  eda = builtins.getFlake "github:OmarSiwy/EDA-Packaged";
  analog = import ./Analog.nix { inherit pkgs eda; };
in
pkgs.mkShell {
  name = "va-check";
  packages = [
    analog.vera
    analog.ngspice
    pkgs.gnumake
    pkgs.python3
  ];
}
