# Test bench for d-flip-flop simulation

.TEMP 25
.OPTION

.param pvcc = 1.05V
.param period1 = 0.25n
.param pw1 = 0.085n
.param tr = 30p
.param tf = 30p
.param period2 = 3.141592654n
.param pw2 = 1.510796n



.lib '/afs/asu.edu/users/a/l/r/alrosen2/425_lab/iPDK/hspice/saed32nm.lib' TT
.include './d_flip_flop.sp'

vvdd vdd! gnd! DC = 1.05
vgnd gnd! gnd! DC = 0

xd_flip_flop Clk D Q d_flip_flop

V1 Clk GND! PULSE (1.05 0 0 tr tf pw1 period1)
V2 D GND! PULSE (0 1.05 0 tr tf pw2 period2)

.measure TRAN T_RISE_Cout TRIG v(Q) VAL = '0.1*pvcc' RISE = 3 TARG v(Q) VAL = '0.9*pvcc' RISE = 3
.measure TRAN t_fall_Cout  TRIG v(Q) VAL = '0.9*pvcc' FALL = 3 TARG v(Q) VAL = '0.1*pvcc' FALL = 3
.measure TRAN tphl_Cout  TRIG v(Clk) VAL = '0.5*pvcc' RISE = 3 TARG v(Q) VAL = '0.5*pvcc' FALL = 3
.measure TRAN tplh_Cout  TRIG v(Clk) VAL = '0.5*pvcc' FALL = 3 TARG v(Q) VAL = '0.5*pvcc' RISE = 3

.tran 2p 8n Start = 0.0

.probe i(*)
.probe v(*)
.option post

.end
