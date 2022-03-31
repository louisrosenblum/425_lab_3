------------------------------------------------------------------------
README File for Interoperable PyCell Library, 2008-06-30
------------------------------------------------------------------------
Table of Contents
------------------------------------------------------------------------
I.   IPL Alliance and the Proof of Concept Library
II.  General Information
III. Source Files
IV.  PyCell Naming Conventions
V.   Description of PyCell Parameters
VI.  Known Problems and Limitations

------------------------------------------------------------------------
I.   IPL Alliance and Proof of Concept Library
------------------------------------------------------------------------
The IPL Alliance is a group of electronic design automation (EDA) 
companies that are collaborating on the creation and distribution of 
an Open Source interoperable PDK library (IPL) that supports the 
OpenAccess database.  IC designers can use the same PDK libraries
in tools from different vendors and in internal tools.

This package contains source code for interoperable PCells developed 
and validated by alliance members.  This source code is licensed under 
Open Source terms contained at the beginning of each source code 
file. 

This source code uses the API and OpenAccess PCell plug-in supplied 
with PyCell Studio(tm) from Ciranova(tm) Inc.

PyCell Studio is a free product available from http://www.ciranova.com. 
To link this package to a technology file and instantiate the PCells 
in an OpenAccess tool, you must use PyCell Studio to build an
OpenAccess library.

This version of the Proof of Concept Library requires PyCell Studio
Version 4.2.5.

For more information about the IPL Alliance, see http://www.iplnow.com.

------------------------------------------------------------------------
II.  General Information
------------------------------------------------------------------------
This file describe the Python modules, Python classes, PyCell names
and parameters, and known problems and limitations of the Interoperable
PyCell Library, (IPL).

The IPL devices are:
    - resistor and resistor pair.
    - MOS transistor and differential pair.
    - spiral inductor.
    - comb capacitor.
    - substrate PNP bipolar transistor.
    - varactor.
    - guard ring.

The resistors and MOS transistors are available in advanced row-stacking
configurations.

------------------------------------------------------------------------
III. Source Files
------------------------------------------------------------------------
__init__.py
        Master Python "init" file describing correspondance of Python
        classes to PyCells in the library.

resistorUnit.py:
        Builds basic strip resistor unit, including contacts at each
        end.  Resistor unit is used to build more complex resistors.

        Calculates minimum default parameter values, based upon
        minimum contact size for processs, including the minimum
        resistor length and width for silicided resistors. 

resistor.py:
        Builds single resistor, using resistor unit for each finger.
        Generates number of fingers for each row, and connects these
        fingers together using "series" or "parallel" connection.

resistorPair.py:
        Builds resistor pair, using resistor unit for each finger.
        Generates number of fingers for each row, and connects
        these fingers for each resistor together using "series" or
        "parallel" connection.

MosUtils.py:
        Define utility classes for creating stacked MOS transistors.
        MosUtil classes are building blocks used for creating MOS
        device PyCells or groups of devices.

Mosfet1.py:
        Builds row-stacking MOS transistor PyCells.

Mosfet2.py:
        Builds single row MOS transistor PyCells with stretch handles
        and auto-abutment.

Mosfet3.py:
        Builds single row MOS transistor PyCells with stretch handles
        and source/drain wiring option.

DiffPair.py:
        Builds row-stacking MOS transistor differential pair PyCells.

DiffPair1.py:
        Builds row-stacking MOS transistor differential pair PyCells
        which pitch matches Mosfet1.  
        Derived from Mosfet1.RowMosfetTemplate.

Varactor.py:
        Builds row-stacking varactor PyCells.
        Derived from Mosfet1.RowMosfetTemplate.

GuardRing.py:
        Builds p-substrate and n-substrate contact guard rings.

inductor.py:
        Builds spiral inductor on one or more adjacent metal layers
        surrounded by guardring with cutout.

        See design equations within file for relationship between
        inductor parameters.

combCapacitor.py:
        Builds comb capacitor on several metal layers.  This device
        is multi-fingered with two sets of interdigitated fingers.
        The various metal layers are connected by vias, up to the top
        metal layer.  There is a parameter to use the bottom metal
        layer to construct a shield.

pnp.py:
        Builds CMOS substrate PNP bipolar transistor, using PNP base
        class, along with several derived PNP classes: pnp2, pnp5 and
        pnp10.

        The devices have emitter sizes hard-wired to 2x2, 5x5 and 10x10.

        The base PNP class is also used to build bandgap cells. These
        bandgap cells are fixed cells, bandgap3x3pnp10 and bandgap4x3pnp10,
        and bandgap5x5pnp5, based upon fixed size arrays of pnp10 and pnp5
        cells.  Bandgap cells bandgap3x3, bandgap4x3 and bandgap5x5 with
        user specified emitter sizes are also provided.

