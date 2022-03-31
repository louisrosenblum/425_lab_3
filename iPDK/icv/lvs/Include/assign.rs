
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




p_l : list of m_st = { 
{"p105"      , pgate_12,     nwnr},
{"p25"       , pgate_25,     nwnr},
{"p18"       , pgate_18,     nwnr},
{"p105_lvt"  , pgate_12_lvt, nwnr},
{"p105_hvt"  , pgate_12_hvt, nwnr}
 };

n_l : list of m_st = {
{"n105"     , ngate_12     , pwell},
{"n25"      , ngate_25     , pwell},
{"n18"      , ngate_18     , pwell},
{"n105_lvt" , ngate_12_lvt , pwell},
{"n105_hvt" , ngate_12_hvt , pwell}
};



rpd_l : list of rpd_st = { 
{"rpdiff"     , pdores     ,psdr,false,true},
{"rndiff"     , ndores     ,nsdr,false,true},
{"rppoly"     , ppores     ,ponr},
{"rnpoly"     , npores     ,ponr,true,false},
{"rppoly_wos" , ppores_sblk,ponr,true,false},
{"rnpoly_wos" , npores_sblk,ponr}
 };





rm_l : list of rm_st = { 
{"rm1" ,m1res,m1},
{"rm2" ,m2res,m2},
{"rm3" ,m3res,m3},
{"rm4" ,m4res,m4},
{"rm5" ,m5res,m5},
{"rm6" ,m6res,m6},
{"rm7" ,m7res,m7},
{"rm8" ,m8res,m8}
 /* {"rm9" ,m9res,m9,false}, */
 };
 

nmos_list:dev_names = {
"n105",
"n25",
"n18",
"n105_lvt",
"n105_hvt"
};

pmos_list:dev_names = {
"p105",
"p25",
"p18",
"p105_lvt",
"p105_hvt"
};










