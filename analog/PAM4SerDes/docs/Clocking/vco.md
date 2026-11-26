# vco

| Field | Value |
|---|---|
| Owner (from git history) | GreenBlueFish |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/vco.va`](../../va/Clocking/vco.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_vco`); [rx_cdr](rx_cdr.md), once (`u_vco`) |
| Section | [Clocking](README.md) |

## Architecture

`vco` is the oscillator. Its output frequency follows its control voltage:

```
f = f_0 + k_vco * (V(v_ctrl) - v_c0)
```

The system needs one in each loop: the transmitter PLL and the receiver CDR each steer their own `vco` to 14 GHz, and every other clock in that half of the chip is derived from it.

### How the model works

The frequency is integrated to a phase, and the output is a square wave that is high during the first half of each cycle. The output swings from 0 to `v_amp` with edges of length `t_rf`.

### Where it sits

- In [tx_pll](tx_pll.md): `v_ctrl` is the loop's `vctl` node; `v_out` is the PLL output `ck`, which goes to [tx_clkgen](tx_clkgen.md) and to the feedback divider [div_n](div_n.md).
- In [rx_cdr](rx_cdr.md): the same, with `ck` going to [rx_clkgen](rx_clkgen.md).

Both parents set `f_0` = 14 GHz, `v_c0` = 0.35 V and `k_vco` = 1.4 GHz/V. The cell's own defaults are different (see the table).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `v_ctrl` | input | Control voltage |
| `v_out` | output | Clock, single-ended, 0 V to `v_amp` |
| `vdd`, `gnd` | inout | Supply and ground. The model does not read `vdd`: the output level is the parameter `v_amp` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `f_0` | 5 GHz | Centre frequency. Both parents set 14 GHz |
| `v_c0` | 0 V | Control voltage that gives `f_0`. Both parents set 0.35 V |
| `k_vco` | 2 GHz/V | Tuning gain. Both parents set 1.4 GHz/V |
| `p_init` | 0 | Initial phase |
| `v_amp` | 0.7 V | Output high level |
| `t_rf` | 2 ps | Output rise and fall time (the comment notes that 0 stalls ngspice) |

### What the model leaves out

- Phase noise and jitter: the oscillator is noiseless.
- Any limit or curvature in the tuning: frequency is a straight line in the control voltage, at any voltage.
- Coarse tuning: the `tx_pll` header notes there is no `band[3:0]` input because this model has none yet.
- The output is a single-ended CMOS clock. The clock trees behind it are CML, so [dcc_cml](dcc_cml.md) makes the differential clock in the model.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- 14 GHz at a control voltage of 0.35 V (`tx_pll.va` and `rx_cdr.va`, parameters `f0`, `vctl0`)
- Tuning gain 1.4 GHz/V (`tx_pll.va` and `rx_cdr.va`, parameter `kvco`)
- Output in the present models: single-ended CMOS, 0 to 0.7 V (`vco.va`, parameter `v_amp`)
- Output edge 2 ps in the model (`vco.va`, parameter `t_rf`)
- The feedback divider behind it is specified for 11.9 to 16.1 GHz (`div_n.va`, parameters `fmin`, `fmax`)
- Coarse tuning (`band[3:0]`) does not exist yet (`tx_pll.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `vco_<what>.svg` (or `.png`), and reference it from this page as `![vco schematic](../img/vco_<what>.svg)`.

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
