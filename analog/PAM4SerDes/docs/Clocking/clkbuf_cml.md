# clkbuf_cml

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/clkbuf_cml.va`](../../va/Clocking/clkbuf_cml.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_buf14`); [rx_clkgen](rx_clkgen.md), once (`u_buf14`) |
| Section | [Clocking](README.md) |

## Architecture

`clkbuf_cml` is a current-mode-logic clock buffer. It takes a differential clock, amplifies it until it limits, and drives it out at the standard CML swing.

The system needs it for two reasons, both in the model's header: it restores the swing, and it isolates loads. In both clock trees it is the cell that drives `clk14`, the fastest and most heavily loaded clock.

### How the model works

- A limiting amplifier: the differential input times `gain`, limited smoothly to plus or minus `vsw`.
- One pole with time constant `tau`.
- A tail current `vsw / rl` steered between two load resistors `rl` to `vdd`. Each output therefore swings between `vdd` - `vsw` and `vdd`.
- At each input crossing a random time shift with standard deviation `rj` is applied to the output.

### Where it sits

In [tx_clkgen](tx_clkgen.md) and [rx_clkgen](rx_clkgen.md): the input comes from [dcc_cml](dcc_cml.md), the output is `clk14_p/n`. `clk14` goes to the first [div2_cml](div2_cml.md) and to the 14 GHz cells of the datapath (see the two clock-tree pages for the lists).

Both parents set `rj` to 40 fs times `rj_scale` and give the instance its own seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | Differential clock |
| `outp`, `outn` | output | Buffered clock, CML levels |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `gain` | 2 | Small-signal differential gain at DC |
| `vsw` | 0.3 V | Saturated differential output amplitude (0.6 V peak-to-peak differential) |
| `tau` | 5.707 ps | Output time constant |
| `vos` | 0 V | Input-referred offset, range -0.1 to +0.1 V |
| `rl` | 200 ohm | Load resistor on each side |
| `rj` | 40 fs | Added random jitter per output crossing, rms |
| `rj_seed` | 6 | Seed of the jitter sequence; every instance needs its own |

### What the model leaves out

- The load does not change the bandwidth: `tau` is a fixed number, whatever is connected to the output.
- The tail current is computed from `vsw` and `rl`. There is no bias input.
- No duty-cycle error of its own, other than through `vos`.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Carries the 14 GHz clock (`tx_clkgen.va` and `rx_clkgen.va`, header)
- Output 0.6 V peak-to-peak differential, each side between `vdd` - 0.3 V and `vdd` (`clkbuf_cml.va`, parameter `vsw`)
- Load resistor 200 ohm per side, which with the swing above means a tail current of 1.5 mA (`clkbuf_cml.va`, parameter `rl` and the line `iss = vsw / rl`)
- Output time constant 5.707 ps (`clkbuf_cml.va`, parameter `tau`)
- Added random jitter 40 fs rms per output crossing (`clkbuf_cml.va`, parameter `rj`)
- Small-signal differential gain 2 at DC (`clkbuf_cml.va`, parameter `gain`)
- In the receiver its loads are the 24 slicers, the DFE, the two retimers and the CDR phase detector (`rx_clkgen.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `clkbuf_cml_<what>.svg` (or `.png`), and reference it from this page as `![clkbuf_cml schematic](../img/clkbuf_cml_<what>.svg)`.

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
