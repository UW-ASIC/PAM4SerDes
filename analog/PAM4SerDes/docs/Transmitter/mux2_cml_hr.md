# mux2_cml_hr

| Field | Value |
|---|---|
| Owner (from git history) | hdsouza13 |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/mux2_cml_hr.va`](../../va/Transmitter/mux2_cml_hr.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), five per path (two at level L4, three final multiplexers) |
| Section | [Transmitter](README.md) |

## Architecture

Differential CML 2:1 multiplexer for the two fastest serializer steps: clock high passes the EVEN input, clock low the ODD input ("hr" is half rate: the clock runs at half the output bit rate). It is transparent, so each input must remain stable throughout its selected half-cycle. Unloaded, the output is plus or minus `itail * rload` around `vdd - itail * rload / 2`.

- Level L4 (`u_l4e`, `u_l4o`), clock `clk7`: two 7 Gb/s lanes each from [cml_dff_x4](../Clocking/cml_dff_x4.md) in; the even and the odd stream at 14 Gb/s out, to [ffe_tapgen_hr](ffe_tapgen_hr.md).
- Final (`u_fin_pre`, `u_fin_main`, `u_fin_post`), clock `clk14`: the even and the odd half of one tap from [ffe_tapgen_hr](ffe_tapgen_hr.md) in; that tap at 28 Gb/s out, to a [predriver_cml](predriver_cml.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `de_p`, `de_n` | input | EVEN data, differential. A positive difference is a 1 |
| `do_p`, `do_n` | input | ODD data, differential |
| `clk_p`, `clk_n` | input | Differential clock: high selects EVEN, low selects ODD |
| `out_p`, `out_n` | output | Multiplexed data, CML |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `itail` | 1.5 mA | Total sink current per output pair, steered between the two loads |
| `rload` | 200 ohm | Load per leg to `vdd`. With `itail` the unloaded swing is 0.6 V peak-to-peak differential |
| `cout` | 5 fF | Capacitance per leg to `vss`; adds RC settling on top of `tpd` |
| `vsoft_data`, `vsoft_clk` | 10 mV, 10 mV | Switching widths of data and clock |
| `vos_data`, `vos_clk` | 0 V, 0 V | Differential offsets of data and clock |
| `tpd` | 5.934 ps | Transport delay. Marked "project estimate" |
| `max_step` | 0.5 ps | Simulation step bound, not a circuit property |

**Not modelled:** a bias input and a headroom limit (the tail current is a parameter), jitter, noise. The header calls the timing and electrical defaults provisional.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- 2 x 7 Gb/s to 14 Gb/s with a 7 GHz clock, and 2 x 14 Gb/s to 28 Gb/s with a 14 GHz clock (`mux2_cml_hr.va`, header)
- Clock high selects the EVEN input, clock low the ODD input (`mux2_cml_hr.va`, header)
- Each input must stay stable through the whole half-cycle in which it is selected (`mux2_cml_hr.va`, header)
- Unloaded output 0.6 V peak-to-peak differential: tail current 1.5 mA, load 200 ohm per leg (`mux2_cml_hr.va`, parameters `itail`, `rload`)
- Delay 5.934 ps, marked as a project estimate (`mux2_cml_hr.va`, parameter `tpd`)
- Output capacitance 5 fF per leg in the model (`mux2_cml_hr.va`, parameter `cout`)
- Timing and electrical defaults are provisional (`mux2_cml_hr.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/mux2_cml_hr_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
