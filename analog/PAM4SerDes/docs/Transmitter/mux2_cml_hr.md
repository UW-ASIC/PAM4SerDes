# mux2_cml_hr

| Field | Value |
|---|---|
| Owner (from git history) | hdsouza13 |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/mux2_cml_hr.va`](../../va/Transmitter/mux2_cml_hr.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), five per path (two at level L4, three final multiplexers) |
| Section | [Transmitter](README.md) |

## Architecture

`mux2_cml_hr` is a differential 2:1 multiplexer in current-mode logic. While the clock is high it passes its EVEN input, while the clock is low its ODD input. The output therefore carries the two inputs one after the other, at twice their rate.

The system needs it for the two fastest steps of the serializer, where CMOS logic is no longer used: making the two 14 Gb/s streams, and the final step to 28 Gb/s. "hr" stands for half rate: the clock runs at half the output bit rate, and both of its levels are used.

### How the model works

- The clock chooses between the two inputs with a smooth switch (width `vsoft_clk`).
- Each data input is limited to plus or minus one (width `vsoft_data`).
- The result is delayed by `tpd`.
- A tail current `itail` is steered between two load resistors `rload` to `vdd`, with a capacitor `cout` on each leg. Unloaded, the output is plus or minus `itail * rload` and its common mode is `vdd - itail * rload / 2`.

The multiplexer is transparent. The header states the consequence: each input must remain stable throughout its selected half-cycle.

### Where it sits

In [tx_ser_ffe_path](tx_ser_ffe_path.md), five instances per path:

| Instances | Clock | Inputs | Output |
|---|---|---|---|
| `u_l4e`, `u_l4o` (level L4) | `clk7` | Two 7 Gb/s lanes each, from [cml_dff_x4](../Clocking/cml_dff_x4.md) | The even and the odd stream at 14 Gb/s, to [ffe_tapgen_hr](ffe_tapgen_hr.md) |
| `u_fin_pre`, `u_fin_main`, `u_fin_post` (final) | `clk14` | The even and the odd half of one tap, from [ffe_tapgen_hr](ffe_tapgen_hr.md) | That tap at 28 Gb/s, to a [predriver_cml](predriver_cml.md) |

### Ports

| Port | Direction | Carries |
|---|---|---|
| `de_p`, `de_n` | input | EVEN data, differential. A positive difference is a 1 |
| `do_p`, `do_n` | input | ODD data, differential |
| `clk_p`, `clk_n` | input | Differential clock: high selects EVEN, low selects ODD |
| `out_p`, `out_n` | output | Multiplexed data, CML |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `itail` | 1.5 mA | Total sink current per output pair |
| `rload` | 200 ohm | Load per leg to `vdd`. With `itail` the unloaded swing is 0.6 V peak-to-peak differential |
| `cout` | 5 fF | Capacitance per leg to `vss`; adds RC settling on top of `tpd` |
| `vsoft_data`, `vsoft_clk` | 10 mV, 10 mV | Switching widths of data and clock |
| `vos_data`, `vos_clk` | 0 V, 0 V | Differential offsets of data and clock |
| `tpd` | 5.934 ps | Transport delay. Marked "project estimate" |
| `max_step` | 0.5 ps | Simulation step bound, not a circuit property |

### What the model leaves out

- The header says the behavioural timing and electrical defaults are provisional.
- The tail current is a parameter. There is no bias input and no headroom limit.
- No jitter and no noise.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- 2 x 7 Gb/s to 14 Gb/s with a 7 GHz clock, and 2 x 14 Gb/s to 28 Gb/s with a 14 GHz clock (`mux2_cml_hr.va`, header)
- Clock high selects the EVEN input, clock low the ODD input (`mux2_cml_hr.va`, header)
- Each input must stay stable through the whole half-cycle in which it is selected (`mux2_cml_hr.va`, header)
- Unloaded output 0.6 V peak-to-peak differential: tail current 1.5 mA, load 200 ohm per leg (`mux2_cml_hr.va`, parameters `itail`, `rload`)
- Delay 5.934 ps, marked as a project estimate (`mux2_cml_hr.va`, parameter `tpd`)
- Output capacitance 5 fF per leg in the model (`mux2_cml_hr.va`, parameter `cout`)
- Timing and electrical defaults are provisional (`mux2_cml_hr.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `mux2_cml_hr_<what>.svg` (or `.png`), and reference it from this page as `![mux2_cml_hr schematic](../img/mux2_cml_hr_<what>.svg)`.

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
