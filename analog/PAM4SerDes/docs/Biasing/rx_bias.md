# rx_bias

| Field | Value |
|---|---|
| Owner | Omar ElSawy |
| Kind | leaf (behavioural model) |
| Model | [`va/Biasing/rx_bias.va`](../../va/Biasing/rx_bias.va) |
| Used in | [`pam4_serdes`](../README.md), once (`u_rxb`) |
| Section | [Biasing](README.md) |

## Architecture

Turns one reference current into every bias the receiver needs, one wire per consumer: the termination reference `vtt`, the VGA gain-control voltage `vctrl`, and 38 reference currents.

`iref` comes from [bias_ref](bias_ref.md). `vtt` goes to [rx_term](../Receiver/rx_term.md) and `vctrl` to [vga](../Receiver/vga.md), both through `rx_top`. The 38 currents are for `ctle`, `vga`, the 24 slicers and the 12 `demux2_cml` cells; those cells have no bias pin yet, so the currents end at the top level. Every output scales with the reference current received.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vdd`, `vss` | inout | Supply (0.7 V) and ground |
| `en` | input | Enable, 0.7 V logic (top-level `rx_en`) |
| `iref` | input | 100 uA reference. Looks like 3.5 kohm to `vss` (`vb_nom / iref_nom`) |
| `vtt` | output | 0.55 V termination reference, through 10 ohm |
| `vctrl` | output | 0.35 V VGA gain control, through 10 ohm |
| `ib_ctle`, `ib_vga` | output | 100 uA each, sourced from `vdd` |
| `ib_slicer[23:0]` | output | 100 uA per slicer |
| `ib_demux[11:0]` | output | 100 uA per CML demultiplexer |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `iref_nom`, `vb_nom` | 100 uA, 0.35 V | Reference current expected, and the input's voltage at that current |
| `vtt_nom` | 0.55 V | Termination reference |
| `vctrl_nom` | 0.35 V | VGA gain-control voltage (mid gain) |
| `ib_nom` | 100 uA | Each current output |
| `vdd_min`, `vdd_w` | 0.6 V, 20 mV | Supply-low gate: lowest supply for a full output, and the width of the transition |
| `ven_th`, `ven_w` | 0.35 V, 20 mV | Enable gate: threshold and width |
| `t_start` | 1 ns | Start-up time constant |
| `rout_v` | 10 ohm | Output resistance of `vtt` and `vctrl` |
| `vdsat`, `rout_i` | 0.1 V, 1 Mohm | Compliance knee (below `vdd`) and output resistance of the current outputs |
| `idd` | 100 uA | Supply current besides the outputs |

**Not modelled:** mismatch between the copies, noise, the gain-control loop that would set `vctrl`. The block prints FAULT when its reference is more than 10 % off while enabled.

**Checked by:** [`test/tb_top.sp`](../../test/tb_top.sp), the whole top level.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- `vtt` 0.55 V: the common mode the test channel drives the pads at (`test/tb_datapath.sp`)
- `vctrl` 0.35 V: mid gain of the VGA, range 0 to 0.7 V (`vga.va`)
- 38 current outputs: 1 CTLE, 1 VGA, 24 slicers, 12 CML demultiplexers (`architecture.txt`)
- 100 uA per output and the 0.7 V supply are placeholders until the consumers are sized

To add: the current each consumer really needs, how `vtt` and `vctrl` are made (resistor string, DAC, loop), mirror topology and headroom at 0.7 V, schematic, references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
