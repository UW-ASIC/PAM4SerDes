# rx_deser_path

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | structural with some inline behaviour |
| Model | [`va/Receiver/rx_deser_path.va`](../../va/Receiver/rx_deser_path.va) |
| Used in | [rx_top](rx_top.md), twice (`u_des_m` for the MSBs, `u_des_l` for the LSBs) |
| Section | [Receiver](README.md) |

## Architecture

The 1:32 deserializer of one binary path: two 14 Gb/s bit streams in, one from each sampling phase, and a 32-bit word per word-clock cycle out. It is a tree of 1:2 demultiplexers plus two pieces written inline in the file, which are not cells of their own.

| Stage | Cell | In to out | Clock |
|---|---|---|---|
| 1 | 2 x [demux2_cml](demux2_cml.md) | 2 x 14 Gb/s to 4 x 7 Gb/s | `clk7` |
| 2 | 4 x [demux2_cml](demux2_cml.md) | 4 x 7 Gb/s to 8 x 3.5 Gb/s | `clk3p5` |
| inline | CML-to-CMOS conversion | 8 lanes: `vdd_cmos` if the difference is positive, 0 V otherwise | none |
| 3 | 8 x [demux2_cmos](demux2_cmos.md) | 8 x 3.5 Gb/s to 16 x 1.75 Gb/s | `clk1p75` |
| 4 | 16 x [demux2_cmos](demux2_cmos.md) | 16 x 1.75 Gb/s to 32 x 0.875 Gb/s | `clk875` |
| inline | output register | 32 bits, copied to `data_out` | `word_clk` rising |

- Lane order: at every stage lane k is split into lane k (the earlier bit, on `q0`) and lane k + N (the later bit, on `q1`), where N is the number of lanes going in. So `data_out[j]` holds time slot j, provided `d0` carries the earlier bit of each pair.
- In [rx_top](rx_top.md), `d0` comes from the phase 1 retimer and `d1` from the phase 0 retimer (both [rx_dec_retime](rx_dec_retime.md)): phase 1 is the earlier of each pair. The clocks come from [rx_clkgen](../Clocking/rx_clkgen.md); `clk875` and `word_clk` are both connected to `clk0p875`. `data_out` is the top-level output `rxd_m` or `rxd_l`.
- The `demux2_cml` instances keep their default `vdd` of 1.0 V, so the CML lanes inside this block sit around 0.85 V and not around 0.55 V like the other CML. Every reader of those lanes looks only at the difference. The `demux2_cmos` defaults are for 0.7 V.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d0_p/n`, `d1_p/n` | input | The two 14 Gb/s streams of this path, CML. `d0` is the earlier bit of each pair |
| `clk7_p/n`, `clk3p5_p/n` | input | CML clocks of stages 1 and 2 |
| `clk1p75`, `clk875` | input | CMOS clocks of stages 3 and 4 |
| `word_clk` | input | Clock of the output register |
| `data_out[0:31]` | output | The word, CMOS levels. Index j is time slot j |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd_cmos` | 0.7 V | CMOS high level of the inline conversion and of the output register |

**Not modelled:** delay and edge time of the inline conversion and of the output register (they switch instantly), supply pins.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

Mostly wiring: see [demux2_cml](demux2_cml.md#topology-research) and [demux2_cmos](demux2_cmos.md#topology-research). The rest of this section is for the two inline pieces, which have no cell of their own yet: the CML-to-CMOS conversion and the 32-bit output register.

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- CML-to-CMOS conversion: 8 lanes at 3.5 Gb/s, between the second and the third demultiplexer stage (`rx_deser_path.va`, code)
- Output register: 32 bits, clocked on the rising edge of the 0.875 GHz word clock, CMOS levels 0 to 0.7 V (`rx_deser_path.va`, code and parameter `vdd_cmos`)
- The words are meant to be read on the falling edge of the word clock (`rx_top.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/rx_deser_path_<what>.svg`); open questions; references.

## Sizing research

Mostly wiring: see [demux2_cml](demux2_cml.md#sizing-research) and [demux2_cmos](demux2_cmos.md#sizing-research). The rest of this section is for the two inline pieces.

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
