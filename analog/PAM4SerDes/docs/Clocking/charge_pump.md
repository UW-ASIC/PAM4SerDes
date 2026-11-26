# charge_pump

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf, ideal (the circuit was scrapped from the design) |
| Model | [`va/Clocking/charge_pump.va`](../../va/Clocking/charge_pump.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_cp`); [rx_cdr](rx_cdr.md), once (`u_cp`) |
| Section | [Clocking](README.md) |

## Architecture

Turns the two pulse outputs of the phase-frequency detector into a current into the loop filter. The header says it is an ideal charge pump, because the charge-pump circuit was scrapped from the design: `I(into out) = icp * en * (u - d)`, where `u`, `d` and `en` are the pin voltages divided by the supply and clamped to 0..1. With rail-to-rail logic inputs that is exactly `+icp`, `-icp` or 0.

- In [tx_pll](tx_pll.md): fed by [pfd](pfd.md), output on `vctl`, enable tied to `vdd` (always on), `icp` = 100 uA.
- In [rx_cdr](rx_cdr.md): fed by [pfd](pfd.md), output on the shared `vctl` node, `icp` = 400 uA. Its enable is `!(lock | force_lock)`, made by the `nor2` cell on the [glue](glue.md) page, so the pump works only during frequency acquisition.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `up`, `dn` | input | Pulses from the PFD |
| `en` | input | Enable. Low switches the pump off; tie to `vdd` for always on |
| `out` | output | Current into the loop filter node |
| `vdd`, `vss` | inout | Supply and ground; the inputs are read as a fraction of the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `icp` | 100 uA | Pump current. `rx_cdr` sets 400 uA |

**Not modelled:** threshold, delay, mismatch between the up and down currents, leakage and an output compliance limit (the header's list). The output is a perfect current source at any `vctl`.

## Topology research

First ask the Clocking lead what provides this function in the real circuit, and record the answer here: the model's header says the charge-pump circuit was scrapped from the design.

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Pump current 100 uA in the transmitter PLL (`tx_pll.va`, parameter `icp`)
- Pump current 400 uA in the receiver's frequency loop (`rx_cdr.va`, parameter `icp`)
- An enable input: the receiver switches the pump off after lock (`charge_pump.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/charge_pump_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
