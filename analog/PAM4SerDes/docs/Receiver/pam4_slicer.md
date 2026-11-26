# pam4_slicer

| Field | Value |
|---|---|
| Owner (from git history) | Justin Fang |
| Kind | structural (3 slicers + 3 DACs, no DFE), not instantiated |
| Model | [`va/Receiver/Slicer/pam4_slicer.va`](../../va/Receiver/Slicer/pam4_slicer.va) |
| Used in | Not in the hierarchy. [rx_decision](rx_decision.md) instantiates its 24 slicers directly |
| Section | [Receiver](README.md) |

## Architecture

`pam4_slicer` is a complete PAM4 slicer for one sampling phase with no equalization: three [slicer](slicer.md)s that share the input and the clock, each with its own [threshold_dac](threshold_dac.md).

**This block is not in the hierarchy.** The receiver uses a DFE, which needs 12 slicers per phase with shifted thresholds, so [rx_decision](rx_decision.md) instantiates 24 slicers directly and lets the DFE model drive their references. `pam4_slicer` remains as the simple case: it is the only place the threshold DAC is used, and it is a way to try the slicer and the DAC together.

### Instances

| Instance | Cell | Role |
|---|---|---|
| `th_top`, `th_mid`, `th_bot` | [threshold_dac](threshold_dac.md) | Thresholds from codes 51, 32 and 13: about +98.9 mV, 0 mV and -98.9 mV |
| `top`, `mid`, `bot` | [slicer](slicer.md) | Compare the input with each threshold |

On every falling clock edge the block prints the three decisions as a thermometer code with `$strobe`. That print is the only thing in the file that is not wiring.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vinp`, `vinn` | input | The PAM4 signal |
| `clkp`, `clkn` | input | Clock; the slicers decide at its rising zero crossing |
| `voutp1`, `voutn1` | output | Decision of the top slicer |
| `voutp2`, `voutn2` | output | Decision of the middle slicer |
| `voutp3`, `voutn3` | output | Decision of the bottom slicer |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `code_top` | 51 | DAC code of the top threshold |
| `code_mid` | 32 | DAC code of the middle threshold |
| `code_bot` | 13 | DAC code of the bottom threshold |

## Topology research

This block is wiring only, so there is no circuit to choose or size here. The topology research lives in the pages of its cells: [slicer](slicer.md#topology-research), [threshold_dac](threshold_dac.md#topology-research).

## Sizing research

This block is wiring only, so there is no circuit to choose or size here. The sizing research lives in the pages of its cells: [slicer](slicer.md#sizing-research), [threshold_dac](threshold_dac.md#sizing-research).
