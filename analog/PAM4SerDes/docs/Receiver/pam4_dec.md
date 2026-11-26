# pam4_dec

| Field | Value |
|---|---|
| Owner (from git history) | Kayhan Baig |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/pam4_dec.va`](../../va/Receiver/pam4_dec.va) |
| Used in | [rx_decision](rx_decision.md), twice (`dec0`, `dec1`: one per phase) |
| Section | [Receiver](README.md) |

## Architecture

Combinational decoder (no clock): it turns the three decisions of one sampling phase, a thermometer code, into the two bits of the PAM4 symbol and undoes the transmitter's Gray coding. With A, B and C the decisions at the -100, 0 and +100 mV thresholds, MSB = B and LSB = A XOR C. The levels -3, -1, +1, +3 give ABC = 000, 100, 110, 111 and MSB/LSB = 00, 01, 11, 10; codes that should not occur give whatever the two equations give.

In [rx_decision](rx_decision.md), one per phase, after the selection in [dfe1_unrolled_hr](dfe1_unrolled_hr.md) and before [rx_dec_retime](rx_dec_retime.md). It reads the positive leg of each differential DFE output.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `a`, `b`, `c` | input | Decisions at the -100, 0 and +100 mV thresholds, as logic levels |
| `msb`, `lsb` | output | The symbol's two bits |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vlow`, `vhigh` | 0 V, 1.8 V | Output levels. `rx_decision` sets `vhigh` = 0.7 V (`vdd`) |
| `vth` | 0.9 V | Input threshold. `rx_decision` sets `vdd` - 0.15 V, the common mode of the DFE's output pairs |
| `tdelay` | 0 | Output delay |
| `trise`, `tfall` | 1 ps, 1 ps | Output edge times |

**Not modelled:** latching, noise, metastability, loading and supply current (the header's list); also supply pins, input hysteresis and bubble correction for invalid codes.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Inputs A, B, C: the decisions at the -100, 0 and +100 mV thresholds (`pam4_dec.va`, header)
- Valid codes ABC = 000, 100, 110, 111 map to MSB/LSB = 00, 01, 11, 10 (`pam4_dec.va`, header)
- Logic: MSB = B, LSB = A XOR C (`pam4_dec.va`, code)
- Invalid codes are not corrected: no bubble correction (`pam4_dec.va`, header)
- Combinational; placed after the DFE's selection and before the decision retiming (`pam4_dec.va`, header)
- One per phase, so each works at 14 GBd (`rx_decision.va`, header)
- Levels in the hierarchy: input threshold `vdd` - 0.15 V (it reads one leg of a CML pair), output 0 to 0.7 V (`rx_decision.va`, header and instance lines)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/pam4_dec_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
