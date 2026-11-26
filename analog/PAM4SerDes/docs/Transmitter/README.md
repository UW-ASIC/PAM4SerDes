# Transmitter

The Transmitter section takes parallel data and sends it as a 28 GBd PAM4 signal: it makes the data, serializes it 32:1, applies a three-tap feed-forward equalizer (FFE) and drives the line.

![Transmitter: data source, two serializer paths, pre-drivers and driver](../img/transmitter.svg)

## How the signal moves through it

A PAM4 symbol carries two bits. The transmitter therefore has **two identical binary paths**, one for the MSB and one for the LSB, and adds them at the very end with weights 2 : 1.

1. [prbs_gray_src](prbs_gray_src.md) makes a PRBS7 pattern: 64 bits, that is 32 Gray-coded symbols, per cycle of the 0.875 GHz word clock.
2. [tx_top](tx_top.md) gives the MSB of every symbol to one [tx_ser_ffe_path](tx_ser_ffe_path.md) and the LSB to the other.
3. Each path serializes its 32 bits and makes three copies of the stream, one unit interval apart: the FFE taps.
4. Six [predriver_cml](predriver_cml.md), one per path and tap, pass the taps to the driver.
5. [pam4_driver](pam4_driver.md) sums the six taps into the output. [tx_bias](../Biasing/tx_bias.md) (Biasing section) sets how much each tap contributes.

### One path, level by level

| Level | Cell | In to out | Clock |
|---|---|---|---|
| source | [prbs_gray_src](prbs_gray_src.md) | PRBS7, 64 bits (32 symbols) per word | `clk0p875` (0.875 GHz) rising |
| L0 | [dff_cmos_x32](../Clocking/dff_cmos_x32.md) | 32 x 0.875 Gb/s, retimed | `clk0p875` rising |
| L1 | 16 x [mux2_cmos](mux2_cmos.md) | 32 to 16 lanes at 1.75 Gb/s | select `clk0p875` |
| L2 | 8 x [mux2_cmos](mux2_cmos.md) | 16 to 8 lanes at 3.5 Gb/s | select `clk1p75` |
| R | [dff_tspc_x8](../Clocking/dff_tspc_x8.md) | 8 lanes retimed | `clk3p5` rising |
| L3 | 4 x [mux2_cs](mux2_cs.md) | 8 to 4 lanes at 7 Gb/s, CMOS in, CML out | `clk3p5` |
| R | [cml_dff_x4](../Clocking/cml_dff_x4.md) | 4 lanes retimed | `clk7` rising |
| L4 | 2 x [mux2_cml_hr](mux2_cml_hr.md) | 4 to 2: even and odd streams at 14 Gb/s | select `clk7` |
| TG | [ffe_tapgen_hr](ffe_tapgen_hr.md) | pre / main / post taps, even and odd, at 14 Gb/s | `clk14` |
| FIN | 3 x [mux2_cml_hr](mux2_cml_hr.md) | one 2:1 per tap: pre, main, post at 28 Gb/s | `clk14` |

Then, per tap and path: [predriver_cml](predriver_cml.md) (6 in total), then [pam4_driver](pam4_driver.md).

Rate check per path: 32 x 0.875 = 16 x 1.75 = 8 x 3.5 = 4 x 7 = 2 x 14 = 1 x 28 Gb/s.

### FFE

Three taps, made at half rate. The taps are x[n] (pre), x[n-1] (main) and x[n-2] (post). The weights are 0.05, 0.80 and 0.15; pre and post are subtracted.

### PAM4 levels and Gray coding

The MSB path carries twice the current of the LSB path, which gives the levels -3, -1, +1, +3. The two PRBS bits of a symbol (`hi`, `lo`) go out as MSB = `hi` and LSB = `hi` XOR `lo`, so going up the levels the PRBS bits read 00, 01, 11, 10.

### Swing

[tx_bias](../Biasing/tx_bias.md) sinks 16 mA in total from the driver's six tail nodes. Into 25 ohm that is 0.4 V peak, or 0.8 V peak-to-peak differential. The split is MSB : LSB = 10.67 mA : 5.33 mA.

### Lane order

Wire j of a path's 32-bit word carries time slot j, and slot 0 is sent first.

## Blocks

| Block | Kind | Owner (from git history) | Purpose |
|---|---|---|---|
| [tx_top](tx_top.md) | structural | Omar El-Sawy (integration) | The complete transmitter: clock tree, data source, two serializer paths, pre-drivers, driver and bias |
| [tx_ser_ffe_path](tx_ser_ffe_path.md) | structural | Omar El-Sawy (integration) | One binary path: 32:1 serializer and the three half-rate FFE taps |
| [prbs_gray_src](prbs_gray_src.md) | leaf | oDNA | Test data source: PRBS7, 64 bits (32 Gray-coded symbols) per word clock |
| [mux2_cmos](mux2_cmos.md) | leaf | oDNA | CMOS 2:1 multiplexer for the two slowest serializer levels |
| [mux2_cs](mux2_cs.md) | placeholder | none yet | **Placeholder.** Ideal charge-steering 2:1 multiplexer: 3.5 to 7 Gb/s, CMOS in, CML out |
| [mux2_cml_hr](mux2_cml_hr.md) | leaf | hdsouza13 | CML 2:1 multiplexer for the two fastest steps: 7 to 14 Gb/s and 14 to 28 Gb/s |
| [ffe_tapgen_hr](ffe_tapgen_hr.md) | leaf | hdsouza13 | Half-rate FFE tap generator: makes the pre, main and post taps from the even and odd 14 Gb/s streams |
| [predriver_cml](predriver_cml.md) | leaf | Zoey Situ | Buffer between each 28 Gb/s tap and the output driver. Ideal in the present model |
| [pam4_driver](pam4_driver.md) | leaf | Zoey Situ | Output stage: sums the six FFE taps into the differential PAM4 signal on the pads |

Three kinds of cell that the transmitter uses are documented in other sections:

- the clock tree, [tx_clkgen](../Clocking/tx_clkgen.md), in Clocking,
- the retiming flops [dff_cmos_x32](../Clocking/dff_cmos_x32.md), [dff_tspc_x8](../Clocking/dff_tspc_x8.md) and [cml_dff_x4](../Clocking/cml_dff_x4.md), also in Clocking,
- the bias block, [tx_bias](../Biasing/tx_bias.md), in Biasing.

## Placeholders and gaps

- **[mux2_cs](mux2_cs.md) is a placeholder with no owner.** It is the charge-steering multiplexer of level L3, used four times per path. Someone needs to take it.
- **[predriver_cml](predriver_cml.md) is ideal** and has no bias pin, so the pre-driver tail current that `tx_bias` provides is unconnected.
- **There is no data input.** The only source is the PRBS generator.
- The channel behind `txp` / `txn` is not part of the design; a testbench supplies it.

## Conventions

- CMOS logic: single-ended, 0 / 0.7 V, threshold 0.35 V.
- CML: differential, each side 0.15 V around `vdd` - 0.15 V, so 0.6 V peak-to-peak differential.
- `vdd` is the 0.7 V core supply; `vddo` is the 1.25 V supply of the output stage.
- `rst` is active high.
