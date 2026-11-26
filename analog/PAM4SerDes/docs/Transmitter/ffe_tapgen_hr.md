# ffe_tapgen_hr

| Field | Value |
|---|---|
| Owner (from git history) | hdsouza13 |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/ffe_tapgen_hr.va`](../../va/Transmitter/ffe_tapgen_hr.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), once per path (`u_tg`) |
| Section | [Transmitter](README.md) |

## Architecture

`ffe_tapgen_hr` makes the three taps of the transmitter's feed-forward equalizer (FFE). A three-tap FFE sends, for every bit, a weighted sum of that bit, the one before it and the one after it. For that the driver needs three copies of the data stream, each one unit interval later than the one before. This block makes those copies.

The system needs it because the channel smears each symbol into its neighbours. Subtracting a little of the neighbouring symbols at the transmitter undoes part of that.

It works at **half rate**: its inputs are the even and the odd bits of the stream, each at 14 Gb/s, and it never handles the 28 Gb/s stream itself. Each tap leaves as an even half and an odd half, and three [mux2_cml_hr](mux2_cml_hr.md) outside this block put the halves together.

### How the model works

Write the serial stream as x[0], x[1], x[2], ... The even input carries E[k] = x[2k], the odd input O[k] = x[2k+1].

- On each **rising** clock edge the block samples E and O. It then works out the three taps for the even position, x[2k], x[2k-1], x[2k-2], and for the odd position, x[2k+1], x[2k], x[2k-1], using the pair it stored one cycle earlier.
- The **odd** outputs are updated on the rising edge and the **even** outputs on the falling edge. This way each bank changes while the final multiplexer is looking at the other one.
- After this common latency the three serialized outputs are pre = x[n], main = x[n-1], post = x[n-2].
- `rst` high clears all stored bits, even when the clock is stopped.

The six outputs are plain CML pairs, all with the same swing. The tap **weights** and **signs** are not applied here: [tx_bias](../Biasing/tx_bias.md) sets the weights through the driver's tail currents, and [pam4_driver](pam4_driver.md) subtracts pre and post.

### Where it sits

In [tx_ser_ffe_path](tx_ser_ffe_path.md): its inputs are the even and odd 14 Gb/s streams from the two level-L4 [mux2_cml_hr](mux2_cml_hr.md), its clock is `clk14` from [tx_clkgen](../Clocking/tx_clkgen.md), and its six outputs go to the three final [mux2_cml_hr](mux2_cml_hr.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `de_p/n`, `do_p/n` | input | Even and odd data streams, 14 Gb/s each, CML |
| `clk_p`, `clk_n` | input | 14 GHz CML clock |
| `rst` | input | Reset, asynchronous, active high, relative to `vss` |
| `pre_e_p/n`, `pre_o_p/n` | output | Pre-cursor tap, even and odd half |
| `main_e_p/n`, `main_o_p/n` | output | Main tap, even and odd half |
| `post_e_p/n`, `post_o_p/n` | output | Post-cursor tap, even and odd half |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `itail` | 1.5 mA | Tail current per differential output pair |
| `rload` | 200 ohm | Load per leg to `vdd`. With `itail` the unloaded swing is 0.6 V peak-to-peak differential |
| `t_cq` | 2 ps | Delay from the stored state to the output, including reset |
| `tr`, `tf` | 2 ps, 2 ps | Output rise and fall time |
| `vth_data`, `vth_clk` | 0 V, 0 V | Differential thresholds. `vth_clk` should match the final multiplexer's `vos_clk` |
| `vth_rst` | 0.35 V | Reset threshold, relative to `vss`. Fixed: it does not track `vdd` |
| `init_bit` | 0 | Value of all stored bits at start-up and after reset |
| `ttol`, `vtol`, `max_step` | 1 fs, 1 uV, 0.5 ps | Simulation tolerances and step bound, not circuit properties |

### What the model leaves out

- Setup time, hold time and metastability are not modelled: the code comment says both inputs must be settled at the rising edge.
- No headroom model (code comment), no jitter, no noise.
- The header says the behavioural timing and electrical defaults are provisional.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Inputs: the even and the odd stream of one binary path at 14 Gb/s, captured on the rising edge of the 14 GHz clock (`ffe_tapgen_hr.va`, header)
- Outputs: three taps spaced one unit interval apart, pre = x[n], main = x[n-1], post = x[n-2], each as an even and an odd half (`ffe_tapgen_hr.va`, header)
- Each output bank is updated while the final multiplexer is not selecting it, and must settle (clock-to-output delay plus transition time) within that half-cycle (`ffe_tapgen_hr.va`, code comment)
- Six unweighted CML pairs, unloaded 0.6 V peak-to-peak differential: tail current 1.5 mA, load 200 ohm per leg (`ffe_tapgen_hr.va`, parameters `itail`, `rload`)
- Clock-to-output delay 2 ps and edges 2 ps in the model; both provisional (`ffe_tapgen_hr.va`, parameters `t_cq`, `tr`, `tf`, and header)
- Reset: asynchronous, active high, threshold fixed at 0.35 V (`ffe_tapgen_hr.va`, port comment and parameter `vth_rst`)
- Tap weights and signs are not applied here: they need a driver with all three tap inputs (`ffe_tapgen_hr.va`, header)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `ffe_tapgen_hr_<what>.svg` (or `.png`), and reference it from this page as `![ffe_tapgen_hr schematic](../img/ffe_tapgen_hr_<what>.svg)`.

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
