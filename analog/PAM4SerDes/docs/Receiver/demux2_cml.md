# demux2_cml

| Field | Value |
|---|---|
| Owner (from git history) | deaconsham |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/demux2_cml.va`](../../va/Receiver/demux2_cml.va) |
| Used in | [rx_deser_path](rx_deser_path.md), six per path (two in stage 1, four in stage 2) |
| Section | [Receiver](README.md) |

## Architecture

`demux2_cml` is a 1:2 demultiplexer in current-mode logic. It takes one fast bit stream and puts it out as two streams at half the rate: every pair of input bits appears side by side on the two outputs.

The system needs it for the first two stages of the deserializer, which work on CML signals at 14 and 7 Gb/s.

### How the model works

The clock runs at half the input bit rate, so each clock period covers two input bits.

- On the **rising** edge it stores the input: this is the earlier bit of the pair.
- On the **falling** edge it puts the stored bit on `q0` and the input at that moment, the later bit, on `q1`.

Both outputs therefore change together, on the falling edge, and each output bit lasts two input bit periods.

### Where it sits

In [rx_deser_path](rx_deser_path.md):

| Stage | Count | Clock | Rate in to out |
|---|---|---|---|
| 1 | 2 | `clk7` | 14 to 7 Gb/s. Inputs from the two [rx_dec_retime](rx_dec_retime.md) |
| 2 | 4 | `clk3p5` | 7 to 3.5 Gb/s. Outputs to the inline CML-to-CMOS conversion |

`rx_deser_path` uses the default parameters. Note the default `vdd` of 1.0 V in the table below.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d_p`, `d_n` | input | Data in, differential, compared at 0 V difference |
| `clk_p`, `clk_n` | input | Clock at half the input bit rate |
| `q0_p/n` | output | The earlier bit of each pair |
| `q1_p/n` | output | The later bit of each pair |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 1.0 V | Supply the output levels follow. Not overridden in the hierarchy |
| `v_swing` | 0.3 V | Swing of each output leg |
| `v_cm` | `vdd` - `v_swing`/2 | Output common mode |
| `tt` | 10 ps | Output rise and fall time |
| `init_q0`, `init_q1` | 0, 0 | Output bits at start-up |

### What the model leaves out

- No clock-to-output delay: the output edge starts at the clock edge.
- Setup and hold times are not checked.
- No jitter, no noise, and no bias or supply pins.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Stage 1: 14 Gb/s in, two 7 Gb/s lanes out, clock 7 GHz (`demux2_cml.va`, header)
- Stage 2: 7 Gb/s in, two 3.5 Gb/s lanes out, clock 3.5 GHz (`rx_deser_path.va`, instance lines)
- The clock runs at half the input bit rate; the earlier bit of each pair is stored on the rising edge, and both outputs change together on the falling edge (`demux2_cml.va`, header)
- Differential signals; each output leg swings 0.3 V around `vdd` - 0.15 V (`demux2_cml.va`, header and parameters `v_swing`, `v_cm`)
- Output edge 10 ps in the model (`demux2_cml.va`, parameter `tt`)
- Stage 1 samples just after the 14 GHz clock's rising edge, because the 7 GHz clock toggles there (`rx_top.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `demux2_cml_<what>.svg` (or `.png`), and reference it from this page as `![demux2_cml schematic](../img/demux2_cml_<what>.svg)`.

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
