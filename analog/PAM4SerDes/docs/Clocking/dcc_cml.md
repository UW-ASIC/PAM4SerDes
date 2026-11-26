# dcc_cml

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/dcc_cml.va`](../../va/Clocking/dcc_cml.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_dcc`); [rx_clkgen](rx_clkgen.md), once (`u_dcc`) |
| Section | [Clocking](README.md) |

## Architecture

The duty-cycle corrector, the first cell of both clock trees: 14 GHz in, the same frequency out with a high time of `duty_target` of the period, as a differential clock (the VCO clock is single-ended). The model measures the input period and runs its own oscillator at that frequency. The header warns that the output phase is not guaranteed to follow the input's rising edge, and says to use the model for functional duty-cycle testing.

In [tx_clkgen](tx_clkgen.md) and [rx_clkgen](rx_clkgen.md): the input is the VCO clock (from [tx_pll](tx_pll.md) or [rx_cdr](rx_cdr.md)), the output goes to [clkbuf_cml](clkbuf_cml.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk_in` | input | 14 GHz clock, single-ended. The port comment notes that a transistor-level CML version will need a differential input |
| `clk_outp`, `clk_outn` | output | Corrected clock, differential. The port comment says "need to confirm" |
| `vss` | inout | Ground. There is no `vdd` pin: the output levels are parameters |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `duty_target` | 0.500 | Output duty cycle, allowed 0.496 to 0.504 |
| `vth` | 0 V | Input threshold. Both parents set 0.35 V, the middle of the CMOS swing |
| `f_init` | 14 GHz | Frequency assumed until two rising edges have been seen |
| `vcm` | 0.6 V | Output common mode. Placeholder |
| `vdiff` | 0.4 V | Output differential amplitude. Placeholder |
| `t_edge` | 1 ps | Output transition time |

**Not modelled:** a correction loop (the model regenerates the clock, so it does not show how well or how fast a real corrector removes a duty-cycle error), jitter. With the placeholder levels each output swings between 0.4 V and 0.8 V, above the 0.7 V supply and not the CML level used elsewhere (0.4 V to 0.7 V); the `clkbuf_cml` behind it limits the signal.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Output duty cycle 49.6 % to 50.4 %, nominal 50 % (`dcc_cml.va`, comment "Project requirement" on `duty_target`)
- CML style (`dcc_cml.va`, header)
- Clock frequency 14 GHz nominal (`dcc_cml.va`, parameter `f_init`)
- Not specified by the project yet, according to the header: transistor topology, control algorithm, output common mode and output swing (`dcc_cml.va`, header)
- A transistor-level CML version will need a differential input; the model's input is single-ended (`dcc_cml.va`, port comment)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/dcc_cml_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
