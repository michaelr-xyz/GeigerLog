#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gweb_radworld.py - GeigerLog support to update RadWorldMap (GMCMAP)

include in programs with:
    include gweb_radworld
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


def setupRadWorldMap():
    """Setup Radiation World Map properties"""

    defname = "setupRadWorldMap: "
    dprint(defname)
    setIndent(1)

    # set properties dialog
    retval = setRadWorldMapProperties()

    if retval == 0:
        msg = "Cancelled, properties unchanged"

    else:
        fprint(header("Radiation World Maps Properties"))
        fprint("Activation:",                   "{}"    .format("Yes" if g.RWMmapActivation else "No"))
        fprint("Map Update Cycle:",             "{} min".format(g.RWMmapUpdateCycle))
        fprint("Selected Variable Stdrd Map:",  "{}"    .format(g.RWMmapStdVarSelected))
        fprint("Selected Variable Radon Map:",  "{}"    .format(g.RWMmapRadVarSelected))

        if g.RWMmapActivation:
            # if g.RWMmapLastUpdate == 0: msg = "Yes - will update after completion of next logging cycle"
            if g.RWMmapLastUpdate == 0: msg = "Yes"
            else:                       msg = "No - will wait for expiry of Map Update Cycle"
        else:
            msg = "N/A (Is not activated)"
        fprint("Map Update ASAP:",              "{}"    .format(msg))

        msg = "ok, new settings: Activation:{}, UpdateCycle:{} min, Variable:{}, Update Now:{}".format(
                    g.RWMmapActivation,
                    g.RWMmapUpdateCycle,
                    g.RWMmapStdVarSelected,
                    "No" if g.RWMmapLastUpdate != 0 else "Yes",
                )

        # set icons
        if g.RWMmapActivation:     icon = 'icon_world_v2.png'
        else:                      icon = 'icon_world_v2_inactive.png'
        g.exgg.GMCmapAction.setIcon(QIcon(QPixmap(os.path.join(g.resDir, icon))))

    dprint(defname + msg)
    setIndent(0)


def setRadWorldMapProperties():
    """Set activation and cycle time"""

    defname = "setRadWorldMapProperties: "

# Activation
    lmean = QLabel("Activate Updates")
    lmean.setMinimumWidth(200)

    r01=QRadioButton("Yes")
    r02=QRadioButton("No")
    r01.setToolTip("Check 'Yes' to send Updates to Radiation World Map in regular intervals")
    r02.setToolTip("Check 'No' to never send Updates to Radiation World Map")
    if g.RWMmapActivation:
        r01.setChecked(True)
        r02.setChecked(False)
    else:
        r01.setChecked(False)
        r02.setChecked(True)
    powergroup = QButtonGroup()
    powergroup.addButton(r01)
    powergroup.addButton(r02)
    hbox0=QHBoxLayout()
    hbox0.addWidget(r01)
    hbox0.addWidget(r02)
    hbox0.addStretch()

# Map Update Cycle
    lctime = QLabel("Map Update Cycle Time [minutes]\n(at least 1 min)")
    ctime  = QLineEdit()
    # ctime.setToolTip('Enter X to update Radiation World Map every X minutes;\nCPM averaged over this period will be used for CPM and ACPM')
    # ctime.setToolTip('Enter X to update Radiation World Map every X minutes;\nThe variable selected for Standard Map will be averaged\nover this period to be used for CPM and ACPM')
    ctime.setToolTip('Enter X to update both Radiation World Maps every X minutes')
    ctime.setText(f"{g.RWMmapUpdateCycle:0.5g}")


# CLASSIC MAP  The selector for variable-to-use for update of CLASSIC CPM map
    # ydprint(defname, "RWMmapStdVarSelected: ",  g.RWMmapStdVarSelected)
    lSvars = QLabel("Select Variable for <b>Standard</b> Map Update &nbsp; ")
    Svars  = QListWidget()
    # Svars.setToolTip('Select the variable you want to use for the Standard map update')

    Svars.setToolTip('Select the variable you want to use for the Standard map update; this\nvariable will be averaged over the Map Update Cycle Time for use as ACPM')
    Svars.setMinimumHeight(230)

    Sitem = QListWidgetItem("None")
    Sitem.setToolTip("No variable selected - make your selection")
    Svars.addItem(Sitem)
    Svars.setCurrentItem(Sitem)
    for vname in g.VarsCopy:
        Sitem = QListWidgetItem(vname)
        Svars.addItem(Sitem)
        if g.varsSetForLogNew[vname] == False:  Sitem.setFlags(Qt.ItemFlag.NoItemFlags)
        if g.RWMmapStdVarSelected == vname:     Svars.setCurrentItem(Sitem)


