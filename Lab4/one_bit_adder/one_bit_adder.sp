************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: one_bit_adder
* View Name:     schematic
* Netlisted on:  Apr  2 11:24:31 2022
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
* Cell Name:    one_bit_adder
* View Name:    schematic
************************************************************************

.SUBCKT one_bit_adder A B Cin Cout Sum
*.PININFO A:I B:I Cin:I Cout:O Sum:O
xMM28 net054 Sum vdd! vdd! p105 m=1 w=600n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM26 Sum net038 vdd! vdd! p105 m=1 w=292.2n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM22 net038 Cin net060 vdd! p105 m=1 w=284.58n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM21 net060 B net061 vdd! p105 m=1 w=284.58n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM20 net061 A vdd! vdd! p105 m=1 w=284.58n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM15 net038 net15 net19 vdd! p105 m=1 w=184.8n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM14 net19 Cin vdd! vdd! p105 m=1 w=61.6n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM13 net19 B vdd! vdd! p105 m=1 w=61.6n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM12 net19 A vdd! vdd! p105 m=1 w=61.6n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM10 Cout net15 vdd! vdd! p105 m=1 w=120n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM5 net15 Cin net11 vdd! p105 m=1 w=120n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM4 net15 A net33 vdd! p105 m=1 w=120n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM3 net33 B vdd! vdd! p105 m=1 w=120n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM2 net11 B vdd! vdd! p105 m=1 w=60n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM0 net11 A vdd! vdd! p105 m=1 w=60n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM29 net054 Sum gnd! gnd! n105 m=1 w=300n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM27 Sum net038 gnd! gnd! n105 m=1 w=146.1n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM25 net058 B gnd! gnd! n105 m=1 w=142.29n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM24 net059 A net058 gnd! n105 m=1 w=142.29n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM23 net038 Cin net059 gnd! n105 m=1 w=142.29n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM18 net033 B gnd! gnd! n105 m=1 w=30.8n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM16 net038 net15 net033 gnd! n105 m=1 w=92.4n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM17 net033 A gnd! gnd! n105 m=1 w=30.8n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM19 net033 Cin gnd! gnd! n105 m=1 w=30.8n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM11 Cout net15 gnd! gnd! n105 m=1 w=60n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM9 net23 B gnd! gnd! n105 m=1 w=30n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM8 net23 A gnd! gnd! n105 m=1 w=30n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM7 net15 Cin net23 gnd! n105 m=1 w=60n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM6 net32 B gnd! gnd! n105 m=1 w=60n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM1 net15 A net32 gnd! n105 m=1 w=60n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

