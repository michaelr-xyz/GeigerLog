#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
gdev_i2c.py - I2C support for dongles ELV, ISS, IOW and mutiple sensors
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

### dongles
import gdev_i2c_Dngl_ELV            as ELV      # I2C dongle ELV
import gdev_i2c_Dngl_ISS            as ISS      # I2C dongle ISS
import gdev_i2c_Dngl_IOW            as IOW      # I2C dongle IOW24
# import gdev_i2c_Dngl_FTD          as FTD      # I2C dongle FT232H - not good! do not use

### sensors
import gdev_i2c_Sensor_LM75         as LM75     # I2C sensor
import gdev_i2c_Sensor_BME280       as BME280   # I2C sensor
import gdev_i2c_Sensor_SCD30        as SCD30    # I2C sensor
import gdev_i2c_Sensor_SCD41        as SCD41    # I2C sensor
import gdev_i2c_Sensor_TSL2591      as TSL2591  # I2C sensor
import gdev_i2c_Sensor_BH1750       as BH1750   # I2C sensor
import gdev_i2c_Sensor_GDK101       as GDK101   # I2C sensor
import gdev_i2c_Sensor_LTR390       as LTR390   # I2C sensor
import gdev_i2c_Sensor_INA228       as INA228   # I2C sensor


Sensors = {
        ### Sensor-         I2C      Activation  Connection Class   Var-    Vars                                  Burn-in
        ### Name            Address  Status      Status     handle  count   list                                  cycles
        ###                 0        1           2          3       4       5                                     6
           "LM75"       : [ None,    False,      False,     None,   1,      ["CPM2nd"                             ],  1 ],
           "BME280"     : [ None,    False,      False,     None,   3,      ["Temp",   "Press",  "Humid"          ],  3 ],
           "SCD30"      : [ None,    False,      False,     None,   3,      ["CPM2nd", "CPM3rd", "CPS3rd"         ],  1 ],
           "SCD41"      : [ None,    False,      False,     None,   3,      ["CPM",    "CPM1st", "CPS1st"         ],  1 ],
           "TSL2591"    : [ None,    False,      False,     None,   2,      ["CPM3rd", "CPS3rd"                   ],  2 ],
           "BH1750"     : [ None,    False,      False,     None,   1,      ["CPM3rd"                             ],  1 ],
           "GDK101"     : [ None,    False,      False,     None,   3,      ["CPM3rd", "CPS3rd", "Temp"           ],  1 ],
           "LTR390"     : [ None,    False,      False,     None,   2,      ["CPM3rd", "CPS3rd"                   ],  1 ],
           "INA228"     : [ None,    False,      False,     None,   4,      ["Temp",   "Press",  "Humid", "Xtra"  ],  1 ],
          }
g.Sensors = Sensors
# irdprint("outside", f"g.Sensors: {g.Sensors}")

### reverse lookup sensors: addr --> name
g.I2CSensorDict[0x10] = "BMM150"
g.I2CSensorDict[0x11] = "BMM150"
g.I2CSensorDict[0x12] = "BMM150"
g.I2CSensorDict[0x13] = "BMM150"

g.I2CSensorDict[0x18] = "GDK101"
g.I2CSensorDict[0x19] = "GDK101"
g.I2CSensorDict[0x1A] = "GDK101"
g.I2CSensorDict[0x1B] = "GDK101"

g.I2CSensorDict[0x23] = "BH1750"
g.I2CSensorDict[0x5C] = "BH1750"

g.I2CSensorDict[0x29] = "TSL2591"

g.I2CSensorDict[0x40] = "INA228"
g.I2CSensorDict[0x41] = "INA228"
g.I2CSensorDict[0x42] = "INA228"
g.I2CSensorDict[0x43] = "INA228"
g.I2CSensorDict[0x44] = "INA228"
g.I2CSensorDict[0x45] = "INA228"
g.I2CSensorDict[0x46] = "INA228"
g.I2CSensorDict[0x47] = "INA228"
# .... and more up to 0x4F (16 possible adresses)

g.I2CSensorDict[0x48] = "LM75"

g.I2CSensorDict[0x53] = "LTR390"

g.I2CSensorDict[0x61] = "SCD30"

g.I2CSensorDict[0x62] = "SCD41"

g.I2CSensorDict[0x76] = "BME280"
g.I2CSensorDict[0x77] = "BME280"


