* Datapath: tx_top -> flat test channel -> rx_top, both on ideal 14 GHz clocks.
* No PLL and no CDR: this checks the wiring, the lane order and the levels only.
* Run with: make -C analog/PAM4SerDes/build/sim link DECK=tb_datapath
* (about a minute on an idle machine, once the devices are built)
*
* PASS: the receiver's words are the transmitted PRBS7, in order, with 0 errors.
* FFE and DFE are off (w_main = 1, alpha = 0) because the test channel is flat.
*
* Two things this deck needs from ngspice (45 or newer):
*  - the default solver. `.option klu` is faster but gives wrong node voltages with
*    these OSDI devices;
*  - the fourth `tran` argument. ngspice's minimum time step is 1e-11 times it, so 1m
*    gives a 10 fs floor; without it the floor is 1e-23 s and the run dies with
*    "timestep too small" just before a clock edge. The models still limit the real step
*    to 0.5 ps.
.include "../build/sim/out/pam4_serdes.cir"

* receiver clock offset from the transmitter's, and the channel's flat gain: with the
* VGA at mid gain (vctrl 0.35 V) this puts +-150 / +-50 mV on the slicers
.param tdrx=27p gch=0.61

Vdd  vdd  0 0.7
Vddo vddo 0 1.25
Vref vref 0 0.6
Ven  en   0 1.25
Vrst rst  0 pulse(0.7 0 1n 20p 20p 1 2)
Vckt cktx 0 pulse(0 0.7 0 5p 5p 30.714p 71.4286p)
Vckr ckrx 0 pulse(0 0.7 {tdrx} 5p 5p 30.714p 71.4286p)

* tx_top pins: ckin rst en vref txp txn pgood vdd vddo vss
Xtx cktx rst en vref txp txn pgood vdd vddo 0 tx_top rj_scale=0 w_pre=0 w_main=1 w_post=0

* flat channel: gain gch, 50 ohm per side into the receiver's 100 ohm termination
Ech chd 0 txp txn {gch}
Ep  sp cm chd 0 1
En  sn cm chd 0 -1
Vcm cm 0 0.55
Rsp sp rxp 50
Rsn sn rxn 50
Vtt   vtt   0 0.55
Vctrl vctrl 0 0.35

* rx_top pins: rx_p rx_n vtt vctrl ckin rst afe_p afe_n clk14_p clk14_n rxd_m[0:31] rxd_l[0:31] clk0p875 vdd vss
Xrx rxp rxn vtt vctrl ckrx rst afe_p afe_n c14p c14n
+ rxm0 rxm1 rxm2 rxm3 rxm4 rxm5 rxm6 rxm7 rxm8 rxm9 rxm10 rxm11 rxm12 rxm13 rxm14 rxm15 rxm16 rxm17 rxm18 rxm19 rxm20 rxm21 rxm22 rxm23 rxm24 rxm25 rxm26 rxm27 rxm28 rxm29 rxm30 rxm31
+ rxl0 rxl1 rxl2 rxl3 rxl4 rxl5 rxl6 rxl7 rxl8 rxl9 rxl10 rxl11 rxl12 rxl13 rxl14 rxl15 rxl16 rxl17 rxl18 rxl19 rxl20 rxl21 rxl22 rxl23 rxl24 rxl25 rxl26 rxl27 rxl28 rxl29 rxl30 rxl31
+ wclk vdd 0 rx_top rj_scale=0 alpha=0

* PRBS checker (test/prbs_chk.va): pins clk m[0:31] l[0:31] err words
.model chk prbs_chk tstart=6.2n
Nchk wclk
+ rxm0 rxm1 rxm2 rxm3 rxm4 rxm5 rxm6 rxm7 rxm8 rxm9 rxm10 rxm11 rxm12 rxm13 rxm14 rxm15 rxm16 rxm17 rxm18 rxm19 rxm20 rxm21 rxm22 rxm23 rxm24 rxm25 rxm26 rxm27 rxm28 rxm29 rxm30 rxm31
+ rxl0 rxl1 rxl2 rxl3 rxl4 rxl5 rxl6 rxl7 rxl8 rxl9 rxl10 rxl11 rxl12 rxl13 rxl14 rxl15 rxl16 rxl17 rxl18 rxl19 rxl20 rxl21 rxl22 rxl23 rxl24 rxl25 rxl26 rxl27 rxl28 rxl29 rxl30 rxl31
+ err words chk

.save v(err) v(words) v(wclk) v(txp) v(txn) v(afe_p) v(afe_n)
.control
set noaskquit
tran 1p 26n 0 1m
let nerr = v(err)[length(v(err)) - 1]
let nwords = v(words)[length(v(words)) - 1]
if (nerr < 0.5) & (nwords > 9.5)
  echo "PASS tb_datapath: $&nerr errors in $&nwords words of 64 bits"
else
  echo "FAIL tb_datapath: $&nerr errors in $&nwords words of 64 bits"
end
quit
.endc
.end
