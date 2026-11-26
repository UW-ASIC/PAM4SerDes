# tx_bias

| Field | Value |
|---|---|
| Owner (from git history) | Krrish Lala |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/tx_bias.va`](../../va/Transmitter/tx_bias.va) |
| Used in | [tx_top](../Transmitter/tx_top.md), once (`u_bias`) |
| Section | [Biasing](README.md) |

## Architecture

Sinks the six tail currents of [pam4_driver](../Transmitter/pam4_driver.md), one per binary path (MSB, LSB) and FFE tap (pre, main, post), and one current for the pre-drivers. Those currents set the output swing (16 mA into 25 ohm = 0.8 V peak-to-peak differential), the 2 : 1 weighting of MSB against LSB, and the FFE tap weights.

`vref` comes from [bias_ref](bias_ref.md), `en` is the top-level pin `tx_en`, and `vdd` is `vddo`. The driver holds the six tail pins at 0.6 V. `i_pdrv` goes to [tx_predrv_bias](tx_predrv_bias.md). With `swing_loop = 1` the model stands for a replica cell and op-amp that make the swing follow `vref` whatever the termination; with 0 it is a plain mirror.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vdd`, `vss` | inout | Supply (1.25 V) and ground |
| `en` | input | Enable, high = on, threshold 0.6 V |
| `vref` | input | 0.6 V reference. Every current scales with `V(vref) / vref_nom` |
| `i_msb_pre`, `i_msb_main`, `i_msb_post` | inout | Sinks for the MSB path's taps: 0.53, 8.53, 1.60 mA |
| `i_lsb_pre`, `i_lsb_main`, `i_lsb_post` | inout | Sinks for the LSB path's taps: 0.27, 4.27, 0.80 mA |
| `i_pdrv` | inout | Sink for the pre-drivers: 6 mA |
| `pgood` | output | High once enabled with supply headroom (top-level `tx_pgood`) |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vppd` | 0.8 V | Target swing, peak-to-peak differential, allowed 0.7 to 0.9 V |
| `rterm_nom`, `rterm_act` | 50, 50 ohm | Nominal and actual termination per side |
| `swing_loop` | 1 | 1 = replica and op-amp loop, 0 = plain mirror |
| `w_pre`, `w_main`, `w_post` | 0.05, 0.80, 0.15 | FFE tap weights; `tx_top` passes the top-level values |
| `msb_ratio`, `ratio_err` | 2.0, 0 | MSB over LSB current, and its fractional error |
| `vod_pd`, `rld_pd`, `n_pd` | 0.2 V, 200 ohm, 6 | Pre-driver swing, load (marked "assumed") and cell count |
| `vref_nom` | 0.6 V | Reference that gives the nominal currents |
| `vdd_nom`, `vdd_min`, `vdd_w` | 1.25, 1.0, 0.03 V | Nominal supply, lowest supply for full current, width of that turn-on |
| `psrr_db` | 40 dB | Supply sensitivity of the reference path |
| `vdsat`, `rout` | 0.15 V, 1 Mohm | Compliance knee and output resistance of each sink |
| `t_en` | 1 ns | Enable settling time constant |
| `vpg_hi`, `vpg_lo` | 1.25, 0 V | Levels of `pgood` |

**Not modelled:** the replica loop's dynamics, offset and stability (it is an equation); noise; temperature; mismatch other than `ratio_err`. The block's own supply current is taken as 1 % of what it sinks.

**Checked by:** [`test/tx_bias_test.sp`](../../test/tx_bias_test.sp) (alone) and [`test/tx_driver_test.sp`](../../test/tx_driver_test.sp) (with the driver).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Swing 0.8 V peak-to-peak differential into 25 ohm, allowed 0.7 to 0.9 V (`tx_bias.va`, header, `vppd`)
- 16 mA in total, MSB : LSB = 2 : 1, taps 0.05 / 0.80 / 0.15 (`tx_bias.va`, header)
- Every output is a sink into `vss`; the driver applies the tap signs (`tx_bias.va`, header)
- The swing should follow the reference, not the termination value: `swing_loop = 1` (`tx_bias.va`, header)
- 1.25 V supply, full current from 1.0 V, 40 dB supply rejection, 0.15 V compliance (`tx_bias.va`, parameters)
- Pre-driver current: 0.2 V over 200 ohm per cell, six cells; the 200 ohm is marked "assumed" (`tx_bias.va`, parameters)

To add: candidates, comparison, the choice and its reason, schematic, open questions, references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
