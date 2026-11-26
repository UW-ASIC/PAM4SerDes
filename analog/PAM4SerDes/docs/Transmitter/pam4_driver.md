# pam4_driver

| Field | Value |
|---|---|
| Owner (from git history) | Zoey Situ |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/pam4_driver.va`](../../va/Transmitter/pam4_driver.va) |
| Used in | [tx_top](tx_top.md), once (`u_drv`) |
| Section | [Transmitter](README.md) |

## Architecture

`pam4_driver` is the transmitter's output stage. It takes six differential data inputs, the three FFE taps of the MSB path and the three of the LSB path, and adds them into one differential signal on the pads.

The system needs it for three things that all happen in this one sum:

- **PAM4**: the MSB taps carry twice the current of the LSB taps, so two binary streams become four levels.
- **FFE**: the main tap adds, the pre and post taps subtract, each with its own weight.
- **Driving the line**: the summed current develops the output swing in the 25 ohm load (the 50 ohm termination in parallel with the 50 ohm line).

### How the model works

Each tap has a differential input and a **tail node**. The driver holds every tail node at `vtail`; [tx_bias](../Biasing/tx_bias.md) sinks that tap's current from it. So the driver does not decide how large a tap is. It only steers the current it is given: to one side or the other, by the sign of that tap's input.

The output is the sum of the six steered currents times `rload`, placed around the common mode `vcm`. With the default bias currents (16 mA in total) and every tap adding, the output is 0.4 V peak, that is 0.8 V peak-to-peak differential.

The four levels, from the code comment:

| MSB wire | LSB wire | Level |
|---|---|---|
| 0 | 0 | -3 |
| 0 | 1 | -1 |
| 1 | 0 | +1 |
| 1 | 1 | +3 |

(The Gray coding is done earlier, in [prbs_gray_src](prbs_gray_src.md).)

With the default tap weights a steady pattern, where all three taps carry the same bit, is de-emphasised to (0.80 - 0.05 - 0.15) x 0.4 V = 0.24 V. The full 0.4 V appears only when pre and post are opposite to main.

### Where it sits

In [tx_top](tx_top.md): the six data inputs come from the six [predriver_cml](predriver_cml.md), the six tail nodes go to [tx_bias](../Biasing/tx_bias.md), and the outputs are the pads `txp` / `txn`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `msb_pre_p/n`, `msb_main_p/n`, `msb_post_p/n` | input | The MSB path's three taps, 28 Gb/s, differential |
| `lsb_pre_p/n`, `lsb_main_p/n`, `lsb_post_p/n` | input | The LSB path's three taps |
| `i_msb_pre`, `i_msb_main`, `i_msb_post` | inout | Tail nodes of the MSB taps: `tx_bias` sinks each tap's current here |
| `i_lsb_pre`, `i_lsb_main`, `i_lsb_post` | inout | Tail nodes of the LSB taps |
| `outp`, `outn` | output | PAM4 output, to the pads |
| `vss` | inout | Ground |

There is no supply pin.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vcm` | 0.9 V | Output common mode |
| `rload` | 25 ohm | Load each tail current develops the swing in |
| `vtail` | 0.6 V | Voltage the tail nodes are held at. `tx_bias` needs more than its `vdsat` |

### What the model leaves out

- The outputs are ideal voltage sources. The load is the parameter `rload`, so whatever is connected to the pads does not change the swing, and the driver has no output impedance.
- The steering is a hard switch on the sign of the input: no gain, no bandwidth, no edge time.
- No supply pin and no headroom limit.
- Run on its own, with nothing sinking current from the tail nodes, it gives 0 V output. The header says so and points to the test with `tx_bias` attached.

Existing testbench: [`test/tx_driver_test.sp`](../../test/tx_driver_test.sp) (driver with `tx_bias`).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Output swing 0.8 V peak-to-peak differential: 16 mA in total into 25 ohm (50 ohm termination in parallel with the 50 ohm line) (`pam4_driver.va`, code comment and parameter `rload`; `tx_bias.va`, header)
- Four levels -3, -1, +1, +3: the MSB taps carry twice the current of the LSB taps (`pam4_driver.va`, code comment)
- FFE: main taps add, pre and post taps subtract; weights 0.05 / 0.80 / 0.15 come from the tail currents (`pam4_driver.va`, code comment; `tx_bias.va`, header)
- Six tail nodes, one per tap; each must sit above the bias block's compliance voltage of 0.15 V. The model holds them at 0.6 V (`pam4_driver.va`, parameter `vtail`; `tx_bias.va`, parameter `vdsat`)
- Output common mode 0.9 V in the model (`pam4_driver.va`, parameter `vcm`)
- Output-stage supply 1.25 V (`tx_bias.va`, header)
- Symbol rate 28 GBd (`tx_ser_ffe_path.va`, header: the taps arrive at 28 Gb/s)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `pam4_driver_<what>.svg` (or `.png`), and reference it from this page as `![pam4_driver schematic](../img/pam4_driver_<what>.svg)`.

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
