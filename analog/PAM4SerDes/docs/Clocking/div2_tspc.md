# div2_tspc

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/div2_tspc.va`](../../va/Clocking/div2_tspc.va) |
| Used in | [tx_clkgen](tx_clkgen.md), three times (`u_d3p5`, `u_d1p75`, `u_d0p875`); [rx_clkgen](rx_clkgen.md), twice (`u_d1p75`, `u_d0p875`) |
| Section | [Clocking](README.md) |

## Architecture

Halves the frequency of a CMOS clock, for the clocks below 7 GHz in both clock trees. The header names the logic style: true single-phase clock (TSPC). The output toggles on the falling edge of the clock; `rst` high forces `q` low and keeps it there. If a clock period falls outside 1/`fmax` .. 1/`fmin` the model prints a warning.

- In [tx_clkgen](tx_clkgen.md): `u_d3p5` (aligned 7 GHz from [phase_aligner](phase_aligner.md) to 3.5 GHz; its `qb` is used as `clk3p5b`), `u_d1p75` (3.5 to 1.75 GHz) and `u_d0p875` (1.75 to 0.875 GHz).
- In [rx_clkgen](rx_clkgen.md): `u_d1p75` (3.5 GHz from [cml2cmos](cml2cmos.md) to 1.75 GHz) and `u_d0p875` (1.75 to 0.875 GHz).
- Both parents set `rj` to 300 fs times `rj_scale` and give every instance its own seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | CMOS clock in |
| `rst` | input | Reset, active high |
| `q`, `qb` | output | Clock at half the frequency and its complement, CMOS |
| `vdd`, `vss` | inout | 0.7 V core supply and ground. The input threshold is half the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `tpd_r` | 30 ps | Delay from clock 50 % to rising `q` 50 % |
| `tpd_f` | 30 ps | Delay from clock (or `rst`) 50 % to falling `q` 50 % |
| `trf` | 25 ps | Output edge duration, 0 to 100 % (a straight ramp) |
| `rj` | 300 fs | Added random jitter per output edge, rms |
| `rj_seed` | 3 | Seed of the jitter sequence; every instance needs its own |
| `rout` | 100 ohm | Output driver resistance, 0 for an ideal source |
| `fmin`, `fmax` | 743.75 MHz, 8.05 GHz | Specified clock frequency range |

**Not modelled:** failure outside the frequency range (only warnings), dependence of the delays on load, supply or input slope, correlated jitter (one independent random draw per output edge).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Specified clock range 743.75 MHz to 8.05 GHz (`div2_tspc.va`, parameters `fmin`, `fmax`)
- Steps used today: 7 to 3.5, 3.5 to 1.75 and 1.75 to 0.875 GHz (`div2_tspc.va`, header; `tx_clkgen.va`; `rx_clkgen.va`)
- Added random jitter 300 fs rms per output edge (`div2_tspc.va`, parameter `rj`)
- Delay 30 ps from clock 50 % to output 50 %, rising and falling; output edge 25 ps (`div2_tspc.va`, parameters `tpd_r`, `tpd_f`, `trf`)
- True single-phase clock (TSPC) logic (`div2_tspc.va`, header)
- Active-high reset that forces `q` low; complementary outputs `q` and `qb` (`div2_tspc.va`, code)
- Output driver resistance 100 ohm (`div2_tspc.va`, parameter `rout`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/div2_tspc_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
