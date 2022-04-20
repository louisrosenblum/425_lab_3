************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: if_neuron
* View Name:     schematic
* Netlisted on:  Apr 19 17:08:26 2022
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

*.GLOBAL vdd!
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
MM26 Sum net038 vdd! vdd! p105 m=1 w=1.21464u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM22 net038 Cin net060 vdd! p105 m=1 w=1.17452u l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
MM21 net060 B net061 vdd! p105 m=1 w=1.17452u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM20 net061 A vdd! vdd! p105 m=1 w=1.17452u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM15 net038 net15 net19 vdd! p105 m=1 w=783.01n l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
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
MM27 Sum net038 gnd! gnd! n105 m=1 w=1.0122u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM25 net058 B gnd! gnd! n105 m=1 w=978.768n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM24 net059 A net058 gnd! n105 m=1 w=978.768n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM23 net038 Cin net059 gnd! n105 m=1 w=978.768n l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
MM18 net033 B gnd! gnd! n105 m=1 w=217.5n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM16 net038 net15 net033 gnd! n105 m=1 w=652.51n l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
MM17 net033 A gnd! gnd! n105 m=1 w=217.5n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM19 net033 Cin gnd! gnd! n105 m=1 w=217.5n l=30n ad=10.5f as=10.5f pd=310n 
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
MM15 net05 Clk gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM11 net12 net05 Q gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM10 Q net13 gnd! gnd! n105 m=1 w=1.40435u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM8 net13 net12 gnd! gnd! n105 m=1 w=939.12n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM4 net11 net8 gnd! gnd! n105 m=1 w=627.9n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM3 D net05 net7 gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM0 net8 net7 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM14 net05 Clk vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM9 Q net13 vdd! vdd! p105 m=1 w=1.67522u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM7 net13 net12 vdd! vdd! p105 m=1 w=1.12694u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM6 net12 net05 net11 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM5 net11 net05 net7 vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM2 net11 net8 vdd! vdd! p105 m=1 w=753.48n l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM1 net8 net7 vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

************************************************************************
* Library Name: Lab4
* Cell Name:    and2
* View Name:    schematic
************************************************************************

.SUBCKT and2 A B F
*.PININFO A:I B:I F:O
MM5 F net7 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM6 net7 A net013 gnd! n105 m=1 w=840n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM7 net013 B gnd! gnd! n105 m=1 w=840n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM4 F net7 vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM9 net7 B vdd! net015 p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM8 net7 A vdd! net016 p105 m=1 w=252n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

************************************************************************
* Library Name: Lab4
* Cell Name:    or3
* View Name:    schematic
************************************************************************

.SUBCKT or3 A B C F
*.PININFO A:I B:I C:I F:O
MM12 net016 B net017 vdd! p105 m=1 w=1.512u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM11 net017 A vdd! vdd! p105 m=1 w=1.512u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM13 net10 C net016 vdd! p105 m=1 w=1.512u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM6 F net10 vdd! vdd! p105 m=1 w=504n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM8 net10 A gnd! gnd! n105 m=1 w=140n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM7 F net10 gnd! gnd! n105 m=1 w=420n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM10 net10 C gnd! gnd! n105 m=1 w=140n l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM9 net10 B gnd! gnd! n105 m=1 w=140n l=30n ad=10.5f as=10.5f pd=310n ps=310n
.ENDS

************************************************************************
* Library Name: Lab4
* Cell Name:    if_neuron
* View Name:    schematic
************************************************************************

.SUBCKT if_neuron CLK Cout1 Cout2 Cout3 F W0 W1 W2 W3 X0<0> X0<1> X0<2> X0<3> 
+ X1<0> X1<1> X1<2> X1<3> X2<0> X2<1> X2<2> X2<3> X3<0> X3<1> X3<2> X3<3>
*.PININFO CLK:I W0:I W1:I W2:I W3:I X0<0>:I X0<1>:I X0<2>:I X0<3>:I X1<0>:I 
*.PININFO X1<1>:I X1<2>:I X1<3>:I X2<0>:I X2<1>:I X2<2>:I X2<3>:I X3<0>:I 
*.PININFO X3<1>:I X3<2>:I X3<3>:I Cout1:O Cout2:O Cout3:O F:O
XI44 net069 net080 net079 net078 net076 net075 net074 net073 Cout3 net085 
+ net086 net087 net088 / four_bit_adder
XI33 net46 net45 net38 net049 net052 net070 net060 net0135 net061 net062 
+ net063 net064 net065 / four_bit_adder
XI0 net046 net041 net042 net043 net045 net048 net050 net0103 net058 net057 
+ net0102 net0101 net098 / four_bit_adder
XI46 CLK net067 F / d_flip_flop
XI43 CLK net061 Cout2 / d_flip_flop
XI42 CLK net065 net073 / d_flip_flop
XI41 CLK net064 net074 / d_flip_flop
XI40 CLK net063 net075 / d_flip_flop
XI39 CLK net062 net076 / d_flip_flop
XI38 CLK net058 Cout1 / d_flip_flop
XI37 CLK net098 net078 / d_flip_flop
XI36 CLK net0101 net079 / d_flip_flop
XI35 CLK net0102 net080 / d_flip_flop
XI34 CLK net057 net069 / d_flip_flop
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
XI1 CLK X0<0> net0108 / d_flip_flop
XI31 net20 W3 net0135 / and2
XI30 net25 W3 net060 / and2
XI27 net27 W3 net070 / and2
XI26 net32 W3 net052 / and2
XI23 net35 W2 net049 / and2
XI22 net40 W2 net38 / and2
XI19 net43 W2 net45 / and2
XI18 net48 W2 net46 / and2
XI15 net51 W1 net0103 / and2
XI14 net56 W1 net050 / and2
XI11 net59 W1 net048 / and2
XI10 net64 W1 net045 / and2
XI7 net67 W0 net043 / and2
XI6 net72 W0 net042 / and2
XI4 net75 W0 net041 / and2
XI2 net0108 W0 net046 / and2
XI47 Cout1 Cout3 Cout2 net067 / or3
.ENDS

