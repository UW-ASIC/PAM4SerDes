# tx_ser_ffe_path

| Field | Value |
|---|---|
| Owner (from git history) | Omar ElSawy (integration) |
| Kind | structural (wiring only) |
| Model | [`va/Transmitter/tx_ser_ffe_path.va`](../../va/Transmitter/tx_ser_ffe_path.va) |
| Used in | [tx_top](tx_top.md), twice (`u_path_m` for the MSB path, `u_path_l` for the LSB path) |
| Section | [Transmitter](README.md) |

## Architecture

One binary path of the transmitter: a 32-bit word at 0.875 GHz in, the same bits at 28 Gb/s out, three times over as the pre-cursor, main and post-cursor taps of the FFE. It is a tree of 2:1 multiplexers with retiming flops between the families of logic.

| Level | Cell | In to out | Clock |
|---|---|---|---|
| L0 | [dff_cmos_x32](../Clocking/dff_cmos_x32.md) | 32 x 0.875 Gb/s, retimed | `clk0p875` rising |
| L1 | 16 x [mux2_cmos](mux2_cmos.md) | 32 to 16 lanes at 1.75 Gb/s | select `clk0p875` |
| L2 | 8 x [mux2_cmos](mux2_cmos.md) | 16 to 8 lanes at 3.5 Gb/s | select `clk1p75` |
| R | [dff_tspc_x8](../Clocking/dff_tspc_x8.md) | 8 lanes retimed | `clk3p5` rising |
| L3 | 4 x [mux2_cs](mux2_cs.md) | 8 to 4 lanes at 7 Gb/s, CMOS in, CML out | `clk3p5` |
| R | [cml_dff_x4](../Clocking/cml_dff_x4.md) | 4 lanes retimed | `clk7` rising |
| L4 | 2 x [mux2_cml_hr](mux2_cml_hr.md) | 4 to 2: the even and the odd stream at 14 Gb/s | select `clk7` |
| TG | [ffe_tapgen_hr](ffe_tapgen_hr.md) | pre / main / post taps, even and odd, at 14 Gb/s | `clk14` |
| FIN | 3 x [mux2_cml_hr](mux2_cml_hr.md) | one 2:1 per tap: pre, main, post at 28 Gb/s | `clk14` |

- Rate check: 32 x 0.875 = 16 x 1.75 = 8 x 3.5 = 4 x 7 = 2 x 14 = 1 x 28 Gb/s.
- Half-rate FFE: the taps are made from the two 14 Gb/s streams, and only the three final multiplexers run at 28 Gb/s. At the output, pre = x[n], main = x[n-1] and post = x[n-2].
- Lane order: `d[j]` carries time slot j of the 32-symbol word, and `d[0]` is sent first. Output k of a level multiplexes input k (first) with input k + N/2 (second), where N is the number of inputs of that level.
- Input sent first: at L1 `in1` (the word changes on `clk0p875` rising; slot k goes to `in1` and slot k + 16 to `in0`); at L2 `in0` (L1's outputs change just after `clk1p75` falls); L3 (`mux2_cs`) and L4 / FIN (`mux2_cml_hr`) send `in0` / `de` first.
- `mux2_cs` is an ideal placeholder: nobody owns it yet.

In [tx_top](tx_top.md): the word comes from [prbs_gray_src](prbs_gray_src.md), the clocks from [tx_clkgen](../Clocking/tx_clkgen.md), and the three taps go to three [predriver_cml](predriver_cml.md) and from there to [pam4_driver](pam4_driver.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d[31:0]` | input | The word: 32 bits, CMOS, new every `clk0p875` cycle |
| `clk0p875`, `clk1p75`, `clk3p5`, `clk3p5b` | input | CMOS clocks |
| `clk7_p/n`, `clk14_p/n` | input | CML clocks |
| `rst` | input | Reset, active high (used by `ffe_tapgen_hr`) |
| `pre_p/n`, `main_p/n`, `post_p/n` | output | The three FFE taps at 28 Gb/s, CML |
| `pa_p`, `pa_n` | output | Retimed 7 Gb/s lane 0 (output 0 of `cml_dff_x4`), for the phase aligner in `tx_clkgen` |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd_cmos` | 0.7 V | CMOS logic high level, the core supply. Sets the levels of `dff_cmos_x32` |
| `vcm_cml` | 0.55 V | CML common mode: `vdd` - 0.15 V, like `clkbuf_cml`. Sets the levels of `cml_dff_x4` |
| `vsw_cml` | 0.3 V | CML differential amplitude (half of the 0.6 V peak-to-peak value) |
| `rj_scale` | 1 | Scale of the added jitter of `dff_tspc_x8` (200 fs): 1 = default, 0 = none |

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

Wiring only. See the cells: [dff_cmos_x32](../Clocking/dff_cmos_x32.md#topology-research), [mux2_cmos](mux2_cmos.md#topology-research), [dff_tspc_x8](../Clocking/dff_tspc_x8.md#topology-research), [mux2_cs](mux2_cs.md#topology-research), [cml_dff_x4](../Clocking/cml_dff_x4.md#topology-research), [mux2_cml_hr](mux2_cml_hr.md#topology-research), [ffe_tapgen_hr](ffe_tapgen_hr.md#topology-research).

## Sizing research

Wiring only. See the cells: [dff_cmos_x32](../Clocking/dff_cmos_x32.md#sizing-research), [mux2_cmos](mux2_cmos.md#sizing-research), [dff_tspc_x8](../Clocking/dff_tspc_x8.md#sizing-research), [mux2_cs](mux2_cs.md#sizing-research), [cml_dff_x4](../Clocking/cml_dff_x4.md#sizing-research), [mux2_cml_hr](mux2_cml_hr.md#sizing-research), [ffe_tapgen_hr](ffe_tapgen_hr.md#sizing-research).
