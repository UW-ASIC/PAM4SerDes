* Clock recovery: the receiver's CDR closes the loop on transmitted PAM4 data.
* tx_top (ideal 14 GHz clock) -> flat test channel -> rx_top, clocked by rx_cdr.
* The frequency acquisition is skipped (force_lock high): both sides start at 14 GHz
* and the loop only has to find the sampling phase.
* Run with: make -C analog/PAM4SerDes/build/sim link DECK=tb_cdr
*
* PASS: once the loop has settled, the receiver's words are the transmitted PRBS7 with
* 0 errors.
*
* tq = 53.571p is the setting pam4_serdes.va uses: the phase detector's quadrature clock
* a quarter period early. With rx_cdr's default (17.857p, a quarter period late) this
* deck FAILS with about 25 bit errors per word: the loop then settles with the clock
* edges on the data transitions. Remove tq below to see it. CHANGELOGS.md, "Clock
* recovery", has the measurements.
*
* The same three ngspice notes as tb_datapath.sp apply: version 45 or newer, the default
* solver (no `.option klu`), and the fourth `tran` argument.
.include "../build/sim/out/pam4_serdes.cir"

Vdd  vdd  0 0.7
Vddo vddo 0 1.25
Vref vref 0 0.6
Ven  en   0 1.25
Vfl  fl   0 0.7
Vrst rst  0 pulse(0.7 0 1n 20p 20p 1 2)
Vckt cktx 0 pulse(0 0.7 0 5p 5p 30.714p 71.4286p)
* 437.5 MHz reference for the (disabled) frequency loop
Vckref ckref 0 pulse(0 0.7 0 30p 30p 1.1128n 2.2857n)

Xtx cktx rst en vref txp txn pgood vdd vddo 0 tx_top rj_scale=0 w_pre=0 w_main=1 w_post=0

Ech chd 0 txp txn 0.61
Ep  sp cm chd 0 1
En  sn cm chd 0 -1
Vcm cm 0 0.55
Rsp sp rxp 50
Rsn sn rxn 50
Vtt   vtt   0 0.55
Vctrl vctrl 0 0.35

* rx_cdr is one device. Pins: ckref din_p din_n clk14_p clk14_n force_lock ck ckfb lock vctl vdd vss
.model cdr rx_cdr rj_div=0 tq=53.571p
Ncdr ckref afe_p afe_n c14p c14n fl ck_rx ckfb lock vctl vdd 0 cdr

Xrx rxp rxn vtt vctrl ck_rx rst afe_p afe_n c14p c14n
+ rxm0 rxm1 rxm2 rxm3 rxm4 rxm5 rxm6 rxm7 rxm8 rxm9 rxm10 rxm11 rxm12 rxm13 rxm14 rxm15 rxm16 rxm17 rxm18 rxm19 rxm20 rxm21 rxm22 rxm23 rxm24 rxm25 rxm26 rxm27 rxm28 rxm29 rxm30 rxm31
+ rxl0 rxl1 rxl2 rxl3 rxl4 rxl5 rxl6 rxl7 rxl8 rxl9 rxl10 rxl11 rxl12 rxl13 rxl14 rxl15 rxl16 rxl17 rxl18 rxl19 rxl20 rxl21 rxl22 rxl23 rxl24 rxl25 rxl26 rxl27 rxl28 rxl29 rxl30 rxl31
+ wclk vdd 0 rx_top rj_scale=0 alpha=0

* count errors only once the loop has settled
.model chk prbs_chk tstart=50n
Nchk wclk
+ rxm0 rxm1 rxm2 rxm3 rxm4 rxm5 rxm6 rxm7 rxm8 rxm9 rxm10 rxm11 rxm12 rxm13 rxm14 rxm15 rxm16 rxm17 rxm18 rxm19 rxm20 rxm21 rxm22 rxm23 rxm24 rxm25 rxm26 rxm27 rxm28 rxm29 rxm30 rxm31
+ rxl0 rxl1 rxl2 rxl3 rxl4 rxl5 rxl6 rxl7 rxl8 rxl9 rxl10 rxl11 rxl12 rxl13 rxl14 rxl15 rxl16 rxl17 rxl18 rxl19 rxl20 rxl21 rxl22 rxl23 rxl24 rxl25 rxl26 rxl27 rxl28 rxl29 rxl30 rxl31
+ err words chk

.save v(err) v(words) v(vctl) v(lock) v(wclk)
.control
set noaskquit
tran 1p 90n 0 10u
let nerr = v(err)[length(v(err)) - 1]
let nwords = v(words)[length(v(words)) - 1]
let vend = v(vctl)[length(v(vctl)) - 1]
echo "vctl at the end: $&vend V"
if (nerr < 0.5) & (nwords > 9.5)
  echo "PASS tb_cdr: $&nerr errors in $&nwords words of 64 bits"
  echo "SPEC Bit errors with the receiver clock recovered from the data | $&nerr in $&nwords words of 64 bits"
  echo "SPEC Clock recovery control voltage, tracking | $&vend V"
else
  echo "FAIL tb_cdr: $&nerr errors in $&nwords words of 64 bits"
end
quit
.endc
.end
