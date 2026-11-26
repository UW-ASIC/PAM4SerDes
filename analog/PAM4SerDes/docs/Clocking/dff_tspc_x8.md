# dff_tspc_x8

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model); retiming flops, used in the TX serializer |
| Model | [`va/Clocking/dff_tspc_x8.va`](../../va/Clocking/dff_tspc_x8.va) |
| Used in | [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), once per path (`u_rcs`), so twice in the transmitter |
| Section | [Clocking](README.md) |

## Architecture

A bank of eight TSPC D flip-flops on one clock (one helper module `dff_tspc_1lane` per lane): each copies its input to its output on the rising clock edge. It retimes the eight 3.5 Gb/s lanes before the charge-steering multiplexers, and is kept with the clocking cells because it is a retiming element. If the data changes less than `tsu` before the clock edge, the flop takes the old value and prints a warning; a change less than `th` after the edge, or a clock period outside 1/`fmax` .. 1/`fmin`, also prints a warning.

In [tx_ser_ffe_path](../Transmitter/tx_ser_ffe_path.md), between level L2 (eight [mux2_cmos](../Transmitter/mux2_cmos.md)) and level L3 (four [mux2_cs](../Transmitter/mux2_cs.md)), clocked by `clk3p5` from [tx_clkgen](tx_clkgen.md). The parent uses the default parameters, except that it sets `rj` to 200 fs times `rj_scale`.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | 3.5 GHz CMOS clock. Flops trigger on its rising edge |
| `d[7:0]` | input | Eight data lanes in, CMOS |
| `q[7:0]` | output | Eight data lanes out, CMOS |
| `vdd`, `vss` | inout | 0.7 V core supply and ground. The thresholds are half the supply |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `tcq` | 30 ps | Delay from clock 50 % to output 50 % |
| `tsu` | 15 ps | Setup time: data stable this long before the clock edge |
| `th` | 8 ps | Hold time: data stable this long after the clock edge |
| `trf` | 25 ps | Output edge duration, 0 to 100 % (a straight ramp) |
| `rj` | 200 fs | Added random jitter per output edge, rms |
| `rj_seed` | 4 | Seed of lane 0's jitter sequence; lane i uses `rj_seed` + 100 i |
| `rout` | 100 ohm | Output driver resistance, 0 for an ideal source |
| `fmin`, `fmax` | 2.975 GHz, 4.025 GHz | Specified clock frequency range |

**Not modelled:** metastability and slow outputs (a timing violation gives a clean old value and a warning), dependence of the delays on load, supply or input slope, reset.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Eight lanes at 3.5 Gb/s, between the CMOS stages and the charge-steering stage (`dff_tspc_x8.va`, header)
- Specified clock range 2.975 to 4.025 GHz (`dff_tspc_x8.va`, parameters `fmin`, `fmax`)
- Clock-to-output delay 30 ps (`dff_tspc_x8.va`, parameter `tcq`)
- Setup time 15 ps, hold time 8 ps (`dff_tspc_x8.va`, parameters `tsu`, `th`)
- Added random jitter 200 fs rms per output edge (`dff_tspc_x8.va`, parameter `rj`)
- Output edge 25 ps, driver resistance 100 ohm (`dff_tspc_x8.va`, parameters `trf`, `rout`)
- True single-phase clock (TSPC) logic, positive-edge triggered (`dff_tspc_x8.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/dff_tspc_x8_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
