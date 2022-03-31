########################################################################
# Copyright (c) 2001-2008 Ciranova, Inc. All Rights Reserved.          #
#                                                                      #
# Permission is hereby granted, free of charge, to any person          #
# obtaining a copy of this software and associated documentation       #
# ("Ciranova Open Code"), to use the Ciranova Open Code without        #
# restriction, including without limitation the right to use, copy,    #
# modify, merge, publish, distribute, sublicense, and sell copies of   #
# the Ciranova Open Code, and to permit persons to whom the Ciranova   #
# Open Code is furnished to do so, subject to the following            #
# conditions:                                                          #
#                                                                      #
# The above copyright notice and this permission notice must be        #
# included in all copies and all distribution, redistribution, and     #
# sublicensing of the Ciranova Open Code. THE CIRANOVA OPEN CODE IS    #
# PROVIDED "AS IS" AND WITHOUT WARRANTY OF ANY KIND, EXPRESS, IMPLIED  #
# OR STATUTORY INCLUDING WITHOUT LIMITATION ANY WARRANTY OF            #
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, TITLE AND         #
# NONINFRINGEMENT. IN NO EVENT SHALL CIRANOVA, INC. BE LIABLE FOR ANY  #
# INDIRECT, PUNITIVE, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES     #
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE CIRANOVA OPEN CODE    #
# OR ANY USE OF THE CIRANOVA OPEN CODE, OR BE LIABLE FOR ANY CLAIM,    #
# DAMAGES OR OTHER LIABILITY, HOWEVER IT ARISES AND ON ANY THEORY OF   #
# LIABILITY, WHETHER IN AN ACTION FOR CONTRACT, STRICT LIABILITY OR    #
# TORT (INCLUDING NEGLIGENCE), OR OTHERWISE, ARISING FROM, OUT OF OR   #
# IN CONNECTION WITH THE CIRANOVA OPEN CODE OR ANY USE OF THE          #
# CIRANOVA OPEN CODE. The Ciranova Open Code is subject to U.S.        #
# export control laws and may be subject to export or import           #
# regulations in other countries, and all use of the Ciranova Open     #
# Code must be in compliance with such laws and regulations.  If any   #
# license for the Ciranova Open Code is obtained pursuant to a         #
# government contract, all use, distribution and/or copying by the     #
# U.S. government shall be subject to this permission notice and any   #
# applicable FAR provisions.                                           #
########################################################################

import os

import combCapacitor
import DiffPair
import DiffPair1

import fastMosfet
#import inductor
import GuardRing
import PNP

import NPN



import Mosfet1
import Mosfet2
import Mosfet3
import Diode
import pnp
import resistor
import resistorPair

import resistorUnit
#import Varactor

