# phase_aligner

| Field | Value |
|---|---|
| Owner (from git history) | Winy |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/phase_aligner.va`](../../va/Clocking/phase_aligner.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_pa`) |
| Section | [Clocking](README.md) |

## Architecture

`phase_aligner` shifts the phase of the 7 GHz CMOS clock until it lines up with the data. It is a small feedback loop of its own.

The system needs it at one specific place in the transmitter. The lower serializer levels run on CMOS clocks, the upper ones on CML clocks, and the two clock families take different paths through the clock tree. Where a CMOS-clocked stage hands its data to a CML-clocked one, the two must be timed so the data is sampled in the middle of the bit. This block watches a lane of data just after that hand-off and moves the CMOS clocks until it is centred.

### How the model works

The file contains the top module `phase_aligner` and eight small helper modules. The top module only wires them:

| Step | Helper | What it does |
|---|---|---|
| 1 | `delay_t3` | Delays the data by 71.43 ps |
| 2 | `mult_1` | Compares the data with its delayed copy: +0.3 V when they differ, -0.3 V when they are the same. This marks the data's transitions |
| 3 | `mult_2` | Multiplies that by the output clock minus 0.35 V (its mid level) |
| 4 | `vi_converter` | Turns the product into a current, 1 mS |
| 5 | `capacitor` | Integrates the current on 1 pF. Its voltage is the loop's state |
| 6 | `pi_control` | Scales the capacitor voltage by 1 / 0.7 V to a setting `m` |
| 7 | `pi` | Delays the input clock by `m` times 142.86 ps, with `m` limited to 0.01 .. 1. This stands for the phase interpolator |
| 8 | `buffer` | Drives the delayed clock out |

The loop is at rest when the average of step 3 is zero. That condition ties the position of the clock's edges to the data's transitions.

### Where it sits

In [tx_clkgen](tx_clkgen.md), between [cml2cmos](cml2cmos.md) (which gives it the 7 GHz CMOS clock) and the first [div2_tspc](div2_tspc.md). So every CMOS clock of the transmitter, 3.5, 1.75 and 0.875 GHz, is derived from its output and moves with it.

Its data input comes from [tx_top](../Transmitter/tx_top.md): lane 0 of the MSB path after [cml_dff_x4](cml_dff_x4.md), converted to a single-ended signal by an ideal `diff2se` cell (see [glue](glue.md)).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `cml_dff_x4` | input | The data to align to: retimed 7 Gb/s lane, single-ended around 0 V |
| `clk7_cml2cmos` | input | 7 GHz CMOS clock from `cml2cmos` |
| `ck_28` | output | The shifted 7 GHz CMOS clock. Despite its name it carries 7 GHz: `tx_clkgen` feeds it to the 7 to 3.5 GHz divider |

There are no supply pins; the helpers use an internal ground.

### Parameters

The top module has no parameters. The values are written in its instance lines:

| Value | Set to | Meaning |
|---|---|---|
| `t3` of `delay_t3` | 71.43 ps | Data delay of the edge detector. The file's comment: one bit at 14 Gb/s |
| `vmid` of `mult_2` | 0.35 V | Mid level of the CMOS clock |
| `g` of `vi_converter` | 1 mS | Voltage-to-current gain |
| `c` of `capacitor` | 1 pF (default) | Loop capacitor |
| `vmax` of `pi_control` | 0.7 V | Capacitor voltage that means full delay |
| `dmax` of `pi` | 142.86 ps | Full delay: one period of 7 GHz |

### What the model leaves out

- The phase interpolator is a pure variable delay. Its smallest delay is about 1.4 ps, not 0, because a zero delay stalls ngspice (the file's comment).
- The multipliers, the delay and the integrator are ideal. There is no jitter, no offset and no leakage on the capacitor.
- The capacitor starts at 0 V, and there is no reset input.

Existing testbenches: [`test/pa_test.sp`](../../test/pa_test.sp) for the whole block, [`test/delay_test.sp`](../../test/delay_test.sp) and [`test/viconv_output_test.sp`](../../test/viconv_output_test.sp) for its parts.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Clock in and out: 7 GHz, CMOS, 0 to 0.7 V (`tx_clkgen.va`, header; `phase_aligner.va`, `vmid` = 0.35 V and `vmax` = 0.7 V)
- Data input: a retimed 7 Gb/s lane, read as a single-ended signal around 0 V (`tx_top.va`, header)
- Delay range of the phase shifter up to 142.86 ps, one period of the 7 GHz clock (`phase_aligner.va`, `dmax`)
- Data delay 71.43 ps in the edge detector (`phase_aligner.va`, `t3`)
- Loop integrator in the model: 1 mS into 1 pF (`phase_aligner.va`, `g` and the default of `c`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `phase_aligner_<what>.svg` (or `.png`), and reference it from this page as `![phase_aligner schematic](../img/phase_aligner_<what>.svg)`.

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
