
/****************************************************************************************
*****************************************************************************************
**                                                                                     **
**  The 32/28nm interoperable process design kit, including the information contained  **
**  therein  ("PDK") is unsupported Confidential Information of Synopsys, Inc.         **
**  ("Synopsys") provided to you as Documentation under the terms of the End User      **
**  Software License Agreement between you or your employer and Synopsys ("License     **
**  Agreement") and you agree not to distribute or disclose the PDK without the        **
**  prior written consent of Synopsys. The PDK IS NOT an item of Licensed Software     **
**  or Licensed Product under the License Agreement.  Synopsys and/or its licensors    **
**  own and shall retain all right, title and interest in and to the PDK and all       **
**  modifications thereto, including all intellectual property rights embodied         **
**  therein. All rights in and to any PDK modifications you make are hereby assigned   **
**  to Synopsys. If you do not agree with this notice, including the disclaimer        **
**  below, then you are not authorized to use the PDK.                                 **
**                                                                                     **
**  THIS PDK IS BEING DISTRIBUTED BY SYNOPSYS SOLELY ON AN "AS IS" BASIS, WITH NO      **
**  INTELLECUTAL PROPERTY INDEMNIFICATION AND NO SUPPORT. ANY EXPRESS OR IMPLIED       **
**  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF               **
**  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE HEREBY DISCLAIMED. IN     **
**  NO EVENT SHALL SYNOPSYS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,   **
**  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT    **
**  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS        **
**  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN            **
**  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING    **
**  IN ANY WAY OUT OF THE USE OF THIS DOCUMENTATION, EVEN IF ADVISED OF THE            **
**  POSSIBILITY OF SUCH DAMAGE.                                                        **
**                                                                                     **
**  -------------------------------------------------------------------------------    **
**                                                                                     **
**  (c) Copyright 2013 Synopsys, Inc.                                                  **
**                                                                                     **
**  -------------------------------------------------------------------------------    **
**                                                                                     **
**  Data contained in this file is created for educational and training purposes       **
**  only and is not recommended for fabrication                                        **
**                                                                                     **
****************************************************************************************/




/*
#########################################################################################
#               -------------------------------------------                             #
#                 SAED 32/28NM 1p9m ICV POLY OD FILL DECK				#
#               -------------------------------------------                             #
#											#
# Revision History:									#
# ------------------------------------------------------------------------------------- #
# Rev.		   date			    what					#
# -------------------------------------------------------------------------------------	#	
# 1.0		02/Feb/2011		(First draft)	                                #                                                     #
# 1.1		20/June/2012		(First draft)       				#
# 					                                                #
#########################################################################################
*/




#include "icv.rh"
#include "math.rh"

#ifndef m_LIBRARY_PATH
#define m_LIBRARY_PATH "/remote/home/stud121/Desktop/antenna_icv/"
#endif

#define  MilkyWay_Y
#define Merge_Input_Original






hierarchy_options (
                    flatten = {"*"}
);

error_options(                                                                                                                                                                   
    error_limit_per_check   = 100000000,                                                                                                                                         
    report_empty_violations = true                                                                                                                                               
);




library(
        cell = "*",
        format = GDSII,
	library_name  = "*"
);




////////////////////////////////////////
/////////// ASSIGNMENTS ////////////////
////////////////////////////////////////



