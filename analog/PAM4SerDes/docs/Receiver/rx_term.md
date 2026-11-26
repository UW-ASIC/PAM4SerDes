# rx_term

| Field | Value |
|---|---|
| Owner (from git history) | Mehak Khan |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/rx_term.va`](../../va/Receiver/rx_term.va) |
| Used in | [rx_afe](rx_afe.md), once (`u_term`) |
| Section | [Receiver](README.md) |

## Architecture

The receiver's input termination: `rterm` between `rx_p` and `rx_n`, and the ESD capacitance `cesd` from each pad to `vref`.

First cell of [rx_afe](rx_afe.md). It hangs on the pads; the [ctle](ctle.md) reads the same two nodes. `vref` is connected to `vtt`, which `rx_bias` makes (see [Biasing](../Biasing/README.md)).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `rx_p`, `rx_n` | inout | The pads |
| `vref` | inout | Termination reference (`vtt`) |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `rterm` | 100 ohm | Differential termination resistance |
| `cesd` | 50 fF | ESD capacitance per side |

**Not modelled:** a DC path from the pads to `vref` (only the two capacitors connect to it, so the pads' common mode is set by whatever drives them), ESD leakage and clamping, pad and package inductance, resistor tolerance and tuning.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Differential termination 100 ohm (`rx_term.va`, parameter `rterm`)
- ESD capacitance 50 fF per side, to the termination reference (`rx_term.va`, parameter `cesd`)
- Signal: 28 GBd PAM4 from the channel (`rx_top.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/rx_term_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
