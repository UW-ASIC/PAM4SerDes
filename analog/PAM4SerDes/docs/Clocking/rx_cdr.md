# rx_cdr

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | structural (wiring, plus the loop filter's C2 and a start-up hold) |
| Model | [`va/Clocking/rx_cdr.va`](../../va/Clocking/rx_cdr.va) |
| Used in | `pam4_serdes` (top level), once (`u_cdr`) |
| Section | [Clocking](README.md) |

## Architecture

Recovers the receiver's clock: a 14 GHz clock whose phase follows the incoming data. One loop filter and one VCO serve two detectors. In frequency acquisition a phase-frequency detector and a 400 uA charge pump compare the reference with the VCO clock divided by 32, like a PLL. When the lock detector asserts, the charge pump is switched off and the linear phase detector steers the VCO alone; `force_lock` high switches the pump off from the start. Loop filter values from the header: R = 2.352 kohm, C = 20 pF, C2 = 1 pF, for a CDR bandwidth of 16.8 MHz and a damping factor of 1.

In `pam4_serdes`: `ckref` comes from [refclk_buf](refclk_buf.md) (`u_ref_rx`); `din_p/n`, the output of [rx_afe](../Receiver/rx_afe.md), and `clk14_p/n`, from [rx_clkgen](rx_clkgen.md), are brought out of [rx_top](../Receiver/rx_top.md); `ck` goes to `ckin` of `rx_top`, so the loop closes through `rx_top`; `lock` goes out as the top-level pin `rx_lock`. The top level sets `rj_div` to 150 fs times its `rj_scale` parameter.

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
| `u_dse`, `u_cse` | `diff2se` (see [glue](glue.md)) | `din_p/n` to a single-ended data signal; `clk14_p/n` to a single-ended in-phase clock |
| `u_q` | `qdelay` (see [glue](glue.md)) | Delays that clock by `tq` to make the quadrature clock |
| `u_pd` | [cdr_pd_linear](cdr_pd_linear.md) | Phase detector: its output current goes into `vctl` all the time; only the charge pump is gated |

- The three glue cells are there because `cdr_pd_linear` reads single-ended signals around 0 V and needs a quadrature clock, which the architecture drawing the header refers to (`Detailed.png`) does not provide.
- As in [tx_pll](tx_pll.md), the file holds `vctl` at `vc0` at the DC operating point and adds the loop filter's shunt capacitor `c2` from `vctl` to `vss` during the transient. There is no `band[3:0]` input, because the `vco` model has no coarse tuning yet.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckref` | input | 437.5 MHz reference, CMOS |
| `din_p`, `din_n` | input | Equalized data from the analog front end |
| `clk14_p`, `clk14_n` | input | 14 GHz CML clock from `rx_clkgen` |
| `force_lock` | input | High skips frequency acquisition |
| `ck` | output | 14 GHz VCO output, single-ended CMOS |
| `ckfb`, `vctl` | output | Divided clock (`ck` / 32) and VCO control voltage, for monitoring. Internal nets of the top level, not pins |
| `lock` | output | High when the frequency loop has locked |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `n` | 32 | Feedback division ratio |
| `icp` | 400 uA | Charge-pump current of the frequency loop |
| `r`, `c`, `c2` | 2.352 kohm, 20 pF, 1 pF | Loop filter resistor, integrating capacitor and shunt capacitor (`vctl` to `vss`) |
| `vc0` | 0.35 V | `vctl` at the start of the transient |
| `f0`, `vctl0`, `kvco` | 14 GHz, 0.35 V, 1.4 GHz/V | VCO frequency, the control voltage that gives it, and the tuning gain |
| `vth` | 0.35 V | PFD input threshold |
| `tq` | 17.857 ps | Quadrature delay, a quarter period. The top level sets 53.571 ps, three quarters of a period: with the default the loop settles with the clock edges on the data transitions. See [Clock recovery](../../../../CHANGELOGS.md#clock-recovery-the-detector-and-the-loop-disagree-on-sign) |
| `rj_div`, `div_seed` | 150 fs, 12 | Feedback divider's added jitter (rms per edge) and its seed |
| `n_lock` | 256 | Good cycles the lock detector needs |

**Checked by:** [`test/tb_cdr.sp`](../../test/tb_cdr.sp) (transmitter, flat test channel, receiver clocked by `rx_cdr`, frequency acquisition skipped).

## Topology research

Wiring only. See the cells: [pfd](pfd.md#topology-research), [charge_pump](charge_pump.md#topology-research), [loop_filter_rc](loop_filter_rc.md#topology-research), [vco](vco.md#topology-research), [div_n](div_n.md#topology-research), [lock_detect](lock_detect.md#topology-research), [cdr_pd_linear](cdr_pd_linear.md#topology-research), [glue](glue.md#topology-research). Treat C2, which is added in this file, as part of the loop filter's research.

## Sizing research

Wiring only. See the cells: [pfd](pfd.md#sizing-research), [charge_pump](charge_pump.md#sizing-research), [loop_filter_rc](loop_filter_rc.md#sizing-research), [vco](vco.md#sizing-research), [div_n](div_n.md#sizing-research), [lock_detect](lock_detect.md#sizing-research), [cdr_pd_linear](cdr_pd_linear.md#sizing-research), [glue](glue.md#sizing-research). Treat C2, which is added in this file, as part of the loop filter's research.
