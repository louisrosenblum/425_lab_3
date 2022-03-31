
#########################################################################################
#########################################################################################
##                                                                                     ##
##  The 32/28nm interoperable process design kit, including the information contained  ##
##  therein  ("PDK") is unsupported Confidential Information of Synopsys, Inc.         ##
##  ("Synopsys") provided to you as Documentation under the terms of the End User      ##
##  Software License Agreement between you or your employer and Synopsys ("License     ##
##  Agreement") and you agree not to distribute or disclose the PDK without the        ##
##  prior written consent of Synopsys. The PDK IS NOT an item of Licensed Software     ##
##  or Licensed Product under the License Agreement.  Synopsys and/or its licensors    ##
##  own and shall retain all right, title and interest in and to the PDK and all       ##
##  modifications thereto, including all intellectual property rights embodied         ##
##  therein. All rights in and to any PDK modifications you make are hereby assigned   ##
##  to Synopsys. If you do not agree with this notice, including the disclaimer        ##
##  below, then you are not authorized to use the PDK.                                 ##
##                                                                                     ##
##  THIS PDK IS BEING DISTRIBUTED BY SYNOPSYS SOLELY ON AN "AS IS" BASIS, WITH NO      ##
##  INTELLECUTAL PROPERTY INDEMNIFICATION AND NO SUPPORT. ANY EXPRESS OR IMPLIED       ##
##  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF               ##
##  MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE HEREBY DISCLAIMED. IN     ##
##  NO EVENT SHALL SYNOPSYS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,   ##
##  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT    ##
##  OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS        ##
##  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN            ##
##  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING    ##
##  IN ANY WAY OUT OF THE USE OF THIS DOCUMENTATION, EVEN IF ADVISED OF THE            ##
##  POSSIBILITY OF SUCH DAMAGE.                                                        ##
##                                                                                     ##
##  -------------------------------------------------------------------------------    ##
##                                                                                     ##
##  (c) Copyright 2013 Synopsys, Inc.                                                  ##
##                                                                                     ##
##  -------------------------------------------------------------------------------    ##
##                                                                                     ##
##  Data contained in this file is created for educational and training purposes       ##
##  only and is not recommended for fabrication                                        ##
##                                                                                     ##
#########################################################################################


proc getCurrentInstance_GR {} {
	return [db::getCurrentRef]
}

proc getCurrentParam_GR {} {
	return [db::getCurrentParam]
}

proc getCurrentParamValue_GR {param_name} {
	return [db::getParamValue $param_name -of [getCurrentInstance_GR]]
}

proc set_Limits_GR {} {
	return [list [list min_width max_width min_height max_height] [list 0.044 50 0.044 50] ]
}

proc getLimitsValueByName_GR { value_name } {
	set names  [lindex [set_Limits_GR] 0]
	set values [lindex [set_Limits_GR] 1]
	
	for {set i 0} {$i < [llength $values]} {incr i} {
		if {[lindex $names $i] == $value_name} {
			return [lindex $values $i]
		}
	}
}

proc IsLayoutEditor { } {
    set inst  [db::getCurrentRef]
    set viewType [oa::getName [oa::getViewType [oa::getDesign $inst]]]
    set viewName [oa::getViewName $inst] 
    if { $viewName == "layout" } {return 1} else {return 0}
}

proc setInstanceParamValue_GR { param value inst} {
	set formval [db::getParamValue $param -of $inst]
	
	if {[IsLayoutEditor]} {
		# param is a variable
		if { [is_variable_MOS $formval] || [is_variable_MOS $value] } {
			set old_val $formval
			set new_val $value
			if { [string compare $old_val $new_val] != 0 } {
				set value [lindex [split $value "u"] 0]
				db::setParamValue $param -value $new_val -of $inst -evalCallbacks 0
			}
		# param is NOT a variable
		} else {
			set old_val [db::engToSci $formval]
			set new_val [db::engToSci $value]
			if { [expr $old_val] != [expr $new_val] } {
				set value [lindex [split $value "u"] 0]
				db::setParamValue $param -value $new_val -of $inst -evalCallbacks 0
			}
		}
	} else {
		 if {[regexp {^\d+\.\d+$} $value] || [regexp {^\d+$} $value]} {
			db::setParamValue $param -value "${value}u" -of $inst -evalCallbacks 0
		} else {
			db::setParamValue $param -value "${value}" -of $inst -evalCallbacks 0
		}	
	}
}


