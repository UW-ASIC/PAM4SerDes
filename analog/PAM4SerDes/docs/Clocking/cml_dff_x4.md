# cml_dff_x4

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model); retiming flops, used in the TX serializer |
| Model | [`va/Clocking/cml_dff_x4.va`](../../va/Clocking/cml_dff_x4.va) |
| Used in | [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), once per path (`u_rcml`), so twice in the transmitter |
| Section | [Clocking](README.md) |

## Architecture

A bank of four differential CML D flip-flops on one differential clock: each copies its input to its output on the rising clock edge. It retimes the four 7 Gb/s lanes from the charge-steering multiplexers, which are clocked from the CMOS clock family, to the 7 GHz CML clock. Its lane 0 output is also the data the [phase_aligner](phase_aligner.md) locks the CMOS clocks to. It is kept with the clocking cells because it is a retiming element.

In [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), between level L3 (four [mux2_cs](../Transmitter/mux2_cs.md)) and level L4 (two [mux2_cml_hr](../Transmitter/mux2_cml_hr.md)), clocked by `clk7_p/n` from [tx_clkgen](tx_clkgen.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk_p`, `clk_n` | input | 7 GHz CML clock. Flops trigger on its rising zero crossing |
| `d0_p/n` .. `d3_p/n` | input | Four differential data lanes in |
| `q0_p/n` .. `q3_p/n` | output | Four differential data lanes out. Lane 0 also goes to the phase aligner |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vcm` | 0.6 V | Output common mode. Marked illustrative; the parent sets 0.55 V |
| `vdiff` | 0.2 V | Output differential amplitude. Marked illustrative; the parent sets 0.3 V |
| `vclk_diff_th`, `vdata_diff_th` | 0 V, 0 V | Differential thresholds of clock and data |
| `t_propogation` | 0 | Clock-to-output delay (spelled this way in the file) |
| `t_rise`, `t_fall` | 0, 0 | Output edge times. The parent sets 5 ps |

**Not modelled:** setup and hold checks (whatever the input is at the clock edge is taken), clock-to-output delay (it is 0), jitter, supply pins, reset and enable. The header says reset and enable are not specified in the project notes it was written from, and calls the interface provisional.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Four lanes at 7 Gb/s, retimed on the rising edge of the 7 GHz CML clock (`tx_ser_ffe_path.va`, header)
- CML levels as set by the parent: common mode 0.55 V, 0.6 V peak-to-peak differential, output edges 5 ps (`tx_ser_ffe_path.va`, instance `u_rcml`)
- The cell's own level defaults are marked illustrative, to be replaced by the real CML interface levels (`cml_dff_x4.va`, comment on `vcm`, `vdiff`)
- Reset and enable: not specified, so the model has neither (`cml_dff_x4.va`, header)
- The interface (differential clock, data and outputs) is marked provisional (`cml_dff_x4.va`, header)
- The model gives no setup, hold or clock-to-output numbers: these are for the owner to set

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/cml_dff_x4_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