fastMosfet.py:
        Builds single row MOS transistor PyCells. Fast means fast pcell
        evaluation.  This PyCell is restricted to using authoring techniques
        applicable for fast pcell evaluation.

techUtils.py:
        Utility methods for accessing technology information.

------------------------------------------------------------------------
IV.  PyCell Naming Conventions
------------------------------------------------------------------------
A. MOSFET naming conventions
    Thin  oxide PMOS devices:  Pmos, Pmos2, Pmos3
    Thin  oxide NMOS devices:  Nmos, Nmos2, Nmos3

    Thick oxide PMOS devices:  PmosH, PmosH2, PmosH3
    Thick oxide NMOS devices:  NmosH, NmosH2, NmosH3

    Differential device types: <device_name>DiffPair
        PmosDiffPair, PmosHDiffPair, PmosDiffPair1, PmosHDiffPair1
        NmosDiffPair, NmosHDiffPair, NmosDiffPair1, NmosHDiffPair1



B. Resistor naming conventions
    <resistorType> <resistorMaterial>  {"Res" | "ResPair"}
    
    There are both poly and diffusion resistors, silicided and
    unsilicided.  There are 8 resistors named:
        SilNPolyRes
        SilPPolyRes
        SilNDiffRes
        SilPDiffRes

        unSilNPolyRes
        unSilPPolyRes
        unSilNDiffRes
        unSilPDiffRes
    
    Similarly, there are 8 resistor pairs named:
        SilNPolyResPair
        SilPPolyResPair
        SilNDiffResPair
        SilPDiffResPair

        unSilNPolyResPair
        unSilPPolyResPair
        unSilNDiffResPair
        unSilPDiffResPair



C. Inductor naming conventions
    Single PyCell named SpiralInductor



D. CombCapacitor naming conventions
    Single PyCell named CombCapacitor



E. PNP and Bandgap naming conventions
    pnp: CMOS substrate PNP bipolar transistor
        pnp2  -   2x2 emitter
        pnp5  -   5x5 emitter
        pnp10 - 10x10 emitter

    bandgap: array of bipolar transistors with 2 or 3 emitters
        bandgap3x3pnp10 - 3x3 array with 10x10 emitter
        bandgap4x3pnp10 - 4x3 array with 10x10 emitter
        bandgap5x5pnp5  - 5x5 array with  5x5  emitter
        bandgap3x3 - 3x3 array with user-defined emitter size
        bandgap4x3 - 4x3 array with user-defined emitter size
        bandgap5x5 - 5x5 array with user-defined emitter size



F. Fast MOSFET naming conventions
    Thin oxide PMOS device:  FastPmos
    Thin oxide NMOS device:  FastNmos

------------------------------------------------------------------------
V.   Description of PyCell Parameters
------------------------------------------------------------------------
A. MOSFET PyCells

Parameter                    Type              Default Value
-------------------------------------------------------------------------
wf                           float             minWidth, no maximum
    Width per finger

lf                           float             minLength, no maximum
    Length per finger

fr                           int               1
    Fingers per row

rw                           int               1
    Rows

diffContactCov               float             1.0
    Fraction of contact coverage over diffusion

diffLeftStyle                string            ContactEdge1
    Left diffusion contact style, for abutment, dummies, etc.

diffRightStyle               string            ContactEdge1
    Right diffusion contact style, for abutment, dummies, etc.

cgSpacingAdd                 float             0.0
    Additional contact-to-gate spacing

wireWidthAdd                 float             0.0
    Additional wire width connecting source/drain contacts

leftDiffAdd                  float             0.0
    Additional left diffusion extension beyond contact

rightDiffAdd                 float             0.0
    Additional right diffusion extension beyond contact

guardRing                    string            (empty string)
    Specify sides of integrated guard ring

ruleset                      string            construction
    Specify which set of rules in the technology file to use

Notes:
    Width specified per finger, not total width.



B. Resistor and ResistorPair PyCells

Parameter                    Type              Default Value
-------------------------------------------------------------------------
wf                           float             minWidth, no maximum
    Width per finger

lf                           float             minLength, no maximum
    Length per finger

fr                           int               1
    Fingers per row

rw                           int               1
    Rows

lcontact                     float             minLength, no maximum
    Contact length

wbar                         float             minWidth, no maximum
    Width of bars

connect                      string            series
    Whether fingers are connected in series or parallel

dummies                      boolean           False
    Whether dummy fingers are included

ruleset                      string            construction
    Specify which set of rules in the technology file to use

Notes:
    Width specified per finger, not total width.

    Length per finger measures actual resistive material, and
    does not include length needed for contacts.

    When requested, dummies are generated at ends of the row.
    Dummies are unconnected.



C. SpiralInductor PyCell

Parameter                    Type              Default Value
-------------------------------------------------------------------------
shape                        string            octagon
    Shape of the inductor

topLayer                     int               4
    Top metal layer

bottomLayer                  int               3
    Bottom metal layer