### Index into Sensors dict
I2CADDR    = 0
I2CACTIV   = 1
I2CCONN    = 2
I2CHNDL    = 3
I2CVCNT    = 4
I2CVARS    = 5
I2CRUNS    = 6



def initI2C():
    """Init the dongle with the sensors"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    g.Devices["I2C"][g.CONN]  = False
    g.Devices["I2C"][g.DNAME] = "I2C Sensors"

    # init the dongle
    if   g.I2CDongleName == "ISS":  g.I2CDongle = ISS.ISSdongle()
    elif g.I2CDongleName == "ELV":  g.I2CDongle = ELV.ELVdongle()
    elif g.I2CDongleName == "IOW":  g.I2CDongle = IOW.IOWdongle()
    # elif g.I2CDongleName == "FTD":  g.I2CDongle = FTD.FTDdongle() # not worth using

    success, msg  = g.I2CDongle.DongleInit()
    if success:
        fprint(msg)
        dprint(msg)
        dprint()
    else:
        setIndent(0)
        return f"Failure initializing dongle '{g.I2CDongle.name}': {msg}\n"

    ####### sensor-init loop ######################
    dprint(f"Sensor Init: Scanning all sensors")
    setIndent(1)
    SensorCount = 0
    for sensor in Sensors:
        if not g.I2CSensor[sensor][0]:
            dprint(defname, f"sensor: {sensor:8s} - not activated")
            continue

        Sensors[sensor][I2CACTIV]   = g.I2CSensor[sensor] [0]  # gglobs: I2CSensor["LM75"] = [False, 0x48, None]
        Sensors[sensor][I2CADDR]    = g.I2CSensor[sensor] [1]
        Sensors[sensor][I2CVARS]    = g.I2CSensor[sensor] [2]

        address = Sensors[sensor][I2CADDR]
        cdprint(defname, f"sensor: {sensor:8s} - is activated for address: 0x{address:02X} ({address})")

        if   sensor == "LM75"    : Sensors[sensor][I2CHNDL] = LM75    .SensorLM75     (address)
        elif sensor == "BME280"  : Sensors[sensor][I2CHNDL] = BME280  .SensorBME280   (address)
        elif sensor == "SCD30"   : Sensors[sensor][I2CHNDL] = SCD30   .SensorSCD30    (address)
        elif sensor == "SCD41"   : Sensors[sensor][I2CHNDL] = SCD41   .SensorSCD41    (address)
        elif sensor == "TSL2591" : Sensors[sensor][I2CHNDL] = TSL2591 .SensorTSL2591  (address)
        elif sensor == "BH1750"  : Sensors[sensor][I2CHNDL] = BH1750  .SensorBH1750   (address)
        elif sensor == "GDK101"  : Sensors[sensor][I2CHNDL] = GDK101  .SensorGDK101   (address)
        elif sensor == "LTR390"  : Sensors[sensor][I2CHNDL] = LTR390  .SensorLTR390   (address)
        elif sensor == "INA228"  : Sensors[sensor][I2CHNDL] = INA228  .SensorINA228   (address)

        response = Sensors[sensor][I2CHNDL].SensorInit()
        if response is None:
            edprint(defname, "response: ", response)
            continue

        if response[0]:
            SensorCount += 1
            Sensors[sensor][I2CCONN] = True
            msg = response[1]
            # fprint(msg)
            # dprint(msg)

        else:
            msg = "Failure initializing sensor {} on dongle {} with message:\n{}".format(sensor, g.I2CDongle.name, response[1])
            Sensors[sensor][I2CCONN] = False
            efprint(msg)

    setIndent(0)
    ###### end sensor-init loop ######################

    if SensorCount == 0:
        returnmsg = "No Sensors found"

    else:
        returnmsg = ""
        fprint(f"I2C device has got {SensorCount} sensor(s)")
        g.Devices["I2C"][g.CONN]  = True

        SensorsBurnIn()

        # set the variables
        allvars = []
        for sensor in Sensors:
            if not Sensors[sensor][I2CACTIV]: continue
            temp = []
            for vname in Sensors[sensor][I2CVARS]:
                # cdprint(defname, f"sensor: {sensor:8s}  vname: {vname}")
                cvname = correctVariableCaps(vname)

                if cvname != "" and cvname != "auto":   temp.append(cvname)
                else:                                   temp.append("Unused")  # need a temporary place holder for a value from the sensor
            Sensors[sensor][I2CVARS] = temp[ : Sensors[sensor][I2CVCNT]]
            allvars += Sensors[sensor][I2CVARS]

        allvars = [s for s in allvars if s != 'Unused'] # remove all "Unused"
        g.I2CVariables = ", ".join(allvars)
        g.I2CVariables = setLoggableVariables("I2C", g.I2CVariables)

        # get all info + extended info
        getInfoI2C(extended=True, FirstCall=True)

    setIndent(0)
    return returnmsg


def SensorsBurnIn():
    """First Values may be invalid"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint()
    cdprint(defname)
    setIndent(1)

    for sensor in Sensors:
        # rdprint(defname + "sensor: ", sensor)
        if Sensors[sensor][I2CCONN]:                        # use connected sensors only
            # make measurements to discard
            cycles = Sensors[sensor][I2CRUNS]
            for i in range(0, cycles):
                cdprint(defname, f"Sensor: {sensor:8s} cycle: {i + 1} of {cycles}")
                Sensors[sensor][I2CHNDL].SensorgetValues()  # get and discard values
                time.sleep(0.05)
    setIndent(0)


