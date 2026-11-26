# glue

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | glue (ideal wiring cells) |
| Model | [`va/Clocking/cdr_glue.va`](../../va/Clocking/cdr_glue.va) and [`va/Clocking/diff2se.va`](../../va/Clocking/diff2se.va) |
| Used in | [rx_cdr](rx_cdr.md): `diff2se` twice, `qdelay` once, `nor2` once; [tx_top](../Transmitter/tx_top.md): `diff2se` once |
| Section | [Clocking](README.md) |

## Architecture

Three small cells that the models' headers call ideal glue: wiring or trivial logic that is not drawn as a block.

| Cell | File | What it does | Why it exists |
|---|---|---|---|
| `diff2se` | `va/Clocking/diff2se.va` | Differential to single-ended: `V(out) = V(p) - V(n)` | [cdr_pd_linear](cdr_pd_linear.md) and [phase_aligner](phase_aligner.md) read single-ended signals around 0 V; the data and clocks they watch are differential |
| `qdelay` | `va/Clocking/cdr_glue.va` | A pure delay, a quarter of the 14 GHz period by default | `cdr_pd_linear` needs a quadrature copy of the 14 GHz clock, and the architecture drawing the headers refer to (`Detailed.png`) has no quadrature source |
| `nor2` | `va/Clocking/cdr_glue.va` | An ideal NOR gate: `y = vdd * (1 - a) * (1 - b)`, with `a` and `b` scaled to 0..1 | Makes the charge-pump enable of the receiver's frequency loop |

`diff2se` was moved to its own file during integration, unchanged, so that `tx_top` can include it without the other two cells.

| Parent | Instance | Cell | Role |
|---|---|---|---|
| [rx_cdr](rx_cdr.md) | `u_dse` | `diff2se` | Analog front end output to `cdr_pd_linear`'s data input |
| [rx_cdr](rx_cdr.md) | `u_cse` | `diff2se` | `clk14_p/n` to `cdr_pd_linear`'s in-phase clock |
| [rx_cdr](rx_cdr.md) | `u_q` | `qdelay` | In-phase clock to quadrature clock |
| [rx_cdr](rx_cdr.md) | `u_en` | `nor2` | `lock`, `force_lock` to the [charge_pump](charge_pump.md) enable |
| [tx_top](../Transmitter/tx_top.md) | `u_pa` | `diff2se` | MSB path's retimed 7 Gb/s lane 0 to `phase_aligner`'s data input |

### Ports

| Cell | Port | Direction | Carries |
|---|---|---|---|
| `diff2se` | `p`, `n` | input | Differential signal |
| `diff2se` | `out` | output | The difference, relative to `vss` |
| `qdelay` | `in` | input | Signal to delay |
| `qdelay` | `out` | output | The same signal, `td` later |
| `nor2` | `a`, `b` | input | Logic inputs, 0 V to `vdd` |
| `nor2` | `y` | output | NOR of the inputs |
| `diff2se`, `qdelay` | `vss` | inout | Ground |
| `nor2` | `vdd`, `vss` | inout | Supply and ground |

The only parameter is `td` of `qdelay`: default 17.857 ps, a quarter of the 14 GHz period. `rx_cdr` passes its `tq`.

**Not modelled:** everything a real cell adds (gain, delay and offset of a differential-to-single-ended stage, phase error of a quadrature clock, gate delay).

## Topology research

For each cell, first decide whether the real circuit needs a cell there at all, and record that decision here.

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- `qdelay`: a quarter of the 14 GHz period, 17.857 ps (`cdr_glue.va`, parameter `td`)
- `nor2`: pump enable = NOT (`lock` OR `force_lock`) (`rx_cdr.va`, header)
- `diff2se`: the detectors behind it read single-ended signals around 0 V; the data and clocks they watch are differential (`diff2se.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/glue_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
