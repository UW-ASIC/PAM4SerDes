# tx_predrv_bias

| Field | Value |
|---|---|
| Owner | Omar ElSawy |
| Kind | leaf (behavioural model) |
| Model | [`va/Biasing/tx_predrv_bias.va`](../../va/Biasing/tx_predrv_bias.va) |
| Used in | [tx_top](../Transmitter/tx_top.md), once (`u_pdb`) |
| Section | [Biasing](README.md) |

## Architecture

Turns the single pre-driver current that [tx_bias](tx_bias.md) sinks into six reference currents, one for each [predriver_cml](../Transmitter/predriver_cml.md). A bias wire serves one consumer, and `tx_bias` has one pre-driver output for six cells.

`isum` is `tx_bias.i_pdrv` (6 mA). Each output is that current divided by `ratio`. There is no enable pin: `tx_bias` already gates `isum`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vdd`, `vss` | inout | Supply (`vddo`, 1.25 V) and ground |
| `isum` | input | 6 mA pulled out by `tx_bias`. Looks like 108 ohm to `vdd`, which puts the pin at 0.6 V |
| `ib[5:0]` | output | 100 uA per pre-driver, sourced from `vdd` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `isum_nom` | 6 mA | Input current expected: six pre-drivers at 1 mA |
| `vb_nom` | 0.65 V | Voltage of the input below `vdd` at that current |
| `ratio` | 60 | Input current over each output current |
| `vdsat`, `rout_i` | 0.15 V, 1 Mohm | Compliance knee and output resistance of each output |

**Not modelled:** mismatch between the six copies, noise. The block prints FAULT when its input is more than 10 % off.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) and every deck that places `tx_top`.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Input 6 mA at 0.6 V: what `tx_bias` provides and expects (`tx_bias.va`, `n_pd`, `vod_pd`, `rld_pd` and its test bias on `i_pdrv`)
- Six outputs of 100 uA into 3.5 kohm at 0.35 V (`predriver_cml.va`, `ib_nom`, `vb_nom`)

To add: whether this stage should exist at all or `tx_bias` should grow six pre-driver outputs (decide with the `tx_bias` owner), mirror topology, schematic, references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
