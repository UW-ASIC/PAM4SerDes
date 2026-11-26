# Integration status

Where the full design stands, as of 2026-11-26. This page says what has been simulated,
how to repeat it, and what each owner still needs to look at. The changes made to get
here are in the [changelogs](../../../CHANGELOGS.md), person by person.

## In one paragraph

Every block has a behavioural Verilog-A model and all of them are wired into one
hierarchy, `pam4_serdes`. The transmitter sends PRBS7 as PAM4 and the receiver recovers
it with no errors through a flat test channel, both on ideal clocks and with the
receiver's clock recovered from the data. The transmitter's PLL settles on its own, but
its simulation stops shortly after lock, and the transmitter stops after 14 ns when the
PLL clocks it. So the complete top level, with both loops running, does not run yet.

## What has been simulated

All of this is ngspice with its default solver, on OSDI devices built by VerA. The three
`make ... link` rows were last run from a clean build with the tools the project shell
provides (VerA 0.23, ngspice 45). The one-off rows were run earlier, with VerA 0.20.

| Check | Result | How to repeat |
|---|---|---|
| The top level elaborates | `vera --lint pam4_serdes.va` reports no errors | from `analog/PAM4SerDes/va/` |
| Driver and bias together | PASS. Levels -0.400, -0.133, +0.133, +0.400 V; FFE peak 0.400 V; de-emphasised 0.240 V; all within 1 mV | `make -C analog/PAM4SerDes/build/sim link DECK=tx_driver_test` |
| Transmitter clock tree | 3.5 GHz and 1.75 GHz clocks measure 285.71 ps and 571.43 ps | one-off run, no deck kept |
| Transmitter alone, FFE on | The PAM4 output decodes to PRBS7 with 0 errors in 444 bits; 0.8 V peak-to-peak | one-off run, no deck kept |
| Datapath: transmitter, flat channel, receiver, ideal clocks | PASS. 0 errors in 17 words (1088 bits). Every one of the 64 output wires carries the right time slot | `make -C analog/PAM4SerDes/build/sim link DECK=tb_datapath` (about a minute on an idle machine) |
| Clock recovery: the same datapath, receiver clocked by `rx_cdr` | PASS. 0 errors in 35 words (2240 bits). The loop puts the data transitions 19.7 ps after the clock edges, 1.8 ps from the middle of the eye. Needs a parameter set at the top level: see below | `make -C analog/PAM4SerDes/build/sim link DECK=tb_cdr` |
| Transmitter PLL alone | Control voltage overshoots during pull-in, then stays within 6 mV of 0.350 V from about 150 ns on. See below for the lock flag | one-off run, no deck kept |

The datapath check runs with the FFE off (`w_main` = 1) and the DFE tap at 0, because
the test channel is flat. The FFE's tap sum is checked by the driver test. The CTLE's
boost and the DFE's tap have not been exercised at all, and **no run yet shows the
equalisers opening an eye on a lossy channel**.

## Not working, worked around, or not verified yet

