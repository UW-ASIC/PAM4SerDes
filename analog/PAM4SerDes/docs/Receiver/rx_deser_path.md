# rx_deser_path

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | structural with some inline behaviour |
| Model | [`va/Receiver/rx_deser_path.va`](../../va/Receiver/rx_deser_path.va) |
| Used in | [rx_top](rx_top.md), twice (`u_des_m` for the MSBs, `u_des_l` for the LSBs) |
| Section | [Receiver](README.md) |

## Architecture

`rx_deser_path` is the deserializer of one binary path. It takes that path's two 14 Gb/s bit streams, one from each sampling phase, and spreads them over 32 wires that change once per word-clock cycle.

It is the mirror image of the transmitter's serializer: the received data is handed on as 32-bit words at 0.875 GHz. There are two instances, one for the MSBs and one for the LSBs.

It is mostly wiring. Two small pieces of behaviour are written inline in the file and are not cells of their own.

### How the data moves through it

It is a tree of 1:2 demultiplexers. Each stage doubles the number of lanes and halves their rate.

| Stage | Cell | In to out | Clock |
|---|---|---|---|
| 1 | 2 x [demux2_cml](demux2_cml.md) | 2 x 14 Gb/s to 4 x 7 Gb/s | `clk7` |
| 2 | 4 x [demux2_cml](demux2_cml.md) | 4 x 7 Gb/s to 8 x 3.5 Gb/s | `clk3p5` |
| inline | CML-to-CMOS conversion | 8 lanes: `vdd_cmos` if the difference is positive, 0 V otherwise | none |
| 3 | 8 x [demux2_cmos](demux2_cmos.md) | 8 x 3.5 Gb/s to 16 x 1.75 Gb/s | `clk1p75` |
| 4 | 16 x [demux2_cmos](demux2_cmos.md) | 16 x 1.75 Gb/s to 32 x 0.875 Gb/s | `clk875` |
| inline | output register | 32 bits, copied to `data_out` | `word_clk` rising |

Lane order: a demultiplexer puts the earlier bit of each pair on its `q0` and the later one on `q1`. At every stage, lane k is split into lane k (earlier) and lane k + N (later), where N is the number of lanes going in. For stage 1 the two inputs are lanes 0 and 1: `d0` goes to lanes 0 and 2, `d1` to lanes 1 and 3. The result is that `data_out[j]` holds time slot j, provided `d0` carries the earlier bit of each pair.

### Where it sits

In [rx_top](rx_top.md):

- `d0` is connected to the **phase 1** retimer and `d1` to the **phase 0** retimer (both [rx_dec_retime](rx_dec_retime.md)). The header of `rx_top.va` explains why phase 1 is the earlier of each pair.
- The clocks come from [rx_clkgen](../Clocking/rx_clkgen.md). `clk875` and `word_clk` are both connected to `clk0p875`.
- `data_out` is the top-level output `rxd_m` or `rxd_l`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d0_p/n`, `d1_p/n` | input | The two 14 Gb/s streams of this path, CML. `d0` is the earlier bit of each pair |
| `clk7_p/n`, `clk3p5_p/n` | input | CML clocks of stages 1 and 2 |
| `clk1p75`, `clk875` | input | CMOS clocks of stages 3 and 4 |
| `word_clk` | input | Clock of the output register |
| `data_out[0:31]` | output | The word, CMOS levels. Index j is time slot j |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd_cmos` | 0.7 V | CMOS high level of the inline conversion and of the output register |

### What the model leaves out

- The inline conversion and the output register are ideal: they switch instantly, with no delay and no edge time.
- The `demux2_cml` instances use their default parameters. Their default `vdd` is 1.0 V, so inside this block the CML lanes sit around 0.85 V and not around 0.55 V like the other CML in the design. Every reader of those lanes looks only at the difference, so the data is not affected.
- The `demux2_cmos` instances also use their defaults, which are for 0.7 V.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

Most of this block is wiring. The topology research lives in the pages of its cells: [demux2_cml](demux2_cml.md#topology-research), [demux2_cmos](demux2_cmos.md#topology-research). Two pieces are written inline in this file and have no cell of their own yet: the CML-to-CMOS conversion and the 32-bit output register. Use the template below for those two.

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- CML-to-CMOS conversion: 8 lanes at 3.5 Gb/s, between the second and the third demultiplexer stage (`rx_deser_path.va`, code)
- Output register: 32 bits, clocked on the rising edge of the 0.875 GHz word clock, CMOS levels 0 to 0.7 V (`rx_deser_path.va`, code and parameter `vdd_cmos`)
- The words are meant to be read on the falling edge of the word clock (`rx_top.va`, header)

To be added by the owner:

- (add requirements here)

### Candidate topologies

One row per circuit you seriously considered. Two or three good candidates are enough.

| Candidate | Source / reference | Pros | Cons |
|---|---|---|---|
| | | | |

### Chosen topology

Which candidate you chose and the reasons, measured against the requirements above. Say what you gave up by not choosing the others.

### Schematic

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `rx_deser_path_<what>.svg` (or `.png`), and reference it from this page as `![rx_deser_path schematic](../img/rx_deser_path_<what>.svg)`.

### Open questions

- (questions for the section lead or for neighbouring blocks' owners)

### References

- (papers, textbook sections, earlier designs; give enough detail that someone else can find them)

## Sizing research

Most of this block is wiring. The sizing research lives in the pages of its cells: [demux2_cml](demux2_cml.md#sizing-research), [demux2_cmos](demux2_cmos.md#sizing-research). Two pieces are written inline in this file and have no cell of their own yet: the CML-to-CMOS conversion and the 32-bit output register. Use the template below for those two.

*To be filled in by the owner during the sizing-research stage, once the topology is chosen.*

The goal of this section is to record the device sizes that meet the block's specs, how they were found, and the simulations that show it.

### Target specs

Copy the requirements from the Topology research section and turn each one into a number you can simulate.

| Spec | Target | Source |
|---|---|---|
| | | |

### Sizing method

How the sizes were found (hand calculation, gm/Id, sweep), with enough detail that someone else can repeat it.

### Devices

| Device | W/L or fingers | Bias point |
|---|---|---|
| | | |

### Simulation results

One row per spec. Name the testbench file so the result can be reproduced.

| Spec | Target | Result | Testbench | Conditions |
|---|---|---|---|---|
| | | | | |

### Corners checked

List the process, voltage and temperature corners you simulated, and say which one was worst.

### Open issues

- (specs not met yet, things left to check)
