# Changelogs

What integration changed in each person's work, and how the top level is put together. Find your name under [Changes, person by person](#changes-person-by-person): an entry says why a file was edited, what changed and what to check. If a change is not what you would have done, say so.

Two rules were followed:

1. A cell is connected through its own ports, as its owner wrote them. Where a default does not fit the design (a 1.0 V logic level in a 0.7 V design), the parameter is set where the cell is instantiated; the cell's file is not touched.
2. A cell's file is changed only when the design cannot work otherwise. Every such change is listed here.

Owners are taken from the git history; correct this file if a name is wrong. What is simulated on every change, and what it measured, is in the [README](README.md#measured-specs).

## How the top-level integration works

### The files

The design is a tree of Verilog-A files under `analog/PAM4SerDes/va/`, drawn in the [design documentation](analog/PAM4SerDes/docs/README.md#hierarchy). A **cell** has behaviour, in an `analog` block. A **structural** file only places other modules and connects them.

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

Each integration file starts with a comment that says what it connects and why: look there first.

### What the wiring has to get right

Cells that work on their own bench fail together in a few specific ways. The structural files get these right:

- **Levels.** The design is 0.7 V CMOS logic and 0.6 V peak-to-peak differential CML around `vdd` - 0.15 V. Cells that default to 1.0 V or 1.8 V are set at the instance; the tables below list every override.
- **Which input goes first.** Wire `j` of a 32-bit word must stay time slot `j` through five mux levels: in `tx_ser_ffe_path`, output `k` of a level takes input `k` first and input `k + N/2` second. One level is wired the other way round (see oDNA's section).
- **Which clock edge.** Each stage must capture the one before it while its data is steady, so `tx_clkgen` and `rx_clkgen` divide on falling edges: a divided clock switches in the middle of the faster data. A cell with only a rising-edge clock gets its differential clock connected swapped where a falling edge is needed.
- **Two phases in the receiver.** Phase 0 samples on the rising edge of the 14 GHz clock and phase 1 on the falling edge, each with its own slicers, decoder and retimer. `rx_top` documents and wires which phase is the earlier symbol.
- **A starting point for the simulator.** Every node needs a DC value, and two cells left a node floating at DC (see Winy's and Mehak's sections).

### From transmitter to receiver

- Transmitter: `prbs_gray_src` makes a 64-bit word (32 symbols of 2 bits) every 0.875 GHz clock cycle, and `tx_top` splits it into an MSB word and an LSB word. Each goes through one `tx_ser_ffe_path`: 32 lanes at 0.875 Gb/s become one stream at 28 Gb/s, in three copies one symbol apart (the FFE's pre, main and post taps). Six `predriver_cml` buffer the six taps and `pam4_driver` adds them: the MSB path with twice the current of the LSB path, pre and post subtracted. `tx_bias` supplies the six currents, so it sets the swing, the 2:1 ratio and the tap weights.
- A testbench connects `txp` / `txn` to `rx_p` / `rx_n` through a channel.
- Receiver: `rx_afe` terminates, equalises and scales the signal, `rx_decision` slices it on both clock phases and decodes each symbol to 2 bits, `rx_dec_retime` retimes them, and two `rx_deser_path` turn each bit stream back into a 32-bit word. `rx_cdr` makes the receiver's 14 GHz clock from the data.

The block pages under [`analog/PAM4SerDes/docs/`](analog/PAM4SerDes/docs/README.md) describe each step, with diagrams.

### How it is simulated

VerA builds one `.va` file into one device of at most 255 unknowns, and `tx_top` alone is far past that. So `.flows/tools/va_deck.py` writes an ngspice deck from the `.va` files: a module that only places modules from other files becomes a `.subckt`, and every other module is built by `vera --emit-osdi` into an OSDI device. The `.va` files stay the only source; nothing generated is edited or committed.

```
./env.sh
make -C analog/PAM4SerDes/build/sim check
```

`check` runs four steps, and CI (`.github/workflows/analog.yaml`) runs the same command:

- `lint`: every `.va` file compiles;
- `arch`: the hierarchy is the one in `analog/PAM4SerDes/architecture.txt`;
- `link`: builds the deck and the devices, runs the decks in `analog/PAM4SerDes/test/` and prints one PASS or FAIL line for each;
- `specs`: writes what the decks measured into the README.

A deck needs three things from ngspice, explained in the header of [`test/tb_datapath.sp`](analog/PAM4SerDes/test/tb_datapath.sp): version 45 or newer; the default solver, not `.option klu`; a fourth argument on `tran`, as in `tran 1p 26n 0 10u`.

### If you change your block

- Keep the port list and the parameter names, and nothing else needs to change.
- If you rename or add a port, change the instance in the file that places your cell (the "Used in" row of your block's page names it).
- If you change a default that is overridden at the instance, check the override.
- If you add, remove or move a cell, regenerate the architecture file in the same commit: `make -C analog/PAM4SerDes/build/sim arch UPDATE=1`.
- Run `make -C analog/PAM4SerDes/build/sim check` before you push.

## Changes, person by person

| Person | Files changed | Set where the cell is instantiated (file unchanged) |
|---|---|---|
| [Zoey Situ](#zoey-situ) | `pam4_driver.va`, `predriver_cml.va` | |
| [Mehak Khan](#mehak-khan) | `rx_decision.va`, `vga.va` | `rx_dec_retime`, `rx_deser_path`, `vga` |
| [Winy](#winy) | `phase_aligner.va` | |
| [Ethan Sun](#ethan-sun) | `cdr_glue.va`, `div_n.va`, `div2_tspc.va`, `dff_tspc_x8.va`, `refclk_buf.va`, `lock_detect.va` | `dff_tspc_x8`, `refclk_buf`, `tx_pll`, `rx_cdr`, the clock generators |
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

- **Why.** The driver took one MSB and one LSB input and set its own swing, so two blocks could not connect to it: `ffe_tapgen_hr` produces three taps per path (pre, main, post), and its header says the tap weights and the PAM4 sum "require a downstream driver with all three tap inputs"; `tx_bias` produces six tail currents, one per path and tap, that were going nowhere.
- **Changed: ports.** Was `(msbp, msbn, lsbp, lsbn, outp, outn)`. Now, in this order: the six differential tap inputs `msb_pre`, `msb_main`, `msb_post`, `lsb_pre`, `lsb_main`, `lsb_post` (each `_p` and `_n`), the six tail pins `i_msb_pre` ... `i_lsb_post`, then `outp`, `outn`, `vss`.
- **Changed: tail pins.** The driver holds each at `vtail` (0.6 V) so that `tx_bias` can sink its current there, and reads that current.
- **Changed: output.** Each tap steers its tail current by the sign of its input, as the MSB and LSB inputs did before; pre and post subtract. The differential output is the steered current times `rload` (25 Ω: the 50 Ω termination in parallel with the 50 Ω line).
- **Changed: parameters.** `vppd` is gone: the swing is `tx_bias`'s to set. New: `rload`, `vtail`. `vcm` is unchanged.
- **Changed: self-test.** The `//!` lines were renamed to the new ports. Run alone, nothing feeds the tail pins, so it prints `VDIFF = 0`; the levels are checked with `tx_bias` attached in `test/tx_driver_test.sp`.
- **What stays the same.** The model is still ideal: the inputs are compared, the output is an ideal voltage. The 2:1 MSB:LSB weighting and the level order are as before (they now come from the 2:1 currents). With FFE off and nominal bias, `tx_driver_test.sp` measures -0.3997, -0.1332, +0.1333, +0.3998 V: the four levels the original produced.
- **For you to check.** Whether a fixed `vtail` on the tail nodes and a fixed `rload` is the model you want, or the driver should have a real termination to a supply.

#### `Transmitter/predriver_cml.va`: bias pin (changed)

- **Why.** `tx_bias` has an output for the pre-driver tail current, and the cell had no pin to take it.
- **Changed: ports.** Now `(inp, inn, outp, outn, ib, vss)`. `ib` takes a reference current from the new `tx_predrv_bias`, one wire per pre-driver. It looks like a diode-connected mirror input: `vb_nom / ib_nom` = 0.35 V / 100 uA = 3.5 kohm to `vss`. Both are new parameters.
- **Changed: swing.** It is `vod` times the bias received over nominal, so a missing bias gives no swing. The cell prints FAULT when its bias is more than 10 % off.
- **What stays the same.** `vcm`, `vod`, the polarity decision and the output levels at nominal bias. Placed six times in `tx_top`, one per path and tap.
- **For you to decide.** The real cell's tail current and how it mirrors the reference.

### Mehak Khan

#### `Receiver/rx_decision.va`: completed (changed)

- **Why.** The file did not compile and was unfinished. It included `slicer.va`, which lives in `Slicer/slicer.va`. It instantiated 6 of the 24 slicers, under three names used twice (`s0`, `s1`, `s2`), and one of the two decoders. It converted the DFE's differential outputs to 1.8 V single-ended logic in its own analog block; the rest of the design is 0.7 V.
- **Changed: slicers.** All 24, `s0` to `s23`, numbered the way `dfe1_unrolled_hr` numbers its reference and candidate buses. Phase 1's slicers get the clock swapped, as the original did.
- **Changed: decoders.** Both, `dec0` and `dec1`, and no analog block. Each decoder reads the positive leg of the DFE's thermometer output and compares it with the DFE's output common mode (`vdd - 0.15` V). The negative legs are unconnected. This is a parameter override on `pam4_dec`, not a new cell.
- **Changed: parameters.** New `vdd` (0.7), `alpha`, `v_level`, `v_thr`, passed to the DFE, so the top level can set the DFE tap. Also an include guard and the corrected include path.
- **Changed: threshold DACs.** 24 `threshold_dac` cells, `d0` to `d23`, one per slicer. Slicer `g` needs `T + alpha * L`; its DAC gets the nearest of the 64 codes, so each reference is within half a step (2.6 mV) of the ideal value. The DFE model still computes the ideal references; they are no longer connected.
- **What stays the same.** The port list, the positional connection style and the partition: slicers, DFE and decoders here, retiming in `rx_dec_retime`.

#### `Receiver/vga.va`: input resistance (changed)

- **Why.** `ctle` drives only the voltage *between* its two outputs, and `vga` drew no input current. The two nodes between them had no path to any reference, so ngspice reports a singular matrix at `ctle_n` and cannot start.
- **What changed.** `vga` already declared `r_in = 1e9` and did not use it. It now puts that resistance from each input to ground. Five lines; nothing else.
- **For you and Kayhan to check.** The CTLE's output common mode is now 0 V, set only by this resistor. One of the two blocks should define it.

#### Set where your cells are instantiated (files not changed)

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `rx_dec_retime` | `rx_top`, once per phase | `vth_data` = 0.35, `vdd` = 0.7 | Defaults are 0.9 V and 1.0 V. |
| `rx_deser_path` | `rx_top`, once per binary path | `vdd_cmos` = 0.7 | Same as the default, tied to the supply parameter. |
| `vga` | `rx_afe` (Ethan's skeleton, already there) | gain range, 0 to 0.7 V control, 0.55 V output common mode | Defaults assume a 1 V supply. |

- The phase-1 retimer is clocked on the falling edge by connecting its clock swapped.
- `rx_deser_path`'s comments call its first input "phase 0", but `rx_top` connects phase 1 there: with these retimers the phase-1 output is the earlier symbol of each pair when the first demux samples (the header of `rx_top.va` explains). With the inputs the other way round the 64 output wires came out in the wrong order.

### Winy

#### `Clocking/phase_aligner.va`: start value for the integrator (changed)

- **Why.** The loop's capacitor is fed only by a current source, so the circuit has no DC operating point: ngspice reports a singular matrix at `vi_ou` and cannot start. The block's own test avoids this with `uic`, which the whole design cannot use: the PLL and CDR loops need the operating point for their starting control voltage.
- **What changed.** In the `capacitor` helper: at the DC operating point the capacitor is held at `v0` (new parameter, default 0 V); in transient it integrates as before. `rx_cdr` and `tx_pll` already do the same for their control voltages.
- **What stays the same.** A transient that starts from 0 V, which is what `uic` gave. Your own test, `test/pa_test.sp`, gives the same three numbers with the original file and with this one (`tgap` 35.37 ps, capacitor voltage 33.91 mV at 1 ns and 73.83 mV at the end).

#### `Clocking/cdr_pd_linear.va` (not changed)

- Placed once, in `rx_cdr`, as you wrote it. The detector works as your test shows, but the loop it sits in pushed the clock away from the detector's lock point, so a parameter of `rx_cdr` is set at the top level: see [Clock recovery](#clock-recovery-the-detector-and-the-loop-disagree-on-sign).
- **Also for you to check.** `phase_aligner.va` and `cdr_pd_linear.va` each define the same four helper modules (`delay_t3`, `mult_1`, `mult_2`, `vi_converter`), identical today. With both files in one design the later definition is used for both, so editing one copy silently changes the other block. They belong in one shared file.

### Ethan Sun

#### `Clocking/cdr_glue.va`: `diff2se` in its own file (changed)

- **Why.** `tx_top` needs `diff2se`: the phase aligner reads a single-ended signal and the data it watches is differential. VerA builds the first module in a file that nothing instantiates, and with all of `cdr_glue.va` included that was `qdelay`: `tx_top.va` built the wrong module.
- **What changed.** `diff2se` moved, unchanged, to `Clocking/diff2se.va`. `cdr_glue.va` includes it, so `rx_cdr.va` needs no change.

#### `Clocking/div_n.va`, `Clocking/div2_tspc.va`: include guards (changed)

- **Why.** Each file is included by two parents (`div2_tspc.va` by `tx_clkgen.va` and `rx_clkgen.va`, `div_n.va` by `tx_pll.va` and `rx_cdr.va`). With both parents in one design, VerA warns that the module "is defined again".
- **What changed.** `` `ifndef PAM4_<NAME>_VA `` and `` `define `` at the top, `` `endif `` at the bottom: the convention your newer files already use. Nothing else.

#### `div2_tspc.va`, `div_n.va`, `dff_tspc_x8.va`, `refclk_buf.va`, `lock_detect.va`: edge breakpoints (changed)

- **Why.** Each of these cells put two `timer()` breakpoints on the corners of every output edge. Built as an ngspice device, a `timer()` is a time point the simulator must land on exactly, and it stops with "timestep too small" when two cells ask for time points closer together than its minimum step. With two clock domains drifting against each other that happens sooner or later: the whole top level stopped at 192 ns, and two PLLs side by side at about 200 to 300 ns.
- **What changed.** `$bound_step(0.25 * trf)` replaces the corner breakpoints and keeps at least four time points on each edge. Fourteen `timer()` lines, five files.
- **What stays the same.** The edge time, the ramp, the jitter and every parameter. The timers that do something (`lock_detect`'s windows, `pfd`'s reset) are untouched.
- **Check.** With the change both runs complete, and `tb_pll` locks at the same control voltage (0.350 V).

#### Set where your cells are instantiated (files not changed)

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `dff_tspc_x8` | `tx_ser_ffe_path` | `rj` = 200 fs x `rj_scale` | Same as the default at `rj_scale` = 1. Lets the top-level jitter knob reach it. |
| `refclk_buf` | `pam4_serdes`, twice | `rj` = 100 fs x `rj_scale`, seeds 1 and 11 | Same as the default; separate noise for the two. |
| `tx_pll`, `rx_cdr` | `pam4_serdes` | `rj_div` = 150 fs x `rj_scale` | Same as the default. |
| `tx_clkgen`, `rx_clkgen` | `tx_top`, `rx_top` | `rj_scale` | Passed down from the top. |
| `rx_cdr` | `pam4_serdes` | `tq` = 53.571 ps (default 17.857 ps) | With the default the loop settles with the clock edges on the data transitions. See [Clock recovery](#clock-recovery-the-detector-and-the-loop-disagree-on-sign). |

Your skeletons `tx_pll`, `rx_cdr`, `tx_clkgen`, `rx_clkgen` and `rx_afe` are used as they are. The one thing in them that needs your attention is the `tq` override above.

### Sudhanshu Tiwari

#### `Clocking/cml2cmos.va`, `Clocking/dcc_cml.va`, `Clocking/loop_filter_rc.va`: include guards (changed)

- **Why.** Each file is included by two parents (for example `dcc_cml.va` by `tx_clkgen.va` and `rx_clkgen.va`). With both parents in one design, VerA warns that the module "is defined again".
- **What changed.** `` `ifndef PAM4_<NAME>_VA `` and `` `define `` at the top, `` `endif `` at the bottom. Nothing else.

#### Set where your cells are instantiated (files not changed)

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `dff_cmos_x32` | `tx_ser_ffe_path` | `vth_clk`, `vth_data` = 0.35, `vhigh` = 0.7, `t_rise`, `t_fall` = 20 ps | Defaults are 0.5 V thresholds, a 1.0 V output and zero edge time. |
| `cml_dff_x4` | `tx_ser_ffe_path` | `vcm` = 0.55, `vdiff` = 0.3, `t_rise`, `t_fall` = 5 ps | Defaults are 0.6 V / 0.2 V and zero edge time; the other CML is 0.55 V / 0.3 V. |

Both are connected pin by pin, because they have one pin per bit and no supply pins.

### GreenBlueFish

#### `Clocking/pfd.va`, `Clocking/vco.va`: include guards (changed)

- **Why.** Both files are included by `tx_pll.va` and by `rx_cdr.va`. With both in one design, VerA warns that the module "is defined again".
- **What changed.** `` `ifndef PAM4_<NAME>_VA `` and `` `define `` at the top, `` `endif `` at the bottom. `pfd.va` also gained the newline its last line was missing. Nothing else.

### oDNA

No file changed.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `mux2_cmos` | `tx_ser_ffe_path`, 24 times | `vth` = 0.35 | Same as the default, tied to the supply parameter. |

- **Serializer level 1.** `mux2_cmos` is a plain mux, not a latch-mux, and the word it reads changes on the rising edge of its select clock. So it passes `in1` first. At that level only, `tx_ser_ffe_path` connects the earlier slot to `in1`.
- **PRBS wires.** `prbs_gray_src` puts symbol 0 on `gray_out[63:62]`. `tx_top` splits the bus into the MSB and LSB words with the order reversed, so wire `j` of each word is time slot `j`.

### hdsouza13

No file changed and nothing overridden. `mux2_cml_hr` is placed five times and `ffe_tapgen_hr` once in each `tx_ser_ffe_path`, with their defaults. The three taps of `ffe_tapgen_hr` now reach the driver (see Zoey's section).

### Krrish Lala

No file changed.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `tx_bias` | `tx_top` | `w_pre`, `w_main`, `w_post` | So the top level can turn the FFE on and off. Defaults unchanged. |

- The six driver tail currents go to `pam4_driver`, which holds each tail node at 0.6 V. `vref` now comes from `bias_ref`.
- `i_pdrv` is one sink for six pre-drivers, and a bias wire serves one consumer. So it goes to the new `tx_predrv_bias`, which holds the pin at 0.6 V (the value your test header biases it at) and makes six 100 uA references. **For you to decide:** keep that stage, or give `tx_bias` six pre-driver outputs and delete it.

### Kayhan Baig

No file changed. `ctle` is placed in `rx_afe` as it was; see the note on its output common mode in Mehak's section.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `pam4_dec` | `rx_decision`, once per phase | `vhigh` = 0.7, `vth` = 0.55 | Defaults are 1.8 V and 0.9 V. The decoder reads one leg of a CML signal, so its threshold is that signal's common mode. |

### deaconsham

No file changed. `demux2_cml` and `demux2_cmos` are placed by `rx_deser_path` as they were.

| Cell | Placed in | Set to | Why |
|---|---|---|---|
| `dfe1_unrolled_hr` | `rx_decision` | `vdd` = 0.7, and `alpha`, `v_level`, `v_thr` from the parent | Default `vdd` is 1.0. |

### Justin Fang

No file changed. `slicer` is placed 24 times in `rx_decision`, and `threshold_dac` 24 times, one per slicer, with `code` set to the nearest code for that slicer's threshold. `pam4_slicer` is not placed.

## Biasing: new blocks and what they changed

The design had one bias block, `tx_bias`, and three bias pins on the top level (`vref`, `vtt`, `vctrl`). It now has a bias network, owned by Omar ElSawy ([Biasing](analog/PAM4SerDes/docs/Biasing/README.md)):

- `bias_ref` makes `vref` and one reference current each for `rx_bias` and `clk_bias`.
- `rx_bias` makes `vtt` and `vctrl`. `pam4_serdes` lost those three pins and gained `bias_en` and `rx_en`.
- `rx_bias` and `clk_bias` also make one reference current for every cell that will need one. `ctle`, `vga`, `slicer`, `demux2_cml` and the clocking cells have no bias pin, so those wires end at the top level. **Owners of those cells:** when you add the pin, load it with `vb_nom / ib_nom` ohms and check it, as `predriver_cml` now does.

## Clock recovery: the detector and the loop disagree on sign

No file of Winy's or Ethan's was changed for this: one parameter is set where `rx_cdr` is instantiated. Both owners should read this and decide where the fix belongs.

**What happened.** With `rx_cdr` as written the loop settled, with a steady control voltage, but the receiver's data was wrong: about 25 bit errors in every 64-bit word. The same receiver on an ideal clock had none.

**Why.** `cdr_pd_linear`'s own test, `test/cdr_pd_linear_test.sp`, measures the average output current at three clock positions:

| Clock edge after the data edge | Average current into the loop filter |
|---|---|
| 16.06 ps (the intended lock point) | +3.4 µA, about zero |
| 10.06 ps (clock 6 ps early) | +56 µA |
| 22.06 ps (clock 6 ps late) | -53 µA |

In `rx_cdr` a current into the loop filter raises the control voltage and the VCO runs faster, so its edges come earlier. An early clock was therefore pushed earlier and a late clock later: the loop left the intended lock point and settled at the detector's other zero, half a symbol away, where the sampling edges sit on the data transitions.

**Measured in the loop**, with `test/tb_cdr.sp`. A symbol is 35.7 ps long, so the middle of the eye is 17.9 ps from a transition. The 1.8 ps in the second row is the detector's own trim (`t18`).

| `tq` of `rx_cdr` | Where the data transitions fall | Result |
|---|---|---|
| 17.857 ps (its default) | 1.5 ps after a clock edge: the clock samples on the transitions | 674 errors in 26 words |
| 53.571 ps | 19.7 ps after a clock edge: the clock samples 1.8 ps from the middle | 0 errors in 35 words |

**What integration did.** `rx_cdr` makes the detector's quadrature clock by delaying the 14 GHz clock by `tq`. `pam4_serdes` sets `tq` to 53.571 ps, three quarters of a period: the same as a quadrature clock a quarter period *early*. That inverts the 28 GHz reference the detector builds from the two clocks, and with it the sign of the loop. `test/tb_cdr.sp` uses the same setting.

**For Winy and Ethan to decide.** The sign can be put right in any one of three places. Pick one, make it the default, and remove the override from `pam4_serdes.va` and `test/tb_cdr.sp`.

- The direction of the quadrature clock (what the override does).
- The sign of the detector's output current (`vi_converter`).
- Half a 28 GHz period, 17.857 ps, more or less on the detector's delay `dt4`.

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
| `va/Biasing/bias_ref.va` | The reference: `vref`, and a current for each bias block. Owner: Omar ElSawy. |
| `va/Biasing/rx_bias.va` | `vtt`, `vctrl` and the receiver's reference currents. Owner: Omar ElSawy. |
| `va/Biasing/clk_bias.va` | The clocking cells' reference currents. Owner: Omar ElSawy. |
| `va/Biasing/tx_predrv_bias.va` | One pre-driver current in, six references out. Owner: Omar ElSawy. |
| `test/prbs_chk.va` | PRBS7 checker for the received words (test equipment). |
| `test/tx_driver_test.sp` | Driver and bias together: the four levels, FFE peak and de-emphasis. |
| `test/tb_datapath.sp` | Transmitter to receiver through a flat channel, ideal clocks, with the checker. |
| `test/tb_cdr.sp` | The same, with `rx_cdr` recovering the receiver's clock from the data. |
| `test/tb_pll.sp` | The transmitter PLL until its lock detector asserts, jitter on. |
| `test/tb_top.sp` | The whole `pam4_serdes` in one run, jitter on. |
| `architecture.txt` | The hierarchy the `arch` check compares the `.va` files with. |
| `.flows/tools/va_deck.py` | Turns the `.va` hierarchy into an ngspice deck (subcircuits of OSDI devices). `--tree` prints the hierarchy. |
| `.flows/tools/va_specs.py` | Writes what the decks measured into the README. |
| `.flows/env/va.nix` | A small shell with only VerA, ngspice, make and python, for CI. |
| `.github/workflows/analog.yaml` | Runs `make check` on every change under `analog/`. |

## Tools and environment

- `analog/PAM4SerDes/build/sim/Makefile`: new `deck`, `link`, `lint`, `arch`, `specs` and `check` targets.
- `.flows/env/Analog.nix`: adds VerA from the EDA-Packaged pin, with two repairs it needs to build and to run (the file explains them), and refuses an ngspice older than 45. The pinned nixpkgs already ships ngspice 45. `.flows/env/shell.nix` prints both versions when the shell starts.
- `.flows/tools/va_deck.py`: `VA_DECK_JOBS` sets how many devices are built at once (default 3; use 1 on a machine short of memory).
- `.gitignore`: `analog/*/build/sim/out/`, the generated decks, devices and logs.
- `docs/`: the site now shows the Markdown under `analog/PAM4SerDes/docs/` and this file.
