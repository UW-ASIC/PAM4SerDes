* Transmitter PLL: refclk_buf + tx_pll, 437.5 MHz x 32 = 14 GHz, jitter on (defaults).
* Run with: make -C analog/PAM4SerDes/build/sim link DECK=tb_pll
*
* PASS: the lock detector asserts (it needs 256 reference cycles in a row inside its
* window, 585 ns) and the control voltage sits within 20 mV of the VCO's centre, 0.35 V.
*
* The same ngspice notes as tb_datapath.sp apply: version 45 or newer, the default
* solver, and the fourth `tran` argument.
.include "../build/sim/out/pam4_serdes.cir"

Vdd vdd 0 0.7
Vtp rtp 0 sin(0.35 0.1 437.5meg)
Vtn rtn 0 sin(0.35 -0.1 437.5meg)

* refclk_buf pins: inp inn out vdd vss.  tx_pll pins: ckref ck ckfb lock vctl vdd vss
.model rb refclk_buf
.model pll tx_pll
Nrb  rtp rtn ckref vdd 0 rb
Npll ckref ck ckfb lock vctl vdd 0 pll

.save v(lock) v(vctl)
.control
set noaskquit
tran 2p 700n 0 10u
let vend = v(vctl)[length(v(vctl)) - 1]
let lend = v(lock)[length(v(lock)) - 1]
meas tran tlock when v(lock)=0.35 rise=1
let tlock_ns = tlock * 1e9
if (lend > 0.6) & (abs(vend - 0.35) < 20m)
  echo "PASS tb_pll: locked after $&tlock_ns ns, control voltage $&vend V"
  echo "SPEC Transmitter PLL: lock detector asserts after | $&tlock_ns ns"
  echo "SPEC Transmitter PLL: control voltage when locked | $&vend V"
else
  echo "FAIL tb_pll: lock $&lend V, control voltage $&vend V"
end
quit
.endc
.end
