#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
gdev_formula.py - GeigerLog's Formula device allows to use the formula interpreter
                  for data generation
"""

###############################################################################
#    This file is part of GeigerLog.
#
#    GeigerLog is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    GeigerLog is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with GeigerLog.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################

__author__          = "ullix"
__copyright__       = "Copyright 2016 - 2025"
__credits__         = [""]
__license__         = "GPL3"


from gsup_utils   import *


def initFormula():
    """Start the Formula device"""

    defname ="initFormula: "

    dprint(defname)
    setIndent(1)

    g.Devices["Formula"][g.DNAME] = "Formula Device"

    if g.FormulaVariables == "auto": g.FormulaVariables = "CPM3rd, CPS3rd"
    g.FormulaVariables = setLoggableVariables("Formula", g.FormulaVariables)

    g.Devices["Formula"][g.CONN] = True

    setIndent(0)
    return ""       # empty string as errmsg, i.e. there was no error


def terminateFormula():
    """Stop the Formula Device"""

    # defname ="terminateFormula: "
    defname = gd(sys._getframe().f_code.co_name)

    dprint(defname)
    setIndent(1)

    g.Devices["Formula"][g.CONN] = False

    dprint(defname, "Terminated")
    setIndent(0)


def getValuesFormula(varlist):
    """Read all data; return empty dict when not available"""

    start = time.time()
    # defname = "getValuesFormula: "
    defname = gd(sys._getframe().f_code.co_name)

    alldata = {}
    for vname in varlist:
        val = applyValueFormula(vname, g.NAN, g.ValueScale[vname])   # depending on formula applied, this may change NAN values to real values
        alldata[vname] = val
        # irdprint(defname,  str(varlist) + "  ", f"alldata[{vname}]:   {alldata[vname]}")

    duration = 1000 * (time.time() - start)
    vprintLoggedValues(defname, varlist, alldata, duration)

    return alldata


def getInfoFormula(extended = False):
    """Info on the Formula Device"""

    tmp      = "{:30s}{}\n"
    FormulaInfo = tmp.format("Configured Connection:", "GeigerLog PlugIn")

    if not g.Devices["Formula"][g.CONN]: return FormulaInfo + "<red>Device is not connected</red>"

    FormulaInfo += tmp.format("Connected Device:",     g.Devices["Formula"][g.DNAME])
    FormulaInfo += tmp.format("Configured Variables:", g.FormulaVariables)
    FormulaInfo += "\n"
    FormulaInfo += tmp.format(getTubeSensitivities(g.FormulaVariables), "")

    # FormulaInfo += "\n"
    fcount = 0
    FormulaInfo += tmp.format("Value Formulas", "")
    for vname in g.VarsCopy:
        val = g.ValueScale[vname].lower()
        if val !="val" and val != "":
            FormulaInfo += tmp.format("   " + vname, g.ValueScale[vname])
            fcount += 1
    if fcount == 0: FormulaInfo += tmp.format("   None", "")

    fcount = 0
    FormulaInfo += "\n"
    FormulaInfo += tmp.format("Graph Formulas", "")
    for vname in g.VarsCopy:
        val = g.GraphScale[vname].lower()
        if val !="val" and val != "":
            FormulaInfo += tmp.format("   " + vname, g.GraphScale[vname])
            fcount += 1
    if fcount == 0: FormulaInfo += tmp.format("   None", "")

    if extended:
        FormulaInfo += tmp.format("Extended Info:", "")
        FormulaInfo += tmp.format("None", "")
        FormulaInfo += "\n"

    return FormulaInfo

