# bias_ref

| Field | Value |
|---|---|
| Owner | Omar ElSawy |
| Kind | leaf (behavioural model) |
| Model | [`va/Biasing/bias_ref.va`](../../va/Biasing/bias_ref.va) |
| Used in | [`pam4_serdes`](../README.md), once (`u_ref`) |
| Section | [Biasing](README.md) |

## Architecture

Makes the one reference the bias network starts from, and gives each bias block its own copy: a 0.6 V voltage for [tx_bias](tx_bias.md) and a 100 uA current each for [rx_bias](rx_bias.md) and [clk_bias](clk_bias.md).

It runs from `vddo` (1.25 V) and is enabled by the top-level pin `bias_en`. The current outputs are sources from `vdd`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vdd`, `vss` | inout | Supply (`vddo`, 1.25 V) and ground |
| `en` | input | Enable, 1.25 V logic, high = on |
| `vref` | output | 0.6 V reference, through 100 ohm |
| `iref_rx`, `iref_clk` | output | 100 uA each, sourced from `vdd` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vref_nom` | 0.6 V | Reference voltage |
| `iref_nom` | 100 uA | Each current copy |
| `vdd_nom` | 1.25 V | Supply the reference is specified at |
| `vdd_min`, `vdd_w` | 1.0 V, 30 mV | Supply-low gate: lowest supply for a full output, and the width of the transition |
| `ven_th`, `ven_w` | 0.6 V, 20 mV | Enable gate: threshold and width |
| `t_start` | 1 ns | Start-up time constant |
| `psrr_db` | 40 dB | Supply rejection of the reference |
| `rout_v` | 100 ohm | Output resistance of `vref` |
| `vdsat`, `rout_i` | 0.15 V, 1 Mohm | Compliance knee (below `vdd`) and output resistance of the current outputs |
| `idd` | 50 uA | Supply current of the core |

**Not modelled:** temperature, noise, mismatch between the copies.

**Checked by:** [`test/tb_top.sp`](../../test/tb_top.sp), the whole top level.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- 0.6 V reference for `tx_bias`, which scales every transmitter current with it (`tx_bias.va`, `vref_nom`)
- Two 100 uA copies, each into a 3.5 kohm diode-connected input at 0.35 V (`rx_bias.va`, `clk_bias.va`)
- 1.25 V supply; full output from 1.0 V up; 40 dB supply rejection (`bias_ref.va`, parameters)

To add: candidates (bandgap, constant-gm, resistor-referenced), comparison, the choice and its reason, the start-up circuit, schematic, references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
