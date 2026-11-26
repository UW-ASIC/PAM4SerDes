# tx_pll

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | structural (wiring, plus the loop filter's C2 and a start-up hold) |
| Model | [`va/Clocking/tx_pll.va`](../../va/Clocking/tx_pll.va) |
| Used in | `pam4_serdes` (top level), once (`u_pll`) |
| Section | [Clocking](README.md) |

## Architecture

`tx_pll` is the transmitter's phase-locked loop. It multiplies the 437.5 MHz reference by 32 and gives the transmitter its 14 GHz clock. It wires the loop's cells together and adds no behaviour of its own, apart from a capacitor and a start-up value on the control node (see Instances).

The system needs it because the transmitter sends 28 GBd with a half-rate clock, so everything in the transmitter is timed from 14 GHz, and that clock has to be locked to the reference.

The model's header states the loop design: a type-II charge-pump loop with damping factor 1 and a bandwidth of 21.875 MHz, using a charge-pump current of 100 uA, R = 25.31 kohm, C = 1.427 pF and C2 = 0.14 pF.

### Where it sits

In the top level `pam4_serdes`:

- `ckref` comes from [refclk_buf](refclk_buf.md) (`u_ref_tx`).
- `ck`, the 14 GHz clock, goes to `ckin` of [tx_top](../Transmitter/tx_top.md), where [tx_clkgen](tx_clkgen.md) builds the clock tree from it. In the present models it is a single-ended CMOS clock, 0 to 0.7 V.
- `lock` goes out as the top-level pin `tx_lock`.
- `ckfb` and `vctl` are monitor outputs. They are internal nets of the top level, not pins.

The top level sets the divider's jitter `rj_div` to 150 fs times its `rj_scale` parameter.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_pfd` | [pfd](pfd.md) | Compares `ckref` with the divided clock `ckfb` and makes the `up` / `dn` pulses |
| `u_cp` | [charge_pump](charge_pump.md) | Turns `up` / `dn` into a current into `vctl`. Its enable is tied to `vdd` (always on) |
| `u_lf` | [loop_filter_rc](loop_filter_rc.md) | R and C from `vctl` to `vss` |
| `u_vco` | [vco](vco.md) | Makes `ck`; its frequency follows `vctl` |
| `u_div` | [div_n](div_n.md) | Divides `ck` by 32 to make `ckfb` |
| `u_lock` | [lock_detect](lock_detect.md) | Watches `ckref` and `ckfb` and drives `lock` |

The file adds two things of its own on the `vctl` node:

- At the DC operating point `vctl` is held at `vc0`, so the filter capacitor starts charged and the node has a DC path.
- During the transient there is a capacitor `c2` from `vctl` to `vss`. This is the loop filter's shunt capacitor C2. The team's `loop_filter_rc` is R + C only, so C2 lives here.

The header also notes that there is no `band[3:0]` input, because the `vco` model has no coarse tuning yet.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckref` | input | 437.5 MHz reference, CMOS |
| `ck` | output | 14 GHz VCO output, single-ended CMOS |
| `ckfb` | output | Divided clock (`ck` / 32), for monitoring |
| `lock` | output | High when the loop is locked |
| `vctl` | output | VCO control voltage, for monitoring |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `n` | 32 | Feedback division ratio |
| `icp` | 100 uA | Charge-pump current |
| `r`, `c` | 25.31 kohm, 1.427 pF | Loop filter resistor and integrating capacitor |
| `c2` | 0.14 pF | Loop filter shunt capacitor, `vctl` to `vss` |
| `vc0` | 0.35 V | `vctl` at the start of the transient |
| `f0`, `vctl0` | 14 GHz, 0.35 V | VCO frequency and the control voltage that gives it |
| `kvco` | 1.4 GHz/V | VCO tuning gain |
| `vth` | 0.35 V | PFD input threshold |
| `rj_div`, `div_seed` | 150 fs, 2 | Feedback divider's added jitter (rms per edge) and its seed |
| `n_lock` | 256 | Good cycles the lock detector needs |

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [pfd](pfd.md#topology-research), [charge_pump](charge_pump.md#topology-research), [loop_filter_rc](loop_filter_rc.md#topology-research), [vco](vco.md#topology-research), [div_n](div_n.md#topology-research), [lock_detect](lock_detect.md#topology-research). The shunt capacitor C2 is added in this file because `loop_filter_rc` is R + C only; treat it as part of the loop filter's research.

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [pfd](pfd.md#sizing-research), [charge_pump](charge_pump.md#sizing-research), [loop_filter_rc](loop_filter_rc.md#sizing-research), [vco](vco.md#sizing-research), [div_n](div_n.md#sizing-research), [lock_detect](lock_detect.md#sizing-research). The shunt capacitor C2 is added in this file because `loop_filter_rc` is R + C only; treat it as part of the loop filter's research.