proc GuardRing {} {

	set edited_param [getCurrentParam_GR]
	
	if {[IsLayoutEditor]} {
		set width [getCurrentParamValue "width"]
		set height [getCurrentParamValue "height"]
		set width [lindex [split [db::sciToEng $width] "u"] 0]
		set height [lindex [split [db::sciToEng $height] "u"] 0]
	} else {
		set width [getCurrentParamValue "width"]
		if {[regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $width] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $width]} {
			set width [lindex [split [db::sciToEng $width] "u"] 0]
		}
		#set l [getCurrentParamValue "height"]
		if {[regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $height] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $height]}  {
			set height [lindex [split [db::sciToEng $height] "u"] 0]
		}
	}
	if {$edited_param == "width"} {
		set max_value_of_width [getLimitsValueByName_GR "max_${edited_param}"]
		set min_value_of_width [getLimitsValueByName_GR "min_${edited_param}"]
		
		if {$width > $max_value_of_width && ([regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $width] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $width])} {
		
			puts "WARNING 0009> The value of \"${edited_param}\" \"${width}\" > ${max_value_of_width} max value..."
			puts "\t\tResetting \"${edited_param}\"  to max value."
			$max_value_of_width
			setInstanceParamValue_GR "${edited_param}" $max_value_of_width [getCurrentInstance_GR]	
		} elseif {$width < $min_value_of_width && ([regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $width] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $width])} {
		
			puts "WARNING 0009> The value of \"${edited_param}\" \"${width}\" < ${min_value_of_width} min value..."
			puts "\t\tResetting \"${edited_param}\"  to min value."
			
			setInstanceParamValue_GR "${edited_param}" $min_value_of_width [getCurrentInstance_GR]
		} elseif {[regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $width] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $width]} {
			setInstanceParamValue_GR "${edited_param}" $width [getCurrentInstance_GR]
		} else {
			setInstanceParamValue_GR "${edited_param}" $we [getCurrentInstance_GR]
		}
	} elseif {$edited_param == "height"} {
		set max_value_of_height [getLimitsValueByName_GR "max_${edited_param}"]
		set min_value_of_height [getLimitsValueByName_GR "min_${edited_param}"]
		
		if {$height > $max_value_of_height && ([regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $height] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $height])} {
		
			puts "WARNING 0009> The value of \"${edited_param}\" \"${height}\" > ${max_value_of_height} max value..."
			puts "\t\tResetting \"${edited_param}\"  to max value."
			
			setInstanceParamValue_GR "${edited_param}" $max_value_of_height [getCurrentInstance_GR]
		} elseif {$height < $min_value_of_height && ([regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $height] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $height])} {
		
			puts "WARNING 0009> The value of \"${edited_param}\" \"${height}\" < ${min_value_of_height} min value..."
			puts "\t\tResetting \"${edited_param}\"  to min value."
			
			setInstanceParamValue_GR "${edited_param}" $min_value_of_height [getCurrentInstance_GR]
		} elseif {[regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $height] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $height]} {
			setInstanceParamValue_GR "${edited_param}" $height [getCurrentInstance_GR]
		} else {
#			setInstanceParamValue_GR "${edited_param}" $l [getCurrentInstance_GR]
		}
	} elseif {$edited_param == "sides"} {
		set side [getCurrentParamValue_GR "sides"]
		set side_values [list "top" "bottom" "right" "left"]
		set new_side [split $side ","]
		set ind 0
		
		foreach i $side_values {
			foreach j $new_side {
				if {$i == $j} {
					incr ind
					break
				}
			}
		}
		
		if {$ind == [llength $new_side] && $ind <= 4 && $ind!=0} {
			setInstanceParamValue_GR "${edited_param}"  $side [getCurrentInstance_GR]
		} else {
			puts "WARNING 0020> Side paramater input error."
			puts "Side parameter is \"top, bottom, left, right\""
			puts "\t\tPlease enter any combination of above mentioned options, splited only by \",\"..."
			setInstanceParamValue_GR "sides"  "top,bottom,right,left" [getCurrentInstance_GR]
		}
	}

}
