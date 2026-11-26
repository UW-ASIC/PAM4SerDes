# loop_filter_rc

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/loop_filter_rc.va`](../../va/Clocking/loop_filter_rc.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_lf`); [rx_cdr](rx_cdr.md), once (`u_lf`) |
| Section | [Clocking](README.md) |

## Architecture

The passive loop filter of the PLL and of the CDR. It turns the charge pump's current pulses into the control voltage that sets the VCO frequency. Two elements: a resistor `R` from the pin `vctrl` to an internal node `n1`, and a capacitor `C` from `n1` to `vss`.

- In [tx_pll](tx_pll.md): on the `vctl` node, with R = 25.31 kohm and C = 1.427 pF.
- In [rx_cdr](rx_cdr.md): on the shared `vctl` node, with R = 2.352 kohm and C = 20 pF.
- Both parents add the shunt capacitor C2 themselves (0.14 pF and 1 pF), because this cell is R + C only.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vctrl` | inout | The loop's control node: charge-pump current in, control voltage out |
| `vss` | inout | Ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `R` | 25.31 kohm | Series resistor. `rx_cdr` sets 2.352 kohm |
| `C` | 1.427 pF | Integrating capacitor. `rx_cdr` sets 20 pF |

**Not modelled:** the shunt capacitor C2, resistor noise, capacitor leakage. The header carries an open note from the author, "Need to confirm Vctrl output node": whether the control voltage is taken at the charge-pump node or at the internal node.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Transmitter PLL: R = 25.31 kohm, C = 1.427 pF, C2 = 0.14 pF, for a type-II loop with damping factor 1 and 21.875 MHz bandwidth at 100 uA pump current (`tx_pll.va`, header)
- Receiver CDR: R = 2.352 kohm, C = 20 pF, C2 = 1 pF, for 16.8 MHz CDR bandwidth and damping factor 1 (`rx_cdr.va`, header)
- C2 is not in this cell today: each parent adds it from `vctl` to `vss` (`tx_pll.va` and `rx_cdr.va`, header)
- Open point from the model: which node is the control voltage output, the charge-pump node or the internal node (`loop_filter_rc.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/loop_filter_rc_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
