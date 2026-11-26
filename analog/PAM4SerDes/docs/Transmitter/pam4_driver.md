# pam4_driver

| Field | Value |
|---|---|
| Owner (from git history) | Zoey Situ |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/pam4_driver.va`](../../va/Transmitter/pam4_driver.va) |
| Used in | [tx_top](tx_top.md), once (`u_drv`) |
| Section | [Transmitter](README.md) |

## Architecture

The transmitter's output stage: it adds the six FFE taps (pre, main and post of the MSB and of the LSB path) into one differential PAM4 signal on the pads.

- Each tap has a tail node, held at `vtail`. [tx_bias](../Biasing/tx_bias.md) sinks the tap's current from it; the driver only steers that current to one side or the other by the sign of the tap's input.
- The output is the sum of the steered currents times `rload` (the 50 ohm termination in parallel with the 50 ohm line), around `vcm`. Main taps add, pre and post taps subtract. The MSB taps carry twice the current of the LSB taps, so the wires (MSB, LSB) 00, 01, 10, 11 give the levels -3, -1, +1, +3.
- With the default bias currents (16 mA in total) the output is 0.4 V peak, 0.8 V peak-to-peak differential, when pre and post are opposite to main. A steady pattern gives (0.80 - 0.05 - 0.15) x 0.4 V = 0.24 V.

In [tx_top](tx_top.md): inputs from the six [predriver_cml](predriver_cml.md), tail nodes to `tx_bias`, outputs to the pads `txp` / `txn`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `msb_pre_p/n`, `msb_main_p/n`, `msb_post_p/n` | input | The MSB path's three taps, 28 Gb/s, differential |
| `lsb_pre_p/n`, `lsb_main_p/n`, `lsb_post_p/n` | input | The LSB path's three taps |
| `i_msb_pre`, `i_msb_main`, `i_msb_post` | inout | Tail nodes of the MSB taps: `tx_bias` sinks each tap's current here |
| `i_lsb_pre`, `i_lsb_main`, `i_lsb_post` | inout | Tail nodes of the LSB taps |
| `outp`, `outn` | output | PAM4 output, to the pads |
| `vss` | inout | Ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vcm` | 0.9 V | Output common mode |
| `rload` | 25 ohm | Load each tail current develops the swing in |
| `vtail` | 0.6 V | Voltage the tail nodes are held at. `tx_bias` needs more than its `vdsat` |

**Not modelled:** output impedance (the outputs are ideal voltage sources, so what is connected to the pads does not change the swing), gain, bandwidth, edge time (the steering is a hard switch on the input sign), a supply pin, a headroom limit. With nothing sinking current from the tail nodes the output is 0 V.

**Checked by:** [`test/tx_driver_test.sp`](../../test/tx_driver_test.sp) (driver with `tx_bias`).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Output swing 0.8 V peak-to-peak differential: 16 mA in total into 25 ohm (50 ohm termination in parallel with the 50 ohm line) (`pam4_driver.va`, code comment and parameter `rload`; `tx_bias.va`, header)
- Four levels -3, -1, +1, +3: the MSB taps carry twice the current of the LSB taps (`pam4_driver.va`, code comment)
- FFE: main taps add, pre and post taps subtract; weights 0.05 / 0.80 / 0.15 come from the tail currents (`pam4_driver.va`, code comment; `tx_bias.va`, header)
- Six tail nodes, one per tap; each must sit above the bias block's compliance voltage of 0.15 V. The model holds them at 0.6 V (`pam4_driver.va`, parameter `vtail`; `tx_bias.va`, parameter `vdsat`)
- Output common mode 0.9 V in the model (`pam4_driver.va`, parameter `vcm`)
- Output-stage supply 1.25 V (`tx_bias.va`, header)
- Symbol rate 28 GBd (`tx_ser_ffe_path.va`, header: the taps arrive at 28 Gb/s)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/pam4_driver_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
