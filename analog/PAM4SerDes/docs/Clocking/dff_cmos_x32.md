# dff_cmos_x32

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model); retiming flops, used in the TX serializer |
| Model | [`va/Clocking/dff_cmos_x32.va`](../../va/Clocking/dff_cmos_x32.va) |
| Used in | [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), once per path (`u_rin`), so twice in the transmitter |
| Section | [Clocking](README.md) |

## Architecture

A bank of 32 D flip-flops on one clock: each copies its input to its output on the rising clock edge. At the start of the serializer it retimes the 32-bit word to the 0.875 GHz word clock. It is kept with the clocking cells because it is a retiming element.

Level L0 of [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md): inputs from [prbs_gray_src](../Transmitter/prbs_gray_src.md), clock `clk0p875` from [tx_clkgen](tx_clkgen.md), outputs to the sixteen [mux2_cmos](../Transmitter/mux2_cmos.md) of level L1.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | Clock, single-ended CMOS. Flops trigger on its rising edge |
| `d0` .. `d31` | input | Data in, one pin per bit |
| `q0` .. `q31` | output | Data out, one pin per bit |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_clk`, `vth_data` | 0.5 V, 0.5 V | Clock and data thresholds. The parent sets 0.35 V |
| `vlow`, `vhigh` | 0 V, 1.0 V | Output levels. The parent sets `vhigh` = 0.7 V |
| `t_propogation` | 0 | Clock-to-output delay (spelled this way in the file) |
| `t_rise`, `t_fall` | 0, 0 | Output edge times. The parent sets 20 ps |

**Not modelled:** setup and hold checks (whatever the input is at the clock edge is taken), clock-to-output delay (it is 0), jitter, supply pins, reset and enable. The header says reset and enable are not specified in the project notes it was written from, and calls the interface provisional.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- 32 lanes at 0.875 Gb/s, retimed on the rising edge of the 0.875 GHz clock (`tx_ser_ffe_path.va`, header)
- CMOS levels 0 to 0.7 V, thresholds at 0.35 V, output edges 20 ps, as set by the parent (`tx_ser_ffe_path.va`, instance `u_rin`)
- Reset and enable: not specified, so the model has neither (`dff_cmos_x32.va`, header)
- The interface (one shared clock, 32 single-ended inputs and outputs) is marked provisional (`dff_cmos_x32.va`, header)
- The model gives no setup, hold or clock-to-output numbers: these are for the owner to set

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/dff_cmos_x32_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
