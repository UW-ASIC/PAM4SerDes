# Half-rate transmitter mux and FFE

`mux2_cml_hr.va` and `ffe_tapgen_hr.va` are the two reusable behavioral cells.
They implement the half-rate transmitter partition shown in the project diagram.
They have been tested with VerA 0.23.0. They are not transistor implementations
or calibrated Sky130 timing/power models.

## Where the cells connect

For one binary path (MSB or already Gray-mapped LSB):

```text
Upstream CML retiming: four 7 Gb/s differential lanes d0, d1, d2, d3
          |
Two mux2_cml_hr cells at clk7: (d0,d2) -> E, (d1,d3) -> O
          |
ffe_tapgen_hr at clk14: input E/O -> PRE E/O, MAIN E/O, POST E/O
          |
Three mux2_cml_hr cells at clk14: serialize one E/O pair per tap
          |
Three 28 Gb/s differential binary taps -> pre-drivers -> PAM4 driver
```

Instantiate this path twice for MSB and mapped LSB. FFE coefficients, tap sign
inversion, MSB:LSB current weighting and PAM4 summation belong to the driver.

The optional wiring example is
[`../../test/tx_cml_ffe/fixtures/tx_cml_ffe_path.va`](../../test/tx_cml_ffe/fixtures/tx_cml_ffe_path.va).
It is a test/integration helper, not a third assigned circuit cell or a complete
transmitter. The tests use explicit ideal clock/data stimuli rather than the
repository's incomplete PLL/clock-tree hierarchy.

## Interfaces

Each `_p/_n` pair is one differential signal. Logic 1 means positive
`V(p,n)`; logic 0 means negative `V(p,n)`, using default offsets.

### mux2_cml_hr

Exact positional port order:

```text
de_p de_n do_p do_n clk_p clk_n out_p out_n vdd vss
```

- `de`: EVEN input; `do`: ODD input.
- Positive differential clock selects EVEN; negative selects ODD.
- The mux follows the selected input continuously, with modeled delay.
- Keep each selected input stable through its output interval; this is not a DFF.
- At clk7, two 7 Gb/s inputs become one 14 Gb/s output.
- At clk14, two 14 Gb/s inputs become one 28 Gb/s output.

### ffe_tapgen_hr

Exact positional port order:

```text
de_p de_n do_p do_n clk_p clk_n rst
pre_e_p pre_e_n pre_o_p pre_o_n
main_e_p main_e_n main_o_p main_o_n
post_e_p post_e_n post_o_p post_o_n
vdd vss
```

Both input bits E[k]=x[2k] and O[k]=x[2k+1] must be stable at the SAME rising
clk14 crossing. There are six output lanes, each 14 Gb/s, not three full-rate
outputs inside this cell.

| Tap | Even lane | Odd lane |
| --- | --- | --- |
| PRE | E[k] | O[k] |
| MAIN | O[k-1] | E[k] |
| POST | E[k-1] | O[k-1] |

The FFE and all final muxes share clk14 and matching clock thresholds. The
EVEN output bank updates on falling edges while ODD is selected. The ODD bank
updates on rising edges from the previous captured pair while EVEN is selected.
This gives one clk14 period of common capture-to-selection latency. After
serialization and that latency, PRE=x[n], MAIN=x[n-1], POST=x[n-2].

At 28 GBd, 1 UI is 35.714 ps and one clk14 period is 71.429 ps. Mux propagation
and output RC add further delay. Tap spacing is one UI, independent of the
common pipeline latency.

The supplied test stimulus toggles clk7 on falling clk14 edges, then captures
the selected input pair at the next clk14 rising edge. The repository's
`cml_dff_x4` retimes all four lanes at rising clk7; its outputs have one UI
to settle through the first muxes before the FFE captures them. The actual
clock generator must provide this phase relationship.

## Compatibility with the current team modules

Reviewed against upstream commit `a70ec8c` on 2026-11-19. The two cells' logic
and ports were retained after reviewing the new neighboring modules. Their
comments were shortened; detailed explanations stay in this guide.

