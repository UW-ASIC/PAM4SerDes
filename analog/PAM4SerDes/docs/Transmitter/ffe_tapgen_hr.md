# ffe_tapgen_hr

| Field | Value |
|---|---|
| Owner (from git history) | hdsouza13 |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/ffe_tapgen_hr.va`](../../va/Transmitter/ffe_tapgen_hr.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), once per path (`u_tg`) |
| Section | [Transmitter](README.md) |

## Architecture

Makes the three FFE taps at half rate. From the even stream E[k] = x[2k] and the odd stream O[k] = x[2k+1], each at 14 Gb/s, it puts out pre = x[n], main = x[n-1] and post = x[n-2], each as an even and an odd half. Three [mux2_cml_hr](mux2_cml_hr.md) outside this block join the halves at 28 Gb/s.

- Inputs are sampled on the rising clock edge. The odd outputs update on the rising edge and the even outputs on the falling edge, so each bank changes while the final multiplexer is looking at the other one. `rst` high clears all stored bits, even when the clock is stopped.
- Weights and signs are not applied here: the six outputs are CML pairs with the same swing. [tx_bias](../Biasing/tx_bias.md) sets the weights through the driver's tail currents, and [pam4_driver](pam4_driver.md) subtracts pre and post.

In [tx_ser_ffe_path](tx_ser_ffe_path.md): inputs from the two level-L4 [mux2_cml_hr](mux2_cml_hr.md), clock `clk14` from [tx_clkgen](../Clocking/tx_clkgen.md), outputs to the three final [mux2_cml_hr](mux2_cml_hr.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `de_p/n`, `do_p/n` | input | Even and odd data streams, 14 Gb/s each, CML |
| `clk_p`, `clk_n` | input | 14 GHz CML clock |
| `rst` | input | Reset, asynchronous, active high, relative to `vss` |
| `pre_e_p/n`, `pre_o_p/n`, `main_e_p/n`, `main_o_p/n`, `post_e_p/n`, `post_o_p/n` | output | Pre-cursor, main and post-cursor tap, each as an even and an odd half |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `itail` | 1.5 mA | Tail current per differential output pair |
| `rload` | 200 ohm | Load per leg to `vdd`. With `itail` the unloaded swing is 0.6 V peak-to-peak differential |
| `t_cq` | 2 ps | Delay from the stored state to the output, including reset |
| `tr`, `tf` | 2 ps, 2 ps | Output rise and fall time |
| `vth_data`, `vth_clk` | 0 V, 0 V | Differential thresholds. `vth_clk` should match the final multiplexer's `vos_clk` |
| `vth_rst` | 0.35 V | Reset threshold, relative to `vss`. Fixed: it does not track `vdd` |
| `init_bit` | 0 | Value of all stored bits at start-up and after reset |
| `ttol`, `vtol`, `max_step` | 1 fs, 1 uV, 0.5 ps | Simulation tolerances and step bound, not circuit properties |

**Not modelled:** setup time, hold time and metastability (both inputs must be settled at the rising edge), headroom, jitter, noise. The header calls the timing and electrical defaults provisional.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Inputs: the even and the odd stream of one binary path at 14 Gb/s, captured on the rising edge of the 14 GHz clock (`ffe_tapgen_hr.va`, header)
- Outputs: three taps spaced one unit interval apart, pre = x[n], main = x[n-1], post = x[n-2], each as an even and an odd half (`ffe_tapgen_hr.va`, header)
- Each output bank is updated while the final multiplexer is not selecting it, and must settle (clock-to-output delay plus transition time) within that half-cycle (`ffe_tapgen_hr.va`, code comment)
- Six unweighted CML pairs, unloaded 0.6 V peak-to-peak differential: tail current 1.5 mA, load 200 ohm per leg (`ffe_tapgen_hr.va`, parameters `itail`, `rload`)
- Clock-to-output delay 2 ps and edges 2 ps in the model; both provisional (`ffe_tapgen_hr.va`, parameters `t_cq`, `tr`, `tf`, and header)
- Reset: asynchronous, active high, threshold fixed at 0.35 V (`ffe_tapgen_hr.va`, port comment and parameter `vth_rst`)
- Tap weights and signs are not applied here: they need a driver with all three tap inputs (`ffe_tapgen_hr.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/ffe_tapgen_hr_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
