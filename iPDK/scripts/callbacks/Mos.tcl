
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


proc toNanometer { val } {
    return [expr $val*1e-6]
}

proc IsLayoutEditor { } {
    set inst  [db::getCurrentRef]
    set viewType [oa::getName [oa::getViewType [oa::getDesign $inst]]]
    set viewName [oa::getViewName $inst] 
    if { $viewName == "layout" } {return 1} else {return 0}
}

proc getCurrentInstance {} {
	return [db::getCurrentRef]
}

proc getCurrentParam {} {
	return [db::getCurrentParam]
}

proc getCurrentParamValue {param_name} {
	return [db::getParamValue $param_name -of [getCurrentInstance]]
}

proc is_variable_MOS { paramValue } {

    if { [regexp {([i][n][s][t])|([p][a][r][e][n][t])|([l][i][n][e][a][g][e])|([P][a][r])} $paramValue match] } {
        return 1
    } elseif { [regexp {(^\[+)}  $paramValue ] } {
        return 1
    } elseif { [regexp {(^[a-zA-Z]+$)|(^[a-zA-Z]+)} $paramValue ]} {
        if { [regexp {(^[a-zA-Z]+)((\*+)|(\/+)|(\-+)|(\++) \
          |(\%+))(([a-zA-Z]+$)|([0-9]+$))} $paramValue ] && ![regexp {(\@+)|(\^+)|(\&+)|(\(+)|(\)+)|(\|+)|(\{+)|(\}+)|(\<+) \
          |(\>+)|(\?+)|(\:+)|(\;+)|(\"+)|(\'+)|(\=+)|(\`+)|(\~+)|(\,+)} $paramValue ]} {
            return 1

         } elseif { [regexp {(^[a-zA-Z]+$)|(^[a-zA-Z]+)} $paramValue ] && ![regexp {(\@+)|(\^+)|(\&+)|(\(+)|(\)+)|(\|+)|(\{+)|(\}+)| \
             (\<+)|(\>+)|(\?+)|(\:+)|(\;+)|(\"+)|(\'+)|(\=+)|(\`+)|(\~+)|(\,+)} $paramValue ]} {
             return 1

         } else {
            
            # input error
             return 2

         }

    # if input begins with a number
    } elseif { ([regexp {(^[0-9]+$)|(^[0-9]+\.[0-9]+$)|(^\.[0-9]+$)} $paramValue ] \
       || [regexp {((^[0-9]+)|(^[0-9]+\.[0-9]+)|(^\.[0-9]+))([a-zA-Z]+$)} $paramValue ] \
       || [regexp {((^[0-9]+)|(^[0-9]+\.[0-9]+)|(^\.[0-9]+))(([a-zA-Z]+)|(\++)|(\!+)| \
        (\#+)|(\$+)|(\%+)|(\[+)|(\]+)|(\_+)|(\/+)|(\*+)|(\-+))} $paramValue ]) && ![regexp { } $paramValue] } {

        if { [regexp {(^[0-9]+)|(^[0-9]+\.[0-9]+)|(^\.[0-9]+)} $paramValue match] } {
            if { [regexp {(^[0-9]+$)|(^[0-9]+\.[0-9]+$)|(^\.[0-9]+$)} $paramValue ] } {
                return 0
            } else {
                  
                  set sample_value [string trimleft $paramValue $match]
                  if {[regexp {^([y]|[z]|[a]|[f]|[p]|[n]|[u]|[m]|[c]|[k]|[M]|(^[m][e][g])|[X]|[G]|[T]|[P]|[E]|[Z]|[Y])$} $sample_value] \
                  && ![regexp {[0-9]$} $sample_value ]} {
                      return 0
 
                  } elseif {[regexp {(^[eE][0-9]+$)|(^[eE]([\-]|[\+])[0-9]+$)} $sample_value check ] || [regexp {(^[0-9]+$)|(^[0-9]+\.[0-9]+$)} \
                    $sample_value check ]} {
                      return 0
              
                  } elseif { [regexp {((\*+)|(\/+)|(\-+)|(\++)|(\%+))(([a-zA-Z]+)|([0-9]+))} $sample_value ] \
                    || [regexp {([a-zA-Z]+)((\*+)|(\/+)|(\-+)|(\++)|(\%+))(([a-zA-Z]+$)|([0-9]+$))} $sample_value ] \
                    && ![regexp {(\@+)|(\^+)|(\&+)|(\(+)|(\)+)|(\|+)|(\{+)|(\}+)|(\<+)|(\>+)|(\?+)|(\:+)|(\;+)| \
                    (\"+)|(\'+)|(\=+)|(\`+)|(\~+)|(\,+)} $sample_value ] } {
                      return 1

                  } elseif { [regexp {(\@+)|(\^+)|(\&+)|(\(+)|(\)+)|(\|+)|(\{+)|(\}+)|(\<+)|(\>+)|(\?+)|(\:+) \
                    |(\;+)|(\"+)|(\'+)|(\=+)|(\`+)|(\~+)|(\,+)} $sample_value ]} {   
                     # input error
                      return 2

                  } else {
                      # input error
                      return 2

                  }
              }
        }
        
    } else {
        return 3

    }

}
proc get_warning {$value_l} {
	puts "Warning 0004> If the value of \"l\" is less than 0.1 than it is equal to one of the following values: 0.03,0.035,0.04,0.045.0.05,0.06,0.08,0.1"
}	
proc correct_value_of_l {value_l} {
	if {$value_l == 0.03 || $value_l == 0.035 || $value_l == 0.04 || $value_l == 0.45 || $value_l == 0.05 || $value_l == 0.6 || $value_l == 0.08 || $value_l == 0.1} {
		return $value_l
	}	
	if {$value_l < 0.035} {
		get_warning $value_l
		return 0.03
	} elseif {$value_l < 0.04} {
		get_warning $value_l	
		return 0.035
	} elseif {$value_l < 0.045} {
		get_warning $value_l
		return 0.04
	} elseif {$value_l < 0.05} {
		get_warning $value_l
		return 0.045
	} elseif {$value_l < 0.06} {
		get_warning $value_l
		return 0.05
	} elseif {$value_l < 0.08} {
		get_warning $value_l
		return 0.06
	} elseif {$value_l < 0.1} {
		get_warning $value_l
		return 0.08
	} else {
		return $value_l
	}
}
proc setInstanceParamValue_MOS { param value inst} {
	set formval [db::getParamValue $param -of $inst]
	
	if {[IsLayoutEditor]} {
		# param is a variable
		if { [is_variable_MOS $formval] || [is_variable_MOS $value] } {
			set old_val $formval
			set new_val $value
			if { [string compare $old_val $new_val] != 0 } {
				db::setParamValue $param -value $value -of $inst -evalCallbacks 0
			}
		# param is NOT a variable
		} else {
			set old_val [db::engToSci $formval]
			set new_val [db::engToSci $value]
			if { [expr $old_val] != [expr $new_val] } {
				db::setParamValue $param -value $value -of $inst -evalCallbacks 0
			}
		}
	} else {
		if {[regexp {^\d+\.\d+$}  $value] || [regexp {^\d+$}  $value]} {
			if {$param == "w" || $param == "wtot" || $param == "l"} {
				db::setParamValue $param -value "${value}u" -of $inst -evalCallbacks 0
			} else {
				db::setParamValue $param -value "${value}" -of $inst -evalCallbacks 0
			}
		} else {
			db::setParamValue $param -value "${value}" -of $inst -evalCallbacks 0
		}
	}
}

proc setLimits_MOS {} {
	set limit 3.5
	set limit_nf_m 1000
	set negativ -3.5
	
	return [list \
		[list min_w max_w min_wtot max_wtot min_l max_l min_nf max_nf min_m max_m  \
			min_diffContactCenterTopOffset max_diffContactCenterTopOffset min_diffContactCenterBottomOffset max_diffContactCenterBottomOffset\
			min_diffContactRightBottomOffset max_diffContactRightBottomOffset min_diffContactRightTopOffset max_diffContactRightTopOffset\
			min_diffContactLeftBottomOffset max_diffContactLeftBottomOffset min_diffContactLeftTopOffset max_diffContactLeftTopOffset\
			min_gateContactLeftOffset max_gateContactLeftOffset min_gateContactRightOffset max_gateContactRightOffset\
			min_cgSpacingAdd max_cgSpacingAdd min_leftDiffAdd max_leftDiffAdd min_rightDiffAdd max_rightDiffAdd\
			min_p_l_18 max_p_l_18 min_p_w_18 max_p_w_18 min_n_l_18 max_n_l_18 min_n_w_18 max_n_w_18\
			min_p_l_25 max_p_l_25 min_p_w_25 max_p_w_25 min_n_l_25 max_n_l_25 min_n_w_25 max_n_w_25]\
		[list 0.1 $limit 0.1 $limit 0.03 $limit 1 $limit_nf_m 1 $limit_nf_m\
			$negativ 0 $negativ 0 $negativ 0 $negativ 0 $negativ 0 $negativ 0 $negativ 0 $negativ 0 0 $limit 0 $limit 0 $limit\
			0.15 $limit 0.16 $limit 0.15 $limit 0.16 $limit\
			0.26 $limit 0.36 $limit 0.26 $limit 0.36 $limit] ]
}

proc getLimitsValueByName_MOS { value_name } {

	set names  [lindex [setLimits_MOS] 0]
	set values [lindex [setLimits_MOS] 1]
	
	for {set i 0} {$i < [llength $values]} {incr i} {
		if {[lindex $names $i] == $value_name} {
			return [lindex $values $i]
		}
	}
}

proc is_variable {param_value param_value_name} {

	if {[regexp {^\d+\.\d+$} $param_value match]} {
		return 1
	} elseif {[regexp {^\d+$} $param_value match]}  {
		return 1
	} elseif {[regexp {^\d+\.$} $param_value match]}  {
		return 1
	} elseif {[regexp {^\.\d+$} $param_value match]}  {
		return 1
	} else {
		puts "WARNING 0002> Parameter \"${param_value_name}\" value \"${param_value}\" is invalid.\n\t\t Resetting to default value."
		setInstanceParamValue_MOS $param_value_name [check_param_value_MOS $param_value_name [getLimitsValueByName_MOS "min_${param_value_name}"] ] [getCurrentInstance]
		return -1
	}
}

proc check_grid_MOS {value grid} {
	set first [lindex [split $value "."] 0]
	set second [lindex [split $value "."] 1]
	
	if {$second == 0} {
		return $value
	} else {
		set temp [expr double(round($value/$grid))]
	}
	return [expr $temp*$grid]
}

proc check_param_value_MOS {param_name param_value} {
	set max_value [getLimitsValueByName_MOS "max_${param_name}"]
	set min_value [getLimitsValueByName_MOS "min_${param_name}"]

	
	if {$param_value > $max_value} {
		puts "WARNING 0009> The value of \"${param_name}\" \"${param_value}\" > ${max_value} max value..."
		puts "\t\tResetting \"${param_name}\"  to max value."
		
				
		return $max_value
	} elseif {$param_value < $min_value} {
		#puts $param_value
		puts "WARNING 0009> The value of \"${param_name}\" \"${param_value}\" < ${min_value} min value..."
		puts "\t\tResetting \"${param_name}\"  to min value."
		return $min_value
	} else {
		return $param_value
	}
}

proc get_param_def { attr inst param} {
    return [db::getAttr $attr -of [db::getParamDefs $param -of $inst]]
}

proc make_editable {controlParamName MODE} {
	set value     [db::getParamValue $controlParamName -of [db::getCurrentRef]]
	set paramType [get_param_def type [db::getCurrentRef] $controlParamName]
	
	if {$paramType == "boolean"} {
		if {$value} {
			return 1
		} else {
			return 0 
		}
	} else {
		if {[regexp $MODE $value]} {
			return 1
		} else {
			return 0  
		}
	}
}

proc is_word {value} {
	if {[regexp {^\d+\.\d+[kMGTPEZYmunpfay]?$} $value] || [regexp {^\d+[kMGTPEZYmunpfay]?$} $value] || [regexp {^\d+e-?\d+} $value] } {
		return 0
	} elseif {[regexp {\{|\}|\[|\]|\`|\!|\@|\#|\$|\%|\^|\&|\*|\(|\)|\_|\-|\+|\=|\||\"|\'|\/|\\|\,|\;|\<|\>| +|^$} $value] } {
		return 2
	} else {
		return 1
	}
}

proc to_user_MOS {value value_name} {
	if {[is_word $value] == 0} {
		if {[regexp {^\d+\.?\d+$} $value] && ($value_name != "nf" || $value_name != "m")} {
			set value [append value "u"]
			set value [db::sciToEng $value]
			set return_value 0
		} else {
			set value [db::sciToEng $value]
			set return_value 0
		}
		if {[regexp {\d+k} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "k"] 0] * pow(10, 9))]
		} elseif {[regexp {\d+M} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "M"] 0] * pow(10, 12))]
		} elseif {[regexp {\d+G} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "G"] 0] * pow(10, 15))]
		} elseif {[regexp {\d+T} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "T"] 0] * pow(10, 18))]
		} elseif {[regexp {\d+P} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "P"] 0] * pow(10, 21))]
		} elseif {[regexp {\d+E} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "E"] 0] * pow(10, 24))]
		} elseif {[regexp {\d+Z} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "Z"] 0] * pow(10, 27))]
		} elseif {[regexp {\d+Y} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "Y"] 0] * pow(10, 30))]
		} elseif {[regexp {\d+m} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "m"] 0] * pow(10, 3))]
		} elseif {[regexp {\d+u} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "u"] 0] * pow(10, 0))]
		} elseif {[regexp {\d+n} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "n"] 0] * pow(10, -3))]
		} elseif {[regexp {\d+p} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "p"] 0] * pow(10, -6))]
		} elseif {[regexp {\d+f} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "f"] 0] * pow(10, -9))]
		} elseif {[regexp {\d+a} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "a"] 0] * pow(10, -12))]
		} elseif {[regexp {\d+z} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "z"] 0] * pow(10, -15))]
		} elseif {[regexp {\d+y} $value]} {
			set return_value  [expr double([lindex [split [db::sciToEng $value] "y"] 0] * pow(10, -18))]
		} else {
			set return_value $value
		}
		if {$value_name == "nf" || $value_name == "m"} {
			return [check_param_value_MOS $value_name [expr int($return_value)]]
			
		} else { 
			if {$value_name == "l" && $return_value <= 0.1} {
				set return_value [check_param_value_MOS $value_name [check_grid_MOS  $return_value 0.001]]
				return [correct_value_of_l $return_value]
			} else {
				return	[check_param_value_MOS $value_name [check_grid_MOS  $return_value 0.001]]
			}	
		}
	} elseif { [is_word $value] == 2 } {
		puts "WARNING 0003> The value \"${value}\" is incorrect, type only letters or/and numbers" 
		puts "\t \t Reseting  \"$value_name\" to correct param value "
		set value "param"
		return $value
	} else {
		return $value
	}	
}

proc Mos32 {} {
	set grid 0.001
	
	set edited_param [getCurrentParam]
	set edited_param_value [getCurrentParamValue $edited_param]
	
	set mode  [getCurrentParamValue "entryMode"]
	set model [getCurrentParamValue_RNDIFF "model"]
	

	if {$model == "p18"} {
		set wpf  [to_user_MOS [getCurrentParamValue "w"] "p_w_18"]
		set l    [to_user_MOS [getCurrentParamValue "l"] "p_l_18"]
		set wtot [to_user_MOS [getCurrentParamValue "wtot"] "p_w_18"]
	} elseif {$model == "n18"} {
		set wpf  [to_user_MOS [getCurrentParamValue "w"] "n_w_18"]
		set l    [to_user_MOS [getCurrentParamValue "l"] "n_l_18"]
		set wtot [to_user_MOS [getCurrentParamValue "wtot"] "n_w_18"]
	} elseif {$model == "n25"} {
		set wpf  [to_user_MOS [getCurrentParamValue "w"] "p_w_25"]
		set l    [to_user_MOS [getCurrentParamValue "l"] "p_l_25"]
		set wtot [to_user_MOS [getCurrentParamValue "wtot"] "p_w_25"]
	} elseif {$model == "p25"} {
		set wpf  [to_user_MOS [getCurrentParamValue "w"] "n_w_25"]
		set l    [to_user_MOS [getCurrentParamValue "l"] "n_l_25"]
		set wtot [to_user_MOS [getCurrentParamValue "wtot"] "n_w_25"]
	} else {
		set wpf  [to_user_MOS [getCurrentParamValue "w"] "w"]
		set l    [to_user_MOS [getCurrentParamValue "l"] "l"]
		set wtot [to_user_MOS [getCurrentParamValue "wtot"] "w"]
	}
	
	set nf   [to_user_MOS [getCurrentParamValue "nf"] "nf"]
	set m    [to_user_MOS [getCurrentParamValue "m"] "m"]
	if {$edited_param == "entryMode" && $edited_param_value == "WidthPerFinger"} {
		set mode "WidthPerFinger"
	} elseif {$edited_param == "entryMode" && $edited_param_value == "TotalWidth"} {
		set mode "TotalWidth"
	}
	if {[IsLayoutEditor]} {
		if {$mode == "WidthPerFinger"} {
			if {$edited_param == "nf"} {
				set wtot [check_grid_MOS [expr $nf*$wpf] $grid ]
				set wpf  [check_grid_MOS [expr $wtot/$nf] $grid ]
				
			} elseif {$edited_param == "w"} {
				set wtot [check_grid_MOS [expr $nf*$wpf] $grid ]
				set wpf  [check_grid_MOS [expr $wtot/$nf] $grid ]
			}
		} elseif {$mode == "TotalWidth" && ( $edited_param == "wtot" || $edited_param == "nf")} {
			if {$model == "p18"} {
				set nf  [check_param_value_MOS "nf" $nf ]
				set wpf [check_param_value_MOS "p_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
				set nf [expr int($nf)]
				set wpf [check_param_value_MOS "p_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
			} elseif {$model == "n18"} {
				set nf  [check_param_value_MOS "nf" $nf ]
				set wpf [check_param_value_MOS "n_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
				set nf [expr int($nf)]
				set wpf [check_param_value_MOS "n_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
			} elseif {$model == "p25"} {
				set nf  [check_param_value_MOS "nf" $nf ]
				set wpf [check_param_value_MOS "p_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
				set nf [expr int($nf)]
				set wpf [check_param_value_MOS "p_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
			} elseif {$model == "n25"} {
				set nf  [check_param_value_MOS "nf" $nf ]
				set wpf [check_param_value_MOS "n_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
				set nf [expr int($nf)]
				set wpf [check_param_value_MOS "n_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
			} else {
				set nf  [check_param_value_MOS "nf" $nf ]
				set wpf [check_param_value_MOS "w" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
				set nf [expr int($nf)]
				set wpf [check_param_value_MOS "w" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
			}		
		}
		
		
	} else {
		if { ($edited_param == "nf" || $edited_param == "w")  && $mode == "WidthPerFinger"} {
			if {![is_word $nf] && ![is_word $wpf]} {
				set nf   [check_param_value_MOS "nf" $nf ]
				set wtot [check_grid_MOS [expr $nf*$wpf] $grid ]
				set nf   [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
			} else {
				set wtot "$wpf"
				set wpf  "$wpf"
				set nf "$nf"
			}
		}
		
		if { ($edited_param == "nf" || $edited_param == "wtot")  && $mode == "TotalWidth"} {
			if {![is_word $nf] && ![is_word $wtot]} {
				if {$model == "p18"} {
					set nf  [check_param_value_MOS "nf" $nf ]
					set wpf [check_param_value_MOS "p_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
					set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
					set nf [expr int($nf)]
					set wpf [check_param_value_MOS "p_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				} elseif {$model == "n18"} {
					set nf  [check_param_value_MOS "nf" $nf ]
					set wpf [check_param_value_MOS "n_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
					set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
					set nf [expr int($nf)]
					set wpf [check_param_value_MOS "n_w_18" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				} elseif {$model == "p25"} {
					set nf  [check_param_value_MOS "nf" $nf ]
					set wpf [check_param_value_MOS "p_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
					set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
					set nf [expr int($nf)]
					set wpf [check_param_value_MOS "p_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				} elseif {$model == "n25"} {
					set nf  [check_param_value_MOS "nf" $nf ]
					set wpf [check_param_value_MOS "n_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
					set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
					set nf [expr int($nf)]
					set wpf [check_param_value_MOS "n_w_25" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				} else {
					set nf  [check_param_value_MOS "nf" $nf ]
					set wpf [check_param_value_MOS "w" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
					set nf  [check_param_value_MOS "nf" [expr double($wtot)/double($wpf)]]
					set nf [expr int($nf)]
					set wpf [check_param_value_MOS "w" [check_grid_MOS [expr double($wtot)/double($nf)] 0.001]]
				}
				
			} else {
				set wtot "$wtot"
				set wpf  "$wtot"
				set nf "$nf"
			}
		}
	}
	
	setInstanceParamValue_MOS "w"    $wpf  [getCurrentInstance]
	setInstanceParamValue_MOS "wtot" $wtot [getCurrentInstance]
	setInstanceParamValue_MOS "nf"   $nf   [getCurrentInstance]
	setInstanceParamValue_MOS "l"    $l    [getCurrentInstance]
	setInstanceParamValue_MOS "m"    $m    [getCurrentInstance]
	
	set diffContactLeftBottomOffset   [getCurrentParamValue "diffContactLeftBottomOffset"]
	set diffContactLeftTopOffset      [getCurrentParamValue "diffContactLeftTopOffset"]
	set diffContactCenterTopOffset    [getCurrentParamValue "diffContactCenterTopOffset"]
	set diffContactCenterBottomOffset [getCurrentParamValue "diffContactCenterBottomOffset"]
	set diffContactRightBottomOffset  [getCurrentParamValue "diffContactRightBottomOffset"]
	set diffContactRightTopOffset     [getCurrentParamValue "diffContactRightTopOffset"]
	set gateContactLeftOffset  [getCurrentParamValue "gateContactLeftOffset"]
	set gateContactRightOffset [getCurrentParamValue "gateContactRightOffset"]
	set cgSpacingAdd [getCurrentParamValue "cgSpacingAdd"]
	set leftDiffAdd  [getCurrentParamValue "leftDiffAdd"]
	set rightDiffAdd [getCurrentParamValue "rightDiffAdd"]
	set guardRing [getCurrentParamValue "guardRing"]

	if {$edited_param == "diffContactLeftBottomOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "diffContactLeftBottomOffset"   $diffContactLeftBottomOffset ] 0.001]
		setInstanceParamValue_MOS "diffContactLeftBottomOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "diffContactLeftTopOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "diffContactLeftTopOffset"   $diffContactLeftTopOffset ] 0.001]
		setInstanceParamValue_MOS "diffContactLeftTopOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "diffContactCenterTopOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "diffContactCenterTopOffset"   $diffContactCenterTopOffset ] 0.001]
		setInstanceParamValue_MOS "diffContactCenterTopOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "diffContactCenterBottomOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "diffContactCenterBottomOffset"   $diffContactCenterBottomOffset ] 0.001]
		setInstanceParamValue_MOS "diffContactCenterBottomOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "diffContactRightBottomOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "diffContactRightBottomOffset"   $diffContactRightBottomOffset ] 0.001]
		setInstanceParamValue_MOS "diffContactRightBottomOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "diffContactRightTopOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "diffContactRightTopOffset"   $diffContactRightTopOffset ] 0.001]
		setInstanceParamValue_MOS "diffContactRightTopOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "gateContactLeftOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "gateContactLeftOffset"   $gateContactLeftOffset ] 0.001]
		setInstanceParamValue_MOS "gateContactLeftOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "gateContactRightOffset"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "gateContactRightOffset"   $gateContactRightOffset ] 0.001]
		setInstanceParamValue_MOS "gateContactRightOffset"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "cgSpacingAdd"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "cgSpacingAdd"   $cgSpacingAdd ] 0.001]
		setInstanceParamValue_MOS "cgSpacingAdd"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "leftDiffAdd"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "leftDiffAdd"   $leftDiffAdd ] 0.001]
		setInstanceParamValue_MOS "leftDiffAdd"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "rightDiffAdd"} {
		set new_offset [check_grid_MOS [check_param_value_MOS "rightDiffAdd"   $rightDiffAdd ] 0.001]
		setInstanceParamValue_MOS "rightDiffAdd"  $new_offset [getCurrentInstance]
		
	} elseif {$edited_param == "guardRing"} {
		set guard_values [list "top" "bottom" "right" "left"]
		set new_guard [split $guardRing ","]
		set ind 0
		
		foreach i $guard_values {
			foreach j $new_guard {
				if {$i == $j} {
					incr ind
					break
				}
			}
		}
		
		if {$ind == [llength $new_guard] && $ind <= 4} {
			setInstanceParamValue_MOS "guardRing"  $guardRing [getCurrentInstance]
		} else {
			puts "WARNING 0020> Guard Ring paramater input error."
			puts "Guard Ring parameter is \"top, bottom, left, right\""
			puts "\t\tPlease enter any combination of above mentioned options, splited only by \",\"..."
			setInstanceParamValue_MOS "guardRing"  "" [getCurrentInstance]
		} 
	}
}
