# cdr_pd_linear

| Field | Value |
|---|---|
| Owner (from git history) | Winy |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/cdr_pd_linear.va`](../../va/Clocking/cdr_pd_linear.va) |
| Used in | [rx_cdr](rx_cdr.md), once (`u_pd`) |
| Section | [Clocking](README.md) |

## Architecture

`cdr_pd_linear` is the phase detector of the receiver's clock recovery. It compares the incoming data with the 14 GHz clock and puts out a current that says how far, and in which direction, the clock is from where it should be. "Linear" means the output is proportional to the phase error, not just its sign.

The system needs it for the tracking step of [rx_cdr](rx_cdr.md): once the frequency loop has brought the VCO to 14 GHz, this detector's current is what keeps the clock locked to the data.

### How the model works

The file contains the top module `cdr_pd_linear` and four small helper modules. The top module only wires them. The file has no comments of its own, so this description is read from the wiring:

| Step | Helper | What it does |
|---|---|---|
| 1 | `delay_t3` | Delays the data by 17.857 ps |
| 2 | `mult_1` (`tdxor`) | Compares the data with its delayed copy: +0.3 V when they differ, -0.3 V when they are the same. This makes a pulse at every data transition |
| 3 | `mult_1` (`clkxor`) | Does the same with the in-phase and the quadrature clock. The result toggles at twice the clock rate |
| 4 | `delay_t3` twice | Delays that by `t18` (1.8 ps) and then by `dt4` (26.78 ps) |
| 5 | `mult_2` (`mixer`) | Multiplies the delayed clock signal by the data-transition pulses |
| 6 | `vi_converter` | Turns the product into the output current, 0.8755 mS |

### Where it sits

In [rx_cdr](rx_cdr.md):

- `vout_b` is the output of the analog front end, converted to single-ended by an ideal `diff2se` cell.
- `clk14_I` is the 14 GHz clock from [rx_clkgen](rx_clkgen.md), also through a `diff2se`.
- `clk14_Q` is that clock delayed a quarter period by the ideal `qdelay` cell. In the full design the top level sets that delay to three quarters of a period, so that the loop settles at this detector's intended lock point. See [Clock recovery](../../../../CHANGELOGS.md#clock-recovery-the-detector-and-the-loop-disagree-on-sign).
- `vi_ou` is connected to the loop's `vctl` node, where [loop_filter_rc](loop_filter_rc.md) turns the current into the VCO control voltage.

The three helper cells are described on the [glue](glue.md) page.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vout_b` | input | Data, single-ended around 0 V |
| `clk14_I` | input | 14 GHz clock, in phase, single-ended around 0 V |
| `clk14_Q` | input | 14 GHz clock, a quarter period later |
| `vi_ou` | output | Output current, into the loop filter node |

There are no supply pins; the helpers use an internal ground.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `t18` | 1.8 ps | First delay on the clock path |
| `dt4` | 26.78 ps | Second delay on the clock path |

Two more values are written in the instance lines: the data delay `t3` = 17.857 ps and the gain `g` = 0.8755 mS.

### What the model leaves out

- `mult_1` compares its inputs with 0 V, so the detector sees only the sign of the PAM4 data, not its four levels.
- The delays, the multiplier and the current source are ideal: no bandwidth limit, no offset, no noise, and the output current has no compliance limit.
- The file does not explain how `t18`, `dt4` and `g` were chosen.

Existing testbench: [`test/cdr_pd_linear_test.sp`](../../test/cdr_pd_linear_test.sp).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Clock 14 GHz, in-phase and quadrature; the quadrature copy is a quarter period, 17.857 ps, later (`rx_cdr.va`, header and parameter `tq`)
- The architecture drawing has no quadrature clock source, so `rx_cdr` makes one with an ideal delay: where the real one comes from is open (`rx_cdr.va`, header)
- Inputs are read as single-ended signals around 0 V; the real data and clock are differential (`rx_cdr.va`, header)
- Output: a current into the loop filter node, gain 0.8755 mS in the model (`cdr_pd_linear.va`, `g`)
- Loop it works in: R = 2.352 kohm, C = 20 pF, C2 = 1 pF, 16.8 MHz CDR bandwidth, damping factor 1 (`rx_cdr.va`, header)
- Internal delays in the model: 17.857 ps on the data, 1.8 ps and 26.78 ps on the clock path (`cdr_pd_linear.va`, `t3`, `t18`, `dt4`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `cdr_pd_linear_<what>.svg` (or `.png`), and reference it from this page as `![cdr_pd_linear schematic](../img/cdr_pd_linear_<what>.svg)`.

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
