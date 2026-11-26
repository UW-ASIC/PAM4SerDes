# tx_bias

| Field | Value |
|---|---|
| Owner (from git history) | Krrish Lala |
| Kind | leaf (behavioural model) |
| Model | [`va/Transmitter/tx_bias.va`](../../va/Transmitter/tx_bias.va) |
| Used in | [tx_top](../Transmitter/tx_top.md), once (`u_bias`) |
| Section | [Biasing](README.md) |

## Architecture

`tx_bias` makes the bias currents of the transmitter's output stage. It sinks six tail currents from the PAM4 driver, one per binary path (MSB, LSB) and FFE tap (pre, main, post), and one more for the pre-drivers.

The system needs it because those currents decide three things at once:

- the **output swing**: the total current into the 25 ohm load,
- the **PAM4 weighting**: the MSB path carries twice the current of the LSB path,
- the **FFE tap weights**: each path's current is split 0.05 / 0.80 / 0.15 between pre, main and post.

With the defaults the total is 16 mA, which gives 0.4 V peak (0.8 V peak-to-peak differential) into 25 ohm.

The model's header describes the circuit it stands for as a current reference with mirrors, where the swing is controlled by a replica cell and an op-amp. Two modes are modelled:

- `swing_loop = 1` (default): the loop forces the replica swing to follow `vref`, so the total current is `vppd * V(vref)/vref_nom / rterm_act`. The swing then does not depend on the actual termination value.
- `swing_loop = 0`: a plain mirror. The total current uses the nominal termination `rterm_nom`, so the swing changes with any termination error.

### Where it sits

`tx_bias` is the only bias block in the design. Its file is in `va/Transmitter/`, but the documentation keeps it in the Biasing section.

In [tx_top](../Transmitter/tx_top.md):

- `vdd` is connected to `vddo`, the 1.25 V output-stage supply.
- `en` and `vref` come from the top-level pins `tx_en` (1.25 V logic, high = on) and `vref` (0.6 V).
- The six `i_*` pins go to the tail nodes of [pam4_driver](../Transmitter/pam4_driver.md), which holds them at 0.6 V.
- `i_pdrv` is **not connected**: [predriver_cml](../Transmitter/predriver_cml.md) is ideal and has no bias pin yet.
- `pgood` goes out as the top-level pin `tx_pgood`.

It is a DC block. It has no clock.

### Ports

| Port | Direction | Carries |
|---|---|---|
| `vdd`, `vss` | inout | Supply (1.25 V in `tx_top`) and ground |
| `en` | input | Enable, high = on. Threshold 0.6 V (`ven_th`) |
| `vref` | input | Reference voltage, 0.6 V nominal. All currents scale with `V(vref)/vref_nom` |
| `i_msb_pre`, `i_msb_main`, `i_msb_post` | inout | Current sinks for the MSB path's three driver taps |
| `i_lsb_pre`, `i_lsb_main`, `i_lsb_post` | inout | Current sinks for the LSB path's three driver taps |
| `i_pdrv` | inout | Current sink for the pre-driver tails (unconnected in `tx_top`) |
| `pgood` | output | Power-good flag: high once the block is enabled and the supply has headroom |

### Parameters

| Parameter | Default | Meaning |
|---|---|---|
| `vppd` | 0.8 V | Target differential peak-to-peak swing, allowed 0.7 to 0.9 V |
| `rterm_nom`, `rterm_act` | 50 ohm, 50 ohm | Nominal and actual termination per side |
| `swing_loop` | 1 | 1 = replica + op-amp loop, 0 = open-loop mirror |
| `w_pre`, `w_main`, `w_post` | 0.05, 0.80, 0.15 | FFE tap weights (magnitudes). `tx_top` passes the top-level values |
| `msb_ratio` | 2.0 | MSB current / LSB current |
| `ratio_err` | 0 | Fractional error of the MSB mirror, for level-mismatch studies |
| `vod_pd`, `rld_pd`, `n_pd` | 0.2 V, 200 ohm, 6 | Pre-driver swing, load (assumed) and number of cells fed by `i_pdrv` |
| `vref_nom` | 0.6 V | Reference value that gives the nominal currents |
| `vdd_nom`, `vdd_min`, `vdd_w` | 1.25 V, 1.0 V, 0.03 V | Nominal supply, lowest supply for full current, width of that turn-on |
| `psrr_db` | 40 dB | Supply sensitivity of the reference path |
| `vdsat` | 0.15 V | Compliance knee of the tail devices: an output needs more than this across it |
| `rout` | 1 Mohm | Output resistance of each sink |
| `t_en` | 1 ns | Time constant of the enable settling |
| `vpg_hi`, `vpg_lo` | 1.25 V, 0 V | Levels of `pgood` |

### What the model leaves out

- The replica loop is an equation, not a loop: it has no dynamics, no offset and no stability question.
- Mismatch exists only as `ratio_err` on the MSB mirror. There is no noise and no temperature dependence.
- The reference is an input. Nothing in the design generates `vref` yet; the parameter comment calls it "e.g. bandgap-derived".
- The pre-driver load `rld_pd` is marked "assumed".
- The block's own supply current is modelled as 1 % of the currents it sinks.

Existing testbenches: [`test/tx_bias_test.sp`](../../test/tx_bias_test.sp) (this block alone) and [`test/tx_driver_test.sp`](../../test/tx_driver_test.sp) (with the driver attached).

## Topology research

*To be filled in by the owner during the topology-research stage.*

The goal of this section is to decide which circuit implements this block, and to write down why, so the next person does not have to redo the search.

### Requirements

What the circuit must do. Start from the [Architecture](#architecture) section above, then add what is missing (supply, load, power, area, noise) and name the source of every number.

Already stated in the model. Parameter defaults are the model's present assumptions, not signed-off specs: confirm or correct each one here.

- Output swing 0.8 V peak-to-peak differential into 50 ohm in parallel with 50 ohm = 25 ohm; allowed range 0.7 to 0.9 V (`tx_bias.va`, header and the range of `vppd`)
- Total driver current 16 mA, split MSB : LSB = 2 : 1, that is 10.67 mA and 5.33 mA (`tx_bias.va`, header)
- FFE taps -0.05 / +0.80 / -0.15, so the tap currents are 0.53 / 8.53 / 1.60 mA on the MSB side and 0.27 / 4.27 / 0.80 mA on the LSB side (`tx_bias.va`, header)
- Output-stage supply 1.25 V (`tx_bias.va`, header)
- Every output is a current sink into `vss` (NMOS-tail behaviour); tap signs are applied by the driver, not here (`tx_bias.va`, header)
- The swing should track the reference and not the actual termination value: the replica + op-amp option, `swing_loop = 1` (`tx_bias.va`, header)
- Model defaults for the output devices: compliance knee 0.15 V (`vdsat`), output resistance 1 Mohm (`rout`), enable settling time constant 1 ns (`t_en`) (`tx_bias.va`, parameters)
- Model defaults for the supply: full current from 1.0 V up (`vdd_min`), supply rejection of the reference path 40 dB (`psrr_db`) (`tx_bias.va`, parameters)
- Pre-driver tail: 0.2 V swing over a 200 ohm load per cell, six cells; the 200 ohm is marked "assumed" (`tx_bias.va`, parameters `vod_pd`, `rld_pd`, `n_pd`)

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

A schematic or a sketch of the chosen circuit. Name its nodes like the ports in the Architecture section. Put the image file in `analog/PAM4SerDes/docs/img/`, named `tx_bias_<what>.svg` (or `.png`), and reference it from this page as `![tx_bias schematic](../img/tx_bias_<what>.svg)`.

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
