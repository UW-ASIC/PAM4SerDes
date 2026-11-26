# ctle

| Field | Value |
|---|---|
| Owner (from git history) | Kayhan Baig |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/ctle.va`](../../va/Receiver/ctle.va) |
| Used in | [rx_afe](rx_afe.md), once (`u_ctle`) |
| Section | [Receiver](README.md) |

## Architecture

The continuous-time linear equalizer: more gain at high frequencies than at low ones, to undo part of the channel loss before slicing. Two stages in a row, given as transfer functions in the header:

- Low-frequency shelf: `Hlf(s) = hf_gain * (s + wzlf) / (s + wplf)`, with the zero a factor of `10^(shelf_db/20)` below the pole `pole_hz`.
- Main peaking: `Hmain(s) = (1 + s/wzm) / (1 + s/wpm)`, with the zero a factor of `10^(main_boost_db/20)` below the pole `main_pole_hz`. `main_boost_db` is the asymptotic high-frequency gain over the DC gain, not the gain at the Nyquist frequency.

In [rx_afe](rx_afe.md), between the pads (terminated by [rx_term](rx_term.md)) and the [vga](vga.md). With the top-level default `main_boost_db` = 0 dB the main stage is flat and only the 1 dB shelf acts.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in_p`, `in_n` | input | Signal from the pads |
| `out_p`, `out_n` | output | Equalized signal. Only the difference is driven: the output has no common mode of its own |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `pole_hz` | 700 MHz | Pole of the low-frequency shelf |
| `shelf_db` | 1.0 dB | Size of the low-frequency shelf |
| `hf_gain` | 1.0 | Gain above the shelf |
| `main_boost_db` | 0 dB | Main peaking boost, 0 to 30 dB |
| `main_pole_hz` | 21 GHz | Pole of the main peaking stage |

**Not modelled:** noise, rail limits, transistor bandwidth, input current (the input does not load the termination), supply pins. The header notes that the derivation it is based on does not define the main-boost pole and zero locations; the 21 GHz pole is the test bench's choice.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Low-frequency shelf: 1 dB, with its pole at 700 MHz (`ctle.va`, parameters `shelf_db`, `pole_hz`)
- Main peaking: boost adjustable from 0 to 30 dB in the model; the boost is the high-frequency gain over the DC gain, not the gain at Nyquist (`ctle.va`, header and the range of `main_boost_db`)
- Main pole 21 GHz, chosen by the test bench; at 15 dB boost that puts the main zero at 3.734 GHz (`ctle.va`, header)
- The derivation does not define where the main pole and zero should be: this is open (`ctle.va`, header)
- The boost is meant to be set by a `bst[3:0]` code; the model uses a number in dB (`rx_afe.va`, header)
- Data: 28 GBd PAM4, so the Nyquist frequency is 14 GHz (follows from the project's symbol rate)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/ctle_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
