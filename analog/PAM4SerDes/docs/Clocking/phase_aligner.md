# phase_aligner

| Field | Value |
|---|---|
| Owner (from git history) | Winy |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/phase_aligner.va`](../../va/Clocking/phase_aligner.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_pa`) |
| Section | [Clocking](README.md) |

## Architecture

A small feedback loop that shifts the 7 GHz CMOS clock until it lines up with the data, so that the hand-off from CMOS-clocked to CML-clocked serializer stages samples in the middle of the bit. The top module has no parameters and only wires eight helper modules from the same file; the values below are written in its instance lines.

| Step | Helper | What it does |
|---|---|---|
| 1 | `delay_t3` | Delays the data by `t3` = 71.43 ps. The file's comment: one bit at 14 Gb/s |
| 2 | `mult_1` | Compares the data with its delayed copy: +0.3 V when they differ, -0.3 V when they are the same. This marks the data's transitions |
| 3 | `mult_2` | Multiplies that by the output clock minus `vmid` = 0.35 V, the mid level of the CMOS clock |
| 4 | `vi_converter` | Turns the product into a current, `g` = 1 mS |
| 5 | `capacitor` | Integrates the current on `c` = 1 pF (default). Its voltage is the loop's state |
| 6 | `pi_control` | Scales the capacitor voltage by 1 / `vmax` to a setting `m`; `vmax` = 0.7 V is the voltage that means full delay |
| 7 | `pi` | Delays the input clock by `m` times `dmax` = 142.86 ps (one period of 7 GHz), with `m` limited to 0.01 .. 1. This stands for the phase interpolator |
| 8 | `buffer` | Drives the delayed clock out |

The loop is at rest when the average of step 3 is zero.

In [tx_clkgen](tx_clkgen.md), between [cml2cmos](cml2cmos.md) and the first [div2_tspc](div2_tspc.md), so every CMOS clock of the transmitter (3.5, 1.75 and 0.875 GHz) moves with its output. Its data input comes from [tx_top](../Transmitter/tx_top.md): lane 0 of the MSB path after [cml_dff_x4](cml_dff_x4.md), through an ideal `diff2se` cell (see [glue](glue.md)).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `cml_dff_x4` | input | The data to align to: retimed 7 Gb/s lane, single-ended around 0 V |
| `clk7_cml2cmos` | input | 7 GHz CMOS clock from `cml2cmos` |
| `ck_28` | output | The shifted 7 GHz CMOS clock. Despite its name it carries 7 GHz: `tx_clkgen` feeds it to the 7 to 3.5 GHz divider |

**Not modelled:** a real phase interpolator (it is a pure variable delay; its smallest delay is about 1.4 ps and not 0, because a zero delay stalls ngspice), jitter, offset, capacitor leakage, a reset input (the capacitor starts at 0 V), supply pins (the helpers use an internal ground).

**Checked by:** [`test/pa_test.sp`](../../test/pa_test.sp) for the whole block, [`test/delay_test.sp`](../../test/delay_test.sp) and [`test/viconv_output_test.sp`](../../test/viconv_output_test.sp) for its parts.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Clock in and out: 7 GHz, CMOS, 0 to 0.7 V (`tx_clkgen.va`, header; `phase_aligner.va`, `vmid` = 0.35 V and `vmax` = 0.7 V)
- Data input: a retimed 7 Gb/s lane, read as a single-ended signal around 0 V (`tx_top.va`, header)
- Delay range of the phase shifter up to 142.86 ps, one period of the 7 GHz clock (`phase_aligner.va`, `dmax`)
- Data delay 71.43 ps in the edge detector (`phase_aligner.va`, `t3`)
- Loop integrator in the model: 1 mS into 1 pF (`phase_aligner.va`, `g` and the default of `c`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/phase_aligner_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
