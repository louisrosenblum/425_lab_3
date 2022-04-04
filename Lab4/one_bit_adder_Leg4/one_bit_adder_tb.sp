# Test bench for one bit adder simulation

.TEMP 25
.OPTION

.param pvcc = 1.05V
.param period1 = 2n
.param pw1 = 0.94n
.param tr = 30p
.param tf = 30p
.param period2 = 4n
.param pw2 = 1.94n
.param period3 = 8n
.param pw3 = 3.94n


.lib '/afs/asu.edu/users/a/l/r/alrosen2/425_lab/iPDK/hspice/saed32nm.lib' TT
.include './one_bit_adder.sp'

vvdd vdd! gnd! DC = 1.05
vgnd gnd! gnd! DC = 0

xone_bit_adder A B Cin Cout Sum one_bit_adder

V1 A GND! PULSE (1.05 0 0 tr tf pw3 period3)
V2 B GND! PULSE (1.05 0 0 tr tf pw2 period2)
V3 Cin GND! PULSE (1.05 0 0 tr tf pw1 period1)

.measure TRAN T_RISE_Cout TRIG v(Cout) VAL = '0.1*pvcc' RISE = 3 TARG v(Cout) VAL = '0.9*pvcc' RISE = 3
.measure TRAN t_fall_Cout  TRIG v(Cout) VAL = '0.9*pvcc' FALL = 3 TARG v(Cout) VAL = '0.1*pvcc' FALL = 3
.measure TRAN tphl_Cout  TRIG v(A) VAL = '0.5*pvcc' RISE = 3 TARG v(Cout) VAL = '0.5*pvcc' FALL = 3
.measure TRAN tplh_Cout  TRIG v(A) VAL = '0.5*pvcc' FALL = 3 TARG v(Cout) VAL = '0.5*pvcc' RISE = 3

.measure TRAN T_RISE_Sum TRIG v(Sum) VAL = '0.1*pvcc' RISE = 3 TARG v(Sum) VAL = '0.9*pvcc' RISE = 3
.measure TRAN t_fall_Sum TRIG v(Sum) VAL = '0.9*pvcc' FALL = 3 TARG v(Sum) VAL = '0.1*pvcc' FALL = 3
.measure TRAN tphl_Sum TRIG v(A) VAL = '0.5*pvcc' RISE = 3 TARG v(Sum) VAL = '0.5*pvcc' FALL = 3
.measure TRAN tplh_Sum TRIG v(A) VAL = '0.5*pvcc' FALL = 3 TARG v(Sum) VAL = '0.5*pvcc' RISE = 3

.tran 2p 16n Start = 0.0

.probe i(*)
.probe v(*)
.option post

.end
