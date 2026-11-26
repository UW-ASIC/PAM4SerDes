* pam4_driver + tx_bias: the driver's swing comes from the bias tail currents.
* Run with: make -C analog/PAM4SerDes/build/sim link DECK=tx_driver_test
* (builds the devices first; ngspice then runs this deck from the test/ folder)
*
* a:  FFE off (w_main = 1), msb/lsb stepped through the four symbols. Expected
*     differential output -0.4, -0.1333, +0.1333, +0.4 V: the levels pam4_driver
*     produced on its own before it took its swing from tx_bias.
* b1: default taps (0.05 / 0.80 / 0.15), every tap adding (pre and post opposite to
*     main): 16 mA into 25 ohm = 0.4 V.
* b2: default taps, a steady pattern (all taps equal): de-emphasised to
*     (0.80 - 0.05 - 0.15) * 0.4 = 0.24 V.
.control
pre_osdi ../build/sim/out/osdi/tx_bias.osdi
pre_osdi ../build/sim/out/osdi/pam4_driver.osdi
.endc
.model bias_noffe tx_bias w_pre=0 w_main=1 w_post=0
.model bias tx_bias
.model drv pam4_driver

Vdd  vddo 0 1.25
Vref vref 0 0.6
Vlo  lo   0 1.1
Vhi  hi   0 1.3
Vmid mid  0 1.2

* a: main inputs stepped through 00, 01, 10, 11 (msb, lsb), 1 ns each
Vmsb am 0 pulse(1.1 1.3 2n 1p 1p 2n 4n)
Vlsb al 0 pulse(1.1 1.3 1n 1p 1p 1n 2n)
* tx_bias pins: vdd vss en vref  i_msb_pre/main/post  i_lsb_pre/main/post  i_pdrv pgood
Nba vddo 0 vddo vref a1 a2 a3 a4 a5 a6 apd apg bias_noffe
* pam4_driver pins: msb pre/main/post (p n each)  lsb pre/main/post (p n each)  six tails  outp outn vss
Nda lo mid am mid lo mid  lo mid al mid lo mid  a1 a2 a3 a4 a5 a6 aop aon 0 drv

* b: default taps, main = +3 (11); pre/post opposite to main in b1, equal in b2
Nbb1 vddo 0 vddo vref c1 c2 c3 c4 c5 c6 bpd1 bpg1 bias
Ndb1 lo mid hi mid lo mid  lo mid hi mid lo mid  c1 c2 c3 c4 c5 c6 b1p b1n 0 drv
Nbb2 vddo 0 vddo vref e1 e2 e3 e4 e5 e6 bpd2 bpg2 bias
Ndb2 hi mid hi mid hi mid  hi mid hi mid hi mid  e1 e2 e3 e4 e5 e6 b2p b2n 0 drv

.control
set noaskquit
tran 10p 4n
let va = v(aop) - v(aon)
let vb1 = v(b1p) - v(b1n)
let vb2 = v(b2p) - v(b2n)
meas tran lvl00 find va at=0.5n
meas tran lvl01 find va at=1.5n
meas tran lvl10 find va at=2.5n
meas tran lvl11 find va at=3.5n
meas tran peak find vb1 at=3.5n
meas tran deemph find vb2 at=3.5n
if (abs(lvl00 + 0.4) > 1m) | (abs(lvl01 + 0.13333) > 1m) | (abs(lvl10 - 0.13333) > 1m) | (abs(lvl11 - 0.4) > 1m) | (abs(peak - 0.4) > 1m) | (abs(deemph - 0.24) > 1m)
  echo "FAIL tx_driver_test: a level is more than 1 mV off (see the values above)"
else
  echo "PASS tx_driver_test: four PAM4 levels, FFE peak and de-emphasis within 1 mV"
end
quit
.endc
.end
