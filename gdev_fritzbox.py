#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gdev_fritzbox.py -  a utility which gets readings from a FritzBox device.
                    Supported are: 'FritzDect 200' but only via Formula Interpreter.
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

###  Documentation: https://fritzconnection.readthedocs.io/en/1.15.0/index.html

### call Fritzbox with connected FRITZ!DECT 200 Smart Power Plug
#   def FRITZBOX200(type="Power"):
#       # Call formulas:
#       #    FRITZBOX200("POWER")            # for current "Leistung"
#       #    FRITZBOX200("ENERGY")           # for current "Gesamtenergy"
#       #    FRITZBOX200("TEMPERATURE")      # for current "Temperatur"
#       return getFritzboxValues(type)

# ### Devices info
# # get_device_information_list
#     # info = g.FritzBoxHomeConn.device_information()          # deprecated
#     info = g.FritzBoxHomeConn.get_device_information_list()
# print(f"info: {info}")                                        # type(info)=list; when Group defined it is 2 items long even with single device
# for fo in info[0]:  print(f"fo: {fo:25s} : {info[0][fo]}")
# ### result:
# # fo: NewAIN                    : grpA6763B-4186C16AF
# # fo: NewDeviceId               : 900
# # fo: NewFunctionBitMask        : 37504
# # fo: NewFirmwareVersion        : 1.0
# # fo: NewManufacturer           : AVM
# # fo: NewProductName            : Group                         ### Group !!!!!!!!
# # fo: NewDeviceName             : Gruppe Steckdosen
# # fo: NewPresent                : CONNECTED
# # fo: NewMultimeterIsEnabled    : ENABLED
# # fo: NewMultimeterIsValid      : VALID
# # fo: NewMultimeterPower        : 164
# # fo: NewMultimeterEnergy       : 29
# # fo: NewTemperatureIsEnabled   : DISABLED
# # fo: NewTemperatureIsValid     : INVALID
# # fo: NewTemperatureCelsius     : 0
# # fo: NewTemperatureOffset      : 0
# # fo: NewSwitchIsEnabled        : ENABLED
# # fo: NewSwitchIsValid          : VALID
# # fo: NewSwitchState            : ON
# # fo: NewSwitchMode             : MANUAL
# # fo: NewSwitchLock             : True
# # fo: NewHkrIsEnabled           : DISABLED
# # fo: NewHkrIsValid             : INVALID
# # fo: NewHkrIsTemperature       : 0
# # fo: NewHkrSetVentilStatus     : CLOSED
# # fo: NewHkrSetTemperature      : 0
# # fo: NewHkrReduceVentilStatus  : CLOSED
# # fo: NewHkrReduceTemperature   : 0
# # fo: NewHkrComfortVentilStatus : CLOSED
# # fo: NewHkrComfortTemperature  : 0
#
# for f1 in info[1]:  print(f"f1: {f1:25s} : {info[1][f1]}")
# ### result:
# # f1: NewAIN                    : 08761 0162816
# # f1: NewDeviceId               : 20000
# # f1: NewFunctionBitMask        : 35712
# # f1: NewFirmwareVersion        : 04.27
# # f1: NewManufacturer           : AVM
# # f1: NewProductName            : FRITZ!Smart Energy 200              ### Plug !!!!!!!!
# # f1: NewDeviceName             : FRITZ!Smart Energy 200 #1
# # f1: NewPresent                : CONNECTED
# # f1: NewMultimeterIsEnabled    : ENABLED
# # f1: NewMultimeterIsValid      : VALID
# # f1: NewMultimeterPower        : 329
# # f1: NewMultimeterEnergy       : 2470
# # f1: NewTemperatureIsEnabled   : ENABLED
# # f1: NewTemperatureIsValid     : VALID
# # f1: NewTemperatureCelsius     : 305
# # f1: NewTemperatureOffset      : 0
# # f1: NewSwitchIsEnabled        : ENABLED
# # f1: NewSwitchIsValid          : VALID
# # f1: NewSwitchState            : ON
# # f1: NewSwitchMode             : MANUAL
# # f1: NewSwitchLock             : True
# # f1: NewHkrIsEnabled           : DISABLED
# # f1: NewHkrIsValid             : INVALID
# # f1: NewHkrIsTemperature       : 0
# # f1: NewHkrSetVentilStatus     : CLOSED
# # f1: NewHkrSetTemperature      : 0
# # f1: NewHkrReduceVentilStatus  : CLOSED
# # f1: NewHkrReduceTemperature   : 0
# # f1: NewHkrComfortVentilStatus : CLOSED
# # f1: NewHkrComfortTemperature  : 0



__author__              = "ullix"
__copyright__           = "Copyright 2016 - 2025"
__credits__             = [""]
__license__             = "GPL3"

from gsup_utils   import *              # all utilities


