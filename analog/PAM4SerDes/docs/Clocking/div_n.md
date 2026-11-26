# div_n

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/div_n.va`](../../va/Clocking/div_n.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_div`); [rx_cdr](rx_cdr.md), once (`u_div`) |
| Section | [Clocking](README.md) |

## Architecture

`div_n` is the feedback divider of a loop. It counts the rising edges of the 14 GHz VCO clock and puts out one cycle for every `n` of them. With `n` = 32 the output is at the reference rate, 437.5 MHz.

The system needs it because the phase-frequency detector compares two clocks at the same rate. Dividing the VCO by 32 is what makes the loop multiply the reference by 32.

### How the model works

- The input is single-ended. It is compared with a threshold at `vth_frac` of the supply, plus `vos`, with hysteresis `vhys`.
- A counter counts rising edges from 0 to `n` - 1. The output is high during the second half of the count, so the duty cycle is 50 % for an even `n`.
- Each output edge comes `tpd` after the input edge that caused it, plus random jitter `rj`, and is a straight ramp of length `trf`, driven through `rout`.
- If an input period falls outside 1/`fmax` .. 1/`fmin` the model prints a warning. It keeps dividing.

### Where it sits

In [tx_pll](tx_pll.md) and in [rx_cdr](rx_cdr.md): the input is the VCO output `ck`, the output is `ckfb`, which goes to [pfd](pfd.md) and [lock_detect](lock_detect.md). Each parent gives its instance its own jitter seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin` | input | VCO clock, single-ended CMOS, 14 GHz |
| `ckout` | output | Divided clock, CMOS, 437.5 MHz with `n` = 32 |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `n` | 32 | Division ratio, 2 to 1023 |
| `vth_frac` | 0.5 | Input threshold as a fraction of the supply |
| `vos` | 0 V | Input-referred offset, added to the threshold |
| `vhys` | 10 mV | Input hysteresis, full width |
| `tpd` | 150 ps | Delay from input crossing to output 50 % |
| `trf` | 30 ps | Output edge duration, 0 to 100 % |
| `rj` | 150 fs | Added random jitter per output edge, rms. The top level scales it with `rj_scale` |
| `rj_seed` | 2 | Seed of the jitter sequence; every instance needs its own |
| `rout` | 100 ohm | Output driver resistance, 0 for an ideal source |
| `fmin`, `fmax` | 11.9 GHz, 16.1 GHz | Specified input frequency range |

### What the model leaves out

- It is a counter, not a chain of divider stages. Nothing about the internal structure (how many stages, which logic style) is modelled.
- The frequency range only produces warnings; the divider does not fail outside it.
- The jitter is one independent random draw per output edge.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Divide the 14 GHz VCO clock by 32 to 437.5 MHz (`div_n.va`, header)
- Specified input range 11.9 to 16.1 GHz (`div_n.va`, parameters `fmin`, `fmax`)
- Single-ended rail-to-rail input, threshold at half the supply (`div_n.va`, header and parameter `vth_frac`)
- Added random jitter 150 fs rms per output edge (`div_n.va`, parameter `rj`)
- Delay 150 ps from input crossing to output 50 %, output edge 30 ps (`div_n.va`, parameters `tpd`, `trf`)
- Input hysteresis 10 mV; output driver resistance 100 ohm (`div_n.va`, parameters `vhys`, `rout`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `div_n_<what>.svg` (or `.png`), and reference it from this page as `![div_n schematic](../img/div_n_<what>.svg)`.

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
