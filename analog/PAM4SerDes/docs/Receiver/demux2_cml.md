# demux2_cml

| Field | Value |
|---|---|
| Owner (from git history) | deaconsham |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/demux2_cml.va`](../../va/Receiver/demux2_cml.va) |
| Used in | [rx_deser_path](rx_deser_path.md), six per path (two in stage 1, four in stage 2) |
| Section | [Receiver](README.md) |

## Architecture

CML 1:2 demultiplexer for the first two deserializer stages. The clock runs at half the input bit rate: the rising edge stores the earlier bit of a pair, and the falling edge puts it on `q0` and the input at that moment, the later bit, on `q1`. Both outputs change together.

In [rx_deser_path](rx_deser_path.md), with the default parameters (note the default `vdd` of 1.0 V): two in stage 1 (`clk7`, 14 to 7 Gb/s, inputs from the two [rx_dec_retime](rx_dec_retime.md)) and four in stage 2 (`clk3p5`, 7 to 3.5 Gb/s, outputs to the inline CML-to-CMOS conversion).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d_p`, `d_n` | input | Data in, differential, compared at 0 V difference |
| `clk_p`, `clk_n` | input | Clock at half the input bit rate |
| `q0_p/n` | output | The earlier bit of each pair |
| `q1_p/n` | output | The later bit of each pair |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 1.0 V | Supply the output levels follow. Not overridden in the hierarchy |
| `v_swing` | 0.3 V | Swing of each output leg |
| `v_cm` | `vdd` - `v_swing`/2 | Output common mode |
| `tt` | 10 ps | Output rise and fall time |
| `init_q0`, `init_q1` | 0, 0 | Output bits at start-up |

**Not modelled:** clock-to-output delay (the output edge starts at the clock edge), setup and hold checks, jitter, noise, bias and supply pins.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Stage 1: 14 Gb/s in, two 7 Gb/s lanes out, clock 7 GHz (`demux2_cml.va`, header)
- Stage 2: 7 Gb/s in, two 3.5 Gb/s lanes out, clock 3.5 GHz (`rx_deser_path.va`, instance lines)
- The clock runs at half the input bit rate; the earlier bit of each pair is stored on the rising edge, and both outputs change together on the falling edge (`demux2_cml.va`, header)
- Differential signals; each output leg swings 0.3 V around `vdd` - 0.15 V (`demux2_cml.va`, header and parameters `v_swing`, `v_cm`)
- Output edge 10 ps in the model (`demux2_cml.va`, parameter `tt`)
- Stage 1 samples just after the 14 GHz clock's rising edge, because the 7 GHz clock toggles there (`rx_top.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/demux2_cml_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
