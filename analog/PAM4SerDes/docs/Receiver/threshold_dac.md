# threshold_dac

| Field | Value |
|---|---|
| Owner (from git history) | Justin Fang |
| Kind | leaf (behavioural model), not instantiated yet |
| Model | [`va/Receiver/Slicer/threshold_dac.va`](../../va/Receiver/Slicer/threshold_dac.va) |
| Used in | Not in the hierarchy yet. Instantiated three times in [pam4_slicer](pam4_slicer.md), which is itself not instantiated |
| Section | [Receiver](README.md) |

## Architecture

`threshold_dac` turns a 6-bit code into one threshold voltage for one slicer. Every slicer is meant to get its own copy, set to the code nearest to the threshold it needs.

**This block is not in the hierarchy yet.** In the present models the DFE block, [dfe1_unrolled_hr](dfe1_unrolled_hr.md), drives all 24 slicer references itself, as ideal voltages. The DAC is used only inside [pam4_slicer](pam4_slicer.md), which is not instantiated either.

The 24 thresholds are all different: three nominal values, each shifted by one of four small amounts for the DFE. The DFE model produces those voltages as ideal sources. In a circuit they have to come from somewhere, and this DAC is the block written for that.

### How the model works

```
vth = vmin + code * (vmax - vmin) / 64
```

and the two outputs sit at `v_commonmode` plus and minus half of `vth`.

With the defaults one step is about 5.2 mV. Code 32 gives exactly 0 mV. The header notes that plus or minus 100 mV cannot be hit exactly; [pam4_slicer](pam4_slicer.md) uses codes 51 and 13, which come to about plus and minus 98.9 mV.

### Where it sits

Nowhere in the simulated hierarchy today. The nodes it is written for are the `vthp` / `vthn` inputs of the [slicer](slicer.md)s, which [dfe1_unrolled_hr](dfe1_unrolled_hr.md) drives at present.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vthp`, `vthn` | output | The threshold, as a differential voltage around `v_commonmode` |

There are no inputs: the code is a parameter.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `code` | 32 | Which of the 64 settings to use, 0 to 63 |
| `vmin`, `vmax` | -0.1666 V, +0.1666 V | Ends of the output range |
| `v_commonmode` | 0.5 V | Midpoint of the output pair |

### What the model leaves out

- The code is a fixed parameter. The file's comment marks this as a placeholder: how the code gets set is still to be asked.
- The steps are perfectly even: no nonlinearity, no noise, no settling time, no output resistance.
- The block prints the code and the threshold with `$strobe`.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Range -166.6 mV to +166.6 mV, 6 bits, 64 settings (`threshold_dac.va`, header)
- One DAC per slicer, set to the code closest to the threshold that slicer needs (`threshold_dac.va`, header)
- With this range and resolution it reaches 0 mV exactly but not plus or minus 100 mV exactly (`threshold_dac.va`, header)
- The thresholds to reach: -100, 0, +100 mV, each shifted by the DFE by plus or minus 12.82 mV or plus or minus 4.27 mV (`slicer.va`, header)
- 24 slicers need a threshold each (`slicer.va`, header)
- How the code gets set is open: the file's comment says to ask the lead (`threshold_dac.va`, comment on `code`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `threshold_dac_<what>.svg` (or `.png`), and reference it from this page as `![threshold_dac schematic](../img/threshold_dac_<what>.svg)`.

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
