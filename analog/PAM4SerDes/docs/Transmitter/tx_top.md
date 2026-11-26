# tx_top

| Field | Value |
|---|---|
| Owner (from git history) | Omar El-Sawy (integration) |
| Kind | structural (wiring only) |
| Model | [`va/Transmitter/tx_top.va`](../../va/Transmitter/tx_top.va) |
| Used in | `pam4_serdes` (top level), once (`u_tx`) |
| Section | [Transmitter](README.md) |

## Architecture

`tx_top` is the complete transmitter. It takes the 14 GHz clock from the PLL and puts a 28 GBd PAM4 signal on the pads `txp` / `txn`. It is wiring only: it connects the cells and adds no behaviour of its own.

A PAM4 symbol carries two bits, so the transmitter is built as **two identical binary paths**, an MSB path and an LSB path. Each one serializes a 32-bit word to 28 Gb/s and makes the three FFE taps. The output driver adds the two paths with weights 2 : 1, which gives the four levels.

### Where it sits

In the top level `pam4_serdes`:

- `ckin` comes from [tx_pll](../Clocking/tx_pll.md) (single-ended CMOS, 14 GHz).
- `en` and `vref` are the top-level pins `tx_en` and `vref`; they go to [tx_bias](../Biasing/tx_bias.md).
- `txp` / `txn` are the output pads. The channel behind them is not part of the design; a testbench supplies it.
- `pgood` goes out as the top-level pin `tx_pgood`.

There is no data input. The only data source is the PRBS generator inside.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_cg` | [tx_clkgen](../Clocking/tx_clkgen.md) | Makes the clock tree from `ckin` |
| `u_pa` | `diff2se` (see [glue](../Clocking/glue.md)) | Converts the MSB path's retimed 7 Gb/s lane 0 to single-ended for the phase aligner inside `tx_clkgen` |
| `u_prbs` | [prbs_gray_src](prbs_gray_src.md) | Makes a 64-bit word (32 Gray-coded symbols) per `clk0p875` cycle |
| `u_path_m`, `u_path_l` | [tx_ser_ffe_path](tx_ser_ffe_path.md) | MSB path and LSB path: 32:1 serializer and FFE taps |
| `u_pd_m_pre` .. `u_pd_l_post` | [predriver_cml](predriver_cml.md), six | One per path and tap, between the path and the driver |
| `u_drv` | [pam4_driver](pam4_driver.md) | Sums the six taps into the PAM4 output |
| `u_bias` | [tx_bias](../Biasing/tx_bias.md) | Sinks the six driver tail currents |

How the word is split between the paths: `prbs_gray_src` puts symbol s (s = 0 is sent first) on `gray_out[63 - 2s]` (MSB) and `gray_out[62 - 2s]` (LSB). The serializer wants time slot j on `d[j]`. So the MSB path gets the odd wires of the word and the LSB path the even wires, with the highest index on `d[0]`.

Three things in the wiring are provisional, as the header says:

- The phase aligner locks to the MSB path only. The LSB path's copy of that lane is left unconnected.
- `tx_bias.i_pdrv`, the pre-driver tail current, is unconnected, because `predriver_cml` is ideal and has no bias pin yet.
- `u_pa` is an ideal glue cell.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin` | input | 14 GHz from `tx_pll`, single-ended CMOS |
| `rst` | input | Reset, active high |
| `en` | input | Enable of `tx_bias`, high = on, 1.25 V logic |
| `vref` | input | 0.6 V reference of `tx_bias` |
| `txp`, `txn` | output | PAM4 output, 28 GBd |
| `pgood` | output | Power-good flag from `tx_bias` |
| `vdd` | inout | 0.7 V core supply |
| `vddo` | inout | 1.25 V output-stage supply (used by `tx_bias`) |
| `vss` | inout | Ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `w_pre` | 0.05 | FFE pre-cursor weight, magnitude (applied negative). Passed to `tx_bias` |
| `w_main` | 0.80 | FFE main-cursor weight. Passed to `tx_bias` |
| `w_post` | 0.15 | FFE post-cursor weight, magnitude (applied negative). Passed to `tx_bias` |
| `rj_scale` | 1 | Scale of the added jitter of the clocking cells. Passed to `tx_clkgen` and to both `tx_ser_ffe_path` |

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [tx_clkgen](../Clocking/tx_clkgen.md#topology-research), [glue](../Clocking/glue.md#topology-research), [prbs_gray_src](prbs_gray_src.md#topology-research), [tx_ser_ffe_path](tx_ser_ffe_path.md#topology-research), [predriver_cml](predriver_cml.md#topology-research), [pam4_driver](pam4_driver.md#topology-research), [tx_bias](../Biasing/tx_bias.md#topology-research).

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [tx_clkgen](../Clocking/tx_clkgen.md#sizing-research), [glue](../Clocking/glue.md#sizing-research), [prbs_gray_src](prbs_gray_src.md#sizing-research), [tx_ser_ffe_path](tx_ser_ffe_path.md#sizing-research), [predriver_cml](predriver_cml.md#sizing-research), [pam4_driver](pam4_driver.md#sizing-research), [tx_bias](../Biasing/tx_bias.md#sizing-research).
