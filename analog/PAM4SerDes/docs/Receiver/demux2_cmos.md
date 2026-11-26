# demux2_cmos

| Field | Value |
|---|---|
| Owner (from git history) | deaconsham |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/demux2_cmos.va`](../../va/Receiver/demux2_cmos.va) |
| Used in | [rx_deser_path](rx_deser_path.md), 24 per path (8 in stage 3, 16 in stage 4) |
| Section | [Receiver](README.md) |

## Architecture

CMOS 1:2 demultiplexer for the last two deserializer stages: the same function as [demux2_cml](demux2_cml.md) with single-ended, rail-to-rail signals. The clock runs at half the input bit rate: the rising edge stores the earlier bit of a pair, and the falling edge puts it on `q0` and the input at that moment, the later bit, on `q1`. Both outputs change together.

In [rx_deser_path](rx_deser_path.md), with the default parameters, which are for the 0.7 V supply: 8 in stage 3 (`clk1p75`, 3.5 to 1.75 Gb/s, inputs from the inline CML-to-CMOS conversion) and 16 in stage 4 (`clk0p875`, 1.75 to 0.875 Gb/s, outputs to the output register).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `d` | input | Data in, CMOS |
| `clk` | input | Clock at half the input bit rate, CMOS |
| `q0` | output | The earlier bit of each pair |
| `q1` | output | The later bit of each pair |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vdd` | 0.7 V | Output high level |
| `vth` | `vdd`/2 | Data and clock threshold |
| `tt` | 10 ps | Output rise and fall time |
| `init_q0`, `init_q1` | 0, 0 | Output bits at start-up |

**Not modelled:** clock-to-output delay (the output edge starts at the clock edge), setup and hold checks, jitter, supply pins.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Stage 3: 3.5 Gb/s in, two 1.75 Gb/s lanes out, clock 1.75 GHz (`demux2_cmos.va`, header)
- Stage 4: 1.75 Gb/s in, two 0.875 Gb/s lanes out, clock 0.875 GHz (`rx_deser_path.va`, instance lines)
- The clock runs at half the input bit rate; the earlier bit of each pair is stored on the rising edge, and both outputs change together on the falling edge (`demux2_cmos.va`, header)
- CMOS levels, single-ended, 0 to 0.7 V, threshold at half the supply (`demux2_cmos.va`, header and parameters `vdd`, `vth`)
- Output edge 10 ps in the model (`demux2_cmos.va`, parameter `tt`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/demux2_cmos_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
