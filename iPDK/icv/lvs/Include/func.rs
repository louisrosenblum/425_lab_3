
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



#include "icv_compare.rh"
#include "math.rh"

compare_doubles : function (d1:double, d2:double, tolerance:double) returning equal:boolean {    
     if( abs((d1-d2)/d1) < tolerance ) { equal = true;}
     else { equal = false; }
}

lvs_all_double_prop_equal : function ( device:device, property:string ) returning equal:boolean {
    propval : double;
    prop_0  : double;

    equal = false;

    count = lvs_count_members(device);
    for( i=0 to count-1 ) {
         memID = lvs_get_member(device, i);
         isProp= lvs_get_double_property(memID, property, propval);

         if( isProp ) {
             if( i == 0 ) { prop_0 = propval; equal = true; }
             else         { equal = compare_doubles(propval, prop_0, 0.00001) && equal; }
         }
         else { equal = false; }
    }
}

calc_width_length_by_ratio : entrypoint function (void) returning void {

    total_w  : double = 0;
    total_l  : double = 0;
    equalL : boolean = false;
    W_mul_L : double = 0;
    W_div_L : double = 0;

    devID = lvs_current_device(); 

    equalL = lvs_all_double_prop_equal(devID, "L");
    
    if( equalL ) {
         // if all Ls are equal, sum the widths and keep the length
         isWprop = lvs_sum(devID, "W", total_w);
         memID = lvs_get_member(devID, 0);
         isWprop= lvs_get_double_property(memID, "L", total_l);
    } 

    else {
         if( lvs_sum_of_products(devID, "W", "L", W_mul_L) &&
	     lvs_sum_of_divisions(devID, "W", "L", W_div_L) )

              { 
                  total_w = sqrt(W_mul_L * W_div_L); 
                  total_l = sqrt(W_mul_L / W_div_L);
              }

         else { 
                  total_l = -1; 
                  total_w = -1; 
              }
    }

    lvs_save_double_property("W", total_w);
    lvs_save_double_property("L", total_l);
}
