# cml2cmos

| Field | Value |
|---|---|
| Owner (from git history) | Sudhanshu Tiwari |
| Kind | leaf (behavioural model) |
| Model | [`va/Clocking/cml2cmos.va`](../../va/Clocking/cml2cmos.va) |
| Used in | [tx_clkgen](tx_clkgen.md), once (`u_c2c`); [rx_clkgen](rx_clkgen.md), once (`u_c2c`) |
| Section | [Clocking](README.md) |

## Architecture

`cml2cmos` converts a clock from CML to CMOS. It reads the sign of a differential input and drives one wire to `vdd` or to `vss`.

The system needs it at the point in each clock tree where the fast CML dividers hand over to the slower CMOS (TSPC) dividers: CML signals swing only 0.3 V per side, and CMOS logic needs the full 0 to 0.7 V.

### Where it sits

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

### What the model leaves out

The header calls it an ideal behavioural converter, and it is: the output switches at the instant the input difference crosses the threshold. There is no delay, no edge time, no jitter, no hysteresis and no duty-cycle error.

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Transmitter instance converts the 7 GHz clock (`tx_clkgen.va`, header)
- Receiver instance converts the 3.5 GHz clock (`rx_clkgen.va`, header)
- Input: CML, 0.6 V peak-to-peak differential (`div2_cml.va`, header, the cell that drives it)
- Output: single-ended CMOS between `vss` and `vdd` (`cml2cmos.va`, header)
- The model gives no delay, edge-time, jitter or duty-cycle numbers: these are for the owner to set

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `cml2cmos_<what>.svg` (or `.png`), and reference it from this page as `![cml2cmos schematic](../img/cml2cmos_<what>.svg)`.

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
