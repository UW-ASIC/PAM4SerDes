# rx_dec_retime

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/rx_dec_retime.va`](../../va/Receiver/rx_dec_retime.va) |
| Used in | [rx_top](rx_top.md), twice (`u_rt0`, `u_rt1`: one per sampling phase) |
| Section | [Receiver](README.md) |

## Architecture

A pair of flip-flops. On each rising clock edge it samples the decoded MSB and LSB of one sampling phase and holds them for a full clock period. It reads CMOS logic levels and drives CML.

In [rx_top](rx_top.md), one per phase: inputs from one [pam4_dec](pam4_dec.md) in [rx_decision](rx_decision.md), clock `clk14` from [rx_clkgen](../Clocking/rx_clkgen.md), outputs to the MSB and the LSB [rx_deser_path](rx_deser_path.md). Phase 1's instance has its clock connected swapped, so it retimes on the falling edge.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `msb_in`, `lsb_in` | input | Decoded bits of one phase, CMOS levels |
| `clk_p`, `clk_n` | input | 14 GHz CML clock; sampling at its rising zero crossing |
| `msb_out_p/n` | output | Retimed MSB, CML |
| `lsb_out_p/n` | output | Retimed LSB, CML |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_data` | 0.9 V | Input threshold. `rx_top` sets 0.35 V |
| `vdd` | 1.0 V | Supply the output levels follow. `rx_top` sets 0.7 V |
| `v_swing` | 0.3 V | Swing of each output leg |
| `v_cm` | `vdd` - `v_swing`/2 | Output common mode |

**Not modelled:** clock-to-output delay and edge time (the outputs change at the instant of the clock edge), setup and hold checks, supply pins. The file has no comments; this page is read from the code and from `rx_top.va`.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Two bits (MSB and LSB) per phase at 14 Gb/s, clock 14 GHz (`rx_top.va`, header)
- Phase 0 is retimed on the rising edge of the clock, phase 1 on the falling edge (`rx_top.va`, header)
- Input: CMOS logic from the decoder, threshold 0.35 V (`rx_top.va`, instance lines)
- Output: CML, each leg swings 0.3 V around `vdd` - 0.15 V (`rx_dec_retime.va`, parameters `v_swing`, `v_cm`)
- Its load is the first deserializer stage, which samples just after the rising edge of the 14 GHz clock (`rx_top.va`, header)
- The model gives no setup, hold or clock-to-output numbers: these are for the owner to set

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/rx_dec_retime_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
