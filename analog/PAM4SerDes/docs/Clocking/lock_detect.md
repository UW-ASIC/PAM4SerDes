# lock_detect

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/lock_detect.va`](../../va/Clocking/lock_detect.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_lock`); [rx_cdr](rx_cdr.md), once (`u_lock`) |
| Section | [Clocking](README.md) |

## Architecture

Tells the rest of the chip whether a loop is locked. Once per reference cycle it compares the rising edge of the reference with the rising edge of the divided clock.

- While unlocked: a cycle is good if there was exactly one feedback edge and the two edges are within `t_win_lock`. After `n_lock` good cycles in a row, `lock` goes high.
- While locked: a cycle is bad if the edges are more than `t_win_unlock` apart or the number of feedback edges is not one. After `n_unlock` bad cycles in a row, or when the reference has no edge for `tmiss`, `lock` goes low.

In [tx_pll](tx_pll.md), `lock` goes out as the top-level pin `tx_lock`. In [rx_cdr](rx_cdr.md) it goes out as `rx_lock` and also switches the frequency loop off: `!(lock | force_lock)` enables the [charge_pump](charge_pump.md). The header calls it the lock detector "for the TX PLL"; the same cell is used in both loops.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckref` | input | Reference clock, CMOS |
| `ckfb` | input | Divided VCO clock, CMOS |
| `lock` | output | High when locked; CMOS level, driven through `rout` |
| `vdd`, `vss` | inout | 0.7 V core supply and ground. The input threshold is half the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `t_win_lock` | 30 ps | Largest phase error that counts towards lock |
| `t_win_unlock` | 60 ps | Phase error above which a cycle counts towards unlock |
| `n_lock` | 256 | Consecutive good cycles needed to assert lock |
| `n_unlock` | 4 | Consecutive bad cycles needed to drop lock |
| `tmiss` | 10 ns | Reference idle time that drops lock |
| `tpd` | 30 ps | Delay from the deciding event to the output's 50 % |
| `trf` | 25 ps | Output edge duration, 0 to 100 % |
| `rout` | 100 ohm | Output driver resistance |

**Not modelled:** a real way to measure a 30 ps window (the model measures edge times exactly); jitter and noise of its own.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- A cycle counts as good when the edges are within 30 ps (`lock_detect.va`, parameter `t_win_lock`)
- A cycle counts as bad when the edges are more than 60 ps apart (`lock_detect.va`, parameter `t_win_unlock`)
- 256 good cycles in a row to assert lock; 4 bad cycles in a row to drop it (`lock_detect.va`, parameters `n_lock`, `n_unlock`)
- Lock drops if the reference is idle for 10 ns (`lock_detect.va`, parameter `tmiss`)
- Compares once per reference cycle, at 437.5 MHz (`lock_detect.va`, header)
- Output delay 30 ps, edge 25 ps, driver resistance 100 ohm (`lock_detect.va`, parameters `tpd`, `trf`, `rout`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/lock_detect_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
