# dcc_cml

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/dcc_cml.va`](../../va/Clocking/dcc_cml.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_dcc`); [rx_clkgen](rx_clkgen.md), once (`u_dcc`) |
| Section | [Clocking](README.md) |

## Architecture

`dcc_cml` is the duty-cycle corrector. It takes the 14 GHz clock from the VCO and puts out a clock of the same frequency whose high time is a set fraction of the period, 50 % by default.

The system needs it because both the transmitter and the receiver are half-rate: they use the rising **and** the falling edge of the 14 GHz clock, one for each of the two symbols in a clock period. If the clock is not high for exactly half the period, the two symbols get different widths.

It is the first cell of both clock trees. In the present models it also turns the single-ended VCO clock into a differential one.

### How the model works

It measures the input period from one rising edge to the next, runs its own oscillator at that frequency, and makes the output high for `duty_target` of each cycle. The header warns that the output phase is not guaranteed to follow the input's rising edge, and says to use the model for functional duty-cycle testing.

### Where it sits

In [tx_clkgen](tx_clkgen.md) and [rx_clkgen](rx_clkgen.md): the input is the VCO clock (from [tx_pll](tx_pll.md) or [rx_cdr](rx_cdr.md)), the output goes to [clkbuf_cml](clkbuf_cml.md). Both parents set the input threshold to 0.35 V, the middle of the CMOS swing.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk_in` | input | 14 GHz clock, single-ended. The port comment notes that a transistor-level CML version will need a differential input |
| `clk_outp`, `clk_outn` | output | Corrected clock, differential. The port comment says "need to confirm" |
| `vss` | inout | Ground. There is no `vdd` pin: the output levels are parameters |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `duty_target` | 0.500 | Output duty cycle, allowed 0.496 to 0.504 |
| `vth` | 0 V | Input threshold. Both parents set 0.35 V |
| `f_init` | 14 GHz | Frequency assumed until two rising edges have been seen |
| `vcm` | 0.6 V | Output common mode. Placeholder |
| `vdiff` | 0.4 V | Output differential amplitude. Placeholder |
| `t_edge` | 1 ps | Output transition time |

### What the model leaves out

- It is not a correction loop. It regenerates the clock, so it does not show how well a real corrector removes a given duty-cycle error, or how long it takes.
- The output levels are placeholders, as the header says. With the defaults each output swings between 0.4 V and 0.8 V, which is not the CML level used elsewhere (0.4 V to 0.7 V) and goes above the 0.7 V supply. The `clkbuf_cml` behind it limits the signal, so the rest of the tree sees normal CML levels.
- No jitter.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Output duty cycle 49.6 % to 50.4 %, nominal 50 % (`dcc_cml.va`, comment "Project requirement" on `duty_target`)
- CML style (`dcc_cml.va`, header)
- Clock frequency 14 GHz nominal (`dcc_cml.va`, parameter `f_init`)
- Not specified by the project yet, according to the header: transistor topology, control algorithm, output common mode and output swing (`dcc_cml.va`, header)
- A transistor-level CML version will need a differential input; the model's input is single-ended (`dcc_cml.va`, port comment)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `dcc_cml_<what>.svg` (or `.png`), and reference it from this page as `![dcc_cml schematic](../img/dcc_cml_<what>.svg)`.

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
