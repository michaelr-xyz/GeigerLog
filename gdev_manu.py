#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
gdev_manu.py - GeigerLog commands to handle manually entering data
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


def initManu():
    """Start the device"""

    defname = "initManu: "

    dprint(defname + "Initializing")
    setIndent(1)

    g.Devices["Manu"][g.DNAME] = "Manual Data Entry"

    # if g.ManuRecordStyle  == "auto": g.ManuRecordStyle  = "Point"                        # choose from: "Point", "Step"
    if g.ManuVariables    == "auto": g.ManuVariables    = "Temp, Press, Humid, Xtra"

    # set variables
    g.ManuVariables = setLoggableVariables("Manu", g.ManuVariables)

    # set all active g.ManuValues to nan
    for vname in g.Devices["Manu"][g.VNAMES]:
        g.ManuValues[vname] = g.NAN

    # device is connected
    g.Devices["Manu"][g.CONN] = True

    setIndent(0)

    return ""  # empty means no errmsg for return


def terminateManu():
    """Stop the Manu"""

    defname ="terminateManu: "

    dprint(defname)
    setIndent(1)

    g.Devices["Manu"][g.CONN]  = False

    dprint(defname, "Terminated")
    setIndent(0)


def getValuesManu(varlist):
    """get the manually entered values; click 'next' to keep dialog open"""

    start = time.time()
    defname = "getValuesManu: "

    alldata = {}
    for vname in varlist:
        alldata[vname] = applyValueFormula(vname, g.ManuValues[vname], g.ValueScale[vname], info=defname)

        # if g.ManuRecordStyle == "Point": g.ManuValues[vname] = g.NAN  # if Style is Point: reset value to NAN after read-out
        g.ManuValues[vname] = g.NAN  # reset value to NAN after read-out

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def setManuValue():
    """Enter a value manually"""


    def fillManuValues():
        msg = ""
        for vname in g.ManuValues:
            # rdprint(defname, "vname: ", vname)
            mval = vnamebox[vname].text().strip().replace(",", ".")
            if mval > "":
                try:    nval = float(mval)
                except: nval = g.NAN
                g.ManuValues[vname] = nval
                msg += "Variable {:6s} :  {:0.9g}\n".format(vname, g.ManuValues[vname])
            else:
                g.ManuValues[vname] = g.NAN
                msg += "Variable {:6s} :  {}     \n".format(vname, "<empty>")

        fprint(header("Manu Device Values"))
        fprint(msg)
        dprint(defname, "\n", msg)
        # ydprint(defname, g.ManuValues)

    defname = "setManuValue: "

    dprint(defname)
    setIndent(1)

    while True:

        fbox = QFormLayout()
        fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        fbox.addRow(QLabel("<span style='font-weight:900;'>Manu Variables</span>"))

        vnamebox = {}
        for vname in g.ManuValues:
            vnamebox.update({vname: QLineEdit()})
            fbox.addRow(QLabel(vname), vnamebox[vname])

        # Dialog box
        d = QDialog()
        d.setWindowIcon(g.iconGeigerLog)
        d.setFont(g.fontstd)
        d.setWindowTitle("Enter Values Manually")
        d.setWindowModality(Qt.WindowModality.WindowModal)
        d.setMinimumWidth(250)

        # Buttons
        bbox = QDialogButtonBox()

        nextButton = QPushButton("Next")
        nextButton.setDefault(True)
        nextButton.setAutoDefault(True)
        nextButton.clicked.connect(lambda: d.done(2))
        bbox.addButton(nextButton, QDialogButtonBox.ButtonRole.ActionRole)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(lambda: d.done(0))
        bbox.addButton(cancelButton, QDialogButtonBox.ButtonRole.ActionRole)

        okButton = QPushButton("Ok")
        okButton.clicked.connect(lambda: d.done(1))
        bbox.addButton(okButton, QDialogButtonBox.ButtonRole.ActionRole)

        layoutV = QVBoxLayout(d)
        layoutV.addLayout(fbox)
        layoutV.addWidget(bbox)

        retval = d.exec()
        #print("reval:", retval)

        if   retval == 0:
            dprint(defname + "Canceling; no changes made")
            break

        elif retval == 1:
            fillManuValues()
            break                 # accept; end while - the only place to break while loop

        elif retval == 2:
            fillManuValues()

    # while loop ends here

    setIndent(0)


def getInfoManu(extended=False):
    """Info on settings of the Manu device"""

    ManuInfo  = "Configured Connection:        GeigerLog PlugIn\n"
    if not g.Devices["Manu"][g.CONN]: return ManuInfo + "<red>Device is not connected</red>"

    ManuInfo += "Connected Device:             {}\n"  .format(g.Devices["Manu"][g.DNAME])
    ManuInfo += "Configured Variables:         {}\n"  .format(g.ManuVariables)
    ManuInfo += getTubeSensitivities(g.ManuVariables)

    if extended:
        ManuInfo += "\n"

    return ManuInfo



# from the geigerlog.cfg:
# not used anymore in config
#
# # MANU RECORD STYLE
# # Determines the treatment of the entered data, Point or Step:
# #
# # Point: A single value is entered. Upon entering a subsequent value, a
# #        straight line will be drawn to connect the two points.
# #        Good for ambient values changing "by itself", like temperature,
# #        sunlight, or CO2.
# #
# # Step:  A value is entered and is reused in all following cycles until
# #        a new value is entered. This results in a horizontal line and
# #        stepwise changes between points.
# #        Good for values which have to be changed intentionally, like
# #        distance of radioactive source from Geiger counter, or applied
# #        anode voltage.
# #
# # Option auto defaults to point
# #
# # Options:        auto | point | step
# # Default       = auto
# ManuRecordStyle = auto
# # ManuRecordStyle = step
