# vga

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/vga.va`](../../va/Receiver/vga.va) |
| Used in | [rx_afe](rx_afe.md), once (`u_vga`) |
| Section | [Receiver](README.md) |

## Architecture

`vga` is the variable-gain amplifier, the last cell of the analog front end. Its gain is set by a control voltage.

The system needs it because the slicers compare the signal with fixed thresholds. The amplitude that arrives depends on the channel, so something has to bring it to the size the thresholds were chosen for. That is this block's job.

### How the model works

- The gain in dB is a straight line in `vctrl`: `min_gain_db` at `v_min`, `max_gain_db` at `v_max`. Outside that range the control voltage is clamped.
- One pole at `fp`.
- The differential output is clipped hard at plus or minus `vout_limit`.
- The two outputs are driven around a fixed common mode.
- Each input has a resistor `r_in` to ground. The code comment gives the reason: the CTLE in front drives only a differential voltage, so without it the input common mode would have no DC path.

Both default gains are below 0 dB, so with the defaults the block attenuates.

### Where it sits

In [rx_afe](rx_afe.md), after the [ctle](ctle.md). Its output is the front end's output: it drives the 24 slicers in [rx_decision](rx_decision.md) and the phase detector in [rx_cdr](../Clocking/rx_cdr.md).

`rx_afe` sets the control range to 0 .. 0.7 V and the output common mode to 0.55 V.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in_p`, `in_n` | input | Signal from the CTLE |
| `vctrl` | input | Gain control voltage |
| `out_p`, `out_n` | output | Amplified signal around the common mode |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `min_gain_db` | -4.703 dB | Gain at `vctrl` = `v_min` |
| `max_gain_db` | -1.847 dB | Gain at `vctrl` = `v_max` |
| `v_min`, `v_max` | 0 V, 1.0 V | Control voltage range. `rx_afe` sets 0 and 0.7 V |
| `common_mode` | 0.9 V | Output common mode. `rx_afe` sets 0.55 V |
| `fp` | 39.16 GHz | Pole frequency |
| `vout_limit` | 0.2 V | Largest differential output, either sign |
| `r_in` | 1 Gohm | Resistance from each input to ground |
| `r_out` | 0 | Declared, but not used in the model |

### What the model leaves out

- No noise and no offset.
- The outputs are ideal voltage sources: the 24 slicers behind them do not load the block.
- The clipping is a hard limit, not a gradual compression.
- Gain control is a continuous voltage; the `g[5:0]` code is not modelled.
- The block prints its output voltage at every time step with `$strobe`.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Gain range -4.703 dB to -1.847 dB (`vga.va`, parameters `min_gain_db`, `max_gain_db`)
- Control voltage 0 to 0.7 V in the hierarchy; the cell's own default range is 0 to 1 V (`rx_afe.va`, header)
- The gain is meant to be set by a `g[5:0]` code, which is not modelled yet (`rx_afe.va`, header)
- Bandwidth: one pole at 39.16 GHz (`vga.va`, parameter `fp`)
- Output limited to plus or minus 0.2 V differential (`vga.va`, parameter `vout_limit`)
- Output common mode 0.55 V in the hierarchy; the cell's own default of 0.9 V is above the 0.7 V supply (`rx_afe.va`, header)
- Levels expected at its output, the slicer inputs: plus or minus 150 mV and plus or minus 50 mV (`slicer.va`, header)
- Loads: 24 slicers and the CDR phase detector (`rx_afe.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `vga_<what>.svg` (or `.png`), and reference it from this page as `![vga schematic](../img/vga_<what>.svg)`.

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
