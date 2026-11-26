# dff_tspc_x8

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model); retiming flops, used in the TX serializer |
| Model | [`va/Clocking/dff_tspc_x8.va`](../../va/Clocking/dff_tspc_x8.va) |
| Used in | [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), once per path (`u_rcs`), so twice in the transmitter |
| Section | [Clocking](README.md) |

## Architecture

`dff_tspc_x8` is a bank of eight D flip-flops on one clock, in true single-phase clock (TSPC) logic. On each rising clock edge every flop copies its input to its output.

The system needs it in the middle of the serializer. After two levels of CMOS multiplexers there are eight lanes at 3.5 Gb/s. This bank retimes them on the 3.5 GHz clock, so they reach the next level, the charge-steering multiplexers that turn them into CML, with fresh timing.

The cell is kept with the clocking cells because it is a retiming element; it is used in the transmitter.

### How the model works

The file has a helper module for one lane, `dff_tspc_1lane`, and the bank instantiates it eight times.

- The output edge comes `tcq` after the clock edge, plus random jitter `rj`, as a straight ramp of length `trf`, driven through `rout`.
- Setup and hold are checked. If the data changes less than `tsu` before the clock edge, the flop takes the **old** value and prints a warning. If it changes less than `th` after the edge, a warning is printed.
- If a clock period falls outside 1/`fmax` .. 1/`fmin` the model prints a warning.

### Where it sits

In [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), between level L2 (eight [mux2_cmos](../Transmitter/mux2_cmos.md)) and level L3 (four [mux2_cs](../Transmitter/mux2_cs.md)). Its clock is `clk3p5` from [tx_clkgen](tx_clkgen.md).

The parent uses the default parameters, except that it sets `rj` to 200 fs times `rj_scale`, so the top-level jitter knob reaches this cell too.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | 3.5 GHz CMOS clock. Flops trigger on its rising edge |
| `d[7:0]` | input | Eight data lanes in, CMOS |
| `q[7:0]` | output | Eight data lanes out, CMOS |
| `vdd`, `vss` | inout | 0.7 V core supply and ground. The thresholds are half the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `tcq` | 30 ps | Delay from clock 50 % to output 50 % |
| `tsu` | 15 ps | Setup time: data stable this long before the clock edge |
| `th` | 8 ps | Hold time: data stable this long after the clock edge |
| `trf` | 25 ps | Output edge duration, 0 to 100 % |
| `rj` | 200 fs | Added random jitter per output edge, rms |
| `rj_seed` | 4 | Seed of lane 0's jitter sequence; lane i uses `rj_seed` + 100 i |
| `rout` | 100 ohm | Output driver resistance, 0 for an ideal source |
| `fmin`, `fmax` | 2.975 GHz, 4.025 GHz | Specified clock frequency range |

### What the model leaves out

- A timing violation gives a clean old value and a warning. There is no metastability and no slow output.
- The delays are fixed numbers. They do not depend on load, supply or input slope.
- No reset.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Eight lanes at 3.5 Gb/s, between the CMOS stages and the charge-steering stage (`dff_tspc_x8.va`, header)
- Specified clock range 2.975 to 4.025 GHz (`dff_tspc_x8.va`, parameters `fmin`, `fmax`)
- Clock-to-output delay 30 ps (`dff_tspc_x8.va`, parameter `tcq`)
- Setup time 15 ps, hold time 8 ps (`dff_tspc_x8.va`, parameters `tsu`, `th`)
- Added random jitter 200 fs rms per output edge (`dff_tspc_x8.va`, parameter `rj`)
- Output edge 25 ps, driver resistance 100 ohm (`dff_tspc_x8.va`, parameters `trf`, `rout`)
- True single-phase clock (TSPC) logic, positive-edge triggered (`dff_tspc_x8.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `dff_tspc_x8_<what>.svg` (or `.png`), and reference it from this page as `![dff_tspc_x8 schematic](../img/dff_tspc_x8_<what>.svg)`.

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
