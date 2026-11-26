# mux2_cs

| Field | Value |
|---|---|
| Owner (from git history) | none yet |
| Kind | placeholder (ideal stand-in, no owner) |
| Model | [`va/Transmitter/placeholders/mux2_cs.va`](../../va/Transmitter/placeholders/mux2_cs.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), four per path (level L3) |
| Section | [Transmitter](README.md) |

## Architecture

`mux2_cs` is the 2:1 multiplexer of serializer level L3. It combines two 3.5 Gb/s lanes into one 7 Gb/s lane, and it is also where the data changes from CMOS levels to CML levels.

**This file is an ideal placeholder with no owner.** Its header says so: it is not a team block, and it exists so that `tx_ser_ffe_path` compiles and simulates until an owner commits the real one. **Someone needs to take this block.**

The name says what the real cell is meant to be: a charge-steering multiplexer.

### How the model works

A latch-multiplexer. Both inputs are captured on the rising clock edge. The output shows `in0` while the clock is high and `in1` while it is low, so `in0` is transmitted first. The output edge comes `tpd` after the clock edge and is a straight ramp of length `trf`.

Inputs and clock are CMOS, with the threshold at half the supply. The outputs are CML at the same levels as [clkbuf_cml](../Clocking/clkbuf_cml.md).

### Where it sits

Level L3 of [tx_ser_ffe_path](tx_ser_ffe_path.md), four instances per path. The inputs come from [dff_tspc_x8](../Clocking/dff_tspc_x8.md), the outputs go to [cml_dff_x4](../Clocking/cml_dff_x4.md). The clocks are `clk3p5` and `clk3p5b` from [tx_clkgen](../Clocking/tx_clkgen.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in0`, `in1` | input | Two 3.5 Gb/s lanes, CMOS |
| `clk` | input | 3.5 GHz CMOS clock |
| `clkb` | input | Its complement. A real charge-steering cell needs it; the ideal model does not read it |
| `outp`, `outn` | output | One 7 Gb/s lane, CML |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vsw` | 0.3 V | Differential output amplitude (half of the peak-to-peak value) |
| `trf` | 10 ps | Output edge duration |
| `tpd` | 40 ps | Clock edge to output zero crossing delay |

### What the model leaves out

Everything that makes a charge-steering cell what it is. The model does not steer charge at all: it is a latch with an ideal output stage. It does not use the clock's complement, and it has no setup or hold time and no jitter. The numbers above are convenient values for the placeholder, not targets.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*This block has no owner yet. To be filled in by whoever takes it, during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Level L3: eight 3.5 Gb/s CMOS lanes in, four 7 Gb/s CML lanes out, clock 3.5 GHz (`mux2_cs.va`, header)
- A charge-steering cell; it needs the complementary clock, which the clock tree already provides as `clk3p5b` (`mux2_cs.va`, header)
- `in0` is sent first: it appears while the clock is high (`mux2_cs.va`, header)
- Output levels like `clkbuf_cml`: 0.6 V peak-to-peak differential, each side between `vdd` - 0.3 V and `vdd` (`mux2_cs.va`, header and parameter `vsw`)
- Its load is the retiming flop `cml_dff_x4`, clocked at 7 GHz (`tx_ser_ffe_path.va`, header)
- Placeholder timing, not a target: 40 ps clock-to-output delay, 10 ps edges (`mux2_cs.va`, parameters `tpd`, `trf`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `mux2_cs_<what>.svg` (or `.png`), and reference it from this page as `![mux2_cs schematic](../img/mux2_cs_<what>.svg)`.

### Open questions

- (questions for the section lead or for neighbouring blocks' owners)

### References

- (papers, textbook sections, earlier designs; give enough detail that someone else can find them)

## Sizing research

*This block has no owner yet. To be filled in by whoever takes it, during the sizing-research stage.*

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
