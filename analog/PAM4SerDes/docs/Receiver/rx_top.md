# rx_top

| Field | Value |
|---|---|
| Owner (from git history) | Omar ElSawy (integration) |
| Kind | structural (wiring only) |
| Model | [`va/Receiver/rx_top.va`](../../va/Receiver/rx_top.va) |
| Used in | `pam4_serdes` (top level), once (`u_rx`) |
| Section | [Receiver](README.md) |

## Architecture

The complete receiver datapath: the PAM4 signal on the pads `rx_p` / `rx_n` in, two 32-bit words per word-clock cycle out.

In `pam4_serdes`: `vtt` and `vctrl` come from `rx_bias` (see [Biasing](../Biasing/README.md)); `ckin` is the 14 GHz VCO clock from [rx_cdr](../Clocking/rx_cdr.md); `afe_p/n` and `clk14_p/n` go back out to the phase detector in `rx_cdr`, which closes the clock recovery loop; `rxd_m[0:31]`, `rxd_l[0:31]` and `clk0p875` (as `rx_wclk`) are top-level outputs. The channel in front of the pads is not part of the design; a testbench supplies it.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_afe` | [rx_afe](rx_afe.md) | Termination, CTLE and VGA |
| `u_cg` | [rx_clkgen](../Clocking/rx_clkgen.md) | Makes the clock tree from `ckin` |
| `u_dec` | [rx_decision](rx_decision.md) | 24 slicers, 24 threshold DACs, DFE and one PAM4 decoder per phase |
| `u_rt0` | [rx_dec_retime](rx_dec_retime.md) | Retimes phase 0's two bits on `clk14` rising |
| `u_rt1` | [rx_dec_retime](rx_dec_retime.md) | Retimes phase 1's two bits on `clk14` falling (its clock is connected swapped) |
| `u_des_m` | [rx_deser_path](rx_deser_path.md) | Deserializes the MSBs to `rxd_m` |
| `u_des_l` | [rx_deser_path](rx_deser_path.md) | Deserializes the LSBs to `rxd_l` |

Phases and word order, from the header of `rx_top.va`:

- Phase 0 is sampled on `clk14` rising and decided on `clk14` falling, so it is retimed on the next rising edge. Phase 1 is half a period later, so its retimer uses the falling edge.
- The deserializer's first stage samples just after `clk14` rising. At that moment the phase-1 retimer still holds the symbol before the one the phase-0 retimer has just taken. So phase 1 is the earlier of each pair: it goes to the deserializer's `d0` (first in time) and phase 0 to `d1`.
- `rxd_m[j]` and `rxd_l[j]` hold the MSB and the LSB of time slot j; slot 0 was received first. Both words change on `clk0p875` rising; read them on its falling edge.
- The bits are Gray decoded: `rxd_m` is the PRBS bit that was sent on the MSB wire, and `rxd_l` is the bit that [prbs_gray_src](../Transmitter/prbs_gray_src.md) XORed into the LSB wire.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `rx_p`, `rx_n` | inout | PAM4 input from the pads, 28 GBd |
| `vtt` | inout | Termination reference |
| `vctrl` | input | VGA gain control voltage, 0 to 0.7 V |
| `ckin` | input | 14 GHz from `rx_cdr`'s VCO, single-ended CMOS |
| `rst` | input | Reset, active high (goes to the clock tree) |
| `afe_p`, `afe_n` | output | Front end output, back to `rx_cdr` |
| `clk14_p`, `clk14_n` | output | 14 GHz CML clock, back to `rx_cdr` |
| `rxd_m[0:31]`, `rxd_l[0:31]` | output | Received MSB word and LSB word, CMOS |
| `clk0p875` | output | Word clock, 0.875 GHz, CMOS |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd_nom` | 0.7 V | Supply the CML and logic levels follow. Sets the levels of `rx_dec_retime` and `rx_deser_path` |
| `main_boost_db` | 0 dB | CTLE main peaking boost. Passed to `rx_afe` |
| `alpha` | 0.08548 | DFE tap: first post-cursor / main cursor. Passed to `rx_decision` |
| `rj_scale` | 1 | Scale of the added jitter of the clocking cells. Passed to `rx_clkgen` |

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

Wiring only. See the cells: [rx_afe](rx_afe.md#topology-research), [rx_clkgen](../Clocking/rx_clkgen.md#topology-research), [rx_decision](rx_decision.md#topology-research), [rx_dec_retime](rx_dec_retime.md#topology-research), [rx_deser_path](rx_deser_path.md#topology-research).

## Sizing research

Wiring only. See the cells: [rx_afe](rx_afe.md#sizing-research), [rx_clkgen](../Clocking/rx_clkgen.md#sizing-research), [rx_decision](rx_decision.md#sizing-research), [rx_dec_retime](rx_dec_retime.md#sizing-research), [rx_deser_path](rx_deser_path.md#sizing-research).