def initFritzBox():
    """make the required FritzBox connections"""

    defname = gd(sys._getframe().f_code.co_name)

    if not g.FritzBoxActivation:
        g.FritzBoxInitialized = False
        # irdprint(defname, f"FB not activated")
        return False

    dprint(defname)
    setIndent(1)

    try:
        from fritzconnection.core.fritzconnection   import FritzConnection
        from fritzconnection.lib.fritzhomeauto      import FritzHomeAutomation
    except Exception as e:
        msg = f"Importing FritzBox support modules failed!"
        exceptPrint(e, defname + msg)
        qefprint(msg)
        g.FritzBoxInitialized = False
        return False

    ### Do FritzBox credentials exist?
    if g.FritzBoxIP == "auto"  or g.FritzBoxPassword == "auto":
        irdprint(defname, f"FritzBox Credentials are not defined")      # they are defined in the private file or in cfg
        g.FritzBoxInitialized = False
        setIndent(0)
        return False

    ### make FB Connection
    # irdprint(defname, f"Connecting Fritzbox")
    # fc = FritzConnection(address= g.FritzBoxIP, password= g.FritzBoxPassword, use_cache=False)       # ohne Cache: ca 4600 ms !!!
    fc = FritzConnection(address= g.FritzBoxIP, password= g.FritzBoxPassword, use_cache=True)          # mit Cache:  20 ... 60 ms

    ### FB Home automation
    g.FritzBoxHomeConn = FritzHomeAutomation(fc)                                                       # 0.02 ... 0.03 ms

    g.FritzBoxInitialized = True
    msg = f"FritzBox is initialized"
    gdprint(defname, msg)
    # fprint(header("FritzBox"))
    # fprint(msg)
    QueuefPrint(header("FritzBox"))
    QueuefPrint(msg, color="<green>")

    setIndent(0)

    return True


def getFritzboxValues(type="Power"):
    """return FritzBox FRITZ!Smart Energy 200 values Power, Energy, Temperature  by means of the TR-064 API"""

    defname = gd(sys._getframe().f_code.co_name)

    start = time.time()

    if not g.FritzBoxInitialized:
          msg = f"FritzBox was called, but is NOT initialized!"
          edprint(defname, msg)
          return g.NAN

    ### next is REQUIRED here, otherwise the value never changes!!!
    ### with it, the value changes every 10 sec

    ### create a list of HomeAutomationDevice instances which are switchable:
    ###       g.FritzBoxSwitchDevices = [d for d in g.FritzBoxHomeConn.get_homeautomation_devices() if d.is_switchable]  # 150 ... 280 ms
    ### result:
    ###    switchable devices: [ain: grpA6763B-4186C16AF, AVM - Group, ain: 08761 0162816, AVM - FRITZ!Smart Energy 200]
    ###       ain: grpA6763B-4186C16AF, AVM - Group             ### I did create a "Gruppe Steckdosen", having single entry: FRITZ!Smart Energy 200 #1
    ###       ain: 08761 0162816, AVM - FRITZ!Smart Energy 200]
    ###
    ### create a list of HomeAutomationDevice instances which are of any type:
    g.FritzBoxSwitchDevices = g.FritzBoxHomeConn.get_homeautomation_devices()
    # irdprint(defname, f"dur get_homeautomation_devices: {1000 * (time.time() - start):0.3f} ms")     # 115 ... 310 ms

    value = g.NAN
    for device in g.FritzBoxSwitchDevices:
        # irdprint(f"device: {device}")                                 # device: ain: 08761 0162816, AVM - FRITZ!Smart Energy 200
        if "Smart Energy 200" in str(device):
            # irdprint(f"device: {device}")                             # device: ain: 08761 0162816, AVM - FRITZ!Smart Energy 200

            if   type.startswith("P"):
                power       = device.MultimeterPower    / 100.0         # Watt
                msg = f"Power[W]:        {power:10.2f}   Dur[ms]: {1000 * (time.time() - start):7.3f}"
                value = power
                # break

            elif type.startswith("E"):
                energy      = device.MultimeterEnergy                   # Watt-Hour Wh
                msg = f"Energy[Wh]:      {energy:10.0f}   Dur[ms]: {1000 * (time.time() - start):7.3f}"
                value = energy
                # break

            elif type.startswith("T"):
                temperature = device.TemperatureCelsius /  10.0         # °C
                msg = f"Temperature[°C]: {temperature:10.1f}   Dur[ms]: {1000 * (time.time() - start):7.3f}"
                value = temperature
                # break

            # cdprint(defname, msg)

    # irdprint(defname, f"dur loop devices: {1000 * (time.time() - start):0.3f} ms")       # 0.03 ... 0.08 ms

    return value


def FRITZBOX200(type="Power"):
    """call Fritzbox with connected FRITZ!DECT 200 Smart Power Plug"""

    return getFritzboxValues(type)

