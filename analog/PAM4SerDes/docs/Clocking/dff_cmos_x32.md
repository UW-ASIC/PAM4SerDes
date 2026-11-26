# dff_cmos_x32

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model); retiming flops, used in the TX serializer |
| Model | [`va/Clocking/dff_cmos_x32.va`](../../va/Clocking/dff_cmos_x32.va) |
| Used in | [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), once per path (`u_rin`), so twice in the transmitter |
| Section | [Clocking](README.md) |

## Architecture

`dff_cmos_x32` is a bank of 32 D flip-flops that share one clock. On each rising clock edge every flop copies its input to its output.

The system needs it at the very start of the serializer. The 32-bit word arrives from the data source, and this bank retimes it to the 0.875 GHz word clock, so that all 32 bits change together at a known moment before the first multiplexer level picks them apart.

The cell is kept with the clocking cells because it is a retiming element; it is used in the transmitter.

### Where it sits

Level L0 of [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md): its inputs are the 32 wires of the word from [prbs_gray_src](../Transmitter/prbs_gray_src.md), its clock is `clk0p875` from [tx_clkgen](tx_clkgen.md), and its outputs go to the sixteen [mux2_cmos](../Transmitter/mux2_cmos.md) of level L1.

The parent sets the levels for the 0.7 V supply: both thresholds 0.35 V, high level 0.7 V, rise and fall time 20 ps.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | Clock, single-ended CMOS. Flops trigger on its rising edge |
| `d0` .. `d31` | input | Data in, one pin per bit |
| `q0` .. `q31` | output | Data out, one pin per bit |

There are no supply pins: the output levels are parameters.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_clk`, `vth_data` | 0.5 V, 0.5 V | Clock and data thresholds. The parent sets 0.35 V |
| `vlow`, `vhigh` | 0 V, 1.0 V | Output levels. The parent sets `vhigh` = 0.7 V |
| `t_propogation` | 0 | Clock-to-output delay (spelled this way in the file) |
| `t_rise`, `t_fall` | 0, 0 | Output edge times. The parent sets 20 ps |

### What the model leaves out

- Setup and hold times are not checked: whatever the input is at the clock edge is taken.
- The clock-to-output delay is 0.
- No jitter, and no reset or enable. The header says neither is specified in the project notes it was written from, and calls the interface provisional.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- 32 lanes at 0.875 Gb/s, retimed on the rising edge of the 0.875 GHz clock (`tx_ser_ffe_path.va`, header)
- CMOS levels 0 to 0.7 V, thresholds at 0.35 V, output edges 20 ps, as set by the parent (`tx_ser_ffe_path.va`, instance `u_rin`)
- Reset and enable: not specified, so the model has neither (`dff_cmos_x32.va`, header)
- The interface (one shared clock, 32 single-ended inputs and outputs) is marked provisional (`dff_cmos_x32.va`, header)
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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `dff_cmos_x32_<what>.svg` (or `.png`), and reference it from this page as `![dff_cmos_x32 schematic](../img/dff_cmos_x32_<what>.svg)`.

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
