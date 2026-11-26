# rx_dec_retime

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/rx_dec_retime.va`](../../va/Receiver/rx_dec_retime.va) |
| Used in | [rx_top](rx_top.md), twice (`u_rt0`, `u_rt1`: one per sampling phase) |
| Section | [Receiver](README.md) |

## Architecture

`rx_dec_retime` is a pair of flip-flops. On each rising clock edge it samples the two decoded bits of one sampling phase, MSB and LSB, and holds them until the next edge. It reads CMOS logic levels and drives CML.

The system needs it between the decision stage and the deserializer. The decoder is combinational, so its outputs change whenever the DFE's selection changes. This block puts the bits back on a clock edge, so the deserializer gets data that is stable for a full clock period.

There is one per phase. The header of `rx_top.va` gives the timing: phase 0 is sampled on `clk14` rising and decided on `clk14` falling, so it is retimed on the next rising edge. Phase 1 is half a period later, so its instance has the clock connected swapped and retimes on the falling edge.

### Where it sits

In [rx_top](rx_top.md): the inputs come from one [pam4_dec](pam4_dec.md) inside [rx_decision](rx_decision.md), the clock is `clk14` from [rx_clkgen](../Clocking/rx_clkgen.md). The MSB output goes to the MSB deserializer path and the LSB output to the LSB path (both [rx_deser_path](rx_deser_path.md)).

`rx_top` sets the input threshold to 0.35 V and `vdd` to 0.7 V.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `msb_in`, `lsb_in` | input | Decoded bits of one phase, CMOS levels |
| `clk_p`, `clk_n` | input | 14 GHz CML clock; sampling at its rising zero crossing |
| `msb_out_p/n` | output | Retimed MSB, CML |
| `lsb_out_p/n` | output | Retimed LSB, CML |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_data` | 0.9 V | Input threshold. `rx_top` sets 0.35 V |
| `vdd` | 1.0 V | Supply the output levels follow. `rx_top` sets 0.7 V |
| `v_swing` | 0.3 V | Swing of each output leg |
| `v_cm` | `vdd` - `v_swing`/2 | Output common mode |

### What the model leaves out

- The outputs change at the instant of the clock edge: no clock-to-output delay and no edge time.
- Setup and hold times are not checked.
- The file has no comments; the description above is read from the code and from `rx_top.va`.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Two bits (MSB and LSB) per phase at 14 Gb/s, clock 14 GHz (`rx_top.va`, header)
- Phase 0 is retimed on the rising edge of the clock, phase 1 on the falling edge (`rx_top.va`, header)
- Input: CMOS logic from the decoder, threshold 0.35 V (`rx_top.va`, instance lines)
- Output: CML, each leg swings 0.3 V around `vdd` - 0.15 V (`rx_dec_retime.va`, parameters `v_swing`, `v_cm`)
- Its load is the first deserializer stage, which samples just after the rising edge of the 14 GHz clock (`rx_top.va`, header)
- The model gives no setup, hold or clock-to-output numbers: these are for the owner to set

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `rx_dec_retime_<what>.svg` (or `.png`), and reference it from this page as `![rx_dec_retime schematic](../img/rx_dec_retime_<what>.svg)`.

### Open questions

- (questions for the section lead or for neighbouring blocks' owners)

### References

- (papers, textbook sections, earlier designs; give enough detail that someone else can find them)

## Sizing research

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
