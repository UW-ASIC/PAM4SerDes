* The whole top level in one run: pam4_serdes on a flat test channel.
* Transmitter PLL, both clock trees, clock recovery, the bias blocks, jitter on.
* Run with: make -C analog/PAM4SerDes/build/sim link DECK=tb_top
* (the longest deck: about a quarter of an hour on an idle machine)
*
* PASS: once both loops have settled, the receiver's words are the transmitted PRBS7
* with 0 errors, the transmitter bias reports good, and the output swing is 0.8 V
* peak-to-peak differential.
*
* What this deck sets, and why:
*  - FFE and DFE off (w_main = 1, alpha = 0): the test channel is flat.
*  - force_lock high: the receiver's frequency acquisition is skipped. Its lock detector
*    needs 256 reference cycles (585 ns), which would triple the run. tb_pll.sp checks
*    the same phase detector, charge pump, filter, VCO, divider and lock detector.
*    tx_lock stays low here for the same reason: this run ends before 585 ns.
*  - the two references are separate sources with different phases, as on a board.
*
* The same ngspice notes as tb_datapath.sp apply: version 45 or newer, the default
* solver, and the fourth `tran` argument.
.include "../build/sim/out/pam4_serdes.cir"

Vdd  vdd  0 0.7
Vddo vddo 0 1.25
Ven  en   0 1.25
Vren ren  0 0.7
Vfl  fl   0 0.7
Vrst rst  0 pulse(0.7 0 1n 20p 20p 1 2)
Vtp rtp 0 sin(0.35 0.1 437.5meg)
Vtn rtn 0 sin(0.35 -0.1 437.5meg)
Vrp rrp 0 sin(0.35 0.1 437.5meg 0 0 100)
Vrn rrn 0 sin(0.35 -0.1 437.5meg 0 0 100)

* pam4_serdes pins: refclk_tx_p refclk_tx_n refclk_rx_p refclk_rx_n rst bias_en tx_en rx_en
*   txp txn tx_lock tx_pgood rx_p rx_n force_lock rxd_m[0:31] rxd_l[0:31] rx_wclk rx_lock
*   vdd vddo vss
X1 rtp rtn rrp rrn rst en en ren txp txn txlock pgood rxp rxn fl
+ rxm0 rxm1 rxm2 rxm3 rxm4 rxm5 rxm6 rxm7 rxm8 rxm9 rxm10 rxm11 rxm12 rxm13 rxm14 rxm15 rxm16 rxm17 rxm18 rxm19 rxm20 rxm21 rxm22 rxm23 rxm24 rxm25 rxm26 rxm27 rxm28 rxm29 rxm30 rxm31
+ rxl0 rxl1 rxl2 rxl3 rxl4 rxl5 rxl6 rxl7 rxl8 rxl9 rxl10 rxl11 rxl12 rxl13 rxl14 rxl15 rxl16 rxl17 rxl18 rxl19 rxl20 rxl21 rxl22 rxl23 rxl24 rxl25 rxl26 rxl27 rxl28 rxl29 rxl30 rxl31
+ wclk rxlock vdd vddo 0 pam4_serdes w_pre=0 w_main=1 w_post=0 alpha=0

* flat channel: gain 0.61, 50 ohm per side into the receiver's 100 ohm termination
Ech chd 0 txp txn 0.61
Ep  sp cm chd 0 1
En  sn cm chd 0 -1
Vcm cm 0 0.55
Rsp sp rxp 50
Rsn sn rxn 50

* count errors only once both loops have settled
.model chk prbs_chk tstart=190n
Nchk wclk
+ rxm0 rxm1 rxm2 rxm3 rxm4 rxm5 rxm6 rxm7 rxm8 rxm9 rxm10 rxm11 rxm12 rxm13 rxm14 rxm15 rxm16 rxm17 rxm18 rxm19 rxm20 rxm21 rxm22 rxm23 rxm24 rxm25 rxm26 rxm27 rxm28 rxm29 rxm30 rxm31
+ rxl0 rxl1 rxl2 rxl3 rxl4 rxl5 rxl6 rxl7 rxl8 rxl9 rxl10 rxl11 rxl12 rxl13 rxl14 rxl15 rxl16 rxl17 rxl18 rxl19 rxl20 rxl21 rxl22 rxl23 rxl24 rxl25 rxl26 rxl27 rxl28 rxl29 rxl30 rxl31
+ err words chk

.save v(err) v(words) v(x1.vctl_tx) v(x1.vctl_rx) v(pgood) v(txp) v(txn) v(x1.vref) v(x1.vtt) v(x1.vctrl)
.control
set noaskquit
tran 1p 215n 0 10u
let nerr = v(err)[length(v(err)) - 1]
let nwords = v(words)[length(v(words)) - 1]
let vtx = v(x1.vctl_tx)[length(v(x1.vctl_tx)) - 1]
let vrx = v(x1.vctl_rx)[length(v(x1.vctl_rx)) - 1]
let pg = v(pgood)[length(v(pgood)) - 1]
let vref = v(x1.vref)[length(v(x1.vref)) - 1]
let vtt = v(x1.vtt)[length(v(x1.vtt)) - 1]
let vctrl = v(x1.vctrl)[length(v(x1.vctrl)) - 1]
let vout = v(txp) - v(txn)
meas tran swing pp vout from=190n to=215n
echo "control voltages at the end: transmitter $&vtx V, receiver $&vrx V"
if (nerr < 0.5) & (nwords > 9.5) & (pg > 1) & (abs(swing - 0.8) < 20m)
  echo "PASS tb_top: $&nerr errors in $&nwords words of 64 bits, swing $&swing V"
  echo "SPEC Bit errors, whole top level (PLL, clock recovery, bias blocks, jitter on) | $&nerr in $&nwords words of 64 bits"
  echo "SPEC Transmitter output swing, peak-to-peak differential | $&swing V"
  echo "SPEC Bias: vref, vtt, vctrl as generated | $&vref, $&vtt, $&vctrl V"
else
  echo "FAIL tb_top: $&nerr errors in $&nwords words, pgood $&pg V, swing $&swing V"
end
quit
.endc
.end
