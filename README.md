# PAM4 SerDes

A 56 Gb/s PAM4 serializer/deserializer (28 GBd, two bits per symbol) by the UW ASIC student team, after Lee et al., JSSC 2015 ("56 Gb/s NRZ/PAM4").

Every block has a behavioural Verilog-A model, and the models are wired into one hierarchy that simulates end to end. **Next: topology research, then sizing research, for every block.** If you own a block, fill in the Topology research section of its page. The tables below take you there.

## Measured specs

Written by CI from the Verilog-A simulations (`make -C analog/PAM4SerDes/build/sim check`). Do not edit this table by hand.

<!-- specs:begin -->
| Spec | Value | Measured by |
|---|---|---|
| Transmitter PAM4 levels, differential | -0.399702, -0.133184, 0.133304, 0.399822 V | `tx_driver_test` |
| Transmitter FFE: peak, de-emphasised level | 0.399822, 0.239809 V | `tx_driver_test` |
| Transmitter PLL: lock detector asserts after | 669.872 ns | `tb_pll` |
| Transmitter PLL: control voltage when locked | 0.350313 V | `tb_pll` |
| Bit errors, transmitter to receiver on ideal clocks | 0 in 17 words of 64 bits | `tb_datapath` |
| Bit errors with the receiver clock recovered from the data | 0 in 35 words of 64 bits | `tb_cdr` |
| Clock recovery control voltage, tracking | 0.351985 V | `tb_cdr` |
| Bit errors, whole top level (PLL, clock recovery, bias blocks, jitter on) | 0 in 22 words of 64 bits | `tb_top` |
| Transmitter output swing, peak-to-peak differential | 0.799643 V | `tb_top` |
| Bias: vref, vtt, vctrl as generated | 0.6, 0.5549, 0.353118 V | `tb_top` |
| Cells in the design | 238 instances of 42 cell types | `architecture.txt` |
| Ideal placeholders still in use | div2_cml, mux2_cs | `architecture.txt` |
<!-- specs:end -->

## Blocks: who owns what, and where to read it

Every block has one page with three sections: **Architecture** (written, from the model), then **Topology research** and **Sizing research** (templates the owner fills in). The pages are `analog/PAM4SerDes/docs/<Section>/<block>.md`. Keep their three `##` headings, because these tables link to them.

Owners are taken from the git history. If a name is wrong, correct it here, in the section overview and on the block's page.

### Biasing

Section overview: [Biasing](analog/PAM4SerDes/docs/Biasing/README.md)

