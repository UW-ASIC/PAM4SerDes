# refclk_buf

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/refclk_buf.va`](../../va/Clocking/refclk_buf.va) |
| Used in | `pam4_serdes` (top level), twice: `u_ref_tx` and `u_ref_rx` |
| Section | [Clocking](README.md) |

## Architecture

Receives the external 437.5 MHz reference clock, which arrives as a differential pair, and drives a rail-to-rail CMOS copy of it for the phase-frequency detector and the lock detector.

Two instances in `pam4_serdes`: `u_ref_tx` (pins `refclk_tx_p`, `refclk_tx_n`) drives `ckref` of [tx_pll](tx_pll.md), and `u_ref_rx` (pins `refclk_rx_p`, `refclk_rx_n`) drives `ckref` of [rx_cdr](rx_cdr.md). The top level sets `rj` to 100 fs times its `rj_scale` parameter and gives the two instances different jitter seeds (1 and 11).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin_p`, `ckin_n` | input | Differential 437.5 MHz reference from the pads |
| `ckref` | output | The same clock as single-ended CMOS, 0 V to `vdd` |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `rterm` | 100 ohm | Differential input termination, between the two pins |
| `vos` | 0 V | Receiver offset, range -0.1 to +0.1 V |
| `vhys` | 20 mV | Receiver hysteresis, full width |
| `tpd` | 50 ps | Delay from input threshold crossing to output 50 % |
| `trf` | 30 ps | Output edge duration, 0 to 100 % |
| `rj` | 100 fs | Added random jitter per edge, rms |
| `rj_seed` | 1 | Seed of the jitter sequence |
| `rout` | 100 ohm | Output driver resistance |

**Not modelled:** supply-induced and low-frequency jitter (the jitter is one independent random draw per edge), an input common-mode range (only the difference is read), dependence of delay and edge time on load, supply or input slope.

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Input: the external 437.5 MHz reference, differential (`refclk_buf.va`, header)
- Output: a rail-to-rail CMOS copy of it (`refclk_buf.va`, header)
- Differential input termination 100 ohm (`refclk_buf.va`, parameter `rterm`)
- Added random jitter 100 fs rms per edge (`refclk_buf.va`, parameter `rj`)
- Delay 50 ps from input crossing to output 50 %, output edge 30 ps (`refclk_buf.va`, parameters `tpd`, `trf`)
- Input hysteresis 20 mV full width; offset range studied -0.1 to +0.1 V (`refclk_buf.va`, parameters `vhys`, `vos`)
- Output driver resistance 100 ohm (`refclk_buf.va`, parameter `rout`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/refclk_buf_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
