# prbs_gray_src

| Field | Value |
|---|---|
| Owner (from git history) | oDNA |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/prbs_gray_src.va`](../../va/Transmitter/prbs_gray_src.va) |
| Used in | [tx_top](tx_top.md), once (`u_prbs`) |
| Section | [Transmitter](README.md) |

## Architecture

The transmitter's PRBS7 data source. On every rising edge of the word clock it puts out the next 64 bits of the sequence, packed as 32 Gray-coded PAM4 symbols.

- Sequence: a 7-bit shift register with feedback from bits 6 and 5 (x^7 + x^6 + 1), repeating every 127 bits. It starts, and restarts on reset, in the all-ones state.
- A symbol takes two successive PRBS bits, `hi` then `lo`, and goes out as (`hi`, `hi` XOR `lo`): MSB wire, then LSB wire. The first symbol of a word is on `gray_out[63:62]`, the last on `gray_out[1:0]`.
- Going up the levels -3, -1, +1, +3 of [pam4_driver](pam4_driver.md), the PRBS bits (`hi`, `lo`) read 00, 01, 11, 10 and the wires (MSB, LSB) 00, 01, 10, 11.

In [tx_top](tx_top.md), clocked by `clk0p875` from [tx_clkgen](../Clocking/tx_clkgen.md). The odd wires (MSBs) go to the MSB [tx_ser_ffe_path](tx_ser_ffe_path.md), the even wires (LSBs) to the LSB path.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `clk` | input | Word clock, 0.875 GHz, CMOS |
| `reset` | input | Reset, active high, read on the rising clock edge |
| `gray_out[63:0]` | output | The word: 32 symbols of 2 bits, CMOS levels |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vhi` | 0.7 V | Output high level |
| `vth` | 0.35 V | Threshold of `clk` and `reset` |
| `tedge` | 5 ps | Output edge time |

**Not modelled:** delay other than the edge time, supply pins. After a clock edge with `reset` high the outputs are all 0.

**Checked by:** [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, ideal clocks).

## Topology research

*To be filled in by the owner.*

Known from the model (defaults are assumptions to confirm):

- PRBS7, polynomial x^7 + x^6 + 1 (`prbs_gray_src.va`, header)
- 64 PRBS bits per clock, grouped into 32 Gray-coded symbols; the first symbol is on `gray_out[63:62]` (`prbs_gray_src.va`, header)
- Gray pair per symbol: (first bit, first bit XOR second bit) (`prbs_gray_src.va`, code comment)
- Word clock 0.875 GHz (`tx_top.va`, header)
- Reset: active high, synchronous, back to the all-ones state (`prbs_gray_src.va`, header and code)
- Output levels CMOS 0 to 0.7 V, edges 5 ps in the model (`prbs_gray_src.va`, parameters `vhi`, `tedge`)

To add: missing requirements (supply, load, power, area, noise) with sources; candidate topologies with pros and cons; the choice and the reason; a schematic (`../img/prbs_gray_src_<what>.svg`); open questions; references.

## Sizing research

*To be filled in by the owner once the topology is chosen.*

Target specs (with source), sizing method, device table, results against the targets, corners checked, open issues.
