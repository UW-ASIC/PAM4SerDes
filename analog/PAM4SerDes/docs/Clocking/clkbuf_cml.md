# clkbuf_cml

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/clkbuf_cml.va`](../../va/Clocking/clkbuf_cml.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_buf14`); [rx_clkgen](rx_clkgen.md), once (`u_buf14`) |
| Section | [Clocking](README.md) |

## Architecture

A current-mode-logic clock buffer. Per the header it restores the swing and isolates loads. It is a limiting amplifier with one pole: the differential input times `gain`, limited smoothly to plus or minus `vsw`, steers a tail current `vsw / rl` between two load resistors `rl` to `vdd`, so each output swings between `vdd` - `vsw` and `vdd`. At each input crossing a random time shift with standard deviation `rj` is applied to the output.

In [tx_clkgen](tx_clkgen.md) and [rx_clkgen](rx_clkgen.md) it drives `clk14`: the input comes from [dcc_cml](dcc_cml.md), and the output goes to the first [div2_cml](div2_cml.md) and to the 14 GHz cells of the datapath (listed on the two clock-tree pages). Both parents set `rj` to 40 fs times `rj_scale` and give the instance its own seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | Differential clock |
| `outp`, `outn` | output | Buffered clock, CML levels |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `gain` | 2 | Small-signal differential gain at DC |
| `vsw` | 0.3 V | Saturated differential output amplitude (0.6 V peak-to-peak differential) |
| `tau` | 5.707 ps | Output time constant |
| `vos` | 0 V | Input-referred offset, range -0.1 to +0.1 V |
| `rl` | 200 ohm | Load resistor on each side |
| `rj` | 40 fs | Added random jitter per output crossing, rms |
| `rj_seed` | 6 | Seed of the jitter sequence; every instance needs its own |

**Not modelled:** load-dependent bandwidth (`tau` is a fixed number), a bias input (the tail current is computed from `vsw` and `rl`), a duty-cycle error of its own other than through `vos`.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Carries the 14 GHz clock (`tx_clkgen.va` and `rx_clkgen.va`, header)
- Output 0.6 V peak-to-peak differential, each side between `vdd` - 0.3 V and `vdd` (`clkbuf_cml.va`, parameter `vsw`)
- Load resistor 200 ohm per side, which with the swing above means a tail current of 1.5 mA (`clkbuf_cml.va`, parameter `rl` and the line `iss = vsw / rl`)
- Output time constant 5.707 ps (`clkbuf_cml.va`, parameter `tau`)
- Added random jitter 40 fs rms per output crossing (`clkbuf_cml.va`, parameter `rj`)
- Small-signal differential gain 2 at DC (`clkbuf_cml.va`, parameter `gain`)
- In the receiver its loads are the 24 slicers, the DFE, the two retimers and the CDR phase detector (`rx_clkgen.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/clkbuf_cml_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
