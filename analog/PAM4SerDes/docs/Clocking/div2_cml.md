# div2_cml

| Field | Value |
|---|---|
| Owner (from git history) | none yet |
| Kind | placeholder (ideal stand-in, no owner) |
| Model | [`va/Clocking/placeholders/div2_cml.va`](../../va/Clocking/placeholders/div2_cml.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_div7`); [rx_clkgen](rx_clkgen.md), twice (`u_div7`, `u_div3p5`) |
| Section | [Clocking](README.md) |

## Architecture

**Ideal placeholder with no owner: someone needs to take this block.** It halves the frequency of a CML clock, for the fastest divider steps; the slower ones use [div2_tspc](div2_tspc.md). The header says this file is not the team's `div2_cml`: it exists so that the two clock trees compile and simulate until the real block is committed. The output toggles on every rising zero crossing of the differential input, at the levels of [clkbuf_cml](clkbuf_cml.md), and starts with `outp` low. To divide on the falling edge, the parent connects the input swapped.

| Parent | Instance | Step | Edge |
|---|---|---|---|
| [tx_clkgen](tx_clkgen.md) | `u_div7` | `clk14` to `clk7` | Rising edge of `clk14` |
| [rx_clkgen](rx_clkgen.md) | `u_div7` | `clk14` to `clk7` | Rising edge of `clk14` |
| [rx_clkgen](rx_clkgen.md) | `u_div3p5` | `clk7` to `clk3p5` | Falling edge of `clk7` (input swapped) |

The outputs feed the CML cells of the datapath and, through [cml2cmos](cml2cmos.md), the CMOS part of each tree.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | Differential clock in |
| `outp`, `outn` | output | Differential clock at half the frequency, CML levels |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vsw` | 0.3 V | Differential output amplitude (half of the peak-to-peak value) |
| `trf` | 5 ps | Output edge duration (a straight ramp) |
| `tpd` | 15 ps | Input zero crossing to output zero crossing delay |

**Not modelled:** a maximum frequency, jitter, reset. The parameter values are convenient for the placeholder, not targets.

## Topology research

*No owner yet. To be filled in by whoever takes this block.*

Known from the model (defaults are assumptions to confirm):

- Divide 14 GHz to 7 GHz in both clock trees, and 7 GHz to 3.5 GHz in the receiver (`tx_clkgen.va` and `rx_clkgen.va`, header)
- Output at the same levels as `clkbuf_cml`: 0.6 V peak-to-peak differential, each side between `vdd` - 0.3 V and `vdd` (`div2_cml.va`, header and parameter `vsw`)
- The receiver needs both a rising-edge and a falling-edge divider; the placeholder gets the second by swapping its inputs (`rx_clkgen.va`, header)
- Placeholder timing, not a target: 15 ps delay, 5 ps edges (`div2_cml.va`, parameters `tpd`, `trf`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/div2_cml_<what>.svg`); open questions; references.

## Sizing research

*No owner yet. To be filled in once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
