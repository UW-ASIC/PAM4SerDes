# Changelogs

What integration changed in each person's work, and how the top level is put together.

Find your name under [Changes, person by person](#changes-person-by-person). If a file of
yours was edited, the entry says why, what changed and what you should check. If the
change is not what you would have done, say so.

Two rules were followed:

1. A cell is connected through its own ports, as its owner wrote them. Where a default
   does not fit the design (a 1.0 V logic level in a 0.7 V design), the parameter is set
   where the cell is instantiated. The cell's file is not touched.
2. A cell's file is changed only when the design cannot work otherwise. Every such change
   is listed here.

Owners are taken from the git history. Correct this file if a name is wrong.

What has been simulated, and what still does not work, is in the
[integration status](analog/PAM4SerDes/docs/status.md).

## How the top-level integration works

### The files

The design is a tree of Verilog-A files under `analog/PAM4SerDes/va/`. A file is either a
**cell** (it has behaviour, in an `analog` block) or a **structural** file (it only places
other modules and connects them).

```
pam4_serdes                 top level                               pam4_serdes.va
├─ refclk_buf  x2           reference clock receivers
├─ tx_pll                   437.5 MHz x 32 = 14 GHz
├─ tx_top                   the transmitter                         Transmitter/tx_top.va
│   ├─ tx_clkgen            14 GHz to 14, 7, 3.5, 1.75, 0.875 GHz
│   ├─ prbs_gray_src        test data, 64 bits per word
│   ├─ tx_ser_ffe_path  x2  32:1 serializer and FFE taps            Transmitter/tx_ser_ffe_path.va
│   ├─ predriver_cml  x6
│   ├─ pam4_driver
│   └─ tx_bias
├─ rx_cdr                   clock recovery
└─ rx_top                   the receiver                            Receiver/rx_top.va
    ├─ rx_afe               termination, CTLE, VGA
    ├─ rx_clkgen            14 GHz to 14, 7, 3.5, 1.75, 0.875 GHz
    ├─ rx_decision          24 slicers, DFE, 2 decoders
    ├─ rx_dec_retime  x2
    └─ rx_deser_path  x2    1:32 deserializer
```

| Structural file | Written by | State before integration |
|---|---|---|
| `pam4_serdes.va` | integration | did not exist |
| `Transmitter/tx_top.va` | integration | did not exist |
| `Transmitter/tx_ser_ffe_path.va` | integration | did not exist |
| `Receiver/rx_top.va` | integration | did not exist |
| `Clocking/tx_pll.va`, `rx_cdr.va`, `tx_clkgen.va`, `rx_clkgen.va` | Ethan Sun | complete, used as they are |
| `Receiver/rx_afe.va` | Ethan Sun | complete, used as it is |
| `Receiver/rx_decision.va` | Mehak Khan | did not compile; completed (see her section) |
| `Receiver/rx_deser_path.va` | Mehak Khan | complete, used as it is |

The four integration files contain no behaviour. Each one starts with a comment that
says what it connects and why, and that comment is the place to look first.

### What the wiring has to get right

Every cell works on its own bench. Putting them together fails in a few specific ways,
and the structural files exist to get these right:

- **Levels.** The design is 0.7 V CMOS logic and 0.6 V peak-to-peak differential CML
  around `vdd` - 0.15 V. Several cells default to 1.0 V or 1.8 V. The instance sets the
  level; the tables below list every such override.
- **Which input goes first.** A 2:1 mux sends one input, then the other. Wire `j` of a
  32-bit word must stay time slot `j` through five mux levels. The rule in
  `tx_ser_ffe_path` is: output `k` of a level takes input `k` first and input `k + N/2`
  second. One level is wired the other way round because of how its mux behaves (see
  oDNA's section).
- **Which clock edge.** Each stage has to capture the stage before it while its data is
  steady. `tx_clkgen` and `rx_clkgen` divide on falling edges so that a divided clock
  switches in the middle of the faster data. A cell that only has a rising-edge clock
  gets its differential clock connected swapped where a falling edge is needed.
- **Two phases in the receiver.** Phase 0 samples on the rising edge of the 14 GHz clock
  and phase 1 on the falling edge. Each has its own slicers, decoder and retimer. The
  deserializer needs to know which phase is the earlier symbol; `rx_top` documents and
  wires that.
- **A starting point for the simulator.** Every node needs a DC value. Two cells left a
  node floating at DC (see Winy's and Mehak's sections).

### From transmitter to receiver

- `prbs_gray_src` makes a 64-bit word every 0.875 GHz clock cycle: 32 symbols of 2 bits.
- `tx_top` splits it into an MSB word and an LSB word. Each goes through one
  `tx_ser_ffe_path`: 32 lanes at 0.875 Gb/s become one stream at 28 Gb/s, in three
  copies one symbol apart (the FFE's pre, main and post taps).
- Six `predriver_cml` buffer the six taps. `pam4_driver` adds them: the MSB path with
  twice the current of the LSB path, pre and post subtracted. `tx_bias` supplies the six
  currents, so it sets the swing, the 2:1 ratio and the tap weights.
- A testbench connects `txp` / `txn` to `rx_p` / `rx_n` through a channel.
- `rx_afe` terminates, equalises and scales the signal. `rx_decision` slices it on both
  clock phases and decodes each symbol to 2 bits. `rx_dec_retime` retimes them and two
  `rx_deser_path` turn each bit stream back into a 32-bit word.
- `rx_cdr` makes the receiver's 14 GHz clock from the data.

The block pages under [`analog/PAM4SerDes/docs/`](analog/PAM4SerDes/docs/README.md)
describe each step, with diagrams.

### How it is simulated

VerA builds one `.va` file into one device, and a device may hold at most 255 unknowns.
`tx_top` alone is far past that, so the hierarchy cannot be one device.

`.flows/tools/va_deck.py` reads the `.va` files and writes an ngspice deck:

- a module that only places modules from other files becomes a `.subckt`;
- every other module is built by `vera --emit-osdi` into an OSDI device.

The `.va` files stay the only source. Nothing generated is edited or committed.

```
./env.sh
make -C analog/PAM4SerDes/build/sim link
```

`link` builds the deck and the devices, then runs the decks in `analog/PAM4SerDes/test/`
and prints one PASS or FAIL line for each. A deck includes the generated file and places
`tx_top`, `rx_top` or the whole `pam4_serdes` as a subcircuit.

Three things a deck needs from ngspice. The header of
[`test/tb_datapath.sp`](analog/PAM4SerDes/test/tb_datapath.sp) explains each:

- version 45 or newer;
- the default solver, not `.option klu`;
- a fourth argument on `tran`, for example `tran 1p 26n 0 1m`.

### If you change your block

- Keep the port list and the parameter names, and nothing else needs to change.
- If you rename or add a port, change the instance in the file that places your cell
  (the "Used in" row of your block's page names it).
- If you change a default that is overridden at the instance, check the override.
- Run `make -C analog/PAM4SerDes/build/sim link` before you push.

## Changes, person by person

| Person | Files changed | Set where the cell is instantiated (file unchanged) |
|---|---|---|
| [Zoey Situ](#zoey-situ) | `pam4_driver.va` | |
| [Mehak Khan](#mehak-khan) | `rx_decision.va`, `vga.va` | `rx_dec_retime`, `rx_deser_path`, `vga` |
| [Winy](#winy) | `phase_aligner.va` | |
| [Ethan Sun](#ethan-sun) | `cdr_glue.va`, `div_n.va`, `div2_tspc.va` | `dff_tspc_x8`, `refclk_buf`, `tx_pll`, `rx_cdr`, the clock generators |
| [Sudhanshu Tiwari](#sudhanshu-tiwari) | `cml2cmos.va`, `dcc_cml.va`, `loop_filter_rc.va` | `dff_cmos_x32`, `cml_dff_x4` |
| [GreenBlueFish](#greenbluefish) | `pfd.va`, `vco.va` | |
| [oDNA](#odna) | none | `mux2_cmos` |
| [hdsouza13](#hdsouza13) | none | |
| [Krrish Lala](#krrish-lala) | none | `tx_bias` |
| [Kayhan Baig](#kayhan-baig) | none | `pam4_dec` |
| [deaconsham](#deaconsham) | none | `dfe1_unrolled_hr` |
| [Justin Fang](#justin-fang) | none | |

All paths below are under `analog/PAM4SerDes/va/`.

### Zoey Situ

#### `Transmitter/pam4_driver.va`: FFE taps and tail currents (changed)

**Why.** The driver took one MSB and one LSB input and set its own swing. Two other
blocks could not connect to it:

- `ffe_tapgen_hr` produces three taps per path (pre, main, post). Its own header says
  the tap weights and the PAM4 sum "require a downstream driver with all three tap
  inputs".
- `tx_bias` produces six tail currents, one per path and tap, that were going nowhere.

**What changed.**

- Ports. Was `(msbp, msbn, lsbp, lsbn, outp, outn)`. Now, in this order: the six
  differential tap inputs `msb_pre`, `msb_main`, `msb_post`, `lsb_pre`, `lsb_main`,
  `lsb_post` (each `_p` and `_n`), the six tail pins `i_msb_pre` ... `i_lsb_post`, then
  `outp`, `outn`, `vss`.
- The driver holds each tail pin at `vtail` (0.6 V) so that `tx_bias` can sink its
  current there, and reads that current.
- Output: each tap steers its tail current by the sign of its input, exactly as the
  MSB and LSB inputs did before. Pre and post subtract. The differential output is the
  steered current times `rload` (25 Ω: the 50 Ω termination in parallel with the 50 Ω
  line).
- Parameters. `vppd` is gone: the swing is `tx_bias`'s to set. New: `rload`, `vtail`.
  `vcm` is unchanged.
- The `//!` self-test lines were renamed to the new ports. Run alone, nothing feeds the
  tail pins, so it prints `VDIFF = 0`. The levels are checked with `tx_bias` attached in
  `test/tx_driver_test.sp`.

**What stays the same.** The model is still ideal: the inputs are compared, the output
is an ideal voltage, the 2:1 MSB:LSB weighting and the level order are as before (they
now come from the 2:1 currents). With FFE off and nominal bias, `tx_driver_test.sp`
measures -0.3997, -0.1332, +0.1333, +0.3998 V: the four levels the original produced.

**For you to check.** Whether holding the tail nodes at a fixed `vtail` and using a
fixed `rload` is the model you want, or whether the driver should have a real
termination to a supply.

#### `Transmitter/predriver_cml.va` (not changed)

Placed six times in `tx_top`, one per path and tap, with its defaults.

### Mehak Khan

#### `Receiver/rx_decision.va`: completed (changed)

**Why.** The file did not compile and was unfinished:

- it included `slicer.va`, which lives in `Slicer/slicer.va`;
- it instantiated 6 of the 24 slicers, under three names used twice (`s0`, `s1`, `s2`);
- it instantiated one of the two decoders;
- it converted the DFE's differential outputs to 1.8 V single-ended logic in its own
  analog block. The rest of the design is 0.7 V.

**What changed.**

- All 24 slicers, `s0` to `s23`, numbered the way `dfe1_unrolled_hr` numbers its
  reference and candidate buses. Phase 1's slicers get the clock swapped, as the
  original did.
- Both decoders, `dec0` and `dec1`.
- No analog block. Each decoder reads the positive leg of the DFE's thermometer output
  and compares it with the DFE's output common mode (`vdd - 0.15` V). The negative legs
  are unconnected. This is a parameter override on `pam4_dec`, not a new cell.
- New parameters `vdd` (0.7), `alpha`, `v_level`, `v_thr`, passed to the DFE, so the top
  level can set the DFE tap.
- Include guard and the corrected include path.

**What stays the same.** The port list, the positional connection style and the
partition: slicers, DFE and decoders here, retiming in `rx_dec_retime`.

#### `Receiver/vga.va`: input resistance (changed)

**Why.** `ctle` drives only the voltage *between* its two outputs, and `vga` drew no
input current. The two nodes between them had no path to any reference, so ngspice
reports a singular matrix at `ctle_n` and cannot start.

**What changed.** `vga` already declared `r_in = 1e9` and did not use it. It now puts
that resistance from each input to ground. Five lines; nothing else.

**For you and Kayhan to check.** The CTLE's output common mode is now 0 V, set only by
this resistor. One of the two blocks should define it.

#### Set where your cells are instantiated (files not changed)

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `rx_dec_retime` | `rx_top`, once per phase | `vth_data` = 0.35, `vdd` = 0.7 | Defaults are 0.9 V and 1.0 V. |
| `rx_deser_path` | `rx_top`, once per binary path | `vdd_cmos` = 0.7 | Same as the default, tied to the supply parameter. |
| `vga` | `rx_afe` (Ethan's skeleton, already there) | gain range, 0 to 0.7 V control, 0.55 V output common mode | Defaults assume a 1 V supply. |

Two wiring notes:

- The phase-1 retimer is clocked on the falling edge by connecting its clock swapped.
- `rx_deser_path`'s comments call its first input "phase 0". `rx_top` connects phase 1
  there. With these retimers the phase-1 output is the earlier symbol of each pair at
  the moment the first demux samples; the header of `rx_top.va` explains. With the
  inputs the other way round the 64 output wires came out in the wrong order.

### Winy

#### `Clocking/phase_aligner.va`: start value for the integrator (changed)

**Why.** The loop's capacitor is fed only by a current source, so the circuit has no DC
operating point: ngspice reports a singular matrix at `vi_ou` and cannot start. The
block's own test avoids this with `uic`. That is not usable for the whole design, where
the PLL and CDR loops need the operating point for their starting control voltage.

**What changed.** In the `capacitor` helper: at the DC operating point the capacitor is
held at `v0` (new parameter, default 0 V); in transient it integrates as before.
`rx_cdr` and `tx_pll` already do the same for their control voltages.

**What stays the same.** A transient that starts from 0 V, which is what `uic` gave.
Your own test, `test/pa_test.sp`, gives the same three numbers with the original file
and with this one (`tgap` 35.37 ps, capacitor voltage 33.91 mV at 1 ns and 73.83 mV at
the end).

#### `Clocking/cdr_pd_linear.va` (not changed)

Placed once, in `rx_cdr`. See [Clock recovery](#clock-recovery-the-detector-and-the-loop-disagree-on-sign)
below: the detector works as your test shows, but the loop it sits in pushed the clock
away from the detector's lock point. A parameter of `rx_cdr` is set at the top level to
put that right; your file is as you wrote it.

**Also for you to check.** `phase_aligner.va` and `cdr_pd_linear.va` each define the
same four helper modules (`delay_t3`, `mult_1`, `mult_2`, `vi_converter`). They are
identical today. When both files are in one design the later definition is used for
both, so editing one copy silently changes the other block. They belong in one shared
file.

### Ethan Sun

#### `Clocking/cdr_glue.va`: `diff2se` in its own file (changed)

**Why.** `tx_top` needs `diff2se`: the phase aligner reads a single-ended signal and
the data it watches is differential. VerA builds the first module in a file that
nothing instantiates. Including all of `cdr_glue.va` made that `qdelay`, so `tx_top.va`
built the wrong module.

**What changed.** The `diff2se` module moved, unchanged, to `Clocking/diff2se.va`.
`cdr_glue.va` includes it, so `rx_cdr.va` needs no change.

#### `Clocking/div_n.va`, `Clocking/div2_tspc.va`: include guards (changed)

**Why.** Each file is included by two parents (`div2_tspc.va` by `tx_clkgen.va` and
`rx_clkgen.va`, `div_n.va` by `tx_pll.va` and `rx_cdr.va`). Once one design includes
both parents, VerA warns that the module "is defined again".

**What changed.** `` `ifndef PAM4_<NAME>_VA `` and `` `define `` at the top, `` `endif ``
at the bottom: the convention your newer files already use. Nothing else.

#### Set where your cells are instantiated (files not changed)

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `dff_tspc_x8` | `tx_ser_ffe_path` | `rj` = 200 fs x `rj_scale` | Same as the default at `rj_scale` = 1. Lets the top-level jitter knob reach it. |
| `refclk_buf` | `pam4_serdes`, twice | `rj` = 100 fs x `rj_scale`, seeds 1 and 11 | Same as the default; separate noise for the two. |
| `tx_pll`, `rx_cdr` | `pam4_serdes` | `rj_div` = 150 fs x `rj_scale` | Same as the default. |
| `tx_clkgen`, `rx_clkgen` | `tx_top`, `rx_top` | `rj_scale` | Passed down from the top. |
| `rx_cdr` | `pam4_serdes` | `tq` = 53.571 ps (default 17.857 ps) | With the default the loop settles with the clock edges on the data transitions. See [Clock recovery](#clock-recovery-the-detector-and-the-loop-disagree-on-sign). |

Your skeletons `tx_pll`, `rx_cdr`, `tx_clkgen`, `rx_clkgen` and `rx_afe` are used as
they are. Two things in them need your attention: the `tq` override above, and "The PLL
past lock" on the status page.

### Sudhanshu Tiwari

#### `Clocking/cml2cmos.va`, `Clocking/dcc_cml.va`, `Clocking/loop_filter_rc.va`: include guards (changed)

**Why.** Each file is included by two parents (for example `dcc_cml.va` by
`tx_clkgen.va` and `rx_clkgen.va`). Once one design includes both parents, VerA warns
that the module "is defined again".

**What changed.** `` `ifndef PAM4_<NAME>_VA `` and `` `define `` at the top, `` `endif ``
at the bottom. Nothing else.

#### Set where your cells are instantiated (files not changed)

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `dff_cmos_x32` | `tx_ser_ffe_path` | `vth_clk`, `vth_data` = 0.35, `vhigh` = 0.7, `t_rise`, `t_fall` = 20 ps | Defaults are 0.5 V thresholds, a 1.0 V output and zero edge time. |
| `cml_dff_x4` | `tx_ser_ffe_path` | `vcm` = 0.55, `vdiff` = 0.3, `t_rise`, `t_fall` = 5 ps | Defaults are 0.6 V / 0.2 V and zero edge time; the other CML is 0.55 V / 0.3 V. |

Both are connected pin by pin, because they have one pin per bit and no supply pins.

### GreenBlueFish

#### `Clocking/pfd.va`, `Clocking/vco.va`: include guards (changed)

**Why.** Both files are included by `tx_pll.va` and by `rx_cdr.va`. Once one design
includes both, VerA warns that the module "is defined again".

**What changed.** `` `ifndef PAM4_<NAME>_VA `` and `` `define `` at the top, `` `endif ``
at the bottom. `pfd.va` also gained the newline its last line was missing. Nothing else.

### oDNA

No file changed.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `mux2_cmos` | `tx_ser_ffe_path`, 24 times | `vth` = 0.35 | Same as the default, tied to the supply parameter. |

Two wiring notes:

- **Serializer level 1.** `mux2_cmos` is a plain mux, not a latch-mux, and the word it
  reads changes on the rising edge of its select clock. So it passes `in1` first. At
  that level only, `tx_ser_ffe_path` connects the earlier slot to `in1`.
- **PRBS wires.** `prbs_gray_src` puts symbol 0 on `gray_out[63:62]`. `tx_top` splits
  the bus into the MSB and LSB words with the order reversed, so wire `j` of each word
  is time slot `j`.

### hdsouza13

No file changed and nothing overridden. `mux2_cml_hr` is placed five times and
`ffe_tapgen_hr` once in each `tx_ser_ffe_path`, with their defaults. The three taps of
`ffe_tapgen_hr` now reach the driver (see Zoey's section).

### Krrish Lala

No file changed.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `tx_bias` | `tx_top` | `w_pre`, `w_main`, `w_post` | So the top level can turn the FFE on and off. Defaults unchanged. |

The six driver tail currents now go to `pam4_driver`, which holds each tail node at
0.6 V. `i_pdrv` is unconnected until a pre-driver has a bias pin.

### Kayhan Baig

No file changed.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `pam4_dec` | `rx_decision`, once per phase | `vhigh` = 0.7, `vth` = 0.55 | Defaults are 1.8 V and 0.9 V. The decoder reads one leg of a CML signal, so its threshold is that signal's common mode. |

`ctle` is placed in `rx_afe` as it was. See the note on its output common mode in
Mehak's section.

### deaconsham

No file changed.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `dfe1_unrolled_hr` | `rx_decision` | `vdd` = 0.7, and `alpha`, `v_level`, `v_thr` from the parent | Default `vdd` is 1.0. |

`demux2_cml` and `demux2_cmos` are placed by `rx_deser_path` as they were.

### Justin Fang

No file changed and nothing overridden. `slicer` is placed 24 times in `rx_decision`.
`threshold_dac` and `pam4_slicer` are not instantiated: `dfe1_unrolled_hr` drives the
24 slicer references itself.

## Clock recovery: the detector and the loop disagree on sign

No file of Winy's or Ethan's was changed for this. One parameter is set where `rx_cdr` is
instantiated. Both owners should read this and decide where the fix belongs.

**What happened.** With `rx_cdr` as written, the loop settled and its control voltage was
steady, but the receiver's data was wrong: about 25 bit errors in every 64-bit word. The
same receiver on an ideal clock had none.

**Why.** `cdr_pd_linear`'s own test, `test/cdr_pd_linear_test.sp`, measures the average
output current at three clock positions:

| Clock edge after the data edge | Average current into the loop filter |
|---|---|
| 16.06 ps (the intended lock point) | +3.4 µA, about zero |
| 10.06 ps (clock 6 ps early) | +56 µA |
| 22.06 ps (clock 6 ps late) | -53 µA |

In `rx_cdr` a current into the loop filter raises the control voltage and the VCO runs
faster, so its edges come earlier. An early clock was therefore pushed earlier and a
late clock later. The loop left the intended lock point and settled at the detector's
other zero, half a symbol away. There the sampling edges sit on the data transitions.

**Measured in the loop**, with `test/tb_cdr.sp`. A symbol is 35.7 ps long, so the middle
of the eye is 17.9 ps from a transition.

| `tq` of `rx_cdr` | Where the data transitions fall | Result |
|---|---|---|
| 17.857 ps (its default) | 1.5 ps after a clock edge: the clock samples on the transitions | 674 errors in 26 words |
| 53.571 ps | 19.7 ps after a clock edge: the clock samples 1.8 ps from the middle | 0 errors in 35 words |

The 1.8 ps is the detector's own trim (`t18`).

**What integration did.** `rx_cdr` makes the detector's quadrature clock by delaying the
14 GHz clock by `tq`. `pam4_serdes` sets `tq` to 53.571 ps, three quarters of a period,
which is the same as a quadrature clock a quarter period *early*. That inverts the
28 GHz reference the detector builds from the two clocks, and with it the sign of the
loop. `test/tb_cdr.sp` uses the same setting.

**For Winy and Ethan to decide.** The sign can be put right in any one of three places:

- the direction of the quadrature clock (what the override does);
- the sign of the detector's output current (`vi_converter`);
- half a 28 GHz period, 17.857 ps, more or less on the detector's delay `dt4`.

Pick one, make it the default, and remove the override from `pam4_serdes.va` and
`test/tb_cdr.sp`.

## New files

Written during integration. None replaces a team member's block.

| File | What it is |
|---|---|
| `va/pam4_serdes.va` | Top level: reference buffers, TX PLL, transmitter, RX CDR, receiver. |
| `va/Transmitter/tx_top.va` | Transmitter: clock generator, PRBS source, two serializer paths, six pre-drivers, driver, bias. |
| `va/Transmitter/tx_ser_ffe_path.va` | One 32:1 serializer path with the FFE tap generator. |
| `va/Receiver/rx_top.va` | Receiver: front end, clock generator, decision, retiming, two deserializer paths. |
| `va/Transmitter/placeholders/mux2_cs.va` | Ideal placeholder for the charge-steering mux. **Nobody owns this block yet.** |
| `va/Clocking/diff2se.va` | The glue cell moved out of `cdr_glue.va`. |
| `test/prbs_chk.va` | PRBS7 checker for the received words (test equipment). |
| `test/tx_driver_test.sp` | Driver and bias together: the four levels, FFE peak and de-emphasis. |
| `test/tb_datapath.sp` | Transmitter to receiver through a flat channel, ideal clocks, with the checker. |
| `test/tb_cdr.sp` | The same, with `rx_cdr` recovering the receiver's clock from the data. |
| `.flows/tools/va_deck.py` | Turns the `.va` hierarchy into an ngspice deck (subcircuits of OSDI devices). |

## Tools and environment

- `analog/PAM4SerDes/build/sim/Makefile`: new `deck` and `link` targets.
- `.flows/env/Analog.nix`: adds VerA from the EDA-Packaged pin, with two repairs it needs
  to build and to run (the file explains them), and refuses an ngspice older than 45. The
  pinned nixpkgs already ships ngspice 45. `.flows/env/shell.nix` prints both versions
  when the shell starts.
- `.flows/tools/va_deck.py`: `VA_DECK_JOBS` sets how many devices are built at once
  (default 3; use 1 on a machine short of memory).
- `.gitignore`: `analog/*/build/sim/out/`, the generated decks, devices and logs.
- `docs/`: the site now shows the Markdown under `analog/PAM4SerDes/docs/` and this file.
