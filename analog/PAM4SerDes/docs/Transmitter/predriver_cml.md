# predriver_cml

| Field | Value |
|---|---|
| Owner (from git history) | Zoey Situ |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/predriver_cml.va`](../../va/Transmitter/predriver_cml.va) |
| Used in | [tx_top](tx_top.md), six times (one per path and FFE tap) |
| Section | [Transmitter](README.md) |

## Architecture

Buffer between the last multiplexer of a serializer path and the output driver. It copies the polarity of its differential input to fixed output levels near the 1.25 V output-stage supply: common mode `vcm`, differential swing `vod` scaled by the bias current it receives. The file calls the levels "temp output values".

In [tx_top](tx_top.md), one per FFE tap (pre, main, post) of each path (MSB, LSB): input from a tap output of [tx_ser_ffe_path](tx_ser_ffe_path.md), output to the matching tap input of [pam4_driver](pam4_driver.md). The bias comes from `tx_predrv_bias` (see [Biasing](../Biasing/README.md)), which makes six copies of `i_pdrv` of [tx_bias](../Biasing/tx_bias.md).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `inp`, `inn` | input | One FFE tap at 28 Gb/s, differential |
| `outp`, `outn` | output | The same bit, non-inverted, at the levels set by `vcm` and `vod` |
| `ib` | input | Bias: a reference current from `tx_predrv_bias`, one wire per pre-driver. The pin loads the wire with `vb_nom / ib_nom` = 3.5 kohm to `vss`, and the output swing scales with the current received |
| `vss` | inout | Ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vcm` | 1.2 V | Output common mode. Temporary value |
| `vod` | 0.2 V | Output differential swing at the nominal bias. Temporary value |
| `ib_nom` | 100 uA | Reference current the cell expects |
| `vb_nom` | 0.35 V | Voltage of the bias pin at that current |

**Not modelled:** gain, bandwidth, delay, edge time, a supply pin. The output switches at the instant the input difference changes sign. The block prints its output voltages with `$strobe`.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Data rate 28 Gb/s: one cell per path and FFE tap, after the final multiplexer (`tx_top.va`, header)
- Input: CML from `mux2_cml_hr`, 0.6 V peak-to-peak differential around 0.55 V (`mux2_cml_hr.va`, parameters `itail`, `rload`)
- Output levels in the model, marked as temporary: common mode 1.2 V, differential swing 0.2 V (`predriver_cml.va`, comment "temp output values")
- The bias block budgets a tail current of 0.2 V / 200 ohm per cell, six cells; the 200 ohm load is marked "assumed" (`tx_bias.va`, parameters `vod_pd`, `rld_pd`, `n_pd`)
- Bias: a reference current on `ib`, one wire per cell from `tx_predrv_bias`, nominally 100 uA at 0.35 V; the output swing scales with it (`predriver_cml.va`, parameters `ib_nom`, `vb_nom`; `tx_top.va`, header)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/predriver_cml_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