| Neighbor | Connection and checked behavior |
| --- | --- |
| `Clocking/cml_dff_x4.va` | `q0/q2` feed the EVEN first mux; `q1/q3` feed the ODD first mux. Its default +/-0.2 V differential output crosses the mux's 0 V threshold correctly. |
| `predriver_cml.va` | One instance per serialized tap, six total across MSB/LSB. Connect final mux `out_p/out_n` to `inp/inn`. Its ideal sign detector accepts the mux's +/-0.3 V differential output. |
| `pam4_driver.va` | Currently accepts only one differential MSB and one LSB input. The integration test connects the two buffered MAIN taps and checks all four PAM4 levels. |

**The current driver does not implement three-tap FFE summation.** PRE and POST
are valid outputs of this path, but the driver needs six differential inputs
(MSB/LSB times PRE/MAIN/POST) and signed tap weights before the complete FFE
architecture is connected. Do not connect several tap outputs to one driver
input. MAIN-only wiring tests the available driver interface, not equalization.

The new `team-neighbors` test instantiates the actual repository modules with
their default parameters, two complete CML/FFE paths and six predrivers. It
checks retimer storage by changing input bits after capture, all six serialized
tap sequences, buffer polarity/levels, and MAIN-only PAM4 output.

The modules use different provisional common-mode/swing settings. Functional
sign detection is compatible; this is not a transistor-level headroom check.
The full clock tree is not part of the passing test: `div2_cml.va` is still
missing, and `tx_clkgen.va` expects ports/parameters that the current `dcc_cml`
and `cml2cmos` modules do not provide. Ideal phased clocks isolate these two
assigned data-path cells from those separate integration gaps.

## Reset and supply adaptation

Reset is active high relative to VSS. It clears history, pending values and
both output banks to `init_bit` (default 0), including while the clock is stopped.
Outputs respond after the modeled transition delay/edge duration.

The default `vth_rst=-1` selects a supply-relative threshold:

```text
reset threshold = rst_fraction * V(vdd,vss)
rst_fraction defaults to 0.5
```

This is 0.35 V at a 0.7 V supply and 0.5 V at a 1.0 V supply. To use a separate
reset voltage domain or retain a fixed threshold, set `vth_rst` explicitly:

```verilog
ffe_tapgen_hr #(.vth_rst(0.35)) taps(/* ports above */);
```

Keep supply and reset levels settled when interpreting valid data. Avoid
simultaneous data/reset changes at a sampling edge. This model does not simulate
metastability or report setup/hold violations.

## Electrical/timing parameters

Both cells use 1.5 mA per output pair and 200 ohms from EACH output leg to VDD.
These match `Clocking/clkbuf_cml.va`'s `vsw=0.3`, `rl=200`, `iss=vsw/rl` defaults.
They give +/-0.3 V differential (0.6 Vppd) with high-impedance external loads.
Common-mode relative to VSS is `V(vdd,vss)-0.15 V`; it follows the supply.

An external 100-ohm differential load reduces the levels to +/-0.06 V.
The models' current sources do not enforce transistor headroom limits.

| Parameter | Default | Meaning |
| --- | --- | --- |
| `itail` | 1.5 mA | Current per differential output pair |
| `rload` | 200 ohms | Internal load per output leg |
| mux `cout` | 5 fF | Assumed capacitance per output leg |
| mux `tpd` | 5.934 ps | Project estimate used as transport delay; RC adds delay |
| mux `vsoft_data`, `vsoft_clk` | 10 mV | Smooth switching widths |
| mux `vos_data`, `vos_clk` | 0 V | Differential decision offsets |
| FFE `t_cq`, `tr`, `tf` | 2 ps each | Assumed event-to-output delay and transitions |
| FFE `vth_data`, `vth_clk` | 0 V | Differential sampling thresholds |
| FFE `vth_rst`, `rst_fraction` | -1, 0.5 | Automatic reset threshold, or fixed override |
| FFE `init_bit` | 0 | Startup/reset history and output bit |
| FFE `ttol`, `vtol` | 1 fs, 1 uV | Numerical crossing tolerances |
| `max_step` | 0.5 ps | Requested simulation time-step bound |

