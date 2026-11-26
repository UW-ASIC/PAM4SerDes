# predriver_cml

| Field | Value |
|---|---|
| Owner (from git history) | Zoey Situ |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/predriver_cml.va`](../../va/Transmitter/predriver_cml.va) |
| Used in | [tx_top](tx_top.md), six times (one per path and FFE tap) |
| Section | [Transmitter](README.md) |

## Architecture

`predriver_cml` sits between the last multiplexer of a serializer path and the output driver. There are six of them: one for each FFE tap (pre, main, post) of each binary path (MSB, LSB).

In the present model its job is small. It reads the polarity of its differential input and puts the same polarity out at fixed levels: a common mode of 1.2 V and a differential swing of 0.2 V. The file calls these "temp output values". So in the model it carries the bit from the 0.7 V CML of the serializer up to levels near the 1.25 V output-stage supply.

The model file has no description of what the real circuit must do beyond that. The owner should state it in the Topology research section below.

### Where it sits

In [tx_top](tx_top.md): each input is one tap output (`pre`, `main` or `post`) of a [tx_ser_ffe_path](tx_ser_ffe_path.md), at 28 Gb/s. Each output goes to the matching tap input of [pam4_driver](pam4_driver.md).

The header of `tx_top` notes that this cell is ideal and has no bias pin yet. [tx_bias](../Biasing/tx_bias.md) already has an output for the pre-driver tail current, `i_pdrv`; it is unconnected.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | One FFE tap at 28 Gb/s, differential |
| `outp`, `outn` | output | The same bit, non-inverted, at the levels set by `vcm` and `vod` |

There are no supply pins and no bias pin.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vcm` | 1.2 V | Output common mode. Temporary value |
| `vod` | 0.2 V | Output differential swing. Temporary value |

### What the model leaves out

Almost everything: the output switches at the instant the input difference changes sign. There is no gain, no bandwidth, no delay, no edge time, no supply and no bias current. The block also prints its output voltages with `$strobe`.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Data rate 28 Gb/s: one cell per path and FFE tap, after the final multiplexer (`tx_top.va`, header)
- Input: CML from `mux2_cml_hr`, 0.6 V peak-to-peak differential around 0.55 V (`mux2_cml_hr.va`, parameters `itail`, `rload`)
- Output levels in the model, marked as temporary: common mode 1.2 V, differential swing 0.2 V (`predriver_cml.va`, comment "temp output values")
- The bias block budgets a tail current of 0.2 V / 200 ohm per cell, six cells; the 200 ohm load is marked "assumed" (`tx_bias.va`, parameters `vod_pd`, `rld_pd`, `n_pd`)
- The cell has no bias pin yet; `tx_bias.i_pdrv` is waiting for one (`tx_top.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `predriver_cml_<what>.svg` (or `.png`), and reference it from this page as `![predriver_cml schematic](../img/predriver_cml_<what>.svg)`.

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
