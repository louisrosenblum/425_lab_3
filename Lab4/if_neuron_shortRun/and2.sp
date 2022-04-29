************************************************************************
* auCdl Netlist:
* 
* Library Name:  Lab4
* Top Cell Name: and2
* View Name:     schematic
* Netlisted on:  Apr 18 14:53:58 2022
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

*.GLOBAL gnd!

*.PIN gnd!

************************************************************************
* Library Name: Lab4
* Cell Name:    and2
* View Name:    schematic
************************************************************************

.SUBCKT and2 A B F
*.PININFO A:I B:I F:O
MM13 F net012 gnd! gnd! n105 m=1 w=1.68u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM10 net012 net08 gnd! gnd! n105 m=1 w=1.68u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM5 net08 net7 gnd! gnd! n105 m=1 w=1.68u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM6 net7 A net013 gnd! n105 m=1 w=3.36u l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM7 net013 B gnd! gnd! n105 m=1 w=3.36u l=30n ad=10.5f as=10.5f pd=310n ps=310n
MM12 F net012 net017 net017 p105 m=1 w=2.016u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM11 net012 net08 net027 net027 p105 m=1 w=2.016u l=30n ad=10.5f as=10.5f 
+ pd=310n ps=310n
MM4 net08 net7 net12 net12 p105 m=1 w=2.016u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM9 net7 B net05 net015 p105 m=1 w=1.008u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
MM8 net7 A net05 net016 p105 m=1 w=1.008u l=30n ad=10.5f as=10.5f pd=310n 
+ ps=310n
.ENDS