# RADON MAP  The selector for variable-to-use for update of RADON CPM map
    # ydprint(defname, "RWMmapRadVarSelected: ",  g.RWMmapRadVarSelected)
    lRvars = QLabel("Select Variable for <b>Radon</b> Map Update")
    Rvars  = QListWidget()
    Rvars.setToolTip('Select the variable you want to use for the Radon map update')
    Rvars.setMinimumHeight(230)

    Ritem = QListWidgetItem("None")
    Ritem.setToolTip("No variable selected - make your selection")
    Rvars.addItem(Ritem)
    Rvars.setCurrentItem(Ritem)
    for vname in g.VarsCopy:
        Ritem = QListWidgetItem(vname)
        Rvars.addItem(Ritem)
        if g.varsSetForLogNew[vname] == False:  Ritem.setFlags(Qt.ItemFlag.NoItemFlags)
        if g.RWMmapRadVarSelected == vname:     Rvars.setCurrentItem(Ritem)


# The checkbox to set immediate update
    lckbox = QLabel("Do First Update ASAP\nNOT recommended, unless there are \nalready enough data collected")
    ckbox  = QCheckBox()
    ckbox.setToolTip  ("A first update will be done after at least one log cycle is completed (not recommended)")
    ckbox.setChecked  (False)
    ckbox.setEnabled  (True)
    ckbox.setTristate (False)


# fill the grid
    graphOptions=QGridLayout()
    graphOptions.addWidget(lmean,          0, 0)
    graphOptions.addLayout(hbox0,          0, 1)

    graphOptions.addWidget(lctime,         1, 0)
    graphOptions.addWidget(ctime,          1, 1)

    graphOptions.addWidget(lSvars,         2, 0)
    graphOptions.addWidget(Svars,          2, 1)

    graphOptions.addWidget(lRvars,         3, 0)
    graphOptions.addWidget(Rvars,          3, 1)

    graphOptions.addWidget(lckbox,         4, 0)
    graphOptions.addWidget(ckbox,          4, 1)


# run the dialog
    d = QDialog() # set parent to None to popup in center of screen
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set up Radiation World Maps")
    d.setWindowModality(Qt.WindowModality.NonModal)

    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: d.done(100))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    # print("retval:", retval)

    if retval == 100:
        # Activation
        if r01.isChecked(): g.RWMmapActivation = True
        else:               g.RWMmapActivation = False

        # Cycletime
        uctime = ctime.text().replace(",", ".")                 # replace any comma with dot
        try:    dt = max(round(abs(float(uctime)), 2), 0.1)
        except: dt = g.RWMmapUpdateCycle
        g.RWMmapUpdateCycle = dt

        # Standard map Variable
        text  = str(Svars.currentItem().text())
        if text == "None": text = "No variable selected"        # no selection was made
        g.RWMmapStdVarSelected = text
        dprint("Variable selection Standard map: ", text)

        # RADON map Variable
        text  = str(Rvars.currentItem().text())
        if text == "None": text = "No variable selected"        # no selection was made
        g.RWMmapRadVarSelected = text
        dprint("Variable selection Radon map: ", text)

        # update-ASAP
        if ckbox.isChecked():   g.RWMmapLastUpdate = 0
        else:                   g.RWMmapLastUpdate = time.time()

    return retval


def getRadWorldMapURL():
    """assemble the data into the url and return url and data msg"""

    defname = "getRadWorldMapURL: "

    if   g.RWMmapStdVarSelected in ("CPM",    "CPS"):         sens = g.Sensitivity[0]
    elif g.RWMmapStdVarSelected in ("CPM1st", "CPS1st"):      sens = g.Sensitivity[1]
    elif g.RWMmapStdVarSelected in ("CPM2nd", "CPS2nd"):      sens = g.Sensitivity[2]
    elif g.RWMmapStdVarSelected in ("CPM3rd", "CPS3rd"):      sens = g.Sensitivity[3]
    else:                                                     sens = g.NAN

    DeltaT  = g.RWMmapUpdateCycle   # DeltaT in minutes, RWMmapUpdateCycle in min

    # mdprint(defname + "g.RWMmapStdVarSelected: {},  DeltaT: {} min".format(g.RWMmapStdVarSelected,    DeltaT)) # classic
    # mdprint(defname + "g.RWMmapRadVarSelected: {},  DeltaT: {} min".format(g.RWMmapRadVarSelected, DeltaT)) # radon

    cpmdata = []
    pcidata = []

