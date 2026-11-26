# threshold_dac

| Field | Value |
|---|---|
| Owner (from git history) | Justin Fang |
| Kind | leaf (behavioural model) |
| Model | [`va/Receiver/Slicer/threshold_dac.va`](../../va/Receiver/Slicer/threshold_dac.va) |
| Used in | [rx_decision](rx_decision.md), 24 times (`d0` .. `d23`, one per slicer). Also three times in [pam4_slicer](pam4_slicer.md), which is not instantiated |
| Section | [Receiver](README.md) |

## Architecture

Turns a 6-bit code into the threshold voltage of one slicer: `vth = vmin + code * (vmax - vmin) / 64`, put out as `v_commonmode` plus and minus half of `vth`. With the defaults one step is about 5.2 mV and code 32 gives exactly 0 mV. Plus or minus 100 mV cannot be hit exactly: codes 51 and 13 come to about plus and minus 98.9 mV.

In [rx_decision](rx_decision.md), one per [slicer](slicer.md), driving its `vthp` / `vthn`. Each DAC gets the code nearest to the reference its slicer needs, so the reference is up to 2.6 mV from the ideal value.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vthp`, `vthn` | output | The threshold, as a differential voltage around `v_commonmode`. There are no inputs: the code is a parameter |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `code` | 32 | Which of the 64 settings to use, 0 to 63 |
| `vmin`, `vmax` | -0.1666 V, +0.1666 V | Ends of the output range |
| `v_commonmode` | 0.5 V | Midpoint of the output pair |

**Not modelled:** a way to set the code at run time (the file's comment marks the parameter as a placeholder and says to ask how the code gets set), nonlinearity (the steps are perfectly even), noise, settling time, output resistance. The block prints the code and the threshold with `$strobe`.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Range -166.6 mV to +166.6 mV, 6 bits, 64 settings (`threshold_dac.va`, header)
- One DAC per slicer, set to the code closest to the threshold that slicer needs (`threshold_dac.va`, header)
- With this range and resolution it reaches 0 mV exactly but not plus or minus 100 mV exactly (`threshold_dac.va`, header)
- The thresholds to reach: -100, 0, +100 mV, each shifted by the DFE by plus or minus 12.82 mV or plus or minus 4.27 mV (`slicer.va`, header)
- 24 slicers need a threshold each (`slicer.va`, header)
- In the hierarchy each DAC gets the nearest of its 64 codes, so its reference is up to half a step, 2.6 mV, from the ideal value (`rx_decision.va`, header)
- How the code gets set is open: the file's comment says to ask the lead (`threshold_dac.va`, comment on `code`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/threshold_dac_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
