# cdr_pd_linear

| Field | Value |
|---|---|
| Owner (from git history) | Winy |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/cdr_pd_linear.va`](../../va/Clocking/cdr_pd_linear.va) |
| Used in | [rx_cdr](rx_cdr.md), once (`u_pd`) |
| Section | [Clocking](README.md) |

## Architecture

The linear phase detector of the receiver's clock recovery: it compares the incoming data with the 14 GHz clock and puts out a current proportional to the phase error. The top module only wires four helper modules from the same file. The file has no comments, so this is read from the wiring; `t3` and `g` are written in the instance lines.

| Step | Helper | What it does |
|---|---|---|
| 1 | `delay_t3` | Delays the data by `t3` = 17.857 ps |
| 2 | `mult_1` (`tdxor`) | Compares the data with its delayed copy: +0.3 V when they differ, -0.3 V when they are the same. This makes a pulse at every data transition |
| 3 | `mult_1` (`clkxor`) | Does the same with the in-phase and the quadrature clock. The result toggles at twice the clock rate |
| 4 | `delay_t3` twice | Delays that by `t18` and then by `dt4` |
| 5 | `mult_2` (`mixer`) | Multiplies the delayed clock signal by the data-transition pulses |
| 6 | `vi_converter` | Turns the product into the output current, `g` = 0.8755 mS |

In [rx_cdr](rx_cdr.md): `vout_b` is the front end's output and `clk14_I` the 14 GHz clock from [rx_clkgen](rx_clkgen.md), each through an ideal `diff2se`; `clk14_Q` is that clock through the ideal `qdelay` (both on the [glue](glue.md) page); `vi_ou` drives the loop's `vctl` node, where [loop_filter_rc](loop_filter_rc.md) turns the current into the control voltage. The top level sets the `qdelay` to three quarters of a period, not a quarter, so that the loop settles at this detector's intended lock point: see [Clock recovery](../../../../CHANGELOGS.md#clock-recovery-the-detector-and-the-loop-disagree-on-sign).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vout_b` | input | Data, single-ended around 0 V |
| `clk14_I` | input | 14 GHz clock, in phase, single-ended around 0 V |
| `clk14_Q` | input | 14 GHz clock, quadrature copy |
| `vi_ou` | output | Output current, into the loop filter node |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `t18` | 1.8 ps | First delay on the clock path |
| `dt4` | 26.78 ps | Second delay on the clock path |

**Not modelled:** the four PAM4 levels (`mult_1` compares its inputs with 0 V, so the detector sees only the sign of the data), bandwidth, offset, noise, an output compliance limit, supply pins (the helpers use an internal ground). The file does not explain how `t18`, `dt4` and `g` were chosen.

**Checked by:** [`test/cdr_pd_linear_test.sp`](../../test/cdr_pd_linear_test.sp).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Clock 14 GHz, in-phase and quadrature; the quadrature copy is a quarter period, 17.857 ps, later (`rx_cdr.va`, header and parameter `tq`)
- The architecture drawing has no quadrature clock source, so `rx_cdr` makes one with an ideal delay: where the real one comes from is open (`rx_cdr.va`, header)
- Inputs are read as single-ended signals around 0 V; the real data and clock are differential (`rx_cdr.va`, header)
- Output: a current into the loop filter node, gain 0.8755 mS in the model (`cdr_pd_linear.va`, `g`)
- Loop it works in: R = 2.352 kohm, C = 20 pF, C2 = 1 pF, 16.8 MHz CDR bandwidth, damping factor 1 (`rx_cdr.va`, header)
- Internal delays in the model: 17.857 ps on the data, 1.8 ps and 26.78 ps on the clock path (`cdr_pd_linear.va`, `t3`, `t18`, `dt4`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/cdr_pd_linear_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