NWELL 		= 	assign({{1}});
DNW		=	assign({{2}});
DIFF		=	assign({{3}});
DDMY            =       assign({{3, 1}});
PIMP		=	assign({{4}});
NIMP		=	assign({{5}});
DIFF_18		=	assign({{6}});
PAD		=	assign({{7}});
ESD_25		=	assign({{8}});
SBLK		=	assign({{9}});
PO		=	assign({{10}});
PODMY		=	assign({{10, 1}});
M1		=	assign({{11}});
M1_TEXT		=	assign_text({{11}});
M1DMY		=	assign({{11, 1}});
VIA1		=	assign({{12}});
M2		=	assign({{13}});
M2_TEXT		=	assign_text({{13}});
M2DMY		=	assign({{13, 1}});
VIA2		=	assign({{14}});
M3		=	assign({{15}});
M3_TEXT		=	assign_text({{15}});
M3DMY		=	assign({{15, 1}});
VIA3		=	assign({{16}});
M4		=	assign({{17}});
M4_TEXT		=	assign_text({{17}});
M4DMY		=	assign({{17, 1}});
VIA4 		=	assign({{18}});
M5		=	assign({{19}});
M5_TEXT		=	assign_text({{19}});
M5DMY		=	assign({{19},{1}});
VIA5		=	assign({{20}});
M6		=	assign({{21}});
M6_TEXT		=	assign_text({{21}});
M6DMY		=	assign({{21, 1}});
VIA6		=	assign({{22}});
M7		=	assign({{23}});
M7_TEXT		=	assign_text({{23}});
M7DMY		=	assign({{23, 1}});
M8		=	assign({{24}});
M8_TEXT		=	assign_text({{24}});
M8DMY		=	assign({{24, 1}});
M9		=	assign({{25}});
M9_TEXT		=	assign_text({{25}});
M9DMY		=	assign({{25, 1}});
CO		=	assign({{26}}); 
VIA7		=	assign({{27}});
VIA8		=	assign({{28}});
HVTIMP		=	assign({{29}});
LVTIMP		=	assign({{30}});
M1PIN		=	assign({{31}});
M1PIN_TEXT	=	assign_text({{31}});
M2PIN		=	assign({{32}});
M2PIN_TEXT	=	assign_text({{32}});
M3PIN		=	assign({{33}});
M3PIN_TEXT	=	assign_text({{33}});
M4PIN		=	assign({{34}});
M4PIN_TEXT	=	assign_text({{34}});
M5PIN		=	assign({{35}});
M5PIN_TEXT	=	assign_text({{35}});
M6PIN		=	assign({{36}});
M6PIN_TEXT	=	assign_text({{36}});
M7PIN		=	assign({{37}});
M7PIN_TEXT	=	assign_text({{37}});
M8PIN		=	assign({{38}});
M8PIN_TEXT	=	assign_text({{38}});
M9PIN		=	assign({{39}});
M9PIN_TEXT	=	assign_text({{39}});
HOTNWL		=	assign({{41}});
DIODMARK	=	assign({{43}});
BJTMARK		=	assign({{44}});
RNW		=	assign({{45}});
RMARKER		=	assign({{46}});
LOGO		=	assign({{48}});
IP		=	assign({{49},{49}});
DM1EXCL 	= 	assign({{61}});
DM2EXCL 	=	assign({{62}});
DM3EXCL 	=	assign({{63}});
DM4EXCL 	=	assign({{64}});
DM5EXCL 	=	assign({{65}});
DM6EXCL 	=	assign({{66}});
DM7EXCL 	=	assign({{67}});
DM8EXCL 	=	assign({{68}});
DM9EXCL 	=	assign({{69}});
DIFF_FM 	=	assign({{100}});
PO_FM 		=	assign({{101}});
DIFF_25         =       assign({{75}});




///////////////////////////DENSITYCHECK//////////////////////////////////



densityEQ_single_PO : function(void) returning void
{
   areaL : double = den_polygon_area("layer1");
   areaW : double = den_window_area();
   RATIO : double = areaL / areaW;
   if (RATIO > 0.00000000001 || RATIO < 0.15)
   den_save_window (error_names = { "RATIO", "area" },
                            values = { RATIO, areaL });
}




densityEQ_single_DIFF : function(void) returning void
{
   areaL : double = den_polygon_area("layer1");
   areaW : double = den_window_area();
   RATIO : double = areaL / areaW;
   if (RATIO > 0.00000000001 || RATIO < 0.15)
   den_save_window (error_names = { "RATIO", "area" },
                            values = { RATIO, areaL });
}



/////////////////////////////////////////////////////////////////////


chip = chip_extent();
cell = cell_extent ( cell_list = {"*"} );
bulk = size ( cell, 1);
PWELL = not ( bulk , NWELL );
NDIFF = and ( NIMP , DDMY );
PDIFF = and ( PIMP , DDMY );
NACT = and ( NDIFF , PWELL );
PACT = and ( PDIFF , NWELL );

ALLPO = PO or PODMY;
ALLDIFF = DIFF or DIFF_18 or DIFF_25 or DDMY;

gLAYER1 = DIFF interacting PO;
gLAYER2 = DIFF_18 interacting PO;
gLAYER3 = DIFF_25 interacting PO;
gLAYER4 = size( DIFF, distance = 0.1, clip_acute = NONE );
gLAYER5 = size( PWELL, distance = 0.07, clip_acute = NONE );
gLAYER6 = size( PWELL, distance = -0.07, clip_acute = NONE );
gLAYER7 = gLAYER5 not gLAYER6; 
gLAYER8 = size( PIMP, distance = 0.07, clip_acute = NONE );
gLAYER9 = size( PIMP, distance = -0.07, clip_acute = NONE );
gLAYER10 = gLAYER8 not gLAYER9;
gLAYER11 = size( NIMP, distance = 0.07, clip_acute = NONE );
gLAYER12 = size( NIMP, distance = -0.07, clip_acute = NONE );
gLAYER13 = gLAYER11 not gLAYER12;





////////////////////////////// PO_FILL ////////////////////////////////

PO_FILL_RULE = gLAYER4 or gLAYER7 or gLAYER10 or gLAYER13;



candidates1 = density(window_layer =chip,
                  layer_hash = { "layer1" => ALLPO },
                  window_function = densityEQ_single_PO,
                  delta_x = 1.0,
                  delta_y = 1.0,
                  resize_delta_xy = true,
                  statistics_file_modes = APPEND);