cells = [
    [GuardRing.PGuardRing,                      "PGuardRing"         ],
    [GuardRing.NGuardRing,                      "NGuardRing"         ],

    #[ inductor.SpiralInductor,                  "SpiralInductor"     ],
    #[ combCapacitor.CombCapacitor,              "CombCapacitor"      ],
    [ Diode.nd,					"nd"			],
    [ Diode.pd,					"pd"			],
    [ resistorUnit.ResistorUnit,                "ResistorUnit"          ],
    #[ resistor.SilNPolyRes,                     "SilNPolyRes"        ],
    #[ resistor.SilPPolyRes,                     "SilPPolyRes"        ],
    #[ resistor.SilNDiffRes,                     "SilNDiffRes"        ],
    #[ resistor.SilPDiffRes,                     "SilPDiffRes"        ],
    [ resistor.rnpoly,                   "rnpoly"      ],
    [ resistor.rppoly,                   "rppoly"      ],
    #[ resistor.rndiff,                   "rndiff"      ],
    #[ resistor.rpdiff,                   "rpdiff"      ],
    [ resistor.rnpoly_wos,               "rnpoly_wos"  ],
    [ resistor.rppoly_wos,               "rppoly_wos"  ],

    #### Uncomment following line for Nwell resistor pair
    ### [ resistor.NWellRes,                        "NWellRes"           ],

    #[ resistorPair.SilNPolyResPair,             "SilNPolyResPair"    ],
    #[ resistorPair.SilPPolyResPair,             "SilPPolyResPair"    ],
    #[ resistorPair.SilNDiffResPair,             "SilNDiffResPair"    ],
    #[ resistorPair.SilPDiffResPair,             "SilPDiffResPair"    ],
    #[ resistorPair.unSilNPolyResPair,           "unSilNPolyResPair"  ],
    #[ resistorPair.unSilPPolyResPair,           "unSilPPolyResPair"  ],
    #[ resistorPair.unSilNDiffResPair,           "unSilNDiffResPair"  ],
    #[ resistorPair.unSilPDiffResPair,           "unSilPDiffResPair"  ],

    #### Uncomment following line for Nwell resistor pair
    ### [ resistorPair.NWellResPair,                "NWellResPair"       ],

#    [ Mosfet1.Pmos,                             "Pmos"               ],
#    [ Mosfet1.Nmos,                             "Nmos"               ],
#    [ Mosfet1.PmosHvt,                          "PmosHvt"            ],
#    [ Mosfet1.NmosH,                            "NmosH"              ],
    [ Mosfet2.Pmos,                             "pmos3t"              ],
    [ Mosfet2.Nmos,                             "nmos3t"              ],
    [ Mosfet2.Pmos,                             "pmos4t"              ],
    [ Mosfet2.Nmos,                             "nmos4t"              ],    
    [ Mosfet2.PmosH,                            "pmos4t_18"           ],
    [ Mosfet2.NmosH,                            "nmos4t_18"           ],    
    [ Mosfet2.PmosH25,                          "pmos4t_25"           ],
    [ Mosfet2.NmosH25,                          "nmos4t_25"           ],
#    [ Mosfet3.Pmos,                             "Pmos3"              ],
#    [ Mosfet3.Nmos,                             "Nmos3"              ],
    [ Mosfet2.PmosHvt,                          "pmos4t_hvt"          ],
    [ Mosfet2.NmosHvt,                          "nmos4t_hvt"          ],
    [ Mosfet2.PmosLvt,                          "pmos4t_lvt"          ],
    [ Mosfet2.NmosLvt,                          "nmos4t_lvt"          ],    
#    [ Mosfet3.PmosH,                            "PmosH3"             ],
#    [ Mosfet3.NmosH,                            "NmosH3"             ],
#    [ DiffPair.PmosDiffPair,                    "PmosDiffPair"       ],
#    [ DiffPair.NmosDiffPair,                    "NmosDiffPair"       ],
#    [ DiffPair.PmosHDiffPair,                   "PmosHDiffPair"      ],
#    [ DiffPair.NmosHDiffPair,                   "NmosHDiffPair"      ],
#    [ DiffPair1.PmosDiffPair,                   "PmosDiffPair1"      ],
#    [ DiffPair1.NmosDiffPair,                   "NmosDiffPair1"      ],
#    [ DiffPair1.PmosHDiffPair,                  "PmosHDiffPair1"     ],
#    [ DiffPair1.NmosHDiffPair,                  "NmosHDiffPair1"     ],
    #[ pnp.pnp2,                                 "pnp2"               ],
    #[ pnp.pnp5,                                 "pnp5"               ],
    #[ pnp.pnp10,                                "pnp10"              ],
    [ NPN.vnpn,					"hnpn"			],
    [ PNP.vpnp,					"vpnp"			],
    [ pnp.bandgap3x3pnp10,                      "bandgap3x3pnp10"    ],
    [ pnp.bandgap4x3pnp10,                      "bandgap4x3pnp10"    ],
    [ pnp.bandgap5x5pnp5,                       "bandgap5x5pnp5"     ],
    [ pnp.bandgap3x3,                           "bandgap3x3"         ],
    [ pnp.bandgap4x3,                           "bandgap4x3"         ],
    [ pnp.bandgap5x5,                           "bandgap5x5"         ],
    #[ Varactor.NVaractor,                       "NVaractor"          ],
    #[ Varactor.NVaractorH,                      "NVaractorH"         ],

    #[fastMosfet.FastPmos,                       "FastPmos"           ],
    #[fastMosfet.FastNmos,                       "FastNmos"           ],
]



def definePcells( lib):
    """Define the cells to be created in the OpenAccess library.
        """
    # Environment variable MyListOfCells is a string which
    # consists of a comma-separated list of the cells to
    # build.
    listOfCells = os.getenv("MyListOfCells")

    if listOfCells:
        listOfCells = listOfCells.split(",")

        # Can't use a dictionary because building PyCells
        # can be order-dependent.  i.e.  masters must be built
        # before reference.
        for cell in cells:
            if cell[1] in listOfCells:
                lib.definePcell( cell[0], cell[1])
    else:
        for cell in cells:
            lib.definePcell( cell[0], cell[1])

