# div2_tspc

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/div2_tspc.va`](../../va/Clocking/div2_tspc.va) |
| Used in | [tx_clkgen](tx_clkgen.md), three times (`u_d3p5`, `u_d1p75`, `u_d0p875`); [rx_clkgen](rx_clkgen.md), twice (`u_d1p75`, `u_d0p875`) |
| Section | [Clocking](README.md) |

## Architecture

`div2_tspc` halves the frequency of a CMOS clock. The header names the logic style: true single-phase clock (TSPC), which needs only one clock wire.

The system needs it for the slower part of both clock trees. Below 7 GHz the clocks are CMOS, and a chain of these dividers makes 3.5, 1.75 and 0.875 GHz for the lower levels of the serializer and the deserializer.

### How the model works

- The output toggles on the **falling** edge of the clock.
- `rst` high forces `q` low and keeps it there; the divider does not toggle while `rst` is high.
- `q` and `qb` are complementary. Each edge comes `tpd_r` or `tpd_f` after the clock edge, plus random jitter `rj`, as a straight ramp of length `trf`, driven through `rout`.
- If a clock period falls outside 1/`fmax` .. 1/`fmin` the model prints a warning.

### Where it sits

| Parent | Instance | Step |
|---|---|---|
| [tx_clkgen](tx_clkgen.md) | `u_d3p5` | Aligned 7 GHz (from [phase_aligner](phase_aligner.md)) to 3.5 GHz. Its `qb` is used as `clk3p5b` |
| [tx_clkgen](tx_clkgen.md) | `u_d1p75` | 3.5 to 1.75 GHz |
| [tx_clkgen](tx_clkgen.md) | `u_d0p875` | 1.75 to 0.875 GHz |
| [rx_clkgen](rx_clkgen.md) | `u_d1p75` | 3.5 GHz (from [cml2cmos](cml2cmos.md)) to 1.75 GHz |
| [rx_clkgen](rx_clkgen.md) | `u_d0p875` | 1.75 to 0.875 GHz |

Both parents set `rj` to 300 fs times `rj_scale` and give every instance its own seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | CMOS clock in |
| `rst` | input | Reset, active high |
| `q`, `qb` | output | Clock at half the frequency and its complement, CMOS |
| `vdd`, `vss` | inout | 0.7 V core supply and ground. The input threshold is half the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `tpd_r` | 30 ps | Delay from clock 50 % to rising `q` 50 % |
| `tpd_f` | 30 ps | Delay from clock (or `rst`) 50 % to falling `q` 50 % |
| `trf` | 25 ps | Output edge duration, 0 to 100 % |
| `rj` | 300 fs | Added random jitter per output edge, rms |
| `rj_seed` | 3 | Seed of the jitter sequence; every instance needs its own |
| `rout` | 100 ohm | Output driver resistance, 0 for an ideal source |
| `fmin`, `fmax` | 743.75 MHz, 8.05 GHz | Specified clock frequency range |

### What the model leaves out

- The frequency range only produces warnings; the divider does not fail outside it.
- The delays are fixed numbers. They do not depend on load, supply or input slope.
- The jitter is one independent random draw per output edge.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Specified clock range 743.75 MHz to 8.05 GHz (`div2_tspc.va`, parameters `fmin`, `fmax`)
- Steps used today: 7 to 3.5, 3.5 to 1.75 and 1.75 to 0.875 GHz (`div2_tspc.va`, header; `tx_clkgen.va`; `rx_clkgen.va`)
- Added random jitter 300 fs rms per output edge (`div2_tspc.va`, parameter `rj`)
- Delay 30 ps from clock 50 % to output 50 %, rising and falling; output edge 25 ps (`div2_tspc.va`, parameters `tpd_r`, `tpd_f`, `trf`)
- True single-phase clock (TSPC) logic (`div2_tspc.va`, header)
- Active-high reset that forces `q` low; complementary outputs `q` and `qb` (`div2_tspc.va`, code)
- Output driver resistance 100 ohm (`div2_tspc.va`, parameter `rout`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `div2_tspc_<what>.svg` (or `.png`), and reference it from this page as `![div2_tspc schematic](../img/div2_tspc_<what>.svg)`.

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
