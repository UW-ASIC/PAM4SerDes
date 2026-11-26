# rx_top

| Field | Value |
|---|---|
| Owner (from git history) | Omar El-Sawy (integration) |
| Kind | structural (wiring only) |
| Model | [`va/Receiver/rx_top.va`](../../va/Receiver/rx_top.va) |
| Used in | `pam4_serdes` (top level), once (`u_rx`) |
| Section | [Receiver](README.md) |

## Architecture

`rx_top` is the complete receiver datapath. It takes the PAM4 signal from the pads `rx_p` / `rx_n` and puts out the received bits as two 32-bit words per word-clock cycle. It is wiring only: it connects the cells and adds no behaviour of its own.

The data goes through four steps:

1. **Front end** ([rx_afe](rx_afe.md)): terminate the line, equalize, set the amplitude.
2. **Decision** ([rx_decision](rx_decision.md)): 24 slicers, a one-tap decision feedback equalizer and two decoders turn the analog signal into two bits per symbol. This runs as two phases, one on each edge of the 14 GHz clock.
3. **Retiming** (two [rx_dec_retime](rx_dec_retime.md), one per phase): bring both phases' bits onto clean clock edges.
4. **Deserializing** (two [rx_deser_path](rx_deser_path.md), one for the MSBs and one for the LSBs): spread the two 14 Gb/s streams of each path over 32 wires at 0.875 Gb/s.

### Where it sits

In the top level `pam4_serdes`:

- `rx_p` / `rx_n` are the input pads. The channel in front of them is not part of the design; a testbench supplies it.
- `vtt` and `vctrl` are top-level pins: the termination reference and the gain control voltage of the VGA.
- `ckin` is the 14 GHz VCO clock from [rx_cdr](../Clocking/rx_cdr.md). [rx_clkgen](../Clocking/rx_clkgen.md) builds the clock tree from it.
- `afe_p/n` (the front end's output) and `clk14_p/n` go back out to the phase detector in `rx_cdr`. This is how the clock recovery loop closes.
- `rxd_m[0:31]`, `rxd_l[0:31]` and `clk0p875` (as `rx_wclk`) are top-level outputs.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_afe` | [rx_afe](rx_afe.md) | Termination, CTLE and VGA |
| `u_cg` | [rx_clkgen](../Clocking/rx_clkgen.md) | Makes the clock tree from `ckin` |
| `u_dec` | [rx_decision](rx_decision.md) | 24 slicers, DFE and one PAM4 decoder per phase |
| `u_rt0` | [rx_dec_retime](rx_dec_retime.md) | Retimes phase 0's two bits on `clk14` rising |
| `u_rt1` | [rx_dec_retime](rx_dec_retime.md) | Retimes phase 1's two bits on `clk14` falling (its clock is connected swapped) |
| `u_des_m` | [rx_deser_path](rx_deser_path.md) | Deserializes the MSBs to `rxd_m` |
| `u_des_l` | [rx_deser_path](rx_deser_path.md) | Deserializes the LSBs to `rxd_l` |

### Phases and word order

These rules are in the header of `rx_top.va`. They matter to anyone who touches the timing.

- Phase 0 is sampled on `clk14` rising and decided on `clk14` falling, so it is retimed on the next rising edge. Phase 1 is half a period later, so its retimer uses the falling edge.
- The deserializer's first stage samples just after `clk14` rising. At that moment the phase-1 retimer still holds the symbol **before** the one the phase-0 retimer has just taken. So phase 1 is the earlier of each pair: it goes to the deserializer's `d0` (first in time) and phase 0 to `d1`.
- `rxd_m[j]` and `rxd_l[j]` hold the MSB and the LSB of time slot j; slot 0 was received first.
- Both words change on `clk0p875` rising. Read them on its falling edge.
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

`rx_dec_retime` and `rx_deser_path` take their levels as parameters; this block sets them for the 0.7 V supply.

| Parameter | Default | Meaning |
|---|---|---|
| `vdd_nom` | 0.7 V | Supply the CML and logic levels follow |
| `main_boost_db` | 0 dB | CTLE main peaking boost. Passed to `rx_afe` |
| `alpha` | 0.08548 | DFE tap: first post-cursor / main cursor. Passed to `rx_decision` |
| `rj_scale` | 1 | Scale of the added jitter of the clocking cells. Passed to `rx_clkgen` |

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [rx_afe](rx_afe.md#topology-research), [rx_clkgen](../Clocking/rx_clkgen.md#topology-research), [rx_decision](rx_decision.md#topology-research), [rx_dec_retime](rx_dec_retime.md#topology-research), [rx_deser_path](rx_deser_path.md#topology-research).

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [rx_afe](rx_afe.md#sizing-research), [rx_clkgen](../Clocking/rx_clkgen.md#sizing-research), [rx_decision](rx_decision.md#sizing-research), [rx_dec_retime](rx_dec_retime.md#sizing-research), [rx_deser_path](rx_deser_path.md#sizing-research).
