# rx_cdr

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | structural (wiring, plus the loop filter's C2 and a start-up hold) |
| Model | [`va/Clocking/rx_cdr.va`](../../va/Clocking/rx_cdr.va) |
| Used in | `pam4_serdes` (top level), once (`u_cdr`) |
| Section | [Clocking](README.md) |

## Architecture

`rx_cdr` recovers the receiver's clock. It makes a 14 GHz clock whose phase follows the incoming data, so the slicers sample each symbol at the right moment. It wires the loop's cells together and adds no behaviour of its own, apart from a capacitor and a start-up value on the control node (see Instances).

The system needs it because the receiver gets no clock from the transmitter. All it has is the data itself and a local reference at nominally the right frequency.

It works in two steps that share one loop filter and one VCO:

1. **Frequency acquisition.** A phase-frequency detector and a 400 uA charge pump compare the reference with the VCO clock divided by 32, like a PLL. This brings the VCO to 14 GHz.
2. **Tracking.** When the lock detector asserts, the charge pump is switched off. The linear phase detector, which compares the data with the 14 GHz clock, then steers the VCO alone.

The top-level pin `force_lock`, when high, switches the charge pump off from the start, so step 1 is skipped.

The model's header states the loop filter values: R = 2.352 kohm, C = 20 pF, C2 = 1 pF, for a CDR bandwidth of 16.8 MHz and a damping factor of 1.

### Where it sits

In the top level `pam4_serdes`:

- `ckref` comes from [refclk_buf](refclk_buf.md) (`u_ref_rx`).
- `din_p/n` is the output of the analog front end, [rx_afe](../Receiver/rx_afe.md), brought out of [rx_top](../Receiver/rx_top.md).
- `clk14_p/n` is the 14 GHz CML clock from [rx_clkgen](rx_clkgen.md), also brought out of `rx_top`.
- `ck`, the VCO output, goes to `ckin` of `rx_top`, where `rx_clkgen` builds the clock tree from it. So the loop closes through `rx_top`: VCO, clock tree, phase detector, VCO.
- `lock` goes out as the top-level pin `rx_lock`.
- `ckfb` and `vctl` are monitor outputs. They are internal nets of the top level, not pins.

The top level sets the divider's jitter `rj_div` to 150 fs times its `rj_scale` parameter.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_pfd` | [pfd](pfd.md) | Frequency acquisition: compares `ckref` with `ckfb` |
| `u_en` | `nor2` (see [glue](glue.md)) | Makes the pump enable `cp_en = !(lock OR force_lock)` |
| `u_cp` | [charge_pump](charge_pump.md) | 400 uA into `vctl` while `cp_en` is high |
| `u_lock` | [lock_detect](lock_detect.md) | Drives `lock` |
| `u_lf` | [loop_filter_rc](loop_filter_rc.md) | R and C from `vctl` to `vss` |
| `u_vco` | [vco](vco.md) | Makes `ck`; its frequency follows `vctl` |
| `u_div` | [div_n](div_n.md) | Divides `ck` by 32 to make `ckfb` |
| `u_dse` | `diff2se` (see [glue](glue.md)) | Data `din_p/n` to a single-ended signal |
| `u_cse` | `diff2se` (see [glue](glue.md)) | `clk14_p/n` to a single-ended in-phase clock |
| `u_q` | `qdelay` (see [glue](glue.md)) | Delays that clock by a quarter period (17.857 ps) to make the quadrature clock |
| `u_pd` | [cdr_pd_linear](cdr_pd_linear.md) | Phase detector: its output current goes into `vctl` |

The three glue cells are there because `cdr_pd_linear` reads single-ended signals around 0 V and needs a quadrature clock, which the architecture drawing the header refers to (`Detailed.png`) does not provide.

The phase detector's output is connected to `vctl` all the time. Only the charge pump is gated.

The file adds two things of its own on the `vctl` node, the same as in [tx_pll](tx_pll.md):

- At the DC operating point `vctl` is held at `vc0`.
- During the transient there is a capacitor `c2` from `vctl` to `vss`: the loop filter's shunt capacitor C2.

The header also notes that there is no `band[3:0]` input, because the `vco` model has no coarse tuning yet.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckref` | input | 437.5 MHz reference, CMOS |
| `din_p`, `din_n` | input | Equalized data from the analog front end |
| `clk14_p`, `clk14_n` | input | 14 GHz CML clock from `rx_clkgen` |
| `force_lock` | input | High skips frequency acquisition |
| `ck` | output | 14 GHz VCO output, single-ended CMOS |
| `ckfb` | output | Divided clock (`ck` / 32), for monitoring |
| `lock` | output | High when the frequency loop has locked |
| `vctl` | output | VCO control voltage, for monitoring |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `n` | 32 | Feedback division ratio |
| `icp` | 400 uA | Charge-pump current of the frequency loop |
| `r`, `c` | 2.352 kohm, 20 pF | Loop filter resistor and integrating capacitor |
| `c2` | 1 pF | Loop filter shunt capacitor, `vctl` to `vss` |
| `vc0` | 0.35 V | `vctl` at the start of the transient |
| `f0`, `vctl0` | 14 GHz, 0.35 V | VCO frequency and the control voltage that gives it |
| `kvco` | 1.4 GHz/V | VCO tuning gain |
| `vth` | 0.35 V | PFD input threshold |
| `tq` | 17.857 ps | Quadrature delay for the phase detector's second clock. The top level sets it to 53.571 ps, three quarters of a period: with the default the loop settles with the clock edges on the data transitions. See [Clock recovery](../../../../CHANGELOGS.md#clock-recovery-the-detector-and-the-loop-disagree-on-sign) |
| `rj_div`, `div_seed` | 150 fs, 12 | Feedback divider's added jitter (rms per edge) and its seed |
| `n_lock` | 256 | Good cycles the lock detector needs |

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [pfd](pfd.md#topology-research), [charge_pump](charge_pump.md#topology-research), [loop_filter_rc](loop_filter_rc.md#topology-research), [vco](vco.md#topology-research), [div_n](div_n.md#topology-research), [lock_detect](lock_detect.md#topology-research), [cdr_pd_linear](cdr_pd_linear.md#topology-research), [glue](glue.md#topology-research). The shunt capacitor C2 is added in this file because `loop_filter_rc` is R + C only; treat it as part of the loop filter's research.

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [pfd](pfd.md#sizing-research), [charge_pump](charge_pump.md#sizing-research), [loop_filter_rc](loop_filter_rc.md#sizing-research), [vco](vco.md#sizing-research), [div_n](div_n.md#sizing-research), [lock_detect](lock_detect.md#sizing-research), [cdr_pd_linear](cdr_pd_linear.md#sizing-research), [glue](glue.md#sizing-research). The shunt capacitor C2 is added in this file because `loop_filter_rc` is R + C only; treat it as part of the loop filter's research.
