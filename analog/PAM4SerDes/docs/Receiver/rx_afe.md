# rx_afe

| Field | Value |
|---|---|
| Owner (from git history) | Ethan Sun (sunezh) |
| Kind | structural (wiring only) |
| Model | [`va/Receiver/rx_afe.va`](../../va/Receiver/rx_afe.va) |
| Used in | [rx_top](rx_top.md), once (`u_afe`) |
| Section | [Receiver](README.md) |

## Architecture

The receiver's analog front end, three cells in a row: the termination, a continuous-time linear equalizer (CTLE) and a variable-gain amplifier (VGA).

In [rx_top](rx_top.md): `rx_p` / `rx_n` are the pads, and `out_p` / `out_n` go to the 24 slicers in [rx_decision](rx_decision.md) and to the phase detector in [rx_cdr](../Clocking/rx_cdr.md).

### Instances

| Instance | Cell | Role |
|---|---|---|
| `u_term` | [rx_term](rx_term.md) | 100 ohm across the pads and the ESD capacitance on each pad |
| `u_ctle` | [ctle](ctle.md) | Equalizer; its input is the pads |
| `u_vga` | [vga](vga.md) | Gain set by `vctrl`; drives the output at a common mode of 0.55 V |

Simplified at this level, from the header:

- The VGA gain is set by an analog voltage, `vctrl`, from 0 to 0.7 V. The `g[5:0]` gain code is not modelled yet.
- `main_boost_db` stands in for the CTLE's `bst[3:0]` code.
- Two of the VGA's defaults do not fit a 0.7 V supply and are overridden: the control range (default 0 to 1 V) and the output common mode (default 0.9 V).

### Ports

| Port | Direction | Carries |
|---|---|---|
| `rx_p`, `rx_n` | inout | PAM4 input from the pads |
| `vtt` | inout | Termination reference |
| `vctrl` | input | VGA gain control, 0 to 0.7 V |
| `out_p`, `out_n` | output | Equalized signal, centred at 0.55 V |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `rterm` | 100 ohm | Differential termination |
| `cesd` | 50 fF | ESD capacitance per side |
| `shelf_db` | 1.0 dB | CTLE low-frequency shelf |
| `main_boost_db` | 0 dB | CTLE main peaking boost (high-frequency gain over DC gain) |
| `vctrl_min`, `vctrl_max` | 0 V, 0.7 V | `vctrl` values that give the lowest and the highest VGA gain |
| `min_gain_db`, `max_gain_db` | -4.703 dB, -1.847 dB | VGA gain at `vctrl_min` and at `vctrl_max` |
| `vcm_out` | 0.55 V | VGA output common mode: `vdd` - 0.15 V, like the other CML |

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

Wiring only. See the cells: [rx_term](rx_term.md#topology-research), [ctle](ctle.md#topology-research), [vga](vga.md#topology-research).

## Sizing research

Wiring only. See the cells: [rx_term](rx_term.md#sizing-research), [ctle](ctle.md#sizing-research), [vga](vga.md#sizing-research).
