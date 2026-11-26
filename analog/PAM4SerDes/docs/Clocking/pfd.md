# pfd

| Field | Value |
|---|---|
| Owner (from git history) | GreenBlueFish |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/pfd.va`](../../va/Clocking/pfd.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_pfd`); [rx_cdr](rx_cdr.md), once (`u_pfd`) |
| Section | [Clocking](README.md) |

## Architecture

`pfd` is a phase-frequency detector. It looks at the rising edges of two clocks, the reference and the feedback clock, and says which one is ahead:

- `up` is high while the reference is ahead,
- `dn` is high while the feedback clock is ahead.

The system needs it to steer a loop. The charge pump turns `up` and `dn` into current, the loop filter turns that into a control voltage, and the VCO speeds up or slows down until the two clocks line up. Because it reacts to frequency as well as phase, it can pull a loop in from far away.

### How the model works

Two flip-flops. A rising edge on `ref` sets `up`; a rising edge on `fb` sets `dn`. When both are set, a reset fires `td_rst` later and clears both. So in lock both outputs pulse together for `td_rst` each cycle.

### Where it sits

- In [tx_pll](tx_pll.md) it compares `ckref` (437.5 MHz) with the VCO clock divided by 32. Its outputs drive the [charge_pump](charge_pump.md).
- In [rx_cdr](rx_cdr.md) it does the same job during frequency acquisition. After lock the charge pump behind it is switched off and [cdr_pd_linear](cdr_pd_linear.md) takes over.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ref` | input | Reference clock, CMOS |
| `fb` | input | Feedback (divided) clock, CMOS |
| `up` | output | High while `ref` is ahead; 0 V to `vdd` |
| `dn` | output | High while `fb` is ahead; 0 V to `vdd` |
| `vdd`, `gnd` | input | Supply and ground. Note the name `gnd`: most other cells call it `vss` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth` | 0.5 V | Clock threshold for an edge. Both parents set 0.35 V |
| `td_rst` | 50 ps | Reset delay (dead zone) |
| `t_rf` | 0 | Output rise and fall time |

### What the model leaves out

- No jitter or noise.
- The inputs have no hysteresis; an edge is a single threshold crossing.
- The outputs switch with `t_rf`, which is 0 by default.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Compares two CMOS clocks at the reference rate, 437.5 MHz (`tx_pll.va`, header)
- Input threshold 0.35 V, set by both parents; the cell's own default is 0.5 V (`tx_pll.va` and `rx_cdr.va`, parameter `vth`)
- Reset delay 50 ps, described as the dead zone (`pfd.va`, parameter `td_rst`)
- `up` and `dn` swing between `gnd` and `vdd` (`pfd.va`, output equations)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `pfd_<what>.svg` (or `.png`), and reference it from this page as `![pfd schematic](../img/pfd_<what>.svg)`.

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
