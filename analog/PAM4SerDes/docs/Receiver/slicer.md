# slicer

| Field | Value |
|---|---|
| Owner (from git history) | Justin Fang |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/Slicer/slicer.va`](../../va/Receiver/Slicer/slicer.va) |
| Used in | [rx_decision](rx_decision.md), 24 times (`s0` .. `s23`). Also three times in [pam4_slicer](pam4_slicer.md), which is not instantiated |
| Section | [Receiver](README.md) |

## Architecture

A clocked comparator. At each rising zero crossing of `clkp` - `clkn` it decides +1 if `V(vinp, vinn) > V(vthp, vthn) + offset` and -1 otherwise, and holds that until the next crossing. The outputs sit at `v_commonmode` plus and minus half of `vswing` times the decision. The header gives the numbers the block is built around: levels of -150, -50, +50 and +150 mV, so thresholds of -100, 0 and +100 mV.

In [rx_decision](rx_decision.md), 24 instances with default parameters. `vinp` / `vinn` is the front end's output, the same for all 24. `vthp` / `vthn` comes from the slicer's own [threshold_dac](threshold_dac.md). The clock is `clk14`, connected swapped on the 12 slicers of phase 1, so they sample on the falling edge. `voutp` / `voutn` goes to [dfe1_unrolled_hr](dfe1_unrolled_hr.md), which picks 3 of each phase's 12.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vinp`, `vinn` | input | The signal to slice |
| `vthp`, `vthn` | input | The threshold, as a differential voltage |
| `clkp`, `clkn` | input | Clock; the decision is taken at its rising zero crossing |
| `voutp`, `voutn` | output | The held decision, differential |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `offset` | 0 V | Input offset, allowed -5 mV to +5 mV |
| `t_risefall` | 5 ps | Output edge time |
| `t_delay` | 0 | Delay from clock to output |
| `v_commonmode` | 0.5 V | Output common mode |
| `vswing` | 300 mV | Output swing of each side, peak to peak |

**Not modelled:** noise (the header gives a budget), regeneration and metastability (the decision is instant, however small the input), kickback, input capacitance, supply pins. The file's comment says the parameter values are placeholders. The default output common mode (0.5 V) is not the 0.55 V of the other CML cells; the DFE reads only the difference.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- PAM4 levels at the input: -150, -50, +50, +150 mV (`slicer.va`, header)
- Thresholds: -100, 0, +100 mV (`slicer.va`, header)
- DFE shifts of the thresholds: plus or minus 12.82 mV and plus or minus 4.27 mV (`slicer.va`, header)
- Two phases at 14 GHz; 24 slicers in total (`slicer.va`, header)
- Offset at most 5 mV (`slicer.va`, header and the range of `offset`)
- Noise budget 3.367 mV rms (`slicer.va`, header)
- Output is one bit of a thermometer code: the three slicers of a set give 000, 001, 011 or 111 (`slicer.va`, header)
- CML slicer: differential input, threshold, clock and output (`slicer.va`, header)
- Output levels in the model, marked as placeholders: common mode 0.5 V, swing 300 mV, edge 5 ps (`slicer.va`, parameters `v_commonmode`, `vswing`, `t_risefall`)
- Time available to the DFE behind it: the selection happens half a clock period after the sample (`dfe1_unrolled_hr.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/slicer_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
