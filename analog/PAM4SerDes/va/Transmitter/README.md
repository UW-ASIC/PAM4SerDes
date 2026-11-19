# Half-rate CML mux and FFE

These two behavioral cells implement the detailed transmitter diagram's CML/FFE
partition. Instantiate this path once for MSB and once for already mapped LSB:

```text
Four retimed 7 Gb/s differential lanes d0, d1, d2, d3
  -> two mux2_cml_hr at clk7: (d0,d2) -> EVEN, (d1,d3) -> ODD
  -> ffe_tapgen_hr at clk14: PRE E/O, MAIN E/O, POST E/O
  -> three mux2_cml_hr at clk14: PRE, MAIN, POST at 28 Gb/s
  -> predrivers -> weighted PAM4 driver
```

Each `_p/_n` pair carries one signal. Positive differential data means bit 1.
The mux selects EVEN when its differential clock is positive, ODD when negative.
It is transparent, so selected data must remain stable throughout that interval.

The FFE captures both inputs together at rising clk14. It updates the ODD output
bank on rising edges and the EVEN bank on falling edges, while each is unselected.
After one clock period of common capture-to-selection latency, the final muxes
produce PRE=x[n], MAIN=x[n-1], POST=x[n-2]. Tap spacing is one UI (35.714 ps).
Tap signs, weights and MSB:LSB summation belong in the driver.

Reset is active high relative to VSS. The default `vth_rst=-1` uses
`rst_fraction*V(vdd,vss)`, with `rst_fraction=0.5`. Set `vth_rst=0.35` explicitly
to retain a fixed 0.35 V threshold. Reset clears history and both output banks
to `init_bit`, including with a stopped clock. Avoid changing data or releasing
reset at the capture edge; setup/hold violations are not modeled.

Default outputs are +/-0.3 V differential (0.6 Vppd) with negligible external
loading: 1.5 mA per output pair and 200 ohms per leg. Common-mode relative to VSS
is `V(vdd,vss)-0.15 V`. Timing and capacitance defaults are provisional, not
transistor characterization. Both files have include guards for hierarchy reuse.

These exact model versions passed 12 VerA 0.23.0 test groups in the integration
branch, including connection to the team's retimer, predrivers and MAIN-only
PAM4 driver. See the [verification results and source hashes](https://github.com/hdsouza13/PAM4SerDes/blob/b708f5fb93364327e630323097721cb9ec1ddbba/analog/PAM4SerDes/test/tx_cml_ffe/VERIFICATION.md)
and [full interface/test guide](https://github.com/hdsouza13/PAM4SerDes/blob/b708f5fb93364327e630323097721cb9ec1ddbba/analog/PAM4SerDes/va/Transmitter/README.md).
That validation does not establish full-link operation: the reviewed driver
still lacks PRE/POST summation and the clock-tree interfaces need integration.
