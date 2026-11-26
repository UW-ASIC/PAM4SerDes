# lock_detect

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/lock_detect.va`](../../va/Clocking/lock_detect.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_lock`); [rx_cdr](rx_cdr.md), once (`u_lock`) |
| Section | [Clocking](README.md) |

## Architecture

`lock_detect` tells the rest of the chip whether a loop is locked. Once per reference cycle it compares the rising edge of the reference with the rising edge of the divided clock.

- While unlocked: a cycle is good if there was exactly one feedback edge and the two edges are within `t_win_lock`. After `n_lock` good cycles in a row, `lock` goes high.
- While locked: a cycle is bad if the edges are more than `t_win_unlock` apart or the number of feedback edges is not one. After `n_unlock` bad cycles in a row, `lock` goes low.
- A watchdog drops `lock` if the reference has no edge for `tmiss`.

The two windows differ, and it takes many more cycles to assert lock than to drop it. This gives the flag hysteresis: it is harder to get lock than to keep it.

### Where it sits

- In [tx_pll](tx_pll.md): `lock` goes out as the top-level pin `tx_lock`.
- In [rx_cdr](rx_cdr.md): `lock` goes out as `rx_lock`, and it also switches the frequency loop off. `!(lock | force_lock)` enables the [charge_pump](charge_pump.md), so once `lock` is high the phase detector tracks the data alone.

The header calls it the lock detector "for the TX PLL"; the same cell is used in both loops.

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

### What the model leaves out

- It measures edge times exactly. A real detector would need its own way to measure a 30 ps window.
- No jitter or noise of its own.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- A cycle counts as good when the edges are within 30 ps (`lock_detect.va`, parameter `t_win_lock`)
- A cycle counts as bad when the edges are more than 60 ps apart (`lock_detect.va`, parameter `t_win_unlock`)
- 256 good cycles in a row to assert lock; 4 bad cycles in a row to drop it (`lock_detect.va`, parameters `n_lock`, `n_unlock`)
- Lock drops if the reference is idle for 10 ns (`lock_detect.va`, parameter `tmiss`)
- Compares once per reference cycle, at 437.5 MHz (`lock_detect.va`, header)
- Output delay 30 ps, edge 25 ps, driver resistance 100 ohm (`lock_detect.va`, parameters `tpd`, `trf`, `rout`)

To be added by the owner:

- (add requirements here)

### Candidate topologies

One row per circuit you seriously considered. Two or three good candidates are enough.

| Candidate | Source / reference | Pros | Cons |
|---|---|---|---|
| | | | |

### Chosen topology

Which candidate you chose and the reasons, measured against the requirements above. Say what you gave up by not choosing the others.

### Schematic

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `lock_detect_<what>.svg` (or `.png`), and reference it from this page as `![lock_detect schematic](../img/lock_detect_<what>.svg)`.

### Open questions

- (questions for the section lead or for neighbouring blocks' owners)

### References

- (papers, textbook sections, earlier designs; give enough detail that someone else can find them)

## Sizing research

*To be filled in by the owner during the sizing-research stage, once the topology is chosen.*

The goal of this section is to record the device sizes that meet the block's specs, how they were found, and the simulations that show it.

### Target specs

Copy the requirements from the Topology research section and turn each one into a number you can simulate.

| Spec | Target | Source |
|---|---|---|
| | | |

### Sizing method

How the sizes were found (hand calculation, gm/Id, sweep), with enough detail that someone else can repeat it.

### Devices

| Device | W/L or fingers | Bias point |
|---|---|---|
| | | |

### Simulation results

One row per spec. Name the testbench file so the result can be reproduced.

| Spec | Target | Result | Testbench | Conditions |
|---|---|---|---|---|
| | | | | |

### Corners checked

List the process, voltage and temperature corners you simulated, and say which one was worst.

### Open issues

- (specs not met yet, things left to check)
