# cml2cmos

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/cml2cmos.va`](../../va/Clocking/cml2cmos.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_c2c`); [rx_clkgen](rx_clkgen.md), once (`u_c2c`) |
| Section | [Clocking](README.md) |

## Architecture

Converts a clock from CML to CMOS: it reads the sign of a differential input and drives one wire to `vdd` or to `vss`. It sits at the point in each clock tree where the CML dividers hand over to the CMOS (TSPC) dividers: CML signals swing only 0.3 V per side, and CMOS logic needs the full 0 to 0.7 V.

- In [tx_clkgen](tx_clkgen.md): it converts the 7 GHz `clk7`. Its input comes from a [div2_cml](div2_cml.md), its output goes to [phase_aligner](phase_aligner.md).
- In [rx_clkgen](rx_clkgen.md): it converts the 3.5 GHz `clk3p5`. Its input comes from a [div2_cml](div2_cml.md), its output goes to the first [div2_tspc](div2_tspc.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | Differential CML clock |
| `out` | output | CMOS clock: `vdd` when the input difference is positive, `vss` otherwise |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vth_diff` | 0 V | Differential decision threshold |

**Not modelled:** delay, edge time, jitter, hysteresis, duty-cycle error. The header calls it an ideal behavioural converter: the output switches at the instant the input difference crosses the threshold.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Transmitter instance converts the 7 GHz clock (`tx_clkgen.va`, header)
- Receiver instance converts the 3.5 GHz clock (`rx_clkgen.va`, header)
- Input: CML, 0.6 V peak-to-peak differential (`div2_cml.va`, header, the cell that drives it)
- Output: single-ended CMOS between `vss` and `vdd` (`cml2cmos.va`, header)
- The model gives no delay, edge-time, jitter or duty-cycle numbers: these are for the owner to set

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/cml2cmos_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
