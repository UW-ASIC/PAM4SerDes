# pfd

| Field | Value |
|---|---|
| Owner (from git history) | GreenBlueFish |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/pfd.va`](../../va/Clocking/pfd.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_pfd`); [rx_cdr](rx_cdr.md), once (`u_pfd`) |
| Section | [Clocking](README.md) |

## Architecture

Phase-frequency detector: `up` is high while the reference is ahead, `dn` while the feedback clock is ahead. The model is two flip-flops: a rising edge on `ref` sets `up`, a rising edge on `fb` sets `dn`, and when both are set a reset clears both `td_rst` later. In lock both outputs pulse together for `td_rst` each cycle.

- In [tx_pll](tx_pll.md) it compares `ckref` (437.5 MHz) with the VCO clock divided by 32 and drives the [charge_pump](charge_pump.md).
- In [rx_cdr](rx_cdr.md) it does the same during frequency acquisition. After lock the charge pump behind it is switched off and [cdr_pd_linear](cdr_pd_linear.md) takes over.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ref` | input | Reference clock, CMOS |
| `fb` | input | Feedback (divided) clock, CMOS |
| `up` | output | High while `ref` is ahead; 0 V to `vdd` |
| `dn` | output | High while `fb` is ahead; 0 V to `vdd` |
| `vdd`, `gnd` | input | Supply and ground. Note the name `gnd`: most other cells call it `vss` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth` | 0.5 V | Clock threshold for an edge. Both parents set 0.35 V |
| `td_rst` | 50 ps | Reset delay (dead zone) |
| `t_rf` | 0 | Output rise and fall time |

**Not modelled:** jitter, noise, input hysteresis (an edge is a single threshold crossing).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Compares two CMOS clocks at the reference rate, 437.5 MHz (`tx_pll.va`, header)
- Input threshold 0.35 V, set by both parents; the cell's own default is 0.5 V (`tx_pll.va` and `rx_cdr.va`, parameter `vth`)
- Reset delay 50 ps, described as the dead zone (`pfd.va`, parameter `td_rst`)
- `up` and `dn` swing between `gnd` and `vdd` (`pfd.va`, output equations)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/pfd_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
