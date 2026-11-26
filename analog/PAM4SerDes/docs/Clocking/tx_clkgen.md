# tx_clkgen

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | structural (wiring only) |
| Model | [`va/Clocking/tx_clkgen.va`](../../va/Clocking/tx_clkgen.va) |
| Used in | [tx_top](../Transmitter/tx_top.md), once (`u_cg`) |
| Section | [Clocking](README.md) |

## Architecture

`tx_clkgen` is the transmitter's clock tree. It takes the 14 GHz clock from the PLL and makes every clock the serializer needs: 14 GHz and 7 GHz as CML, and 3.5, 1.75 and 0.875 GHz as CMOS.

The system needs it because the serializer is a tree of 2:1 multiplexers. Each level runs at twice the rate of the one before, so each level needs its own clock, and all of them must come from the same source to stay aligned.

### Where it sits

In [tx_top](../Transmitter/tx_top.md). Its input `ckin` is the single-ended CMOS output of [tx_pll](tx_pll.md). Its outputs go to these cells:

| Clock | Type | Used by |
|---|---|---|
| `clk14_p/n` (14 GHz) | CML | [ffe_tapgen_hr](../Transmitter/ffe_tapgen_hr.md) and the three final [mux2_cml_hr](../Transmitter/mux2_cml_hr.md) (14 to 28 Gb/s) |
| `clk7_p/n` (7 GHz) | CML | [cml_dff_x4](cml_dff_x4.md) and the two [mux2_cml_hr](../Transmitter/mux2_cml_hr.md) of level L4 |
| `clk3p5`, `clk3p5b` (3.5 GHz) | CMOS | [dff_tspc_x8](dff_tspc_x8.md) and the four [mux2_cs](../Transmitter/mux2_cs.md) of level L3 (`clk3p5b` is the complement) |
| `clk1p75` (1.75 GHz) | CMOS | Select of the eight [mux2_cmos](../Transmitter/mux2_cmos.md) of level L2 |
| `clk0p875` (0.875 GHz) | CMOS | [prbs_gray_src](../Transmitter/prbs_gray_src.md), [dff_cmos_x32](dff_cmos_x32.md), select of the sixteen [mux2_cmos](../Transmitter/mux2_cmos.md) of level L1 |

### Instances

The cells form one chain:

| Instance | Cell | Role |
|---|---|---|
| `u_dcc` | [dcc_cml](dcc_cml.md) | Corrects the duty cycle of `ckin` and makes it differential. Threshold set to 0.35 V |
| `u_buf14` | [clkbuf_cml](clkbuf_cml.md) | Drives `clk14` |
| `u_div7` | [div2_cml](div2_cml.md) | `clk14` to `clk7`. **Ideal placeholder.** Toggles on the rising edge of `clk14` |
| `u_c2c` | [cml2cmos](cml2cmos.md) | `clk7` to a single-ended CMOS clock |
| `u_pa` | [phase_aligner](phase_aligner.md) | Shifts the 7 GHz CMOS clock so that it lines up with the data on `pa_data` |
| `u_d3p5` | [div2_tspc](div2_tspc.md) | Aligned 7 GHz to `clk3p5` and `clk3p5b` |
| `u_d1p75` | [div2_tspc](div2_tspc.md) | `clk3p5` to `clk1p75` |
| `u_d0p875` | [div2_tspc](div2_tspc.md) | `clk1p75` to `clk0p875` |

Each `div2_tspc` toggles on the falling edge of its input.

`pa_data` is the retimed 7 Gb/s lane 0 of the MSB path. It comes from [cml_dff_x4](cml_dff_x4.md) through an ideal `diff2se` cell (see [glue](glue.md)) in `tx_top`. The phase aligner sits between the CML part and the CMOS part of the tree, so the CMOS clocks follow the data that the CML part retimes.

The parent passes `rj_scale`; this block uses it to scale the jitter of `clkbuf_cml` (40 fs) and of the three `div2_tspc` (300 fs each), and gives each instance its own seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin` | input | 14 GHz from `tx_pll`, single-ended CMOS |
| `rst` | input | Reset, active high: resets the `div2_tspc` dividers (`q` low) |
| `pa_data` | input | Data the phase aligner locks to, single-ended around 0 V |
| `clk14_p/n`, `clk7_p/n` | output | CML clocks |
| `clk3p5`, `clk3p5b`, `clk1p75`, `clk0p875` | output | CMOS clocks |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_dcc` | 0.35 V | `dcc_cml` input threshold: mid-swing of the CMOS VCO output |
| `rj_scale` | 1 | Scale of the added jitter of the clocking cells: 1 = defaults, 0 = none |

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [dcc_cml](dcc_cml.md#topology-research), [clkbuf_cml](clkbuf_cml.md#topology-research), [div2_cml](div2_cml.md#topology-research), [cml2cmos](cml2cmos.md#topology-research), [phase_aligner](phase_aligner.md#topology-research), [div2_tspc](div2_tspc.md#topology-research).

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [dcc_cml](dcc_cml.md#sizing-research), [clkbuf_cml](clkbuf_cml.md#sizing-research), [div2_cml](div2_cml.md#sizing-research), [cml2cmos](cml2cmos.md#sizing-research), [phase_aligner](phase_aligner.md#sizing-research), [div2_tspc](div2_tspc.md#sizing-research).
