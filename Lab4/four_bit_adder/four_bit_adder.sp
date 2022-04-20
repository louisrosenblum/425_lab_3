************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: four_bit_adder
* View Name:     schematic
* Netlisted on:  Apr 16 14:23:20 2022
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

.GLOBAL vdd!
+        gnd!

*.PIN vdd!
*+    gnd!

************************************************************************
* Library Name: Lab4
* Cell Name:    one_bit_adder
* View Name:    schematic
************************************************************************

.SUBCKT one_bit_adder A B Cin Cout Sum
*.PININFO A:I B:I Cin:I Cout:O Sum:O
xMM26 Sum net038 vdd! vdd! p105 m=1 w=1.21464u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM22 net038 Cin net060 vdd! p105 m=1 w=1.17452u l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
xMM21 net060 B net061 vdd! p105 m=1 w=1.17452u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM20 net061 A vdd! vdd! p105 m=1 w=1.17452u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM15 net038 net15 net19 vdd! p105 m=1 w=783.01n l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
xMM14 net19 Cin vdd! vdd! p105 m=1 w=522n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM13 net19 B vdd! vdd! p105 m=1 w=522n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM12 net19 A vdd! vdd! p105 m=1 w=522n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM10 Cout net15 vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM5 net15 Cin net11 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM4 net15 A net33 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM3 net33 B vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM2 net11 B vdd! vdd! p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM0 net11 A vdd! vdd! p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM27 Sum net038 gnd! gnd! n105 m=1 w=1.0122u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM25 net058 B gnd! gnd! n105 m=1 w=978.768n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM24 net059 A net058 gnd! n105 m=1 w=978.768n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM23 net038 Cin net059 gnd! n105 m=1 w=978.768n l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
xMM18 net033 B gnd! gnd! n105 m=1 w=217.5n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM16 net038 net15 net033 gnd! n105 m=1 w=652.51n l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
xMM17 net033 A gnd! gnd! n105 m=1 w=217.5n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM19 net033 Cin gnd! gnd! n105 m=1 w=217.5n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM11 Cout net15 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM9 net23 B gnd! gnd! n105 m=1 w=210n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM8 net23 A gnd! gnd! n105 m=1 w=210n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM7 net15 Cin net23 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM6 net32 B gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM1 net15 A net32 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

************************************************************************
* Library Name: Lab4
* Cell Name:    four_bit_adder
* View Name:    schematic
************************************************************************

.SUBCKT four_bit_adder A0 A1 A2 A3 B0 B1 B2 B3 Cout Sum0 Sum1 Sum2 Sum3
*.PININFO A0:I A1:I A2:I A3:I B0:I B1:I B2:I B3:I Cout:O Sum0:O Sum1:O Sum2:O 
*.PININFO Sum3:O
XI3 A3 B3 net35 Cout Sum3 / one_bit_adder
XI2 A2 B2 net32 net35 Sum2 / one_bit_adder
XI1 A1 B1 net30 net32 Sum1 / one_bit_adder
XI0 A0 B0 gnd! net30 Sum0 / one_bit_adder
.ENDS

