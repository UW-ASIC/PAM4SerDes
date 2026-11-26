# loop_filter_rc

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/loop_filter_rc.va`](../../va/Clocking/loop_filter_rc.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_lf`); [rx_cdr](rx_cdr.md), once (`u_lf`) |
| Section | [Clocking](README.md) |

## Architecture

`loop_filter_rc` is the passive loop filter of the PLL and of the CDR. The charge pump pushes current pulses into it, and it turns them into the smooth control voltage that sets the VCO frequency.

The circuit in the model is two elements:

- a resistor `R` from the pin `vctrl` to an internal node `n1`,
- a capacitor `C` from `n1` to `vss`.

The capacitor integrates the current (this is what makes the loop type II) and the resistor adds the zero that keeps the loop stable.

### Where it sits

- In [tx_pll](tx_pll.md): on the `vctl` node, with R = 25.31 kohm and C = 1.427 pF.
- In [rx_cdr](rx_cdr.md): on the shared `vctl` node, with R = 2.352 kohm and C = 20 pF.

Both parents add the shunt capacitor C2 themselves (0.14 pF and 1 pF), because this cell is R + C only.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vctrl` | inout | The loop's control node: charge-pump current in, control voltage out |
| `vss` | inout | Ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `R` | 25.31 kohm | Series resistor. `rx_cdr` sets 2.352 kohm |
| `C` | 1.427 pF | Integrating capacitor. `rx_cdr` sets 20 pF |

### What the model leaves out

- The shunt capacitor C2 (added by the parents, see above).
- Resistor noise and capacitor leakage.
- The header carries an open note from the author: "Need to confirm Vctrl output node", that is, whether the control voltage is taken at the charge-pump node or at the internal node.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Transmitter PLL: R = 25.31 kohm, C = 1.427 pF, C2 = 0.14 pF, for a type-II loop with damping factor 1 and 21.875 MHz bandwidth at 100 uA pump current (`tx_pll.va`, header)
- Receiver CDR: R = 2.352 kohm, C = 20 pF, C2 = 1 pF, for 16.8 MHz CDR bandwidth and damping factor 1 (`rx_cdr.va`, header)
- C2 is not in this cell today: each parent adds it from `vctl` to `vss` (`tx_pll.va` and `rx_cdr.va`, header)
- Open point from the model: which node is the control voltage output, the charge-pump node or the internal node (`loop_filter_rc.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `loop_filter_rc_<what>.svg` (or `.png`), and reference it from this page as `![loop_filter_rc schematic](../img/loop_filter_rc_<what>.svg)`.

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
