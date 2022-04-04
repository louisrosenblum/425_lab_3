************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: one_bit_adder_Leg4
* View Name:     schematic
* Netlisted on:  Apr  3 22:07:11 2022
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
* Cell Name:    one_bit_adder_Leg4
* View Name:    schematic
************************************************************************

.SUBCKT one_bit_adder_Leg4 A B Cin Cout Sum
*.PININFO A:I B:I Cin:I Cout:O Sum:O
MM26 Sum net017 vdd! vdd! p105 m=1 w=1.215u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM22 net017 Cin net060 vdd! p105 m=1 w=1.174u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM21 net060 A net061 vdd! p105 m=1 w=1.174u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM20 net061 B vdd! vdd! p105 m=1 w=1.174u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM15 net017 net15 net19 vdd! p105 m=1 w=784n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM14 net19 Cin vdd! vdd! p105 m=1 w=522n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM13 net19 B vdd! vdd! p105 m=1 w=522n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM12 net19 A vdd! vdd! p105 m=1 w=522n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM10 Cout net15 vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM5 net15 Cin net11 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM4 net15 A net33 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM3 net33 B vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM2 net11 B vdd! vdd! p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM0 net11 A vdd! vdd! p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM27 Sum net017 gnd! gnd! n105 m=1 w=1.014u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM25 net058 B gnd! gnd! n105 m=1 w=978n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM24 net059 A net058 gnd! n105 m=1 w=978n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM23 net017 Cin net059 gnd! n105 m=1 w=978n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM18 net033 B gnd! gnd! n105 m=1 w=218n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM16 net017 net15 net033 gnd! n105 m=1 w=654n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM17 net033 A gnd! gnd! n105 m=1 w=218n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM19 net033 Cin gnd! gnd! n105 m=1 w=218n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM11 Cout net15 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM9 net23 B gnd! gnd! n105 m=1 w=210n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM8 net23 A gnd! gnd! n105 m=1 w=210n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM7 net15 Cin net23 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM6 net32 B gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM1 net15 A net32 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

