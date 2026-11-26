# slicer

| Field | Value |
|---|---|
| Owner (from git history) | Justin Fang |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/Slicer/slicer.va`](../../va/Receiver/Slicer/slicer.va) |
| Used in | [rx_decision](rx_decision.md), 24 times (`s0` .. `s23`). Also three times in [pam4_slicer](pam4_slicer.md), which is not instantiated |
| Section | [Receiver](README.md) |

## Architecture

`slicer` is a clocked comparator. On each rising clock edge it compares the differential input with a differential threshold and holds the answer, high or low, until the next rising edge.

The system needs it to turn the analog PAM4 signal into decisions. One slicer answers one question: is the signal above this threshold? Three slicers with three thresholds separate the four levels. The receiver uses 24 of them; the [rx_decision](rx_decision.md) page explains why.

### How the model works

At the rising zero crossing of `clkp` - `clkn`:

```
decision = +1  if  V(vinp, vinn) > V(vthp, vthn) + offset   else  -1
```

The two outputs then sit at `v_commonmode` plus and minus half of `vswing` times the decision, with edges of length `t_risefall`.

The header gives the numbers the block is built around: the levels are -150, -50, +50 and +150 mV, so the thresholds are -100, 0 and +100 mV.

### Where it sits

In [rx_decision](rx_decision.md), 24 instances:

- `vinp` / `vinn`: the front end's output, the same for all 24.
- `vthp` / `vthn`: the reference for this slicer, driven by [dfe1_unrolled_hr](dfe1_unrolled_hr.md).
- `clkp` / `clkn`: `clk14`. The 12 slicers of phase 1 have it connected swapped, so they sample on the falling edge.
- `voutp` / `voutn`: back to the DFE, which picks 3 of each phase's 12.

`rx_decision` uses the default parameters.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vinp`, `vinn` | input | The signal to slice |
| `vthp`, `vthn` | input | The threshold, as a differential voltage |
| `clkp`, `clkn` | input | Clock; the decision is taken at its rising zero crossing |
| `voutp`, `voutn` | output | The held decision, differential |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `offset` | 0 V | Input offset, allowed -5 mV to +5 mV |
| `t_risefall` | 5 ps | Output edge time |
| `t_delay` | 0 | Delay from clock to output |
| `v_commonmode` | 0.5 V | Output common mode |
| `vswing` | 300 mV | Output swing of each side, peak to peak |

The file's comment says these values are placeholders.

### What the model leaves out

- Noise: the header gives a noise budget, but the model is noiseless.
- Regeneration: the decision is instant and always clean, however small the input is. There is no metastability and no clock-to-output delay (`t_delay` is 0).
- Kickback onto the input and the threshold, and any input capacitance.
- The output common mode default (0.5 V) is not the 0.55 V the other CML cells use. The DFE reads only the difference, so the hierarchy is not affected.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- PAM4 levels at the input: -150, -50, +50, +150 mV (`slicer.va`, header)
- Thresholds: -100, 0, +100 mV (`slicer.va`, header)
- DFE shifts of the thresholds: plus or minus 12.82 mV and plus or minus 4.27 mV (`slicer.va`, header)
- Two phases at 14 GHz; 24 slicers in total (`slicer.va`, header)
- Offset at most 5 mV (`slicer.va`, header and the range of `offset`)
- Noise budget 3.367 mV rms (`slicer.va`, header)
- Output is one bit of a thermometer code: the three slicers of a set give 000, 001, 011 or 111 (`slicer.va`, header)
- CML slicer: differential input, threshold, clock and output (`slicer.va`, header)
- Output levels in the model, marked as placeholders: common mode 0.5 V, swing 300 mV, edge 5 ps (`slicer.va`, parameters `v_commonmode`, `vswing`, `t_risefall`)
- Time available to the DFE behind it: the selection happens half a clock period after the sample (`dfe1_unrolled_hr.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `slicer_<what>.svg` (or `.png`), and reference it from this page as `![slicer schematic](../img/slicer_<what>.svg)`.

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
