# Transmitter adaptation verification

Result: **PASS** using the actual files in this repository layout.

Base repository commit: `a70ec8c7ca1e0570d47b876099c80d95cf3f0547`.
Simulator: `vera 0.23.0`; Zig `0.18.0-dev.349+d924f83bf`.
Run timestamp (UTC): `2026-11-19T22:33:38.466266+00:00`.

| Check | Result |
| --- | --- |
| mux2_cml_hr-test | PASS: lint and check passed |
| ffe_tapgen_hr-test | PASS: lint and check passed |
| tx_cml_ffe_path-test | PASS: lint and check passed |
| include-guards | PASS: cells and test wrapper can be included repeatedly without duplicate modules |
| mux-dc | PASS: all eight input/clock combinations, polarity, swing and common-mode |
| mux-transient | PASS: 172 outputs: 7/14 GHz interleaving, held-clock transparency, 100-ohm load; 4768 settled hold checks |
| ffe-half-rate-init0 | PASS: 240 half-rate tap values; phase hold, poisoned inputs, reset/refill, all six common-modes |
| ffe-half-rate-init1 | PASS: 240 half-rate tap values; phase hold, poisoned inputs, reset/refill, all six common-modes |
| half-rate-tx-msb-lsb | PASS: 128 symbols/path; 768 final tap values; 10 muxes + 2 FFEs; bank hold and common-mode |
| supply-reset-1p0 | PASS: 84 tap values; automatic/fixed reset thresholds, stopped-clock reset, VSS=0.0 V |
| supply-reset-1p8 | PASS: 84 tap values; automatic/fixed reset thresholds, stopped-clock reset, VSS=0.2 V |
| team-neighbors | PASS: 128 retimed bits, 384 taps, 384 buffered taps, 64 MAIN-only PAM4 symbols; all four levels |

Earlier checks of unchanged Make recipes: GNU Make tx-help and dry-run of tx-lint/tx-check/tx-test under Ubuntu WSL, including executable paths with spaces; lint from a different working directory; nonzero exit and FAIL report for a missing compiler.

The full simulation ran on Windows through the portable Python entry point. The Linux Make recipes were inspected via dry-run; a Linux VerA simulation was not run. No OpenVAF/OSDI, ESPice or transistor integration is claimed.

The new reset tests keep reset release clear of clock crossings. They check startup history separately from filled history, automatic/fixed thresholds at 1.0/1.8 V, VSS=0.2 V and reset with the clock stopped.

The team-neighbors test uses the actual upstream cml_dff_x4, six predriver_cml instances and pam4_driver, with both MSB/LSB CML/FFE paths. It verifies retimer storage, all three taps per path and all four MAIN-only PAM4 levels. The driver currently has no PRE/POST inputs or FFE summation. The clock tree still has a missing div2_cml and mismatched helper interfaces; ideal phased clocks are used, not tx_clkgen.

Tested model SHA-256 hashes:

- `va/Transmitter/mux2_cml_hr.va`: `b654c9472645d978b651aa6fc5448e00832906c7ecca1ab17f5eede162aab7c5`
- `va/Transmitter/ffe_tapgen_hr.va`: `293794e485992d12873031edf33b55c120a8ec2e357d0488d2531d8a7a3fbc37`
- `test/tx_cml_ffe/fixtures/tx_cml_ffe_path.va`: `c1f35eaebdfe7dce31f1b0f4e87a16e8cce53d455e2165949e70078568888f4d`

Tested upstream neighbor SHA-256 hashes:

- `va/Clocking/cml_dff_x4.va`: `552f798852e88fa57dbd26bb6a6efcda3c305caef4572e5914773b24942f2104`
- `va/Transmitter/predriver_cml.va`: `319ab68d7c3554cec5c3472e5c7c861142e661e62bc6c9a70d2e3d7ca7c8dbd5`
- `va/Transmitter/pam4_driver.va`: `70838e8eff6cff866222c044b51549e21340fe781b77f8082cd17a21fbb36502`
