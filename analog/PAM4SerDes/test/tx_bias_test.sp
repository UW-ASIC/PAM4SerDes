* tx_bias testbench  (openvaf tx_bias.va -> tx_bias.osdi, loaded by ngspice)
* Spec source: UWASIC wiki "Mathematical Derivation" -> PAM4 Driver
*   I_total = 16 mA, MSB:LSB = 2:1, taps -0.05/+0.80/-0.15
*   swing 0.8 Vppd (0.7-0.9 allowed) into 50 ohm || 50 ohm, termination +/-5%
*   output-stage supply 1.25 V
.control
pre_osdi tx_bias.osdi
.endc

.model txb       tx_bias
.model txb_hi    tx_bias rterm_act=52.5
.model txb_lo    tx_bias rterm_act=47.5
.model txb_olhi  tx_bias rterm_act=52.5 swing_loop=0
.model txb_v07   tx_bias vppd=0.7
.model txb_v09   tx_bias vppd=0.9

* pin order: vdd vss en vref  msb_pre msb_main msb_post  lsb_pre lsb_main lsb_post  pdrv pgood
* N1: nominal, every output measured separately
N1 vdd 0 en vref  mpre mmain mpost  lpre lmain lpost  pdrv pgood txb

* N2..N6: corner instances, all six driver tails summed through one ammeter
N2 vdd 0 en vref  s2 s2 s2 s2 s2 s2  tail pg2 txb_hi
N3 vdd 0 en vref  s3 s3 s3 s3 s3 s3  tail pg3 txb_lo
N4 vdd 0 en vref  s4 s4 s4 s4 s4 s4  tail pg4 txb_olhi
N5 vdd 0 en vref  s5 s5 s5 s5 s5 s5  tail pg5 txb_v07
N6 vdd 0 en vref  s6 s6 s6 s6 s6 s6  tail pg6 txb_v09

Vdd  vdd  0 1.25
Vref vref 0 0.6
Ven  en   0 dc 1.25 pulse(0 1.25 2n 50p 50p 100n 200n)

* each tail output held at 0.6 V (driver common-source node) through an ammeter
Vt  tail 0 0.6
Vm1 tail mpre  0
Vm2 tail mmain 0
Vm3 tail mpost 0
Vl1 tail lpre  0
Vl2 tail lmain 0
Vl3 tail lpost 0
Vpd tail pdrv  0
Vs2 tail s2 0
Vs3 tail s3 0
Vs4 tail s4 0
Vs5 tail s5 0
Vs6 tail s6 0
Rpg pgood 0 1meg

.control
set noaskquit
let fails = 0

* ---------- 1) enable transient ----------
tran 10p 20n
meas tran i_off find i(Vm2) at=1n
meas tran i_on  find i(Vm2) at=15n
meas tran pg_on find v(pgood) at=15n
meas tran pg_off find v(pgood) at=1n
if (i_off > 10e-6) | (abs(i_on - 8.533e-3) > 0.01*8.533e-3) | (pg_on < 1.2) | (pg_off > 0.05)
  echo "FAIL enable"
  let fails = fails + 1
else
  echo "PASS enable: off -> on, pgood asserts"
end

* ---------- 2) nominal DC currents ----------
op
let imp  = i(Vm1)*1e3
let imm  = i(Vm2)*1e3
let imq  = i(Vm3)*1e3
let ilp  = i(Vl1)*1e3
let ilm  = i(Vl2)*1e3
let ilq  = i(Vl3)*1e3
let ipd  = i(Vpd)*1e3
let imsb = imp + imm + imq
let ilsb = ilp + ilm + ilq
let itot = imsb + ilsb
let ratio = imsb / ilsb
* Vppd = 2 * I_total * (R/2) = I_total * 50
let vppd  = itot * 1e-3 * 50
echo "---- nominal (mA); spec MSB 0.533/8.533/1.600  LSB 0.267/4.267/0.800  total 16 ----"
print imp imm imq ilp ilm ilq ipd
print imsb ilsb itot ratio vppd
let e_tot = abs(itot - 16) / 16
let e_rat = abs(ratio - 2) / 2
let e_mm  = abs(imm - 8.5333) / 8.5333
let e_lm  = abs(ilm - 4.2667) / 4.2667
if (e_tot > 0.01) | (e_rat > 0.01) | (e_mm > 0.01) | (e_lm > 0.01)
  echo "FAIL nominal currents"
  let fails = fails + 1
else
  echo "PASS nominal currents within 1% (16 mA, 2:1, taps)"
end

* ---------- 3) termination +/-5%: replica loop holds swing, open loop does not ----------
let v_hi   = i(Vs2) * 52.5
let v_lo   = i(Vs3) * 47.5
let v_olhi = i(Vs4) * 52.5
echo "---- swing (Vppd) at Rterm 52.5 / 47.5 (replica)  and 52.5 (open loop) ----"
print v_hi v_lo v_olhi
if (abs(v_hi - 0.8) > 0.008) | (abs(v_lo - 0.8) > 0.008)
  echo "FAIL replica swing control"
  let fails = fails + 1
else
  echo "PASS replica loop keeps 0.8 Vppd at +/-5% termination"
end

* ---------- 4) programmable swing 0.7 / 0.9 Vppd ----------
let v07 = i(Vs5) * 50
let v09 = i(Vs6) * 50
print v07 v09
if (abs(v07 - 0.7) > 0.007) | (abs(v09 - 0.9) > 0.009)
  echo "FAIL swing range"
  let fails = fails + 1
else
  echo "PASS swing settable over 0.7-0.9 Vppd"
end

* ---------- 5) supply: 1.25 V +/-5% must not move the current by > 0.5% ----------
dc Vdd 1.1875 1.3125 0.0625
let dev = (i(Vm2) - 8.5333e-3) / 8.5333e-3
print i(Vm2) dev
if (abs(dev[0]) > 0.005) | (abs(dev[2]) > 0.005)
  echo "FAIL supply sensitivity"
  let fails = fails + 1
else
  echo "PASS supply +/-5% -> current within 0.5%"
end

* ---------- 6) reference sweep: currents scale with vref ----------
dc Vref 0.5 0.7 0.05
print i(Vm2) i(Vl2)

echo "==== failures: $&fails ===="
.endc
.end
