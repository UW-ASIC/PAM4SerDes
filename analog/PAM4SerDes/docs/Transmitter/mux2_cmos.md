# mux2_cmos

| Field | Value |
|---|---|
| Owner (from git history) | oDNA |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/mux2_cmos.va`](../../va/Transmitter/mux2_cmos.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), 24 per path (16 at level L1, 8 at level L2) |
| Section | [Transmitter](README.md) |

## Architecture

`mux2_cmos` is a 2:1 multiplexer in CMOS logic. The select input chooses which of the two data inputs appears at the output: `in0` while select is low, `in1` while it is high.

The system needs it for the two slowest levels of the serializer. When the select input is a clock at the rate of the incoming data, the output carries the two inputs one after the other, at twice the rate.

### How the model works

The output voltage follows the selected input through a resistor `rout` into a capacitor `cout`. The switch between the inputs is smooth, over about `vsmooth` of select voltage. The multiplexer is transparent: there is no latch in it, so the output follows whatever the selected input does.

### Where it sits

In [tx_ser_ffe_path](tx_ser_ffe_path.md):

| Level | Count | Select clock | Rate in to out |
|---|---|---|---|
| L1 | 16 | `clk0p875` | 0.875 to 1.75 Gb/s |
| L2 | 8 | `clk1p75` | 1.75 to 3.5 Gb/s |

L1 takes its inputs from [dff_cmos_x32](../Clocking/dff_cmos_x32.md). L2 drives [dff_tspc_x8](../Clocking/dff_tspc_x8.md). Which input is sent first is different at the two levels; the lane-order rules are on the [tx_ser_ffe_path](tx_ser_ffe_path.md) page.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in0`, `in1` | input | The two data lanes, CMOS |
| `sel` | input | Select: low = `in0`, high = `in1`. Driven by a clock |
| `out` | output | The multiplexed lane, CMOS |

There are no supply pins: the output takes its levels from the inputs.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth` | 0.35 V | Select threshold |
| `vsmooth` | 0.01 V | Width of the select transition |
| `rout` | 100 ohm | Output driver resistance. An estimate |
| `cout` | 20 fF | Output capacitance. An estimate |

### What the model leaves out

- The header says `rout` and `cout` are estimated values, written before the block was specified.
- The output is a mix of the input voltages, so it has no drive strength or supply of its own.
- No delay other than the output RC, and no jitter.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Level L1: two 0.875 Gb/s lanes to one at 1.75 Gb/s, select clock 0.875 GHz (`tx_ser_ffe_path.va`, header)
- Level L2: two 1.75 Gb/s lanes to one at 3.5 Gb/s, select clock 1.75 GHz (`tx_ser_ffe_path.va`, header)
- CMOS levels 0 to 0.7 V, select threshold 0.35 V (`mux2_cmos.va`, parameter `vth`)
- Output resistance 100 ohm and output capacitance 20 fF; both are marked as estimates (`mux2_cmos.va`, header)
- Its load at level L2 is the retiming flop `dff_tspc_x8`, setup time 15 ps (`dff_tspc_x8.va`, parameter `tsu`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `mux2_cmos_<what>.svg` (or `.png`), and reference it from this page as `![mux2_cmos schematic](../img/mux2_cmos_<what>.svg)`.

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
