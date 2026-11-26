# glue

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | glue (ideal wiring cells) |
| Model | [`va/Clocking/cdr_glue.va`](../../va/Clocking/cdr_glue.va) and [`va/Clocking/diff2se.va`](../../va/Clocking/diff2se.va) |
| Used in | [rx_cdr](rx_cdr.md): `diff2se` twice, `qdelay` once, `nor2` once; [tx_top](../Transmitter/tx_top.md): `diff2se` once |
| Section | [Clocking](README.md) |

## Architecture

This page covers three small cells that the model's headers call **ideal glue**. They stand for wiring or trivial logic that is not drawn as a block, so they add no non-ideal behaviour.

| Cell | File | What it does |
|---|---|---|
| `diff2se` | `va/Clocking/diff2se.va` | Differential to single-ended: `V(out) = V(p) - V(n)` |
| `qdelay` | `va/Clocking/cdr_glue.va` | A pure delay, a quarter of the 14 GHz period by default |
| `nor2` | `va/Clocking/cdr_glue.va` | An ideal NOR gate: `y = vdd * (1 - a) * (1 - b)`, with `a` and `b` scaled to 0..1 |

They exist because two of the team's blocks expect inputs that the blocks around them do not provide:

- [cdr_pd_linear](cdr_pd_linear.md) and [phase_aligner](phase_aligner.md) read single-ended signals around 0 V. The data and clocks they watch are differential. `diff2se` bridges that.
- `cdr_pd_linear` needs a quadrature copy of the 14 GHz clock. The architecture drawing the headers refer to (`Detailed.png`) has no quadrature source, so `qdelay` makes one by delaying the clock a quarter period.
- `nor2` makes the charge-pump enable of the receiver's frequency loop.

`diff2se` was moved to its own file during integration, unchanged, so that `tx_top` can include it without the other two cells.

### Where it sits

| Parent | Instance | Cell | Role |
|---|---|---|---|
| [rx_cdr](rx_cdr.md) | `u_dse` | `diff2se` | Analog front end output to `cdr_pd_linear`'s data input |
| [rx_cdr](rx_cdr.md) | `u_cse` | `diff2se` | `clk14_p/n` to `cdr_pd_linear`'s in-phase clock |
| [rx_cdr](rx_cdr.md) | `u_q` | `qdelay` | In-phase clock to quadrature clock |
| [rx_cdr](rx_cdr.md) | `u_en` | `nor2` | `lock`, `force_lock` to the [charge_pump](charge_pump.md) enable |
| [tx_top](../Transmitter/tx_top.md) | `u_pa` | `diff2se` | MSB path's retimed 7 Gb/s lane 0 to `phase_aligner`'s data input |

### Ports

| Cell | Port | Direction | Carries |
|---|---|---|---|
| `diff2se` | `p`, `n` | input | Differential signal |
| `diff2se` | `out` | output | The difference, relative to `vss` |
| `diff2se` | `vss` | inout | Ground |
| `qdelay` | `in` | input | Signal to delay |
| `qdelay` | `out` | output | The same signal, `td` later |
| `qdelay` | `vss` | inout | Ground |
| `nor2` | `a`, `b` | input | Logic inputs, 0 V to `vdd` |
| `nor2` | `y` | output | NOR of the inputs |
| `nor2` | `vdd`, `vss` | inout | Supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `td` (of `qdelay`) | 17.857 ps | Delay: a quarter of the 14 GHz period. `rx_cdr` passes its `tq` |

`diff2se` and `nor2` have no parameters.

### What the model leaves out

Everything: these cells are exact by design. A real differential-to-single-ended stage has gain, delay and offset; a real quadrature clock has a phase error; a real gate has delay.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

These three cells are ideal stand-ins. For each one, first decide whether the real circuit needs a cell there at all, and record that decision here. The headers give the reason each exists: the two detectors read single-ended signals, and the architecture drawing has no quadrature clock source.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- `qdelay`: a quarter of the 14 GHz period, 17.857 ps (`cdr_glue.va`, parameter `td`)
- `nor2`: pump enable = NOT (`lock` OR `force_lock`) (`rx_cdr.va`, header)
- `diff2se`: the detectors behind it read single-ended signals around 0 V; the data and clocks they watch are differential (`diff2se.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `glue_<what>.svg` (or `.png`), and reference it from this page as `![glue schematic](../img/glue_<what>.svg)`.

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
