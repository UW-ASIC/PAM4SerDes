# mux2_cs

| Field | Value |
|---|---|
| Owner (from git history) | none yet |
| Kind | placeholder (ideal stand-in, no owner) |
| Model | [`va/Transmitter/placeholders/mux2_cs.va`](../../va/Transmitter/placeholders/mux2_cs.va) |
| Used in | [tx_ser_ffe_path](tx_ser_ffe_path.md), four per path (level L3) |
| Section | [Transmitter](README.md) |

## Architecture

**Ideal placeholder with no owner: someone needs to take this block.** It is the 2:1 multiplexer of serializer level L3, meant to be a charge-steering cell: two 3.5 Gb/s CMOS lanes in, one 7 Gb/s CML lane out. The model is a latch-multiplexer: both inputs are captured on the rising clock edge, and the output shows `in0` while the clock is high and `in1` while it is low, so `in0` is sent first.

In [tx_ser_ffe_path](tx_ser_ffe_path.md): inputs from [dff_tspc_x8](../Clocking/dff_tspc_x8.md), outputs to [cml_dff_x4](../Clocking/cml_dff_x4.md), clocks `clk3p5` and `clk3p5b` from [tx_clkgen](../Clocking/tx_clkgen.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `in0`, `in1` | input | Two 3.5 Gb/s lanes, CMOS. Thresholds are at half the supply |
| `clk` | input | 3.5 GHz CMOS clock |
| `clkb` | input | Its complement. A real charge-steering cell needs it; the ideal model does not read it |
| `outp`, `outn` | output | One 7 Gb/s lane, CML, at the levels of [clkbuf_cml](../Clocking/clkbuf_cml.md) |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vsw` | 0.3 V | Differential output amplitude (half of the peak-to-peak value) |
| `trf` | 10 ps | Output edge duration (a straight ramp) |
| `tpd` | 40 ps | Clock edge to output zero crossing delay |

**Not modelled:** charge steering (the model is a latch with an ideal output stage), setup and hold time, jitter. The parameter values are convenient for the placeholder, not targets.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*No owner yet. To be filled in by whoever takes this block.*

Known from the model (defaults are assumptions to confirm):

- Level L3: eight 3.5 Gb/s CMOS lanes in, four 7 Gb/s CML lanes out, clock 3.5 GHz (`mux2_cs.va`, header)
- A charge-steering cell; it needs the complementary clock, which the clock tree already provides as `clk3p5b` (`mux2_cs.va`, header)
- `in0` is sent first: it appears while the clock is high (`mux2_cs.va`, header)
- Output levels like `clkbuf_cml`: 0.6 V peak-to-peak differential, each side between `vdd` - 0.3 V and `vdd` (`mux2_cs.va`, header and parameter `vsw`)
- Its load is the retiming flop `cml_dff_x4`, clocked at 7 GHz (`tx_ser_ffe_path.va`, header)
- Placeholder timing, not a target: 40 ps clock-to-output delay, 10 ps edges (`mux2_cs.va`, parameters `tpd`, `trf`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/mux2_cs_<what>.svg`); open questions; references.

## Sizing research

*No owner yet. To be filled in once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
