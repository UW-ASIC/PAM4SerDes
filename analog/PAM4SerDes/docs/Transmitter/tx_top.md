# tx_top

| Field | Value |
|---|---|
| Owner (from git history) | Omar ElSawy (integration) |
| Kind | structural (wiring only) |
| Model | [`va/Transmitter/tx_top.va`](../../va/Transmitter/tx_top.va) |
| Used in | `pam4_serdes` (top level), once (`u_tx`) |
| Section | [Transmitter](README.md) |

## Architecture

The complete transmitter: 14 GHz clock in, 28 GBd PAM4 out on the pads `txp` / `txn`. Two identical binary paths, MSB and LSB, each serialize a 32-bit word to 28 Gb/s and make the three FFE taps; the driver adds the paths with weights 2 : 1. There is no data input: the PRBS generator inside is the only source.

In `pam4_serdes`: `ckin` comes from [tx_pll](../Clocking/tx_pll.md), `en` is the top-level pin `tx_en`, `vref` comes from `bias_ref` (see [Biasing](../Biasing/README.md)) and `pgood` goes out as `tx_pgood`. The channel behind the pads is not part of the design; a testbench supplies it.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_cg` | [tx_clkgen](../Clocking/tx_clkgen.md) | Makes the clock tree from `ckin` |
| `u_pa` | `diff2se` (see [glue](../Clocking/glue.md)) | Ideal glue: converts the MSB path's retimed 7 Gb/s lane 0 to single-ended for the phase aligner inside `tx_clkgen` |
| `u_prbs` | [prbs_gray_src](prbs_gray_src.md) | Makes a 64-bit word (32 Gray-coded symbols) per `clk0p875` cycle |
| `u_path_m`, `u_path_l` | [tx_ser_ffe_path](tx_ser_ffe_path.md) | MSB path and LSB path: 32:1 serializer and FFE taps |
| `u_pd_m_pre` .. `u_pd_l_post` | [predriver_cml](predriver_cml.md), six | One per path and tap, between the path and the driver |
| `u_pdb` | `tx_predrv_bias` (see [Biasing](../Biasing/README.md)) | Turns `tx_bias.i_pdrv` into six reference currents, one wire per pre-driver |
| `u_drv` | [pam4_driver](pam4_driver.md) | Sums the six taps into the PAM4 output |
| `u_bias` | [tx_bias](../Biasing/tx_bias.md) | Sinks the six driver tail currents and `i_pdrv` |

- Word split: `prbs_gray_src` puts symbol s (s = 0 is sent first) on `gray_out[63 - 2s]` (MSB) and `gray_out[62 - 2s]` (LSB). The serializer wants time slot j on `d[j]`, so the MSB path gets the odd wires of the word and the LSB path the even wires, with the highest index on `d[0]`.
- The phase aligner locks to the MSB path only. The LSB path's copy of that lane is left unconnected.

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
| `vddo` | inout | 1.25 V output-stage supply (used by `tx_bias` and `tx_predrv_bias`) |
| `vss` | inout | Ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `w_pre` | 0.05 | FFE pre-cursor weight, magnitude (applied negative). Passed to `tx_bias` |
| `w_main` | 0.80 | FFE main-cursor weight. Passed to `tx_bias` |
| `w_post` | 0.15 | FFE post-cursor weight, magnitude (applied negative). Passed to `tx_bias` |
| `rj_scale` | 1 | Scale of the added jitter of the clocking cells. Passed to `tx_clkgen` and to both `tx_ser_ffe_path` |

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

Wiring only. See the cells: [tx_clkgen](../Clocking/tx_clkgen.md#topology-research), [glue](../Clocking/glue.md#topology-research), [prbs_gray_src](prbs_gray_src.md#topology-research), [tx_ser_ffe_path](tx_ser_ffe_path.md#topology-research), [predriver_cml](predriver_cml.md#topology-research), [pam4_driver](pam4_driver.md#topology-research), [tx_bias](../Biasing/tx_bias.md#topology-research).

## Sizing research

Wiring only. See the cells: [tx_clkgen](../Clocking/tx_clkgen.md#sizing-research), [glue](../Clocking/glue.md#sizing-research), [prbs_gray_src](prbs_gray_src.md#sizing-research), [tx_ser_ffe_path](tx_ser_ffe_path.md#sizing-research), [predriver_cml](predriver_cml.md#sizing-research), [pam4_driver](pam4_driver.md#sizing-research), [tx_bias](../Biasing/tx_bias.md#sizing-research).
