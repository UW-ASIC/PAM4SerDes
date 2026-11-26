# rx_decision

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | structural (wiring only) |
| Model | [`va/Receiver/rx_decision.va`](../../va/Receiver/rx_decision.va) |
| Used in | [rx_top](rx_top.md), once (`u_dec`) |
| Section | [Receiver](README.md) |

## Architecture

`rx_decision` turns the equalized analog signal into bits. It holds 24 slicers, the decision feedback equalizer (DFE) and two PAM4 decoders. It is wiring only.

The system needs 24 slicers, and not just 3, because of how the DFE is built. Three thresholds separate the four PAM4 levels. The DFE removes the echo of the previous symbol, and it does so by "unrolling": for every one of the four values the previous symbol could have had, there is a set of three slicers with thresholds already shifted for that case. That is 3 x 4 = 12 slicers. The receiver is half-rate, with one set per sampling phase, which makes 24.

### Where it sits

In [rx_top](rx_top.md): its input is the output of [rx_afe](rx_afe.md), its clock is `clk14` from [rx_clkgen](../Clocking/rx_clkgen.md), and its four outputs (two bits per phase) go to the two [rx_dec_retime](rx_dec_retime.md).

### Instances

| Instance | Cell | Role |
|---|---|---|
| `s0` .. `s11` | [slicer](slicer.md) | Phase 0: sample on the rising edge of the clock |
| `s12` .. `s23` | [slicer](slicer.md) | Phase 1: sample on the falling edge (their clock is connected swapped) |
| `dfe` | [dfe1_unrolled_hr](dfe1_unrolled_hr.md) | Drives all 24 slicer references; per phase, picks the 3 slicer outputs that belong to the previous symbol |
| `dec0`, `dec1` | [pam4_dec](pam4_dec.md) | One per phase: 3-bit thermometer code to 2 bits |

Slicer numbering, the same as in the DFE: slicer g = 12 x phase + 3 x hypothesis + threshold.

Two details of the wiring, from the header:

- The DFE's thermometer outputs are differential, but the decoders read single-ended logic. Each decoder takes the positive leg and compares it with the DFE's output common mode, `vdd` - 0.15 V. The negative legs are left unconnected.
- The slicers are used with their default parameters.

The threshold DAC, [threshold_dac](threshold_dac.md), is **not** instantiated: the DFE model drives the slicer references itself.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vinp`, `vinn` | input | Equalized PAM4 signal from the front end |
| `clk_p`, `clk_n` | input | 14 GHz CML clock |
| `msb0`, `lsb0` | output | Phase 0's decoded bits, CMOS levels |
| `msb1`, `lsb1` | output | Phase 1's decoded bits, CMOS levels |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 0.7 V | Supply the CML and logic levels follow |
| `alpha` | 0.08548 | DFE tap: first post-cursor / main cursor |
| `v_level` | 50 mV | The PAM4 levels at the slicers are -3, -1, +1, +3 times this |
| `v_thr` | 100 mV | The slicer thresholds are -1, 0, +1 times this |

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [slicer](slicer.md#topology-research), [dfe1_unrolled_hr](dfe1_unrolled_hr.md#topology-research), [pam4_dec](pam4_dec.md#topology-research).

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [slicer](slicer.md#sizing-research), [dfe1_unrolled_hr](dfe1_unrolled_hr.md#sizing-research), [pam4_dec](pam4_dec.md#sizing-research).