def terminateI2C():
    """shutting down thread, closing ELV, resetting connection flag"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    dprint(defname + g.I2CDongle.DongleTerminate())    # does nothing but closing the port

    g.Devices["I2C"][g.CONN]  = False

    dprint(defname + "Terminated")
    setIndent(0)


def resetI2C():
    """Reset the ELV dongle and sensors"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname + "---------------------------------------------------")
    setIndent(1)

    setBusyCursor()

    fprint(header("Resetting I2C System"))
    fprint("In progress ...")
    QtUpdate()

    # reset the dongle
    try:
        msg = g.I2CDongle.DongleReset()                               # takes >=3 sec on ELV
        dprint(defname + "Dongle: {} - {}".format(g.I2CDongle.name, msg))
    except Exception as e:
        exceptPrint(e, defname + "DongleReset failed")

    # reset all sensors
    for sensor in Sensors:
        # cdprint(defname + "sensor: ", sensor)
        if Sensors[sensor][I2CCONN]:
            try:
                msg = Sensors[sensor][I2CHNDL].SensorReset()
                dprint(defname + "Sensor: {} - {}".format(sensor, msg))
            except Exception as e:
                exceptPrint(e, defname + "Resetting sensor {} failed".format(sensor))

    SensorsBurnIn()

    fprint("I2C System Reset done")
    dprint(defname + "Done")

    setNormalCursor()
    setIndent(0)


