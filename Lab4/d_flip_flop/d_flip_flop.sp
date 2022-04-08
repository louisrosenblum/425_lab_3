************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: d_flip_flop
* View Name:     schematic
* Netlisted on:  Apr  7 16:59:54 2022
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
* Cell Name:    d_flip_flop
* View Name:    schematic
************************************************************************

.SUBCKT d_flip_flop Clk D Q
*.PININFO Clk:I D:I Q:O
xMM15 net05 Clk gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM13 net20 Q gnd! gnd! n105 m=1 w=2.1u l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM11 net12 net05 Q gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM10 Q net13 gnd! gnd! n105 m=1 w=1.40435u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM8 net13 net12 gnd! gnd! n105 m=1 w=939.12n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM4 net11 net8 gnd! gnd! n105 m=1 w=627.9n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM3 D net05 net7 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM0 net8 net7 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM14 net05 Clk vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM12 net20 Q vdd! vdd! p105 m=1 w=2.52u l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM9 Q net13 vdd! vdd! p105 m=1 w=1.67522u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM7 net13 net12 vdd! vdd! p105 m=1 w=1.12694u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM6 net12 net05 net11 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM5 net11 net05 net7 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM2 net11 net8 vdd! vdd! p105 m=1 w=753.48n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM1 net8 net7 vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

