# dfe1_unrolled_hr

| Field | Value |
|---|---|
| Owner (from git history) | deaconsham |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/dfe1_unrolled_hr.va`](../../va/Receiver/dfe1_unrolled_hr.va) |
| Used in | [rx_decision](rx_decision.md), once (`dfe`) |
| Section | [Receiver](README.md) |

## Architecture

`dfe1_unrolled_hr` is the decision feedback equalizer (DFE): one tap, unrolled, half rate.

The system needs a DFE because, even after the CTLE, each symbol leaves an echo in the next one. The header writes the received signal as

```
r[n] = x[n] + alpha * x[n-1]
```

where x[n] is the symbol that was sent and `alpha` is the size of the echo. A DFE removes the echo by using the decision it has already made about x[n-1].

The direct way, subtracting `alpha * x[n-1]` from the input before slicing, needs the previous decision to be ready and fed back within one symbol period, a tight loop at 28 GBd. **Unrolling** avoids that loop. The slicers compare the input against thresholds that are already shifted for every value the previous symbol could have had, all at once, and this block chooses afterwards which comparison was the right one.

### How the model works

The block does two things.

**1. It drives the 24 slicer references.** For slicer g:

```
ref[g] = T_k + alpha * L_h
T_k = {-1, 0, +1} * v_thr              the three PAM4 thresholds
L_h = {-3, -1, +1, +3} * v_level       the four values the previous symbol could have had
g   = 12 * phase + 3 * h + k
```

**2. It selects.** For each phase it picks the 3 slicer outputs ("candidates") whose hypothesis h equals the level the other phase decided one unit interval earlier. Those 3 bits are that phase's thermometer code, and their sum is the level it hands to the other phase.

The timing makes this safe: phase 0 samples on the rising clock edge and is resolved on the falling edge, reading phase 1's level. Phase 1 samples on the falling edge and is resolved on the rising edge, reading phase 0's level. So each selection reads a value that is not changing at that moment.

### Where it sits

In [rx_decision](rx_decision.md):

- `ref_p/n[0:23]` go to the threshold inputs of the 24 [slicer](slicer.md)s.
- `cand_p/n[0:23]` come back from the slicer outputs.
- `therm_p/n[0:5]`, three bits per phase, go to the two [pam4_dec](pam4_dec.md).
- The clock is `clk14` from [rx_clkgen](../Clocking/rx_clkgen.md).

`rx_decision` sets `vdd` to 0.7 V and passes `alpha`, `v_level` and `v_thr`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk_p`, `clk_n` | input | 14 GHz CML clock |
| `cand_p[0:23]`, `cand_n[0:23]` | input | The 24 slicer decisions. Positive means the input is above that slicer's reference |
| `ref_p[0:23]`, `ref_n[0:23]` | output | The 24 slicer references, as differential voltages |
| `therm_p[0:5]`, `therm_n[0:5]` | output | Thermometer code: index 3 x phase + k, at -`v_thr`, 0, +`v_thr` |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 1.0 V | Supply the output levels follow. `rx_decision` sets 0.7 V |
| `v_swing` | 0.3 V | Swing of each output leg |
| `v_cm` | `vdd` - `v_swing`/2 | Common mode of the references and of the outputs |
| `alpha` | 0.08548 | The tap: first post-cursor / main cursor |
| `v_level` | 50 mV | PAM4 levels are -3, -1, +1, +3 times this |
| `v_thr` | 100 mV | Thresholds are -1, 0, +1 times this |
| `tt` | 10 ps | Output rise and fall time |
| `init_level` | 0 | Level assumed before the first symbol |

### What the model leaves out

- The references are ideal voltages. In a real receiver something has to generate 24 different thresholds; that is the job [threshold_dac](threshold_dac.md) is meant for.
- The selection is instant: no multiplexer delay, no setup time on the candidates.
- `alpha` is a fixed parameter. Nothing adapts it to the channel.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- One tap: received signal r[n] = x[n] + alpha * x[n-1], with alpha = 0.08548 (first post-cursor over main cursor) (`dfe1_unrolled_hr.va`, header and parameter `alpha`)
- 24 references, ref = T + alpha * L, with T = -100, 0, +100 mV and L = -150, -50, +50, +150 mV (`dfe1_unrolled_hr.va`, header and parameters `v_thr`, `v_level`)
- Half rate: two phases, each at 14 GBd (`dfe1_unrolled_hr.va`, header)
- Timing: phase 0 samples on the rising clock edge and is resolved on the falling edge; phase 1 samples on the falling edge and is resolved on the rising edge. Each selection therefore reads the other phase's result half a clock period after it was made (`dfe1_unrolled_hr.va`, header)
- Output: a 3-bit thermometer code per phase, at -100, 0 and +100 mV (`dfe1_unrolled_hr.va`, header)
- Output levels: each leg swings 0.3 V around `vdd` - 0.15 V, edges 10 ps in the model (`dfe1_unrolled_hr.va`, parameters `v_swing`, `v_cm`, `tt`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `dfe1_unrolled_hr_<what>.svg` (or `.png`), and reference it from this page as `![dfe1_unrolled_hr schematic](../img/dfe1_unrolled_hr_<what>.svg)`.

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
