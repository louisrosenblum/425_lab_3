************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: if_neuron
* View Name:     schematic
* Netlisted on:  Apr 15 14:29:27 2022
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

************************************************************************
* Library Name: Lab4
* Cell Name:    d_flip_flop
* View Name:    schematic
************************************************************************

.SUBCKT d_flip_flop Clk D Q
*.PININFO Clk:I D:I Q:O
xMM15 net05 Clk gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
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

************************************************************************
* Library Name: Lab4
* Cell Name:    and2
* View Name:    schematic
************************************************************************

.SUBCKT and2 A B F
*.PININFO A:I B:I F:O
xMM5 F net7 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM3 net17 B gnd! gnd! n105 m=1 w=840n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM0 net7 A net17 gnd! n105 m=1 w=840n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM4 F net7 net12 net12 p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM2 net7 B net8 net18 p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM1 net7 A net8 net19 p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

************************************************************************
* Library Name: Lab4
* Cell Name:    or3
* View Name:    schematic
************************************************************************

.SUBCKT or3 A B C F
*.PININFO A:I B:I C:I F:O
xMM6 F net10 net15 net15 p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM2 net10 C net18 net23 p105 m=1 w=1.512u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM1 net18 B net19 net22 p105 m=1 w=1.512u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM0 net19 A net20 net21 p105 m=1 w=1.512u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
xMM7 F net10 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM5 net10 C gnd! gnd! n105 m=1 w=140n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM4 net10 B gnd! gnd! n105 m=1 w=140n l=30n ad=10.5f as=10.5f pd=310n ps=310n
xMM3 net10 A gnd! gnd! n105 m=1 w=140n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

************************************************************************
* Library Name: Lab4
* Cell Name:    if_neuron
* View Name:    schematic
************************************************************************

.SUBCKT if_neuron CLK F W0 W1 W2 W3 X0<0> X0<1> X0<2> X0<3> X1<0> X1<1> X1<2> 
+ X1<3> X2<0> X2<1> X2<2> X2<3> X3<0> X3<1> X3<2> X3<3>
*.PININFO CLK:I W0:I W1:I W2:I W3:I X0<0>:I X0<1>:I X0<2>:I X0<3>:I X1<0>:I 
*.PININFO X1<1>:I X1<2>:I X1<3>:I X2<0>:I X2<1>:I X2<2>:I X2<3>:I X3<0>:I 
*.PININFO X3<1>:I X3<2>:I X3<3>:I F:O
XI44 net081 net080 net079 net078 net076 net075 net074 net073 net096 net085 
+ net086 net087 net088 / four_bit_adder
XI33 net46 net45 net38 net068 net069 net070 net071 net072 net061 net062 net063 
+ net064 net065 / four_bit_adder
XI0 net17 net18 net70 net69 net62 net85 net54 net53 net77 net78 net79 net80 
+ net81 / four_bit_adder
XI46 net028 net067 F / d_flip_flop
XI43 net028 net061 net084 / d_flip_flop
XI42 net028 net065 net073 / d_flip_flop
XI41 net028 net064 net074 / d_flip_flop
XI40 net028 net063 net075 / d_flip_flop
XI39 net028 net062 net076 / d_flip_flop
XI38 net028 net77 net077 / d_flip_flop
XI37 net028 net81 net078 / d_flip_flop
XI36 net028 net80 net079 / d_flip_flop
XI35 net028 net79 net080 / d_flip_flop
XI34 net028 net78 net081 / d_flip_flop
XI32 CLK X3<3> net20 / d_flip_flop
XI29 CLK X3<2> net25 / d_flip_flop
XI28 CLK X3<1> net27 / d_flip_flop
XI25 CLK X3<0> net32 / d_flip_flop
XI24 CLK X2<3> net35 / d_flip_flop
XI21 CLK X2<2> net40 / d_flip_flop
XI20 CLK X2<1> net43 / d_flip_flop
XI17 CLK X2<0> net48 / d_flip_flop
XI16 CLK X1<3> net51 / d_flip_flop
XI13 CLK X1<2> net56 / d_flip_flop
XI12 CLK X1<1> net59 / d_flip_flop
XI9 CLK X1<0> net64 / d_flip_flop
XI8 CLK X0<3> net67 / d_flip_flop
XI5 CLK X0<2> net72 / d_flip_flop
XI3 CLK X0<1> net75 / d_flip_flop
XI1 CLK X0<0> net76 / d_flip_flop
XI31 net20 W3 net072 / and2
XI30 net25 W3 net071 / and2
XI27 net27 W3 net070 / and2
XI26 net32 W3 net069 / and2
XI23 net35 W2 net068 / and2
XI22 net40 W2 net38 / and2
XI19 net43 W2 net45 / and2
XI18 net48 W2 net46 / and2
XI15 net51 W1 net53 / and2
XI14 net56 W1 net54 / and2
XI11 net59 W1 net85 / and2
XI10 net64 W1 net62 / and2
XI7 net67 W0 net69 / and2
XI6 net72 W0 net70 / and2
XI4 net75 W0 net18 / and2
XI2 net76 W0 net17 / and2
XI45 net077 net096 net084 net067 / or3
.ENDS

