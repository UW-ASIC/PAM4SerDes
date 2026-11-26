# clk_bias

| Field | Value |
|---|---|
| Owner | Omar ElSawy |
| Kind | leaf (behavioural model) |
| Model | [`va/Biasing/clk_bias.va`](../../va/Biasing/clk_bias.va) |
| Used in | [`pam4_serdes`](../README.md), once (`u_ckb`) |
| Section | [Biasing](README.md) |

## Architecture

Turns one reference current into one 100 uA reference for every clocking cell that needs a bias, one wire per consumer. Each consumer mirrors its copy up to the current it needs.

`iref` comes from [bias_ref](bias_ref.md). The clocking cells have no bias pin yet, so the twelve outputs end at the top level. Every output scales with the reference current received.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vdd`, `vss` | inout | Supply (0.7 V) and ground |
| `en` | input | Enable (top-level `bias_en`) |
| `iref` | input | 100 uA reference. Looks like 3.5 kohm to `vss` |
| `ib_cp_tx`, `ib_cp_rx` | output | For the charge pumps of [tx_pll](../Clocking/tx_pll.md) and [rx_cdr](../Clocking/rx_cdr.md) |
| `ib_pd_rx` | output | For [cdr_pd_linear](../Clocking/cdr_pd_linear.md) |
| `ib_vco_tx`, `ib_vco_rx` | output | For the two [vco](../Clocking/vco.md) cells |
| `ib_dcc_tx`, `ib_dcc_rx` | output | For the two [dcc_cml](../Clocking/dcc_cml.md) cells |
| `ib_buf_tx`, `ib_buf_rx` | output | For the two [clkbuf_cml](../Clocking/clkbuf_cml.md) cells |
| `ib_div_tx`, `ib_div_rx[1:0]` | output | For the three [div2_cml](../Clocking/div2_cml.md) cells |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `iref_nom`, `vb_nom` | 100 uA, 0.35 V | Reference current expected, and the input's voltage at that current |
| `ib_nom` | 100 uA | Each output |
| `vdd_min`, `vdd_w` | 0.6 V, 20 mV | Supply-low gate: lowest supply for a full output, and the width of the transition |
| `ven_th`, `ven_w` | 0.35 V, 20 mV | Enable gate: threshold and width |
| `t_start` | 1 ns | Start-up time constant |
| `vdsat`, `rout_i` | 0.1 V, 1 Mohm | Compliance knee (below `vdd`) and output resistance of each output |
| `idd` | 50 uA | Supply current besides the outputs |

**Not modelled:** mismatch between the copies, noise. The block prints FAULT when its reference is more than 10 % off while enabled.

**Checked by:** [`test/tb_top.sp`](../../test/tb_top.sp), the whole top level.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Twelve outputs: 2 charge pumps, 1 phase detector, 2 VCOs, 2 duty-cycle correctors, 2 clock buffers, 3 CML dividers (`architecture.txt`)
- Charge-pump currents the models use: 100 uA in `tx_pll`, 400 uA in `rx_cdr` (their `icp` parameters)
- 100 uA per output is a placeholder until the consumers are sized

To add: the current each consumer needs, noise the charge pumps and VCOs can accept from their bias, mirror topology at 0.7 V, schematic, references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
