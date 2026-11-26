# vco

| Field | Value |
|---|---|
| Owner (from git history) | GreenBlueFish |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/vco.va`](../../va/Clocking/vco.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_vco`); [rx_cdr](rx_cdr.md), once (`u_vco`) |
| Section | [Clocking](README.md) |

## Architecture

The oscillator of each loop: the transmitter PLL and the receiver CDR each steer their own `vco` to 14 GHz. Its frequency follows its control voltage, `f = f_0 + k_vco * (V(v_ctrl) - v_c0)`, and its output is a square wave that is high during the first half of each cycle.

In [tx_pll](tx_pll.md) and [rx_cdr](rx_cdr.md): `v_ctrl` is the loop's `vctl` node, and `v_out` is the loop output `ck`, which goes to [tx_clkgen](tx_clkgen.md) or [rx_clkgen](rx_clkgen.md) and to the feedback divider [div_n](div_n.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `v_ctrl` | input | Control voltage |
| `v_out` | output | Clock, single-ended, 0 V to `v_amp` |
| `vdd`, `gnd` | inout | Supply and ground. The model does not read `vdd`: the output level is the parameter `v_amp` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `f_0` | 5 GHz | Centre frequency. Both parents set 14 GHz |
| `v_c0` | 0 V | Control voltage that gives `f_0`. Both parents set 0.35 V |
| `k_vco` | 2 GHz/V | Tuning gain. Both parents set 1.4 GHz/V |
| `p_init` | 0 | Initial phase |
| `v_amp` | 0.7 V | Output high level |
| `t_rf` | 2 ps | Output rise and fall time (the comment notes that 0 stalls ngspice) |

**Not modelled:** phase noise and jitter, any limit or curvature in the tuning, coarse tuning (no `band[3:0]` input), a differential output (the clock trees behind it are CML, so [dcc_cml](dcc_cml.md) makes the differential clock).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- 14 GHz at a control voltage of 0.35 V (`tx_pll.va` and `rx_cdr.va`, parameters `f0`, `vctl0`)
- Tuning gain 1.4 GHz/V (`tx_pll.va` and `rx_cdr.va`, parameter `kvco`)
- Output in the present models: single-ended CMOS, 0 to 0.7 V (`vco.va`, parameter `v_amp`)
- Output edge 2 ps in the model (`vco.va`, parameter `t_rf`)
- The feedback divider behind it is specified for 11.9 to 16.1 GHz (`div_n.va`, parameters `fmin`, `fmax`)
- Coarse tuning (`band[3:0]`) does not exist yet (`tx_pll.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/vco_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