- **Clock recovery works only with an override.** With `rx_cdr` as written, the loop
  settles with the clock edges on the data transitions and the data is wrong (about 25
  bit errors per 64-bit word). The detector and the loop disagree on sign. The top level
  sets `rx_cdr`'s `tq` to 53.571 ps to put that right, and Winy and Ethan need to decide
  where the fix belongs. The measurements are in the
  [changelogs](../../../CHANGELOGS.md#clock-recovery-the-detector-and-the-loop-disagree-on-sign).
  Frequency acquisition (the FLL and its hand-over to the detector) has not been run:
  the check starts both sides at 14 GHz with `force_lock` high.
- **The PLL past lock.** `tx_pll` on its own pulls in and settles, but ngspice then
  stops with "timestep too small" somewhere between 245 and 317 ns, once the loop is
  locked. It happens with the cells' jitter on or off. Giving the PFD outputs a 10 ps
  edge did not help (tried on a copy, not kept). The cause is not found. Because of it,
  the lock flag has never been seen to assert: `lock_detect` needs 256 good reference
  cycles, about 585 ns.
- **The whole top level in one run.** `pam4_serdes` (both loops, transmitter and
  receiver together) elaborates and builds. One run was tried, with the receiver's
  frequency acquisition skipped: ngspice stops after 14 ns with "timestep too small" at
  `m2_ou`, the multiplier inside the transmitter's `phase_aligner`. That run is the first
  time the transmitter was clocked by `tx_pll` and not by an ideal clock. The cause is
  not found; a deck with only `tx_pll` and `tx_top` is the next thing to try. The PLL
  item above would stop the run later in any case.
- **Equalisation.** No lossy channel model exists in the repo yet.
- **Jitter.** Every check above sets `rj_scale` = 0 (the clocking cells' added jitter
  off). Nothing has been run with it on, apart from one PLL run.

## Running it

```
./env.sh
make -C analog/PAM4SerDes/build/sim link
```

`link` composes the hierarchy and runs the decks in `analog/PAM4SerDes/test/`, printing
one PASS or FAIL line per deck. Logs go to `analog/PAM4SerDes/build/sim/out/`.

Three things will bite you if you write your own deck:

1. **Use ngspice 45 or newer.** ngspice 44 cannot place an OSDI device with more than 18
   pins, and several cells have more (`dff_cmos_x32` has 65).
2. **Do not use `.option klu`.** It is several times faster and gives wrong node voltages
   with these devices: the same deck gives the right operating point with the default
   solver and a wrong one with KLU.
3. **Give `tran` a fourth argument**, for example `tran 1p 26n 0 1m`. ngspice's minimum
   time step is 1e-11 times that argument. Without it the minimum is 1e-23 s and runs die
   with "timestep too small" just before a clock edge. The models limit the real step to
   0.5 ps either way.

Why the hierarchy needs a tool: VerA builds one `.va` file into one device and caps a
device at 255 unknowns. `tx_top` alone is far past that. `.flows/tools/va_deck.py` turns
every purely structural module into a subcircuit and every other module into a device, so
the `.va` files stay the only source.

## Open items, by owner

None of these stops the skeleton from running. Each is something the model does not do
yet, or a place where two blocks do not quite agree. Owners are from the git history.

### Nobody yet

- **`mux2_cs`** (charge-steering mux, serializer level 3) is an ideal placeholder in
  `va/Transmitter/placeholders/`. It needs an owner.
- **`div2_cml`** (CML divide-by-2, both clock generators) is an ideal placeholder in
  `va/Clocking/placeholders/`. It needs an owner.
- **A lossy channel model** and a testbench that turns the FFE, CTLE and DFE on.

### Zoey Situ: `pam4_driver`, `predriver_cml`

- `pam4_driver` drives an ideal voltage that switches instantly, with a fixed common
  mode. It has no termination and no supply pin. Its ports changed; see the changelog.
- `predriver_cml` is ideal and has no bias pin, so `tx_bias.i_pdrv` is unconnected. Its
  default levels (1.2 V common mode) do not relate to either supply.
- Both call `$strobe` on every time step.

### Krrish Lala: `tx_bias`

- Six of the seven outputs are now used by the driver. `i_pdrv` waits for a pre-driver
  with a bias pin.
- `pgood` and `en` are 1.25 V logic; every other logic pin of the design is 0.7 V.
- Nothing in the design generates `vref`; it is a top-level pin.

### oDNA: `mux2_cmos`, `prbs_gray_src`

- `mux2_cmos` is a plain 2:1 mux with no latch. It passes whichever input is selected,
  including while that input is changing, and which input goes first depends on when the
  data changes. `tx_ser_ffe_path` wires level 1 the other way round because of this. A
  latch-mux would remove the special case.

### hdsouza13: `ffe_tapgen_hr`, `mux2_cml_hr`

- Both limit the simulator's step to 0.5 ps (`max_step`) at all times. That bound sets
  the run time of every deck that includes the transmitter.

### Sudhanshu Tiwari: `dff_cmos_x32`, `cml_dff_x4`, `dcc_cml`, `cml2cmos`, `loop_filter_rc`

- `dff_cmos_x32` and `cml_dff_x4` have one pin per bit (65 and 18 pins) and no supply
  pins; their levels are parameters, defaulting to 1.0 V logic and zero edge time. The
  skeleton overrides them. Both capture on the rising edge only.
- `dcc_cml` regenerates its output from the measured input period, so the output's
  phase is not tied to the input's edges (its header says so). The whole clock tree
  hangs off it.
- `cml2cmos` switches its output instantly.
- `loop_filter_rc` has no second capacitor; `tx_pll` and `rx_cdr` add C2 themselves.

### GreenBlueFish: `vco`, `pfd`

- `vco` has a single-ended CMOS output and no band input. The architecture calls for a
  CML VCO with coarse tuning.
- `pfd`'s outputs have zero edge time by default (`t_rf` = 0).

### Winy: `phase_aligner`, `cdr_pd_linear`

- The two files each define the same four helper modules (`delay_t3`, `mult_1`,
  `mult_2`, `vi_converter`). Linting the top level warns that each "is defined again";
  the later definition wins. They are identical today. Edit one copy and the other
  block silently changes. They belong in one shared file.
- When `tx_pll` clocks the transmitter, the simulation stops after 14 ns at this block's
  multiplier (`m2_ou`); see "The whole top level in one run" above.
- On an ideal clock, in a run 14 ns long, the phase aligner's delay was still moving at the end
  (about 36 ps of drift, slowing). The data was error-free throughout, but the loop has
  not been shown to settle.
- `cdr_pd_linear` works as its own test shows, but its sign is opposite to what
  `rx_cdr`'s loop needs; see "Clock recovery works only with an override" above.
- `cdr_pd_linear` uses every zero crossing of the PAM4 signal. Only the symmetric
  transitions cross zero in the middle; the others pull the lock point around (the
  measured transitions spread over about 9 ps).

### Ethan Sun: clocking skeletons and cells

- The PLL run stopping after lock (above) sits in `tx_pll` and its cells.
- `rx_cdr`'s `tq` is overridden at the top level; see "Clock recovery works only with an
  override" above. `test/tb_cdr.sp` shows both behaviours.
- The charge pump is ideal, with no output limit: during PLL pull-in the control voltage
  reaches 1.45 V on a 0.7 V supply.
- `rx_cdr` and `tx_pll` each carry a small analog block (C2 and the start-up value of
  the control voltage) next to their wiring.

### Mehak Khan: `rx_decision`, `rx_dec_retime`, `rx_deser_path`, `vga`, `rx_term`

- `rx_dec_retime` is a behavioural retimer whose outputs step instantly. The
  architecture uses the clocking team's `cml_dff_x4` there.
- `rx_deser_path` does its own CML-to-CMOS conversion and output register in an analog
  block instead of instantiating `cml2cmos` and `dff_cmos_x32`. Because of that it
  compiles into one device of about 235 unknowns (43 pins plus 192 internal); the limit
  is 255.
- `rx_decision` was rewritten; see the changelog.
- `rx_deser_path`'s comments call its first input "phase 0". `rx_top` feeds it phase 1,
  because that is the earlier symbol of each pair with these retimers (the header of
  `rx_top.va` explains). The comment or the retimer should change so the two agree.
- The CML demuxes inside `rx_deser_path` run at their default 1.0 V levels, not 0.7 V.
  Nothing reads them single-ended, so nothing breaks.

### Justin Fang: `slicer`, `threshold_dac`, `pam4_slicer`

- `threshold_dac` and `pam4_slicer` are not instantiated. The DFE model drives the 24
  slicer references itself. Decide with deaconsham which block owns the references.

### deaconsham: `dfe1_unrolled_hr`, `demux2_cml`, `demux2_cmos`

- `dfe1_unrolled_hr` generates the 24 reference voltages as ideal sources (see above).

### Kayhan Baig: `ctle`, `pam4_dec`

- `ctle` drives only the difference between its outputs. Their common mode is set by
  the VGA's input resistance (see the changelog). Decide with Mehak which block sets it.
- `pam4_dec` defaults to 1.8 V logic; the skeleton overrides it to 0.7 V.

### Project-wide

- The models are written for a 0.7 V core supply; the repository description says
  Sky130. One of the two is out of date.

## Tool issues found on the way

For whoever maintains the flow.

| Tool | Issue | Workaround in place |
|---|---|---|
| ngspice 45, KLU | Wrong node voltages with OSDI devices in a large circuit; correct with the default solver | Decks do not use KLU |
| ngspice 44 | OSDI devices limited to 18 pins | `make link` refuses to run below 45 |
| ngspice, OSDI | A device's step bound can drive the time step below the minimum, ending the run | Fourth `tran` argument |
| VerA | 255 unknowns per device | `va_deck.py` composes subcircuits |
| VerA | Builds the first module nothing instantiates, so a file with two such modules cannot be built for the second | One module per file where it mattered (`diff2se.va`) |
| EDA-Packaged's `vera` (0.23) | As published it does not build on Linux (its VPI library refuses the ABI Zig picks in the nix sandbox), and it ships without the Zig it needs to build devices | `.flows/env/Analog.nix` names a glibc target and wraps that Zig in. Not in a binary cache: the first `./env.sh` builds it, a few minutes and about 3 GB of memory |
