# ctle

| Field | Value |
|---|---|
| Owner (from git history) | Kayhan Baig |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/ctle.va`](../../va/Receiver/ctle.va) |
| Used in | [rx_afe](rx_afe.md), once (`u_ctle`) |
| Section | [Receiver](README.md) |

## Architecture

`ctle` is the continuous-time linear equalizer. It is a filter that passes high frequencies with more gain than low ones.

The system needs it because a channel does the opposite: it attenuates high frequencies more than low ones, which smears each symbol into the next. Boosting the high frequencies at the receiver undoes part of that before the signal is sliced.

### How the model works

Two stages in a row, both given as transfer functions in the header:

- **Low-frequency shelf**: `Hlf(s) = hf_gain * (s + wzlf) / (s + wplf)`, with the zero a factor of `10^(shelf_db/20)` below the pole. Frequencies well below `pole_hz` get `shelf_db` less gain than frequencies well above it.
- **Main peaking**: `Hmain(s) = (1 + s/wzm) / (1 + s/wpm)`, with the zero a factor of `10^(main_boost_db/20)` below the pole `main_pole_hz`. Its gain is 1 at DC and rises to `main_boost_db` at high frequency.

The header points out that `main_boost_db` is the asymptotic high-frequency gain over the DC gain, not the gain at the Nyquist frequency.

### Where it sits

In [rx_afe](rx_afe.md), between the pads (terminated by [rx_term](rx_term.md)) and the [vga](vga.md).

`rx_afe` passes `shelf_db` and `main_boost_db`. The top-level default of `main_boost_db` is 0 dB, which leaves the main peaking stage flat; only the 1 dB shelf acts.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in_p`, `in_n` | input | Signal from the pads |
| `out_p`, `out_n` | output | Equalized signal. Only the difference is driven: the output has no common mode of its own |

There are no supply pins.

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `pole_hz` | 700 MHz | Pole of the low-frequency shelf |
| `shelf_db` | 1.0 dB | Size of the low-frequency shelf |
| `hf_gain` | 1.0 | Gain above the shelf |
| `main_boost_db` | 0 dB | Main peaking boost, 0 to 30 dB |
| `main_pole_hz` | 21 GHz | Pole of the main peaking stage |

### What the model leaves out

The header says it: an ideal, noiseless differential model, with no rail limits and no transistor bandwidth. Two more things follow from the code:

- The input draws no current, so it does not load the termination.
- The header notes that the derivation it is based on does not define the main-boost pole and zero locations; the 21 GHz pole is the test bench's choice.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Low-frequency shelf: 1 dB, with its pole at 700 MHz (`ctle.va`, parameters `shelf_db`, `pole_hz`)
- Main peaking: boost adjustable from 0 to 30 dB in the model; the boost is the high-frequency gain over the DC gain, not the gain at Nyquist (`ctle.va`, header and the range of `main_boost_db`)
- Main pole 21 GHz, chosen by the test bench; at 15 dB boost that puts the main zero at 3.734 GHz (`ctle.va`, header)
- The derivation does not define where the main pole and zero should be: this is open (`ctle.va`, header)
- The boost is meant to be set by a `bst[3:0]` code; the model uses a number in dB (`rx_afe.va`, header)
- Data: 28 GBd PAM4, so the Nyquist frequency is 14 GHz (follows from the project's symbol rate)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `ctle_<what>.svg` (or `.png`), and reference it from this page as `![ctle schematic](../img/ctle_<what>.svg)`.

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
