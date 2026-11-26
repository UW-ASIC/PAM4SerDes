# rx_clkgen

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | structural (wiring only) |
| Model | [`va/Clocking/rx_clkgen.va`](../../va/Clocking/rx_clkgen.va) |
| Used in | [rx_top](../Receiver/rx_top.md), once (`u_cg`) |
| Section | [Clocking](README.md) |

## Architecture

`rx_clkgen` is the receiver's clock tree. It takes the 14 GHz clock recovered by the CDR and makes every clock the receiver needs: 14, 7 and 3.5 GHz as CML, and 1.75 and 0.875 GHz as CMOS.

The system needs it because the receiver samples at 14 GHz (two phases) and then spreads the data over more and slower wires, one 1:2 demultiplexer level at a time. Each level needs a clock at half the rate of the one before.

### Where it sits

In [rx_top](../Receiver/rx_top.md). Its input `ckin` is the single-ended CMOS output of the VCO in [rx_cdr](rx_cdr.md). Its outputs go to these cells:

| Clock | Type | Used by |
|---|---|---|
| `clk14_p/n` (14 GHz) | CML | The 24 slicers and the DFE in [rx_decision](../Receiver/rx_decision.md), the two [rx_dec_retime](../Receiver/rx_dec_retime.md), and back out to the phase detector in [rx_cdr](rx_cdr.md) |
| `clk7_p/n` (7 GHz) | CML | First [demux2_cml](../Receiver/demux2_cml.md) stage of [rx_deser_path](../Receiver/rx_deser_path.md) |
| `clk3p5_p/n` (3.5 GHz) | CML | Second [demux2_cml](../Receiver/demux2_cml.md) stage |
| `clk1p75` (1.75 GHz) | CMOS | First [demux2_cmos](../Receiver/demux2_cmos.md) stage |
| `clk0p875` (0.875 GHz) | CMOS | Second [demux2_cmos](../Receiver/demux2_cmos.md) stage and the output register. It is also the top-level pin `rx_wclk` |

### Instances

The cells form one chain:

| Instance | Cell | Role |
|---|---|---|
| `u_dcc` | [dcc_cml](dcc_cml.md) | Corrects the duty cycle of `ckin` and makes it differential. Threshold set to 0.35 V |
| `u_buf14` | [clkbuf_cml](clkbuf_cml.md) | Drives `clk14` |
| `u_div7` | [div2_cml](div2_cml.md) | `clk14` to `clk7`, on the rising edge of `clk14`. **Ideal placeholder** |
| `u_div3p5` | [div2_cml](div2_cml.md) | `clk7` to `clk3p5`, on the falling edge of `clk7` (its input is connected swapped). **Ideal placeholder** |
| `u_c2c` | [cml2cmos](cml2cmos.md) | `clk3p5` to a single-ended CMOS clock |
| `u_d1p75` | [div2_tspc](div2_tspc.md) | 3.5 GHz to `clk1p75` |
| `u_d0p875` | [div2_tspc](div2_tspc.md) | `clk1p75` to `clk0p875` |

Each `div2_tspc` toggles on the falling edge of its input.

Compared with [tx_clkgen](tx_clkgen.md), the CML part reaches one level lower (3.5 GHz is CML here) and there is no phase aligner: the CDR already locks the clock to the data.

The parent passes `rj_scale`; this block uses it to scale the jitter of `clkbuf_cml` (40 fs) and of the two `div2_tspc` (300 fs each), and gives each instance its own seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin` | input | 14 GHz from `rx_cdr`'s VCO, single-ended CMOS |
| `rst` | input | Reset, active high: resets the `div2_tspc` dividers (`q` low) |
| `clk14_p/n`, `clk7_p/n`, `clk3p5_p/n` | output | CML clocks |
| `clk1p75`, `clk0p875` | output | CMOS clocks |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_dcc` | 0.35 V | `dcc_cml` input threshold: mid-swing of the CMOS VCO output |
| `rj_scale` | 1 | Scale of the added jitter of the clocking cells: 1 = defaults, 0 = none |

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [dcc_cml](dcc_cml.md#topology-research), [clkbuf_cml](clkbuf_cml.md#topology-research), [div2_cml](div2_cml.md#topology-research), [cml2cmos](cml2cmos.md#topology-research), [div2_tspc](div2_tspc.md#topology-research).

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [dcc_cml](dcc_cml.md#sizing-research), [clkbuf_cml](clkbuf_cml.md#sizing-research), [div2_cml](div2_cml.md#sizing-research), [cml2cmos](cml2cmos.md#sizing-research), [div2_tspc](div2_tspc.md#sizing-research).
