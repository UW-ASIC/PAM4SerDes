# mux2_cmos

| Field | Value |
|---|---|
| Owner (from git history) | oDNA |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/mux2_cmos.va`](../../va/Transmitter/mux2_cmos.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), 24 per path (16 at level L1, 8 at level L2) |
| Section | [Transmitter](README.md) |

## Architecture

CMOS 2:1 multiplexer for the two slowest serializer levels: the output follows `in0` while `sel` is low and `in1` while it is high, through `rout` into `cout`. It is transparent (no latch).

In [tx_ser_ffe_path](tx_ser_ffe_path.md): 16 at level L1 (select `clk0p875`, 0.875 to 1.75 Gb/s, inputs from [dff_cmos_x32](../Clocking/dff_cmos_x32.md)) and 8 at level L2 (select `clk1p75`, 1.75 to 3.5 Gb/s, outputs to [dff_tspc_x8](../Clocking/dff_tspc_x8.md)). Which input is sent first differs between the two levels; the lane-order rules are on that page.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in0`, `in1` | input | The two data lanes, CMOS |
| `sel` | input | Select: low = `in0`, high = `in1`. Driven by a clock |
| `out` | output | The multiplexed lane, CMOS |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth` | 0.35 V | Select threshold |
| `vsmooth` | 0.01 V | Width of the select transition: the switch between the inputs is smooth |
| `rout` | 100 ohm | Output driver resistance. An estimate, written before the block was specified |
| `cout` | 20 fF | Output capacitance. An estimate, written before the block was specified |

**Not modelled:** supply pins and drive strength (the output is a mix of the input voltages), delay other than the output RC, jitter.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Level L1: two 0.875 Gb/s lanes to one at 1.75 Gb/s, select clock 0.875 GHz (`tx_ser_ffe_path.va`, header)
- Level L2: two 1.75 Gb/s lanes to one at 3.5 Gb/s, select clock 1.75 GHz (`tx_ser_ffe_path.va`, header)
- CMOS levels 0 to 0.7 V, select threshold 0.35 V (`mux2_cmos.va`, parameter `vth`)
- Output resistance 100 ohm and output capacitance 20 fF; both are marked as estimates (`mux2_cmos.va`, header)
- Its load at level L2 is the retiming flop `dff_tspc_x8`, setup time 15 ps (`dff_tspc_x8.va`, parameter `tsu`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/mux2_cmos_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
