# vga

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/vga.va`](../../va/Receiver/vga.va) |
| Used in | [rx_afe](rx_afe.md), once (`u_vga`) |
| Section | [Receiver](README.md) |

## Architecture

The variable-gain amplifier, the last cell of the analog front end: it brings the signal to the amplitude the slicer thresholds were chosen for.

- The gain in dB is a straight line in `vctrl` between `v_min` and `v_max`, clamped outside that range. Both default gains are below 0 dB, so with the defaults the block attenuates.
- One pole at `fp`, a hard clip at plus or minus `vout_limit`, a fixed output common mode, and `r_in` from each input to ground (the CTLE drives only a differential voltage, so the input common mode needs a DC path).

In [rx_afe](rx_afe.md), after the [ctle](ctle.md). It drives the 24 slicers in [rx_decision](rx_decision.md) and the phase detector in [rx_cdr](../Clocking/rx_cdr.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in_p`, `in_n` | input | Signal from the CTLE |
| `vctrl` | input | Gain control voltage |
| `out_p`, `out_n` | output | Amplified signal around the common mode |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `min_gain_db` | -4.703 dB | Gain at `vctrl` = `v_min` |
| `max_gain_db` | -1.847 dB | Gain at `vctrl` = `v_max` |
| `v_min`, `v_max` | 0 V, 1.0 V | Control voltage range. `rx_afe` sets 0 and 0.7 V |
| `common_mode` | 0.9 V | Output common mode. `rx_afe` sets 0.55 V |
| `fp` | 39.16 GHz | Pole frequency |
| `vout_limit` | 0.2 V | Largest differential output, either sign |
| `r_in` | 1 Gohm | Resistance from each input to ground |
| `r_out` | 0 | Declared, but not used in the model |

**Not modelled:** noise, offset, loading by the slicers (the outputs are ideal voltage sources), gradual compression, the `g[5:0]` gain code, supply pins. The block prints its output voltage at every time step with `$strobe`.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Gain range -4.703 dB to -1.847 dB (`vga.va`, parameters `min_gain_db`, `max_gain_db`)
- Control voltage 0 to 0.7 V in the hierarchy; the cell's own default range is 0 to 1 V (`rx_afe.va`, header)
- The gain is meant to be set by a `g[5:0]` code, which is not modelled yet (`rx_afe.va`, header)
- Bandwidth: one pole at 39.16 GHz (`vga.va`, parameter `fp`)
- Output limited to plus or minus 0.2 V differential (`vga.va`, parameter `vout_limit`)
- Output common mode 0.55 V in the hierarchy; the cell's own default of 0.9 V is above the 0.7 V supply (`rx_afe.va`, header)
- Levels expected at its output, the slicer inputs: plus or minus 150 mV and plus or minus 50 mV (`slicer.va`, header)
- Loads: 24 slicers and the CDR phase detector (`rx_afe.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/vga_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
