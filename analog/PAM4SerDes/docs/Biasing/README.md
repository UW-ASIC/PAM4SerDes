# Biasing

The Biasing section covers the currents and reference voltages that the other blocks run on.

![Biasing: bias block, reference pins and supplies](../img/biasing.svg)

Today this section is small: one block, and a handful of top-level pins. Most of what a finished chip's bias network does is not in the models yet. This page lists what is there and what is missing, so that nobody assumes a bias exists when it does not.

## How bias reaches the circuits today

- **The transmitter's output stage** is the only part with a real bias path. [tx_bias](tx_bias.md) takes the reference voltage `vref` and sinks six tail currents from [pam4_driver](../Transmitter/pam4_driver.md). Those currents set the output swing, the 2 : 1 weighting of the MSB path against the LSB path, and the FFE tap weights.
- **Everything else** has no bias input. The CML cells either take their tail current as a parameter (`clkbuf_cml`, `mux2_cml_hr`, `ffe_tapgen_hr`) or drive ideal voltage levels.
- **The receiver** is set from outside through two pins: `vctrl` for the gain of the [vga](../Receiver/vga.md) and `vtt` as the termination reference of [rx_term](../Receiver/rx_term.md).

## Blocks

| Block | Kind | Owner (from git history) | Purpose |
|---|---|---|---|
| [tx_bias](tx_bias.md) | leaf | Krrish Lala | Sinks the six PAM4 driver tail currents, which set the output swing, the 2:1 MSB:LSB weighting and the FFE tap weights |

The file of `tx_bias` is in `va/Transmitter/`; there is no Biasing folder in `va/`. The documentation keeps it here because the project is organised as four sections.

## Bias, reference and supply pins of the top level

These are pins of `pam4_serdes`. In the present design all of them are supplied from outside.

| Pin | Value | What it does |
|---|---|---|
| `vref` | 0.6 V | Reference into [tx_bias](tx_bias.md). All of its currents scale with this voltage |
| `tx_en` | 1.25 V logic, high = on | Enable of [tx_bias](tx_bias.md) |
| `vctrl` | 0 to 0.7 V | Gain control voltage of the [vga](../Receiver/vga.md) |
| `vtt` | not stated in the models; to be filled in by the owner | Termination reference of the receiver ([rx_term](../Receiver/rx_term.md)) |
| `vdd` | 0.7 V | Core supply |
| `vddo` | 1.25 V | Supply of the transmitter's output stage |
| `vss` | 0 V | Ground |

`tx_bias` also drives one status pin, `tx_pgood`: high once the block is enabled and its supply has headroom.

## What does not exist yet

- **No receiver bias block.** Nothing generates bias currents for the front end, the slicers or the CML demultiplexers.
- **The pre-drivers have no bias pin.** `tx_bias` already has an output for their tail current, `i_pdrv`, but it is unconnected because [predriver_cml](../Transmitter/predriver_cml.md) is ideal.
- **The slicer thresholds come from the DFE model**, [dfe1_unrolled_hr](../Receiver/dfe1_unrolled_hr.md), as ideal voltages. The block written to generate them, [threshold_dac](../Receiver/threshold_dac.md), is not instantiated.
- **Nothing generates `vref`.** It is a pin.
- **No bias for the clocking cells.** None of them has a bias input: the charge-pump current and the clock buffer's tail current are parameters, and the other cells are ideal.

Each of these is a gap between the models and a complete circuit. Whether a gap becomes a new block is for the project lead to decide. If you take one, add its page to this folder, with the same three sections as the other block pages.