# classic
    if g.RWMmapStdVarSelected != "No variable selected":
        try:
            timedata, cpmdata, deltaTime  = getTimeCourseInLimits(g.RWMmapStdVarSelected, DeltaT)
            # mdprint(defname + "cpmdata[:10] ... [-10:]: ", cpmdata[:10], "...", cpmdata[-10:])
        except Exception as e:
            srcinfo = "No proper data available"
            exceptPrint(e, defname + srcinfo)

# radon
    if g.RWMmapRadVarSelected != "No variable selected":
        try:
            timedata, pcidata, deltaTime  = getTimeCourseInLimits(g.RWMmapRadVarSelected, DeltaT)
            # mdprint(defname + "pcidata[:10] ... [-10:]: ", pcidata[:10], "...", pcidata[-10:])
        except Exception as e:
            srcinfo = "No proper data available"
            exceptPrint(e, defname + srcinfo)

# collate
    data         = {}
    data['AID']  = g.gmcmapUserID
    data['GID']  = g.gmcmapCounterID
    if len(cpmdata) > 0:
        cpm_mean     = np.nanmean(cpmdata)
        data['CPM']  = "{:3.1f}".format(cpm_mean)
        data['ACPM'] = data['CPM']
        data['uSV']  = "{:3.3f}".format(cpm_mean / sens)

    if len(pcidata) > 0:
        data['pCi']  = "{:3.2f}".format(np.nanmean(pcidata))

    if len(data) > 2:
        baseURL      = g.gmcmapWebsite + "/" + g.gmcmapURL
        gmcmapURL    = "http://" + baseURL + "?" + urllib.parse.urlencode(data)                         # MUST use 'http://' in front!
    else:
        gmcmapURL    = "No data"

    return gmcmapURL


def updateRadWorldMap():
    """get a new data set and send as message to GMCmap"""

    defname = "updateRadWorldMap: "

    dprint(defname)
    setIndent(1)

    gmcmapURL = getRadWorldMapURL()                                 # gmcmapURL has the url with data as GET
    dprint(defname, "URL:  " + gmcmapURL)

    fprint(header("Update Radiation World Maps"))
    if gmcmapURL != "No data":
        try:
            fprint(f"{stime()}  Server Call with: {gmcmapURL}")
            with urllib.request.urlopen(gmcmapURL) as response:
                answer = response.read()
            mdprint(defname + "RAW Server Response: ", answer)

        except Exception as e:
            answer  = b"Bad URL"
            srcinfo = "Bad URL: " + gmcmapURL
            exceptPrint("pushToWeb: " + str(e), srcinfo)

        # remove the HTML code from answer
        cleanAnswer = "{}".format((re.sub('<[^<]+?>', '', answer.decode('UTF-8', errors='replace'))).strip())
        dprint("Server Response cleaned: ", cleanAnswer)
        msg1        = f"Map Updating got server response: '{cleanAnswer}' "
        msg2        = f"on URL: {gmcmapURL}"

        # Evaluate server answer
        if b"ERR0" in answer:
            # Success
            #   b"ERR0" in answer     => Ok
            g.exgg.addMsgToLog("Success", msg1 + msg2)
            smsg = "Server Response: OK"
            fprint(f"{stime()}  {smsg}")
            mdprint(defname, smsg)

        else:
            # Failure
            #   b"ERR1" in answer     => wrong userid
            #   b"ERR2" in answer     => wrong counterid
            #   b"Bad URL" in answer  => misformed URL => typo in GeigerLog config?
            #   other                 => other errors, including ERR3 (when wrong url was used)
            efprint (f"{stime()} FAILURE")
            qefprint(msg1)
            qefprint(msg2)
            mdprint(defname, msg1 + msg2)
            g.exgg.addMsgToLog("FAILURE", msg1 + msg2)
    else:
        efprint("{} FAILURE - {}".format(stime(), gmcmapURL) )
        g.exgg.addMsgToLog("FAILURE", "Updating Radiation World Map: " + gmcmapURL)

    setIndent(0)

