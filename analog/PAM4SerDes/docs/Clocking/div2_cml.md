# div2_cml

| Field | Value |
|---|---|
| Owner (from git history) | none yet |
| Kind | placeholder (ideal stand-in, no owner) |
| Model | [`va/Clocking/placeholders/div2_cml.va`](../../va/Clocking/placeholders/div2_cml.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_div7`); [rx_clkgen](rx_clkgen.md), twice (`u_div7`, `u_div3p5`) |
| Section | [Clocking](README.md) |

## Architecture

`div2_cml` halves the frequency of a CML clock: it toggles its output once per input cycle.

**This file is an ideal placeholder with no owner.** Its header says so: it is not the team's `div2_cml`, and it exists so that the two clock trees compile and simulate until the real block is committed. **Someone needs to take this block.**

The system needs the real one for the fastest divider steps: 14 to 7 GHz in both clock trees, and 7 to 3.5 GHz in the receiver. These steps are CML in the clock trees; the slower ones use [div2_tspc](div2_tspc.md).

### How the model works

The output toggles on every rising zero crossing of the differential input. The output's zero crossing comes `tpd` after the input's, and the edge is a straight ramp of length `trf`. The output levels match [clkbuf_cml](clkbuf_cml.md). At start-up `outp` is low.

To divide on the falling edge instead, the parent connects the input swapped.

### Where it sits

| Parent | Instance | Step | Edge |
|---|---|---|---|
| [tx_clkgen](tx_clkgen.md) | `u_div7` | `clk14` to `clk7` | Rising edge of `clk14` |
| [rx_clkgen](rx_clkgen.md) | `u_div7` | `clk14` to `clk7` | Rising edge of `clk14` |
| [rx_clkgen](rx_clkgen.md) | `u_div3p5` | `clk7` to `clk3p5` | Falling edge of `clk7` (input swapped) |

The input of the first step comes from [clkbuf_cml](clkbuf_cml.md). The outputs feed the CML cells of the datapath and, through [cml2cmos](cml2cmos.md), the CMOS part of each tree.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | Differential clock in |
| `outp`, `outn` | output | Differential clock at half the frequency, CML levels |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vsw` | 0.3 V | Differential output amplitude (half of the peak-to-peak value) |
| `trf` | 5 ps | Output edge duration |
| `tpd` | 15 ps | Input zero crossing to output zero crossing delay |

### What the model leaves out

Everything a real divider has to get right: there is no maximum frequency, no jitter, no reset and no start-up behaviour other than "starts with `outp` low". The numbers above are convenient values for the placeholder, not targets.

## Topology research

*This block has no owner yet. To be filled in by whoever takes it, during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Divide 14 GHz to 7 GHz in both clock trees, and 7 GHz to 3.5 GHz in the receiver (`tx_clkgen.va` and `rx_clkgen.va`, header)
- Output at the same levels as `clkbuf_cml`: 0.6 V peak-to-peak differential, each side between `vdd` - 0.3 V and `vdd` (`div2_cml.va`, header and parameter `vsw`)
- The receiver needs both a rising-edge and a falling-edge divider; the placeholder gets the second by swapping its inputs (`rx_clkgen.va`, header)
- Placeholder timing, not a target: 15 ps delay, 5 ps edges (`div2_cml.va`, parameters `tpd`, `trf`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `div2_cml_<what>.svg` (or `.png`), and reference it from this page as `![div2_cml schematic](../img/div2_cml_<what>.svg)`.

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