| Block | Owner | Architecture | Topology research | Sizing research |
|---|---|---|---|---|
| bias_ref | Omar ElSawy | [read](analog/PAM4SerDes/docs/Biasing/bias_ref.md#architecture) | [read / write](analog/PAM4SerDes/docs/Biasing/bias_ref.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Biasing/bias_ref.md#sizing-research) |
| tx_bias | Krrish Lala | [read](analog/PAM4SerDes/docs/Biasing/tx_bias.md#architecture) | [read / write](analog/PAM4SerDes/docs/Biasing/tx_bias.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Biasing/tx_bias.md#sizing-research) |
| tx_predrv_bias | Omar ElSawy | [read](analog/PAM4SerDes/docs/Biasing/tx_predrv_bias.md#architecture) | [read / write](analog/PAM4SerDes/docs/Biasing/tx_predrv_bias.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Biasing/tx_predrv_bias.md#sizing-research) |
| rx_bias | Omar ElSawy | [read](analog/PAM4SerDes/docs/Biasing/rx_bias.md#architecture) | [read / write](analog/PAM4SerDes/docs/Biasing/rx_bias.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Biasing/rx_bias.md#sizing-research) |
| clk_bias | Omar ElSawy | [read](analog/PAM4SerDes/docs/Biasing/clk_bias.md#architecture) | [read / write](analog/PAM4SerDes/docs/Biasing/clk_bias.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Biasing/clk_bias.md#sizing-research) |

### Clocking

Section overview: [Clocking](analog/PAM4SerDes/docs/Clocking/README.md)

| Block | Owner (from git history) | Architecture | Topology research | Sizing research |
|---|---|---|---|---|
| refclk_buf | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/refclk_buf.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/refclk_buf.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/refclk_buf.md#sizing-research) |
| tx_pll | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/tx_pll.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Clocking/tx_pll.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Clocking/tx_pll.md#sizing-research) |
| pfd | GreenBlueFish | [read](analog/PAM4SerDes/docs/Clocking/pfd.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/pfd.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/pfd.md#sizing-research) |
| charge_pump | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/charge_pump.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/charge_pump.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/charge_pump.md#sizing-research) |
| loop_filter_rc | Sudhanshu Tiwari | [read](analog/PAM4SerDes/docs/Clocking/loop_filter_rc.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/loop_filter_rc.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/loop_filter_rc.md#sizing-research) |
| vco | GreenBlueFish | [read](analog/PAM4SerDes/docs/Clocking/vco.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/vco.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/vco.md#sizing-research) |
| div_n | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/div_n.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/div_n.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/div_n.md#sizing-research) |
| lock_detect | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/lock_detect.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/lock_detect.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/lock_detect.md#sizing-research) |
| tx_clkgen | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/tx_clkgen.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Clocking/tx_clkgen.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Clocking/tx_clkgen.md#sizing-research) |
| rx_clkgen | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/rx_clkgen.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Clocking/rx_clkgen.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Clocking/rx_clkgen.md#sizing-research) |
| dcc_cml | Sudhanshu Tiwari | [read](analog/PAM4SerDes/docs/Clocking/dcc_cml.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/dcc_cml.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/dcc_cml.md#sizing-research) |
| clkbuf_cml | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/clkbuf_cml.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/clkbuf_cml.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/clkbuf_cml.md#sizing-research) |
| div2_cml | none yet | [read](analog/PAM4SerDes/docs/Clocking/div2_cml.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/div2_cml.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/div2_cml.md#sizing-research) |
| cml2cmos | Sudhanshu Tiwari | [read](analog/PAM4SerDes/docs/Clocking/cml2cmos.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/cml2cmos.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/cml2cmos.md#sizing-research) |
| phase_aligner | Winy | [read](analog/PAM4SerDes/docs/Clocking/phase_aligner.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/phase_aligner.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/phase_aligner.md#sizing-research) |
| div2_tspc | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/div2_tspc.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/div2_tspc.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/div2_tspc.md#sizing-research) |
| rx_cdr | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/rx_cdr.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Clocking/rx_cdr.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Clocking/rx_cdr.md#sizing-research) |
| cdr_pd_linear | Winy | [read](analog/PAM4SerDes/docs/Clocking/cdr_pd_linear.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/cdr_pd_linear.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/cdr_pd_linear.md#sizing-research) |
| cdr_glue (`qdelay`, `nor2`) | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/glue.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/glue.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/glue.md#sizing-research) |
| diff2se | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/glue.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/glue.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/glue.md#sizing-research) |
| dff_cmos_x32 | Sudhanshu Tiwari | [read](analog/PAM4SerDes/docs/Clocking/dff_cmos_x32.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/dff_cmos_x32.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/dff_cmos_x32.md#sizing-research) |
| dff_tspc_x8 | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Clocking/dff_tspc_x8.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/dff_tspc_x8.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/dff_tspc_x8.md#sizing-research) |
| cml_dff_x4 | Sudhanshu Tiwari | [read](analog/PAM4SerDes/docs/Clocking/cml_dff_x4.md#architecture) | [read / write](analog/PAM4SerDes/docs/Clocking/cml_dff_x4.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Clocking/cml_dff_x4.md#sizing-research) |

### Transmitter

Section overview: [Transmitter](analog/PAM4SerDes/docs/Transmitter/README.md)

| Block | Owner (from git history) | Architecture | Topology research | Sizing research |
|---|---|---|---|---|
| tx_top | Omar ElSawy (integration) | [read](analog/PAM4SerDes/docs/Transmitter/tx_top.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Transmitter/tx_top.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Transmitter/tx_top.md#sizing-research) |
| tx_ser_ffe_path | Omar ElSawy (integration) | [read](analog/PAM4SerDes/docs/Transmitter/tx_ser_ffe_path.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Transmitter/tx_ser_ffe_path.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Transmitter/tx_ser_ffe_path.md#sizing-research) |
| prbs_gray_src | oDNA | [read](analog/PAM4SerDes/docs/Transmitter/prbs_gray_src.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/prbs_gray_src.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/prbs_gray_src.md#sizing-research) |
| mux2_cmos | oDNA | [read](analog/PAM4SerDes/docs/Transmitter/mux2_cmos.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/mux2_cmos.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/mux2_cmos.md#sizing-research) |
| mux2_cs | none yet | [read](analog/PAM4SerDes/docs/Transmitter/mux2_cs.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/mux2_cs.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/mux2_cs.md#sizing-research) |
| mux2_cml_hr | hdsouza13 | [read](analog/PAM4SerDes/docs/Transmitter/mux2_cml_hr.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/mux2_cml_hr.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/mux2_cml_hr.md#sizing-research) |
| ffe_tapgen_hr | hdsouza13 | [read](analog/PAM4SerDes/docs/Transmitter/ffe_tapgen_hr.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/ffe_tapgen_hr.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/ffe_tapgen_hr.md#sizing-research) |
| predriver_cml | Zoey Situ | [read](analog/PAM4SerDes/docs/Transmitter/predriver_cml.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/predriver_cml.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/predriver_cml.md#sizing-research) |
| pam4_driver | Zoey Situ | [read](analog/PAM4SerDes/docs/Transmitter/pam4_driver.md#architecture) | [read / write](analog/PAM4SerDes/docs/Transmitter/pam4_driver.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Transmitter/pam4_driver.md#sizing-research) |

### Receiver

Section overview: [Receiver](analog/PAM4SerDes/docs/Receiver/README.md)

| Block | Owner (from git history) | Architecture | Topology research | Sizing research |
|---|---|---|---|---|
| rx_top | Omar ElSawy (integration) | [read](analog/PAM4SerDes/docs/Receiver/rx_top.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Receiver/rx_top.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Receiver/rx_top.md#sizing-research) |
| rx_afe | Ethan Sun (sunezh) | [read](analog/PAM4SerDes/docs/Receiver/rx_afe.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Receiver/rx_afe.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Receiver/rx_afe.md#sizing-research) |
| rx_term | Mehak Khan | [read](analog/PAM4SerDes/docs/Receiver/rx_term.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/rx_term.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/rx_term.md#sizing-research) |
| ctle | Kayhan Baig | [read](analog/PAM4SerDes/docs/Receiver/ctle.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/ctle.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/ctle.md#sizing-research) |
| vga | Mehak Khan | [read](analog/PAM4SerDes/docs/Receiver/vga.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/vga.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/vga.md#sizing-research) |
| rx_decision | Mehak Khan | [read](analog/PAM4SerDes/docs/Receiver/rx_decision.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Receiver/rx_decision.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Receiver/rx_decision.md#sizing-research) |
| slicer | Justin Fang | [read](analog/PAM4SerDes/docs/Receiver/slicer.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/slicer.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/slicer.md#sizing-research) |
| threshold_dac | Justin Fang | [read](analog/PAM4SerDes/docs/Receiver/threshold_dac.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/threshold_dac.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/threshold_dac.md#sizing-research) |
| pam4_slicer | Justin Fang | [read](analog/PAM4SerDes/docs/Receiver/pam4_slicer.md#architecture) | [see its cells](analog/PAM4SerDes/docs/Receiver/pam4_slicer.md#topology-research) | [see its cells](analog/PAM4SerDes/docs/Receiver/pam4_slicer.md#sizing-research) |
| dfe1_unrolled_hr | deaconsham | [read](analog/PAM4SerDes/docs/Receiver/dfe1_unrolled_hr.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/dfe1_unrolled_hr.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/dfe1_unrolled_hr.md#sizing-research) |
| pam4_dec | Kayhan Baig | [read](analog/PAM4SerDes/docs/Receiver/pam4_dec.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/pam4_dec.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/pam4_dec.md#sizing-research) |
| rx_dec_retime | Mehak Khan | [read](analog/PAM4SerDes/docs/Receiver/rx_dec_retime.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/rx_dec_retime.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/rx_dec_retime.md#sizing-research) |
| rx_deser_path | Mehak Khan | [read](analog/PAM4SerDes/docs/Receiver/rx_deser_path.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/rx_deser_path.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/rx_deser_path.md#sizing-research) |
| demux2_cml | deaconsham | [read](analog/PAM4SerDes/docs/Receiver/demux2_cml.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/demux2_cml.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/demux2_cml.md#sizing-research) |
| demux2_cmos | deaconsham | [read](analog/PAM4SerDes/docs/Receiver/demux2_cmos.md#architecture) | [read / write](analog/PAM4SerDes/docs/Receiver/demux2_cmos.md#topology-research) | [read / write](analog/PAM4SerDes/docs/Receiver/demux2_cmos.md#sizing-research) |

Notes:

- `div2_cml` and `mux2_cs` are ideal placeholders with no owner. Someone needs to take each one.
- `charge_pump` and the glue cells (`qdelay`, `nor2`, `diff2se`) are ideal on purpose. Their pages say what has to be settled first.
- `pam4_slicer` has a model but is not placed in the hierarchy.
- Structural blocks (`tx_pll`, `tx_top`, `rx_top` and the like) are wiring only. Their research sections point to the pages of their cells.

## Architecture at a glance

![Top level: transmitter, receiver and their clocking](analog/PAM4SerDes/docs/img/top.svg)

- **Transmitter.** A PLL multiplies a 437.5 MHz reference by 32 to 14 GHz. A PRBS7 source makes 32 Gray-coded symbols per word. Two identical paths (MSB, LSB) serialize 32:1 and make three FFE taps at half rate. The driver sums the six taps into 0.8 V peak-to-peak differential PAM4.
- **Receiver.** Termination, CTLE and VGA condition the signal. Twenty-four slicers and a one-tap unrolled DFE decide each symbol on two phases of the 14 GHz clock. Decoders, retimers and two 1:32 deserializers give two 32-bit words per 0.875 GHz word clock.
- **Clocking.** The receiver has its own loop: it locks to a reference, then a linear phase detector tracks the data. Each side divides 14 GHz down to 0.875 GHz.
- **Biasing.** One reference feeds a bias block per side. Every consumer gets a wire of its own.

The models are written for a 0.7 V core supply (their comments say ASAP7). The channel between the pads is not part of the design; a testbench supplies it.

The [documentation index](analog/PAM4SerDes/docs/README.md) has the full hierarchy, the top-level pins and the four section overviews.

## Check the design

```bash
./env.sh                                     # ngspice 45 and VerA (the first run builds VerA: minutes)
make -C analog/PAM4SerDes/build/sim check    # lint, arch, link, specs
```

| Step | What it does |
|---|---|
| `lint` | Every `.va` file compiles (`vera --lint`) |
| `arch` | The hierarchy in the `.va` files is the one in [`architecture.txt`](analog/PAM4SerDes/architecture.txt). After a deliberate change: `make ... arch UPDATE=1` |
| `link` | Builds one ngspice deck and the devices from the `.va` hierarchy, then runs the test decks. One PASS or FAIL line each; `link DECK=tb_cdr` runs one |
| `specs` | Writes what the decks measured into the table above |

| Deck in [`analog/PAM4SerDes/test/`](analog/PAM4SerDes/test) | Checks |
|---|---|
| `tx_driver_test` | Driver and bias: the four PAM4 levels, FFE peak and de-emphasis |
| `tb_pll` | The transmitter PLL locks, jitter on |
| `tb_datapath` | Transmitter to receiver on ideal clocks: wiring, lane order, levels |
| `tb_cdr` | The same with the receiver's clock recovered from the data |
| `tb_top` | The whole top level in one run: PLL, clock recovery, bias blocks, jitter on |

CI ([`.github/workflows/analog.yaml`](.github/workflows/analog.yaml)) runs the same command on every change under `analog/` and, on `main`, commits the specs table.

If you write a deck for the hierarchy:

- `.include "../build/sim/out/pam4_serdes.cir"` and place the top level or a part of it (`X1 <pins> pam4_serdes`), pins in the order of the module's port list. Do not edit the generated deck: the `.va` files are the source.
- Use ngspice's default solver. `.option klu` gives wrong node voltages with these devices on ngspice 45.
- Give `tran` its fourth argument, `tran 1p <tstop> 0 10u`. It sets ngspice's minimum time step (1e-11 times it); without it runs stop with "timestep too small".
- Need a device of your own (a checker)? Add it to `VA_ALSO` in the Makefile.

## Changelog

[`CHANGELOGS.md`](CHANGELOGS.md): what integration changed in each person's work, and how the top level is put together. If your model was touched, the reason is there.

## Hosted documentation

The same pages, with the diagrams, are published at [https://uw-asic.github.io/PAM4SerDes/](https://uw-asic.github.io/PAM4SerDes/) once GitHub Pages is enabled for the repo. Until then, start from the [documentation index](analog/PAM4SerDes/docs/README.md).

## Repository layout

```
analog/PAM4SerDes/va/               the Verilog-A models
  pam4_serdes.va                    top level
  Biasing/  Clocking/  Transmitter/  Receiver/
analog/PAM4SerDes/test/             test decks
analog/PAM4SerDes/docs/             one page per block
analog/PAM4SerDes/architecture.txt  the hierarchy CI checks the models against
.flows/tools/va_deck.py             .va hierarchy -> ngspice deck and devices
.flows/tools/va_specs.py            deck output -> the specs table above
docs/                               the documentation website (Vite + React, bun)
CHANGELOGS.md                       what integration changed, per person
```

## Environment and generic flow documentation

This repository was started from the UWASIC design template, and the template's tooling is still here.

Enter the project environment with:

```bash
./env.sh
```

The generic flow documentation (environment setup, the digital, analog and mixed-signal flows, and TinyTapeout integration) lives in the docs site under [`docs/`](docs). To view it locally:

```bash
cd docs/
bun install
bun run dev
```