my_func1: function ( void ) returning void{
   strike : polygon = fp_get_current_polygon();
   fp_generate_fill(
      polygon = strike,
      width = 0.05,
      height = 3,
      space_x = 0.137,
      space_y = 0.1,
      stagger_x = 0.0,
      stagger_y = 0.0
     );
}


candidates1_1 = candidates1 not PO_FILL_RULE;

fillOutput_PO  = fill_pattern( candidates1_1,
                               fill_function = my_func1,
                               output_aref = {output_aref = true}
);


/////////////////////////// DIFF_FILL ///////////////////////////////////////

gLAYER14 = size( DIFF_18, distance = 0.15, clip_acute = NONE );
gLAYER15 = size( DIFF_25, distance = 0.15, clip_acute = NONE );
gLAYER16 = size( PO, distance = 0.1, clip_acute = NONE );
gLAYER17 = size( DNW, distance = 1.5, clip_acute = NONE );



DIFF_FILL_RULE = gLAYER14 or gLAYER15 or gLAYER16 or gLAYER17 ;

candidates2 = density(window_layer =chip,
                  layer_hash = { "layer1" => ALLDIFF },
                  window_function = densityEQ_single_DIFF,
                  delta_x = 1.0,
                  delta_y = 1.0,
                  resize_delta_xy = true,
                  statistics_file_modes = APPEND);



my_func2: function ( void ) returning void{
   strike : polygon = fp_get_current_polygon();
   fp_generate_fill(
      polygon = strike,
      width = 0.097,
      height = 3,
      space_x = 0.09,
      space_y = 0.1,
      stagger_x = 0.0,
      stagger_y = 0.0
     );
}


candidates2_1 = candidates2 not (DIFF_FILL_RULE or PO_FILL_RULE);

candidates2_2 = shrink(
                       candidates2_1,
                       west = 0.07
);

fillOutput_DIFF  = fill_pattern( candidates2_2,
                           fill_function = my_func2,
                          output_aref = {output_aref = true}
);


///////////////////////////// TRANZISTOR ////////////////////////////////

fillOutput_PO1 = size( fillOutput_PO, distance = 0.2, clip_acute = NONE );
fillOutput_DIFF1 = size( fillOutput_DIFF, distance = 0.2, clip_acute = NONE );
candidates = candidates1 or candidates2;




my_func3: function ( void ) returning void{
   strike : polygon = fp_get_current_polygon();
   fp_generate_fill(
      polygon = strike,
      width = 0.264,
      height = 0.1,
      space_x = 0.1,
      space_y = 0.22,
      stagger_x = 0.0,
      stagger_y = 0.0
     );
}


candidates3_1 = candidates not (DIFF_FILL_RULE or PO_FILL_RULE or fillOutput_PO1 or fillOutput_DIFF1);

candidates3_2 = shrink(
                       candidates3_1,
                       west = 0.08,
                       south = 0.06
);


fillOutput_TDIFF  = fill_pattern(
                                 candidates3_2,
                                 fill_function = my_func3,
                                 output_aref = {output_aref = true}
);





my_func4: function ( void ) returning void{
   strike : polygon = fp_get_current_polygon();
   fp_generate_fill(
      polygon = strike,
      width = 0.06,
      height = 0.22,
      space_x = 0.122,
      space_y = 0.1,
      stagger_x = 0.0,
      stagger_y = 0.0
     );
}




candidates4_1 = candidates not (DIFF_FILL_RULE or PO_FILL_RULE or fillOutput_PO1 or fillOutput_DIFF1);

fillOutput_TPO  = fill_pattern(
                               candidates4_1,
                               fill_function = my_func4,
                               output_aref = {output_aref = true}
);






/////////////////////////////// WRITEGDS /////////////////////////////

#ifndef  MilkyWay_Y

gds_fh1 = gds_library ("TESTGDS_OUT.gds");
                     write_gds(
                               gds_fh1,
                               holding_cell = "TEST" , 
#ifdef Merge_Input_Original
                               merge_input_layout = true,
#endif
                               cell_prefix = "O_",  

                               layers = {
	                                 {fillOutput_DIFF, {3, 1} },
                                         {fillOutput_PO,  {10, 1} },
	                                 {fillOutput_TDIFF, {3, 1} },
                                         {fillOutput_TPO,  {10, 1} },
    }
); 


#endif



////////////////////////////// WRITEMILKYWAY ///////////////////////////

#ifdef MilkyWay_Y
m_library = milkyway_library ("design_results" , ".");
write_milkyway ( 
	output_library = m_library,
	output_cell = "out",
	view ="filled_",
	mode = OVERWRITE,
	output_hierarchy = true,
	technology_file = "saed32nm_1p9m_mw.tf",
	
                           layers = {
                                     {fillOutput_DIFF, {3, 1} },
                                     {fillOutput_PO,  {10, 1} },
	                             {fillOutput_TDIFF, {3, 1} },
                                     {fillOutput_TPO,  {10, 1} },
     }
);

#endif
PO_FILL = fillOutput_TPO;
DIFF_FILL = fillOutput_TDIFF;


