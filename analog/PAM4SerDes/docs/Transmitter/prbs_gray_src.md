# prbs_gray_src

| Field | Value |
|---|---|
| Owner (from git history) | oDNA |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/prbs_gray_src.va`](../../va/Transmitter/prbs_gray_src.va) |
| Used in | [tx_top](tx_top.md), once (`u_prbs`) |
| Section | [Transmitter](README.md) |

## Architecture

`prbs_gray_src` is the transmitter's data source. On every rising edge of the word clock it produces the next 64 bits of a PRBS7 sequence, packed as 32 PAM4 symbols.

The system needs it because the transmitter has no data input: this block is what gives the serializer something to send. A PRBS7 sequence looks random but repeats every 127 bits, so a receiver can check what it gets.

### How the model works

- The sequence comes from a 7-bit shift register with feedback from bits 6 and 5 (x^7 + x^6 + 1). It starts, and restarts on reset, in the all-ones state.
- Each symbol takes two successive PRBS bits: `hi` first, then `lo`.
- Each symbol is put out as the pair (`hi`, `hi` XOR `lo`). This is the **Gray coding**: the first wire of the pair becomes the MSB of the PAM4 symbol and the second the LSB. With it, neighbouring PAM4 levels differ in only one of the two PRBS bits.
- The first symbol of a word is on `gray_out[63:62]`, the last on `gray_out[1:0]`.

| PRBS bits (`hi`, `lo`) | MSB wire | LSB wire | PAM4 level |
|---|---|---|---|
| 0, 0 | 0 | 0 | -3 |
| 0, 1 | 0 | 1 | -1 |
| 1, 1 | 1 | 0 | +1 |
| 1, 0 | 1 | 1 | +3 |

(The level column is what [pam4_driver](pam4_driver.md) does with the two wires.)

### Where it sits

In [tx_top](tx_top.md): clocked by `clk0p875` from [tx_clkgen](../Clocking/tx_clkgen.md), reset by `rst`. [tx_top](tx_top.md) splits the word between the two [tx_ser_ffe_path](tx_ser_ffe_path.md) instances: the odd wires (the MSBs) go to the MSB path, the even wires (the LSBs) to the LSB path.

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

### What the model leaves out

It is a digital block written in Verilog-A: no delay other than the edge time, no supply pins. After a clock edge with `reset` high the outputs are all 0.

Existing testbench for the whole datapath: [`test/tb_datapath.sp`](../../test/tb_datapath.sp) (transmitter, flat test channel, receiver, on ideal clocks).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- PRBS7, polynomial x^7 + x^6 + 1 (`prbs_gray_src.va`, header)
- 64 PRBS bits per clock, grouped into 32 Gray-coded symbols; the first symbol is on `gray_out[63:62]` (`prbs_gray_src.va`, header)
- Gray pair per symbol: (first bit, first bit XOR second bit) (`prbs_gray_src.va`, code comment)
- Word clock 0.875 GHz (`tx_top.va`, header)
- Reset: active high, synchronous, back to the all-ones state (`prbs_gray_src.va`, header and code)
- Output levels CMOS 0 to 0.7 V, edges 5 ps in the model (`prbs_gray_src.va`, parameters `vhi`, `tedge`)

To be added by the owner:

- (add requirements here)

### Candidate topologies

One row per circuit you seriously considered. Two or three good candidates are enough.

| Candidate | Source / reference | Pros | Cons |
|---|---|---|---|
| | | | |

### Chosen topology

Which candidate you chose and the reasons, measured against the requirements above. Say what you gave up by not choosing the others.

### Schematic

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `prbs_gray_src_<what>.svg` (or `.png`), and reference it from this page as `![prbs_gray_src schematic](../img/prbs_gray_src_<what>.svg)`.

### Open questions

- (questions for the section lead or for neighbouring blocks' owners)

### References

- (papers, textbook sections, earlier designs; give enough detail that someone else can find them)

## Sizing research

*To be filled in by the owner during the sizing-research stage, once the topology is chosen.*

The goal of this section is to record the device sizes that meet the block's specs, how they were found, and the simulations that show it.

### Target specs

Copy the requirements from the Topology research section and turn each one into a number you can simulate.

| Spec | Target | Source |
|---|---|---|
| | | |

### Sizing method

How the sizes were found (hand calculation, gm/Id, sweep), with enough detail that someone else can repeat it.

### Devices

| Device | W/L or fingers | Bias point |
|---|---|---|
| | | |

### Simulation results

One row per spec. Name the testbench file so the result can be reproduced.

| Spec | Target | Result | Testbench | Conditions |
|---|---|---|---|---|
| | | | | |

### Corners checked

List the process, voltage and temperature corners you simulated, and say which one was worst.

### Open issues

- (specs not met yet, things left to check)