def getInfoI2C(extended=False, FirstCall=False):
    """Calls the devices via serial on FirstCall=True only; otherwise conflicting double
    access to serial port may result"""

    defname = gd(sys._getframe().f_code.co_name)

    if   g.I2CDongleName == "ISS":
        info = "Configured Connection:        Port: {} \n".format(g.I2Cusbport)

    elif g.I2CDongleName == "ELV":

        info = "Configured Connection:        Port: {} Baud: {} Timeouts[s]: R:{} W:{}\n".format\
                                    (
                                        g.I2Cusbport,
                                        g.I2Cbaudrate,
                                        g.I2CtimeoutR,
                                        g.I2CtimeoutW
                                    )

    elif g.I2CDongleName == "IOW" or g.I2CDongleName == "FTD":    # FTD is NOT in use
        info = "Configured Connection:        Native USB connection\n"

    if not g.Devices["I2C"][g.CONN]: return info + "<red>Device is not connected</red>"

    infoExt = info

    if FirstCall:
        # on first call query all devices and sensors and assemble info

        # Dongle
        # cdprint(defname + "dongle: ----------------------------------------------", g.I2CDongle.name)
        # cdprint(defname, f"dongle: {g.I2CDongle.name}  {info}")

        DongleInfo     = g.I2CDongle.DongleGetInfo()  # on ELV like: ['Last Adress:0xED', 'Baudrate:115200 bit/s', 'I2C-Clock:99632 Hz', 'Y00', 'Y10', 'Y20', 'Y30', 'Y40', 'Y50', 'Y60', 'Y70']
        g.Devices["I2C"][g.DNAME] = g.I2CDongle.name  # on ELV like: ['ELV USB-I2C-Interface v1.8 (Cal:5E)'

        info += "{:30s}{}\n" .format("Connected Device:", "Dongle: {}".format(g.I2CDongle.name))
        info += "{:30s}{}\n" .format("Configured Variables:", g.I2CVariables)
        info += "\n"

        infoExt  = info
        infoExt += "Dongle: {}\n".format(g.I2CDongle.name)
        infoExt += "\n".join(DongleInfo)
        infoExt += "\n"
        infoExt += "\n"

        # Sensors
        for sensor in Sensors:
            if Sensors[sensor][I2CCONN]:
                SensorInfo = Sensors[sensor][I2CHNDL].SensorGetInfo()
                # irdprint(defname, f"sensor: {sensor}   SensorInfo: {SensorInfo}")

                vmsg     = " - Variables: " + ", ".join("{}".format(x) for x in g.Sensors[sensor][5]) + "\n"
                msg      = f"{'Sensor: ' + sensor:30s}{SensorInfo[0]:25s}{vmsg}"

                info    += msg
                infoExt += msg #+ "\n"
                for si in SensorInfo[1:]:
                    infoExt += " "*11 + si + "\n"
        info += "\n"
        g.I2CInfo      = info
        g.I2CInfoExt   = infoExt

    else:
        # on 2nd and later calls
        if extended:    info = g.I2CInfoExt
        else:           info = g.I2CInfo

    # Tube sensitivities
    info += getTubeSensitivities(g.I2CVariables)

    cdprint(defname, f"\n{info}  \n{infoExt}")

    return info


def scanI2CBus():
    """scans the I2C bus by writing 0x00 to each address from 0 ... 127"""

    # scan full bus
    # duration: Dongle: ISS: Found a total of 5 I2C device(s) in   50 ms     1.0x
    # duration: Dongle: ELV: Found a total of 5 I2C device(s) in  170 ms     3.4x
    # duration: Dongle: IOW: Found a total of 5 I2C device(s) in 1010 ms    20.2x

    # check single address
    # duration: Dongle: ISS: 0.27 ... 0.39 ms   (avg=0.31 ms)                1.0x
    # duration: Dongle: ELV: 1.04 ... 5.13 ms   (avg=1.22 ms)                3.9x
    # duration: Dongle: IOW: 5.2 ...  8.3  ms   (avg=7.7 ms)                24.8x

    defname = gd(sys._getframe().f_code.co_name)

    g.I2CDongle.DongleScanPrep("Start")    # needed for ELV dongle

    devicecount = 0
    start       = time.time()
    dscan       = defname + "\n" # cumulative scan string
    scanfmt     = "0x{:02X}  "
    scan        = "       0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F"
    fprint(header("Scanning I2C Bus"))
    fprint(scan)
    QtUpdate()
    scan        = scanfmt.format(0) + "-- "

    # addr=0x00 is General Call Address for devices;
    # They may or may not respond; gives no conclusive info, therefore skip it.
    # Multiple other addresses are also not available, but my devices do not
    # seem to respond at those addresses
    # https://www.i2c-bus.org/addressing/general-call-address/
    for addr in range(1, 128):
        if addr % 16  == 0:
            fprint(scan)
            QtUpdate()
            dscan += scan + "\n"
            scan   = scanfmt.format(addr)

        try:
            if g.I2CDongle.DongleAddrIsUsed(addr):
                scan   += "{:02X} ".format(addr)
                devicecount += 1
            else:
                scan   += "-- "
        except Exception as e:
            exceptPrint(e, defname + "Failure with DongleAddrIsUsed")

    duration = time.time() - start
    scan += f"\n\nFound a total of {devicecount} I2C device(s) in {duration:0.2f} sec\n"
    fprint(scan)
    dprint(dscan + scan)

    g.I2CDongle.DongleScanPrep("End")    # needed for ELV dongle


