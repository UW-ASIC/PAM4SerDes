# demux2_cmos

| Field | Value |
|---|---|
| Owner (from git history) | deaconsham |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/demux2_cmos.va`](../../va/Receiver/demux2_cmos.va) |
| Used in | [rx_deser_path](rx_deser_path.md), 24 per path (8 in stage 3, 16 in stage 4) |
| Section | [Receiver](README.md) |

## Architecture

`demux2_cmos` is a 1:2 demultiplexer in CMOS logic. It does the same job as [demux2_cml](demux2_cml.md) with single-ended, rail-to-rail signals: one bit stream in, two streams at half the rate out.

The system needs it for the last two stages of the deserializer, which work on CMOS signals at 3.5 and 1.75 Gb/s.

### How the model works

The clock runs at half the input bit rate, so each clock period covers two input bits.

- On the **rising** edge it stores the input: this is the earlier bit of the pair.
- On the **falling** edge it puts the stored bit on `q0` and the input at that moment, the later bit, on `q1`.

Both outputs therefore change together, on the falling edge, and each output bit lasts two input bit periods.

### Where it sits

In [rx_deser_path](rx_deser_path.md):

| Stage | Count | Clock | Rate in to out |
|---|---|---|---|
| 3 | 8 | `clk1p75` | 3.5 to 1.75 Gb/s. Inputs from the inline CML-to-CMOS conversion |
| 4 | 16 | `clk0p875` | 1.75 to 0.875 Gb/s. Outputs to the output register |

`rx_deser_path` uses the default parameters, which are for the 0.7 V supply.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d` | input | Data in, CMOS |
| `clk` | input | Clock at half the input bit rate, CMOS |
| `q0` | output | The earlier bit of each pair |
| `q1` | output | The later bit of each pair |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 0.7 V | Output high level |
| `vth` | `vdd`/2 | Data and clock threshold |
| `tt` | 10 ps | Output rise and fall time |
| `init_q0`, `init_q1` | 0, 0 | Output bits at start-up |

### What the model leaves out

- No clock-to-output delay: the output edge starts at the clock edge.
- Setup and hold times are not checked.
- No jitter and no supply pins.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Stage 3: 3.5 Gb/s in, two 1.75 Gb/s lanes out, clock 1.75 GHz (`demux2_cmos.va`, header)
- Stage 4: 1.75 Gb/s in, two 0.875 Gb/s lanes out, clock 0.875 GHz (`rx_deser_path.va`, instance lines)
- The clock runs at half the input bit rate; the earlier bit of each pair is stored on the rising edge, and both outputs change together on the falling edge (`demux2_cmos.va`, header)
- CMOS levels, single-ended, 0 to 0.7 V, threshold at half the supply (`demux2_cmos.va`, header and parameters `vdd`, `vth`)
- Output edge 10 ps in the model (`demux2_cmos.va`, parameter `tt`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `demux2_cmos_<what>.svg` (or `.png`), and reference it from this page as `![demux2_cmos schematic](../img/demux2_cmos_<what>.svg)`.

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