The delays, capacitance and switching widths are provisional. A passing
behavioral test does not show that Sky130 devices achieve 28 GBd, these delays,
or operation at the testbench's 0.7 V supply. Supply tests at 1.0/1.8 V verify
the model equations and reset interface, not process operating specifications.

## Run the checks

Requirements: Python 3.9+ standard library, VerA, and the Zig version required
by that VerA release. Tested pair: **VerA 0.23.0** and
**Zig 0.18.0-dev.349+d924f83bf**. A wrapped VerA may supply Zig itself.
See [VerA installation](https://openfat.github.io/VerA/using/install.html).
There is no automatic tool download or modification of the machine's PATH.

From the repository root, with tools on PATH:

```sh
python3 analog/PAM4SerDes/test/tx_cml_ffe/run_checks.py
```

Or pass executable paths (including paths containing spaces):

```sh
python3 analog/PAM4SerDes/test/tx_cml_ffe/run_checks.py \
  --vera /path/to/vera --zig /path/to/zig
```

On Windows use `python` instead of `python3`, or use
`analog\PAM4SerDes\test\tx_cml_ffe\run_checks.cmd` with the same arguments.
The runner resolves model/fixture paths relative to itself and works from any
working directory. Environment alternatives: `VERA` and `VERA_ZIG` contain
executable paths, not shell command strings.

Repository Makefile entry points:

```sh
make -C analog/PAM4SerDes/build/va tx-lint
make -C analog/PAM4SerDes/build/va tx-check
make -C analog/PAM4SerDes/build/va tx-test VERA=/path/to/vera VERA_ZIG=/path/to/zig
```

`tx-*` targets can run outside the Nix shell. They explicitly select these
models in the Transmitter subfolder. Existing OpenVAF/OSDI targets are separate
and retain their original environment requirements. The repository Nix shell
does not currently install VerA; provide it separately as described above.

Results are written under `analog/PAM4SerDes/build/va/tx-cml-ffe-results/`:

- `report.json`: functional pass/fail, version and exact source hashes.
- `lint-report.json` / `check-report.json`: compilation-only modes, without
  overwriting a previous functional report.
- `*.csv`: output waveforms and expected/actual bit comparisons.
- `team-neighbors-summary.json`: checks using the actual retimer, predrivers
  and MAIN-only PAM4 driver; their source hashes are recorded in `report.json`.
- `*.log`: compiler diagnostics and simulator output, including W0650 warnings.
- `generated/` and `build/`: fixtures and compiler scratch files.

These generated files are ignored by Git. `--output DIR` chooses another
location. A failed check exits nonzero. Do not run Python with `-O`, which
would remove assertions; the runner explicitly rejects it.

Coverage includes all eight mux DC combinations; 7/14 GHz interleaving;
held-clock transparency and unselected-input rejection; differential loading;
FFE both-phase outputs, reset/refill and deliberately changed inputs after
capture; two connected MSB/LSB test paths; include guards; supply-relative and
fixed reset thresholds; nonzero VSS; and asynchronous reset with a stopped clock.

## Simulator boundary

The mux uses `absdelay`; the FFE uses monitored events and `transition`.
Use a simulator that implements those operators. These tests validate the
VerA functional runner, not OpenVAF/OSDI or ESPice integration. The repository's
default OSDI compile target is not the execution path for these two cells.
Do not replace delay or event behavior with an approximation merely to get
another compiler to accept the source. Porting to another backend requires
the same expected-output tests there. Spectre has not been run for this addition.

The package does not add the missing clock divider, serializer stages, driver
tap summation or channel. Tests do not establish jitter, BER, physical timing
margins or full-link operation.
