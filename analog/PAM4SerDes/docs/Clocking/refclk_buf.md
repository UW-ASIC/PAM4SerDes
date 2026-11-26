# refclk_buf

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/refclk_buf.va`](../../va/Clocking/refclk_buf.va) |
| Used in | `pam4_serdes` (top level), twice: `u_ref_tx` and `u_ref_rx` |
| Section | [Clocking](README.md) |

## Architecture

`refclk_buf` receives the external 437.5 MHz reference clock, which arrives as a differential pair, and drives a rail-to-rail CMOS copy of it.

The system needs it because the cells that use the reference, the phase-frequency detector and the lock detector, read a single-ended CMOS clock. There are two instances: one for the transmitter's PLL and one for the receiver's CDR.

### How the model works

- The input pair is terminated with `rterm` between the two pins.
- A comparator with offset `vos` and hysteresis `vhys` decides when the input has crossed.
- Each output edge comes `tpd` after the input crossing, plus a random amount with standard deviation `rj`.
- The output edge is a straight ramp of length `trf` between `vss` and `vdd`, driven through `rout`.

### Where it sits

Both instances are in the top level `pam4_serdes`:

| Instance | Input pins | Output goes to |
|---|---|---|
| `u_ref_tx` | `refclk_tx_p`, `refclk_tx_n` | `ckref` of [tx_pll](tx_pll.md) |
| `u_ref_rx` | `refclk_rx_p`, `refclk_rx_n` | `ckref` of [rx_cdr](rx_cdr.md) |

The top level sets `rj` to 100 fs times its `rj_scale` parameter and gives the two instances different jitter seeds (1 and 11).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin_p`, `ckin_n` | input | Differential 437.5 MHz reference from the pads |
| `ckref` | output | The same clock as single-ended CMOS, 0 V to `vdd` |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `rterm` | 100 ohm | Differential input termination |
| `vos` | 0 V | Receiver offset, range -0.1 to +0.1 V |
| `vhys` | 20 mV | Receiver hysteresis, full width |
| `tpd` | 50 ps | Delay from input threshold crossing to output 50 % |
| `trf` | 30 ps | Output edge duration, 0 to 100 % |
| `rj` | 100 fs | Added random jitter per edge, rms |
| `rj_seed` | 1 | Seed of the jitter sequence |
| `rout` | 100 ohm | Output driver resistance |

### What the model leaves out

- The jitter is one independent random draw per edge. There is no supply-induced or low-frequency jitter.
- The input has no common-mode range: only the difference between the two pins is read.
- Delay and edge time are fixed numbers. They do not depend on load, supply or input slope.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Input: the external 437.5 MHz reference, differential (`refclk_buf.va`, header)
- Output: a rail-to-rail CMOS copy of it (`refclk_buf.va`, header)
- Differential input termination 100 ohm (`refclk_buf.va`, parameter `rterm`)
- Added random jitter 100 fs rms per edge (`refclk_buf.va`, parameter `rj`)
- Delay 50 ps from input crossing to output 50 %, output edge 30 ps (`refclk_buf.va`, parameters `tpd`, `trf`)
- Input hysteresis 20 mV full width; offset range studied -0.1 to +0.1 V (`refclk_buf.va`, parameters `vhys`, `vos`)
- Output driver resistance 100 ohm (`refclk_buf.va`, parameter `rout`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `refclk_buf_<what>.svg` (or `.png`), and reference it from this page as `![refclk_buf schematic](../img/refclk_buf_<what>.svg)`.

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