width                        float             10 * minWidth(topLayer)
    Width of metal winding

space                        float             4 * minSpace(layer)
    Spacing between metal winding

outerDiam                    float             10 * ( width + space)
    Outer diameter

turns                        float             1.0
    Number of turns

useViaFill                   boolean           False
    Use via fill to connect multiple metal layers.

fillToMinDiam                boolean           False
    Override specification of turns; fill to minimum inner diameter.

ruleset                      string            construction
    Specify which set of rules in the technology file to use
 


D. CombCapacitor PyCell

Parameter                    Type              Default Value
-------------------------------------------------------------------------
wf                           float             minWidth, no maximum
    Width per finger

lf                           float             minLength, no maximum
    Length per finger

nf                           int               4
    Number of fingers for terminal2.

topLayer (top layer)         int               5
    Top metal layer

bottomLayer (bottom layer)   int               1
    Bottom metal layer

bottomShield                 boolean           True
    Whether to generate a bottom metal shield.

dummies                      boolean           True
    Whether dummy fingers are included

ruleset                      string            construction
    Specify which set of rules in the technology file to use

Notes:
    When requested, dummies are generated at all sites.
 


E. PNP PyCells

Parameter                    Type              Default Value
-------------------------------------------------------------------------
fr                           int               1
    Fingers per row

rw                           int               1
    Rows

ruleset                      string            construction
    Specify which set of rules in the technology file to use



F. Bandgap PyCells

Parameter                    Type              Default Value
-------------------------------------------------------------------------
ruleset                      string            construction
    Specify which set of rules in the technology file to use
we                           float             2.0
    Width of emitter for Bandgap cells with user-defined emitter sizes
he                           float             2.0
    Height of emitter for Bandgap cells with user-defined emitter sizes



G. GuardRing PyCells

Parameter                    Type              Default Value
-------------------------------------------------------------------------
width                        float             minWidth( diffusion)

height                       float             minWidth( diffusion)

sides                        string            top,bottom,left,right

ruleset                      string            construction
    Specify which set of rules in the technology file to use



H. Fast MOSFET PyCells
   Parameter with same name should be same as MOSFET PyCells.
   Parameter differences are intended to demonstrate the fast evaluation
   techniques.

Parameter                    Type              Default Value
-------------------------------------------------------------------------
wf                           float             minWidth
    Width per finger

lf                           float             minLength
    Length per finger

fr                           int               1
    Number of fingers

diffLeftStyle                string            ContactEdge
    Left diffusion contact style, for abutment usage. Must be 'ContactEdge',
    'ContactEdgeAbut', 'DiffAbut', 'DiffEdgeAbut', 'DiffHalf'.

diffRightStyle               string            ContactEdge
    Right diffusion contact style, for abutment usage. Choices are same as
    diffLeftStyle.

leftCont                     boolean           True
    Whether left source/drain(SD) contact should be connected to metal1

rightCont                    boolean           True
    Whether right SD contact should be connected to metal1

centerCont                   boolean           True
    Whether center SD contact's should be connected to metal1

routeSrc                     string            Bottom
    Specify routing direction of source contacts. Must be 'None', 'Top',
    or 'Bottom'.

routeDrn                     string            Top
    Specify routing direction of drain contacts. Choices are same as routeSrc.

routeGate                    string            Both
    Specify routing direction(s) of gate fingers. Must be 'None', 'Top',
    'Bottom', or 'Both'.

largeDrn                     boolean           False
    Whether drain should be on outside instead of source on outside

leftDummy                    boolean           False
    Whether left dummy finger should be generated

rightDummy                   boolean           False
    Whether right dummy finger should be generated

leftTap                      string            None
    Whether left well tap contact should be generated. Must be 'None' or
    'Detached'.

rightTap                     string            None
    Whether right well tap contact should be generated. Choices are same
    as leftTap.

gateSpacingAdd               float             0
    Increase gate to gate spacing by value

cgSpacingAdd                 float             0
    Increase (all) gate to contact cut by value

leftDiffAdd                  float             0
    Increase left diffusion side by value

rightDiffAdd                 float             0
    Increase right diffusion side by value

leftCgSpacingAdd             float             0
    Increase leftmost contact cut to leftmost gate by value

rightCgSpacingAdd            float             0
    Increase rightmost contact cut to rightmost gate by value

------------------------------------------------------------------------
VI.  Known Problems and Limitations
------------------------------------------------------------------------

A.  The SpiralInductor PyCell may generate design rule errors for
    the circular shaped inductor, if "free angle" geometries are not
    allowed by the process design rules.  This is unavoidable.  To
    approximate a circular shape, it is necessary to use some shapes
    which are neither orthogonal nor lie on a 45 degree angle.

    Such design rule errors should either be ignored, or waived.
    Alternatively, other inductor shapes, such as rectangle or
    octagon, should be used instead.

# end
