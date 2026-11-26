# div_n

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/div_n.va`](../../va/Clocking/div_n.va) |
| Used in | [tx_pll](tx_pll.md), once (`u_div`); [rx_cdr](rx_cdr.md), once (`u_div`) |
| Section | [Clocking](README.md) |

## Architecture

The feedback divider of a loop. A counter counts the rising edges of the 14 GHz VCO clock from 0 to `n` - 1, and the output is high during the second half of the count (50 % duty cycle for an even `n`). With `n` = 32 the output is at the reference rate, 437.5 MHz. If an input period falls outside 1/`fmax` .. 1/`fmin` the model prints a warning and keeps dividing.

In [tx_pll](tx_pll.md) and in [rx_cdr](rx_cdr.md): the input is the VCO output `ck`, the output is `ckfb`, which goes to [pfd](pfd.md) and [lock_detect](lock_detect.md). Each parent gives its instance its own jitter seed.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `ckin` | input | VCO clock, single-ended CMOS, 14 GHz |
| `ckout` | output | Divided clock, CMOS, 437.5 MHz with `n` = 32 |
| `vdd`, `vss` | inout | 0.7 V core supply and ground |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `n` | 32 | Division ratio, 2 to 1023 |
| `vth_frac` | 0.5 | Input threshold as a fraction of the supply |
| `vos` | 0 V | Input-referred offset, added to the threshold |
| `vhys` | 10 mV | Input hysteresis, full width |
| `tpd` | 150 ps | Delay from input crossing to output 50 % |
| `trf` | 30 ps | Output edge duration, 0 to 100 % (a straight ramp) |
| `rj` | 150 fs | Added random jitter per output edge, rms. The top level scales it with `rj_scale` |
| `rj_seed` | 2 | Seed of the jitter sequence; every instance needs its own |
| `rout` | 100 ohm | Output driver resistance, 0 for an ideal source |
| `fmin`, `fmax` | 11.9 GHz, 16.1 GHz | Specified input frequency range |

**Not modelled:** the internal structure (it is a counter, not a chain of divider stages), failure outside the frequency range (only warnings), correlated jitter (one independent random draw per output edge).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- Divide the 14 GHz VCO clock by 32 to 437.5 MHz (`div_n.va`, header)
- Specified input range 11.9 to 16.1 GHz (`div_n.va`, parameters `fmin`, `fmax`)
- Single-ended rail-to-rail input, threshold at half the supply (`div_n.va`, header and parameter `vth_frac`)
- Added random jitter 150 fs rms per output edge (`div_n.va`, parameter `rj`)
- Delay 150 ps from input crossing to output 50 %, output edge 30 ps (`div_n.va`, parameters `tpd`, `trf`)
- Input hysteresis 10 mV; output driver resistance 100 ohm (`div_n.va`, parameters `vhys`, `rout`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/div_n_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
