# Test bench for four bit adder simulation

.TEMP 25
.OPTION

.param pvcc = 1.05V
.param period1 = 2n
.param pw1 = 0.94n
.param tr = 30p
.param tf = 30p
.param period2 = 3.14n
.param pw2 = 1.57n
.param period3 = 4.68n
.param pw3 = 2.34n
.param period4 = 5.75n
.param pw4 = 2.875n

.param period5 = 1.8n
.param pw5 = 0.9n
.param period6 = 3.5n
.param pw6 = 1.75n
.param period7 = 4n
.param pw7 = 2n
.param period8 = 6.5n
.param pw8 = 3.25n

.lib '/afs/asu.edu/users/a/l/r/alrosen2/425_lab/iPDK/hspice/saed32nm.lib' TT
.include './four_bit_adder.sp'

vvdd vdd! gnd! DC = 1.05
vgnd gnd! gnd! DC = 0

xfour_bit_adder A0 A1 A2 A3 B0 B1 B2 B3 Cout Sum0 Sum1 Sum2 Sum3 four_bit_adder

V0 A0 GND! DC = 1.05
V1 A1 GND! DC = 1.05
V2 A2 GND! DC = 1.05
V3 A3 GND! DC = 1.05

V4 B0 GND! DC = 1.05
V5 B1 GND! DC = 1.05
V6 B2 GND! DC = 1.05
V7 B3 GND! DC = 1.05

.measure TRAN T_RISE_Cout TRIG v(A0) VAL = '0.1*pvcc' RISE = 3 TARG v(Cout) VAL = '0.9*pvcc' RISE = 3
.measure TRAN t_fall_Cout  TRIG v(A0) VAL = '0.9*pvcc' FALL = 3 TARG v(Cout) VAL = '0.1*pvcc' FALL = 3
.measure TRAN tphl_Cout  TRIG v(A0) VAL = '0.5*pvcc' RISE = 3 TARG v(Cout) VAL = '0.5*pvcc' FALL = 3
.measure TRAN tplh_Cout  TRIG v(A0) VAL = '0.5*pvcc' FALL = 3 TARG v(Cout) VAL = '0.5*pvcc' RISE = 3


.tran 2p 32n Start = 0.0

.probe i(*)
.probe v(*)
.option post

.end
