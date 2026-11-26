# rx_term

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/rx_term.va`](../../va/Receiver/rx_term.va) |
| Used in | [rx_afe](rx_afe.md), once (`u_term`) |
| Section | [Receiver](README.md) |

## Architecture

`rx_term` is the receiver's input termination. It puts a resistor across the two pads and models the capacitance that the ESD protection adds to each pad.

The system needs the resistor so that the signal arriving on the 100 ohm differential line is absorbed and not reflected. The capacitance is modelled because it sits on the signal path and limits the bandwidth of the input.

### How the model works

Three elements:

- `rterm` between `rx_p` and `rx_n`,
- `cesd` from `rx_p` to `vref`,
- `cesd` from `rx_n` to `vref`.

### Where it sits

First cell of [rx_afe](rx_afe.md). It hangs on the pads; the [ctle](ctle.md) reads the same two nodes. `vref` is connected to the top-level pin `vtt`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `rx_p`, `rx_n` | inout | The pads |
| `vref` | inout | Termination reference (`vtt`) |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `rterm` | 100 ohm | Differential termination resistance |
| `cesd` | 50 fF | ESD capacitance per side |

### What the model leaves out

- There is no DC path from the pads to `vref`: only the two capacitors connect to it. The common mode of the pads is set by whatever drives them.
- The ESD devices are a fixed capacitance. No leakage, no clamping, no pad or package inductance.
- No resistor tolerance or tuning.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Differential termination 100 ohm (`rx_term.va`, parameter `rterm`)
- ESD capacitance 50 fF per side, to the termination reference (`rx_term.va`, parameter `cesd`)
- Signal: 28 GBd PAM4 from the channel (`rx_top.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `rx_term_<what>.svg` (or `.png`), and reference it from this page as `![rx_term schematic](../img/rx_term_<what>.svg)`.

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
