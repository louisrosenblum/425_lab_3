# Test bench for one bit adder simulation

.TEMP 25
.OPTION

.param pvcc = 1.05V
.param period1 = 4n
.param pw1 = 1.94n
.param tr = 30p
.param tf = 30p
.param period2 = 1m
.param pw2 = 0.5m
.param period3 = 1m
.param pw3 = 0.5m


.lib '/afs/asu.edu/users/a/l/r/alrosen2/425_lab/iPDK/hspice/saed32nm.lib' TT
.include './one_bit_adder.sp'

vvdd vdd! gnd! DC = 1.05
vgnd gnd! gnd! DC = 0

xone_bit_adder A B Cin Cout Sum one_bit_adder

V1 B GND! PULSE (0 1.05 0 tr tf pw1 period1)
V2 A GND! PULSE (0 1.05 0 tr tf pw2 period2)
V3 Cin GND! PULSE (1.05 0 0 tr tf pw3 period3)

.measure TRAN T_RISE_Cout TRIG v(Cout) VAL = '0.1*pvcc' RISE = 3 TARG v(Cout) VAL = '0.9*pvcc' RISE = 3
.measure TRAN t_fall_Cout  TRIG v(Cout) VAL = '0.9*pvcc' FALL = 3 TARG v(Cout) VAL = '0.1*pvcc' FALL = 3
.measure TRAN tphl_Cout  TRIG v(A) VAL = '0.5*pvcc' RISE = 3 TARG v(Cout) VAL = '0.5*pvcc' FALL = 3
.measure TRAN tplh_Cout  TRIG v(A) VAL = '0.5*pvcc' FALL = 3 TARG v(Cout) VAL = '0.5*pvcc' RISE = 3

.measure TRAN T_RISE_Sum TRIG v(Sum) VAL = '0.1*pvcc' RISE = 3 TARG v(Sum) VAL = '0.9*pvcc' RISE = 3
.measure TRAN t_fall_Sum TRIG v(Sum) VAL = '0.9*pvcc' FALL = 3 TARG v(Sum) VAL = '0.1*pvcc' FALL = 3
.measure TRAN tphl_Sum TRIG v(A) VAL = '0.5*pvcc' RISE = 3 TARG v(Sum) VAL = '0.5*pvcc' FALL = 3
.measure TRAN tplh_Sum TRIG v(A) VAL = '0.5*pvcc' FALL = 3 TARG v(Sum) VAL = '0.5*pvcc' RISE = 3

.tran 2p 12n Start = 0.0

.probe i(*)
.probe v(*)
.option post

.end
