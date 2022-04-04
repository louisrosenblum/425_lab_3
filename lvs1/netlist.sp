************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: one_bit_adder_Leg1
* View Name:     schematic
* Netlisted on:  Apr  3 11:31:50 2022
************************************************************************

*.BIPOLAR
*.RESI = 2000 
*.RESVAL
*.CAPVAL
*.DIOPERI
*.DIOAREA
*.EQUATION
*.SCALE METER
*.MEGA
.PARAM

.GLOBAL gnd!
+        vdd!

*.PIN gnd!
*+    vdd!

************************************************************************
* Library Name: Lab4
* Cell Name:    one_bit_adder_Leg1
* View Name:    schematic
************************************************************************

.SUBCKT one_bit_adder_Leg1 A B Cin CoutNot
*.PININFO A:I B:I Cin:I CoutNot:O
MM5 CoutNot Cin net11 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM4 CoutNot A net33 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM3 net33 B vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM2 net11 B vdd! vdd! p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM0 net11 A vdd! vdd! p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM9 net23 B gnd! gnd! n105 m=1 w=210n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM8 net23 A gnd! gnd! n105 m=1 w=210n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM7 CoutNot Cin net23 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM6 net32 B gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM1 CoutNot A net32 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
.ENDS

