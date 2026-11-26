# dfe1_unrolled_hr

| Field | Value |
|---|---|
| Owner (from git history) | deaconsham |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/dfe1_unrolled_hr.va`](../../va/Receiver/dfe1_unrolled_hr.va) |
| Used in | [rx_decision](rx_decision.md), once (`dfe`) |
| Section | [Receiver](README.md) |

## Architecture

One-tap, unrolled, half-rate decision feedback equalizer. The header writes the received signal as `r[n] = x[n] + alpha * x[n-1]`. The slicers compare against thresholds already shifted for every value the previous symbol could have had, and this block picks the right comparison afterwards, so no decision is fed back within a symbol period.

- References: `ref[g] = T_k + alpha * L_h` for slicer g = 12 x phase + 3 x h + k, with T_k = {-1, 0, +1} x `v_thr` and L_h = {-3, -1, +1, +3} x `v_level`. [rx_decision](rx_decision.md) leaves these outputs unconnected: each slicer's reference comes from its own [threshold_dac](threshold_dac.md).
- Selection: per phase, the 3 slicer outputs whose hypothesis h equals the level the other phase decided one unit interval earlier. They are that phase's thermometer code, and their sum is the level handed to the other phase.
- Timing: phase 0 samples on the rising clock edge and is resolved on the falling edge, reading phase 1's level; phase 1 samples on the falling edge and is resolved on the rising edge. Each selection reads a value that is not changing.

In [rx_decision](rx_decision.md): candidates from the 24 [slicer](slicer.md)s, thermometer code to the two [pam4_dec](pam4_dec.md), clock `clk14` from [rx_clkgen](../Clocking/rx_clkgen.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk_p`, `clk_n` | input | 14 GHz CML clock |
| `cand_p[0:23]`, `cand_n[0:23]` | input | The 24 slicer decisions. Positive means the input is above that slicer's reference |
| `ref_p[0:23]`, `ref_n[0:23]` | output | The 24 ideal slicer references, as differential voltages. Not connected in `rx_decision` |
| `therm_p[0:5]`, `therm_n[0:5]` | output | Thermometer code, three bits per phase: index 3 x phase + k, at -`v_thr`, 0, +`v_thr` |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 1.0 V | Supply the output levels follow. `rx_decision` sets 0.7 V |
| `v_swing` | 0.3 V | Swing of each output leg |
| `v_cm` | `vdd` - `v_swing`/2 | Common mode of the references and of the outputs |
| `alpha` | 0.08548 | The tap: first post-cursor / main cursor. Passed by `rx_decision`, like `v_level` and `v_thr` |
| `v_level` | 50 mV | PAM4 levels are -3, -1, +1, +3 times this |
| `v_thr` | 100 mV | Thresholds are -1, 0, +1 times this |
| `tt` | 10 ps | Output rise and fall time |
| `init_level` | 0 | Level assumed before the first symbol |

**Not modelled:** multiplexer delay and setup time on the candidates (the selection is instant), adaptation of `alpha` to the channel (it is a fixed parameter), supply pins.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- One tap: received signal r[n] = x[n] + alpha * x[n-1], with alpha = 0.08548 (first post-cursor over main cursor) (`dfe1_unrolled_hr.va`, header and parameter `alpha`)
- 24 references, ref = T + alpha * L, with T = -100, 0, +100 mV and L = -150, -50, +50, +150 mV (`dfe1_unrolled_hr.va`, header and parameters `v_thr`, `v_level`)
- Half rate: two phases, each at 14 GBd (`dfe1_unrolled_hr.va`, header)
- Timing: phase 0 samples on the rising clock edge and is resolved on the falling edge; phase 1 samples on the falling edge and is resolved on the rising edge. Each selection therefore reads the other phase's result half a clock period after it was made (`dfe1_unrolled_hr.va`, header)
- Output: a 3-bit thermometer code per phase, at -100, 0 and +100 mV (`dfe1_unrolled_hr.va`, header)
- Output levels: each leg swings 0.3 V around `vdd` - 0.15 V, edges 10 ps in the model (`dfe1_unrolled_hr.va`, parameters `v_swing`, `v_cm`, `tt`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/dfe1_unrolled_hr_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
