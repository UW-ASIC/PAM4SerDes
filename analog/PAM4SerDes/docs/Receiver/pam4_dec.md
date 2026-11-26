# pam4_dec

| Field | Value |
|---|---|
| Owner (from git history) | Kayhan Baig |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/pam4_dec.va`](../../va/Receiver/pam4_dec.va) |
| Used in | [rx_decision](rx_decision.md), twice (`dec0`, `dec1`: one per phase) |
| Section | [Receiver](README.md) |

## Architecture

`pam4_dec` is a small piece of logic. It takes the three decisions of one sampling phase, a thermometer code, and turns them into the two bits of the PAM4 symbol.

The system needs it because three slicers give three bits for what is really a 2-bit value. The decoder also undoes the Gray coding of the transmitter, so its outputs are the two PRBS bits that were sent.

### How the model works

Inputs A, B and C are the decisions at the -100 mV, 0 mV and +100 mV thresholds.

```
MSB = B
LSB = A XOR C
```

| Level | A | B | C | MSB | LSB |
|---|---|---|---|---|---|
| -3 | 0 | 0 | 0 | 0 | 0 |
| -1 | 1 | 0 | 0 | 0 | 1 |
| +1 | 1 | 1 | 0 | 1 | 1 |
| +3 | 1 | 1 | 1 | 1 | 0 |

The block is combinational: no clock. Codes that should not occur (for example A = 0 with B = 1) simply give whatever the two equations give.

### Where it sits

In [rx_decision](rx_decision.md), one per phase, after the selection in [dfe1_unrolled_hr](dfe1_unrolled_hr.md) and before [rx_dec_retime](rx_dec_retime.md). The header gives the same placement rule: after the hypothesis selection, before the decision retiming.

The DFE's outputs are differential and this block reads single-ended logic. `rx_decision` therefore connects the positive leg of each pair and sets the threshold to the pair's common mode, `vdd` - 0.15 V. It sets the output high level to `vdd`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `a`, `b`, `c` | input | Decisions at the -100, 0 and +100 mV thresholds, as logic levels |
| `msb`, `lsb` | output | The symbol's two bits |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vlow`, `vhigh` | 0 V, 1.8 V | Output levels. `rx_decision` sets `vhigh` = 0.7 V |
| `vth` | 0.9 V | Input threshold. `rx_decision` sets `vdd` - 0.15 V |
| `tdelay` | 0 | Output delay |
| `trise`, `tfall` | 1 ps, 1 ps | Output edge times |

### What the model leaves out

The header lists it: no clock, no latching, no noise, no metastability, no loading and no supply current. There is no hysteresis on the inputs, and no bubble correction for invalid codes.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Inputs A, B, C: the decisions at the -100, 0 and +100 mV thresholds (`pam4_dec.va`, header)
- Valid codes ABC = 000, 100, 110, 111 map to MSB/LSB = 00, 01, 11, 10 (`pam4_dec.va`, header)
- Logic: MSB = B, LSB = A XOR C (`pam4_dec.va`, code)
- Invalid codes are not corrected: no bubble correction (`pam4_dec.va`, header)
- Combinational; placed after the DFE's selection and before the decision retiming (`pam4_dec.va`, header)
- One per phase, so each works at 14 GBd (`rx_decision.va`, header)
- Levels in the hierarchy: input threshold `vdd` - 0.15 V (it reads one leg of a CML pair), output 0 to 0.7 V (`rx_decision.va`, header and instance lines)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `pam4_dec_<what>.svg` (or `.png`), and reference it from this page as `![pam4_dec schematic](../img/pam4_dec_<what>.svg)`.

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