def getValuesI2C(varlist):
    """Read all I2C data"""

    gVstart = time.time()

    defname = gd(sys._getframe().f_code.co_name)
    # cdprint(defname, f"Variables: {varlist}")
    setIndent(1)

    # set sensor values for all vars to NAN
    SensorValues = {}
    for vname in g.VarsCopy:    SensorValues [vname] = g.NAN

    # get the data from the sensors
    for sensor in Sensors:
        if Sensors[sensor][I2CCONN]:
            sval = Sensors[sensor][I2CHNDL].SensorgetValues() # sval is tuple with 1 ... N values
            # irdprint(defname + "sensor: ", sensor, ", value: ", sval)
            for i in range(Sensors[sensor][I2CVCNT]):
                try:                    svname = Sensors[sensor][I2CVARS][i]
                except Exception as e:  svname = None
                # rdprint(defname, "i: {}  sval: {}  svname: {}".format(i, sval, svname))
                if svname is not None: SensorValues[svname] = sval[i]
    # rdprint(defname + "SensorValues: ", SensorValues)

    # scale values and set to alldata
    alldata = {}
    for vname in varlist:
        if vname == "Unused" or vname == "None": continue
        sval         = SensorValues[vname]
        scaled_sval  = round(applyValueFormula(vname, sval, g.ValueScale[vname]), 3)
        alldata.update({vname: scaled_sval})

    gVdur = 1000 * (time.time() - gVstart)

    setIndent(0)
    vprintLoggedValues(defname, varlist, alldata, gVdur)

    return alldata


def forceCalibration():
    """force CO2 calibration on the SCD30 and SCD41 sensor"""

    defname = gd(sys._getframe().f_code.co_name)

    # request the CO2 ref value
    frc = getCO2RefValue()
    if np.isnan(frc): return

    mdprint(defname + "refVal: ", frc)

    if Sensors["SCD30"][I2CHNDL] is not None:
        Sensors["SCD30"][I2CHNDL].SCD30setFRC(frc)
        fprint("Sensor SCD30 is calibrated")
    else:
        efprint("Sensor SCD30 is not available")

    QtUpdate()

    if Sensors["SCD41"][I2CHNDL] is not None:
        Sensors["SCD41"][I2CHNDL].SCD41setFRC(frc)
        fprint("Sensor SCD41 is calibrated")
    else:
        efprint("Sensor SCD41 is not available")

    QtUpdate()

    # set all info + extended info
    getInfoI2C(extended=True, FirstCall=True)


def getCO2RefValue():
    """Enter a value manually"""

    defname = gd(sys._getframe().f_code.co_name)

    # getCO2RefValue should not be callable when logging
    if g.logging:
        g.exgg.showStatusMessage("Cannot change sensor calibration when logging! Stop logging first")
        return

    dprint(defname)
    setIndent(1)

    # Calib Value
    lv1 = QLabel("Enter Reference CO2 [ppm]\n(Not less than 400)")
    lv1.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    v1  = QLineEdit()
    v1.setToolTip("Enter the CO2 calibration value for the SCD41 sensor")
    v1.setText("")

    graphOptions=QGridLayout()
    graphOptions.setContentsMargins(10,10,10,10) # spacing around the graph options

    graphOptions.addWidget(lv1,     0, 0)
    graphOptions.addWidget(v1,      0, 1)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setWindowTitle("Set CO2 Reference Value")
    d.setWindowModality(Qt.WindowModality.WindowModal)
    d.setMinimumWidth(400)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    g.btn = bbox.button(QDialogButtonBox.StandardButton.Ok)
    g.btn.setEnabled(True)

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(graphOptions)
    layoutV.addWidget(bbox)

    retval = d.exec()
    # print("reval:", retval)

    co2ref = g.NAN

    if retval != 1:
        # ESCAPE pressed or Cancel Button
        dprint(defname + "Canceling; no changes made")

    else:
        # OK pressed
        fprint(header("Calibrate CO2 Sensors"))
        QtUpdate()

        v1val = v1.text().strip().replace(",", ".")
        # cdprint("v1.text: ", v1.text(), ", v1val: ", v1val)

        if v1val > "":
            try:
                co2ref = int(float(v1val))
                cdprint("co2ref: ", co2ref, ", v1val: ", v1val)

            except Exception as e:
                msg = "CO2 Reference must be given as a number of at least '400' (ppm); you entered: '{}'".format(v1val)
                exceptPrint(e, msg)
                efprint(msg)
                co2ref = g.NAN

            if co2ref < 400:
                efprint("CO2 Reference value must be at least '400' ppm; you entered: {} ppm".format(v1val))
                co2ref = g.NAN

    setIndent(0)

    return co2ref

