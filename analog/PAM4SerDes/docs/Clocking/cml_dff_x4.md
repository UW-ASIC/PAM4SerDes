# cml_dff_x4

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model); retiming flops, used in the TX serializer |
| Model | [`va/Clocking/cml_dff_x4.va`](../../va/Clocking/cml_dff_x4.va) |
| Used in | [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), once per path (`u_rcml`), so twice in the transmitter |
| Section | [Clocking](README.md) |

## Architecture

`cml_dff_x4` is a bank of four differential D flip-flops in current-mode logic, on one differential clock. On each rising clock edge every flop copies its input to its output.

The system needs it near the top of the serializer. The four 7 Gb/s lanes come out of the charge-steering multiplexers, which are clocked from the CMOS clock family. This bank retimes them to the 7 GHz CML clock, so the last two multiplexer levels, which run on CML clocks, get data with clean timing.

Its lane 0 output has a second job: it is the data that the [phase_aligner](phase_aligner.md) locks the CMOS clocks to.

The cell is kept with the clocking cells because it is a retiming element; it is used in the transmitter.

### Where it sits

In [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), between level L3 (four [mux2_cs](../Transmitter/mux2_cs.md)) and level L4 (two [mux2_cml_hr](../Transmitter/mux2_cml_hr.md)). Its clock is `clk7_p/n` from [tx_clkgen](tx_clkgen.md).

The parent sets the levels to match the other CML cells: common mode 0.55 V, amplitude 0.3 V (0.6 V peak-to-peak differential), rise and fall time 5 ps.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk_p`, `clk_n` | input | 7 GHz CML clock. Flops trigger on its rising zero crossing |
| `d0_p/n` .. `d3_p/n` | input | Four differential data lanes in |
| `q0_p/n` .. `q3_p/n` | output | Four differential data lanes out. Lane 0 also goes to the phase aligner |

There are no supply pins: the output levels are parameters.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vcm` | 0.6 V | Output common mode. Marked illustrative; the parent sets 0.55 V |
| `vdiff` | 0.2 V | Output differential amplitude. Marked illustrative; the parent sets 0.3 V |
| `vclk_diff_th`, `vdata_diff_th` | 0 V, 0 V | Differential thresholds of clock and data |
| `t_propogation` | 0 | Clock-to-output delay (spelled this way in the file) |
| `t_rise`, `t_fall` | 0, 0 | Output edge times. The parent sets 5 ps |

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

- Four lanes at 7 Gb/s, retimed on the rising edge of the 7 GHz CML clock (`tx_ser_ffe_path.va`, header)
- CML levels as set by the parent: common mode 0.55 V, 0.6 V peak-to-peak differential, output edges 5 ps (`tx_ser_ffe_path.va`, instance `u_rcml`)
- The cell's own level defaults are marked illustrative, to be replaced by the real CML interface levels (`cml_dff_x4.va`, comment on `vcm`, `vdiff`)
- Reset and enable: not specified, so the model has neither (`cml_dff_x4.va`, header)
- The interface (differential clock, data and outputs) is marked provisional (`cml_dff_x4.va`, header)
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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `cml_dff_x4_<what>.svg` (or `.png`), and reference it from this page as `![cml_dff_x4 schematic](../img/cml_dff_x4_<what>.svg)`.

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
