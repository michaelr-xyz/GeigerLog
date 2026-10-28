#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gdev_gemf.py - GeigerLog commands to handle the GQ EMF devices

include in programs with:
    import gdev_gemf
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
__credits__         = []
__license__         = "GPL3"

# device command coding taken from:
# - GQ-RFC1701 GQ EMF Communication Protocol
# - Test Device:  GQ-EMF390v2Re 3.75


from gsup_utils   import *
import gsup_sql                             # database handling (needed for History stuff)


# Data in 256 byte of config
# Zero Calibration: EmfDev: "zero calibration feature has been removed."
# see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10559, Reply#4
cfgKeyLoDefault = {
#
#    key                       Value,     Index width
    "Power"                : [ None,     [0,        1] ],     # // 0x00 Power state (read only, not settable!)
    "Speaker"              : [ None,     [1,        1] ],     # SpeakerOnOff
    "IdleDisplayMode"      : [ None,     [2,        1] ],     #
    "BackLightTOSec"       : [ None,     [3,        1] ],     # timeout in sec
    "IdleTextState"        : [ None,     [4,        1] ],     #
    "SwivelDisplay"        : [ None,     [5,        1] ],     # // 0x05
    "nDisplayContrast"     : [ None,     [6,        1] ],     #
    "nLargeFontMode"       : [ None,     [7,        1] ],     #
    "nLCDBackLightLevel"   : [ None,     [8,        1] ],     #
    "nReverseDisplayMode"  : [ None,     [9,        1] ],     #
    "LARGEFONTMODE"        : [ None,     [10,       1] ],     # // 0x0A
    "ALARMTYPE"            : [ None,     [11,       1] ],     #
    "EMFALARM"             : [ None,     [12,       1] ],     #
    "EFALARM"              : [ None,     [13,       1] ],     #
    "RFALARM"              : [ None,     [14,       1] ],     #
    "CUMMULATIVETIMEOFRFG" : [ None,     [15,       1] ],     # _CUMMULATIVETIMEOUTFORRFGRAPH
    "LED_ONOFF"            : [ None,     [16,       1] ],     #
    "Base_Frequency"       : [ None,     [17,       1] ],     #
    "Channel_Spacing"      : [ None,     [18,       1] ],     #
    "Bandwidth"            : [ None,     [19,       1] ],     #
    "ZeroCalibration"      : [ None,     [20,       4] ],     # // 0x14 (4 Bytes) # not in use any more
    "Reserved"             : [ None,     [24,       1] ],     #
    "RfDensityUnit"        : [ None,     [25,       1] ],     # // 0x19
    "RfBrowserScale"       : [ None,     [26,       1] ],     #
    "LargeFontEMForRF"     : [ None,     [27,       1] ],     #
    "SpiSaveData"          : [ None,     [28,       1] ],     #
    "SpiCircularAddress"   : [ None,     [29,       1] ],     #
    "MaximumBytes"         : [ None,     [30,       1] ],     # // 0x1E
}
cfgKeyLo = cfgKeyLoDefault.copy()    # shallow copy


def initGEMF():
    """
    Sets configuration, gets counter version, verifies communication
    Return: on success: ""
            on failure: <errmessage>
    """

    ## local ##################################################################################

    def getGEMF_SerialSetting():
        """test all USB-To-Serial ports and return first found port and baudrate with device
        matching ID and/or Serial number if so requested"""

        defname = "getGEMF_SerialSetting: "

        # 1st: find all ports
        PortsFound = getGEMF_SerialPorts("GEMF")
        # rdprint(defname, "PortsFound: ", PortsFound)

        # 2nd: find baudrate
        portfound   = None
        baudfound   = None
        for port in PortsFound:
            baudrate = getGEMF_SerialBaudrate(port)     # like: port: '/dev/ttyUSB0'
            if baudrate is not None and baudrate > 0:
                portfound = port
                baudfound = baudrate
                break

        return (portfound, baudfound)


    def getGEMF_SerialPorts(device):
        """
        gets all USB-to-Serial port names which MATCH USB's vid + pid associated with device.
        """

        # output by: lsusb
        # NOTE: idVendor 0x1a86 and idProduct 0x7523 (seems same for all EMF and all GMC)
        # EMF-390:               GQ-EMF390v2Re 3.75
        #   bcdUSB               1.10
        #   bcdDevice            2.64
        #   idVendor             0x1a86 QinHeng Electronics
        #   idProduct            0x7523 HL-340 USB-Serial adapter
        #   iProduct             2 USB Serial
        #

        defname = "getGEMF_SerialPorts: "

        dprint(defname, "for device: '{}'".format(device))
        setIndent(1)

        PortsFound  = []
        ports       = getPortList(symlinks=False)
        for port in ports:
            irdprint(defname, "port: ", port)

            if g.GEMF_simul:
                # simulation - append all ports found
                PortsFound.append(port.device)
                irdprint(defname, f"Simulation GEMF: PortsFound: {PortsFound}")

            else:
                # use real data from USB port
                # append ONLY those ports with matching vid & pid
                if port.vid == 0x1a86 and port.pid == 0x7523:
                    tmplt_match = "Port: '{}' - Found Chip ID match for device '{}' at vid:0x{:04x}, pid:0x{:04x}"
                    gdprint(defname, tmplt_match.format(port, device, port.vid, port.pid))
                    PortsFound.append(port.device)
                else:
                    dprint(defname, f"Port: '{port}' - Chip ID does not match")

        setIndent(0)
        return PortsFound


    def getGEMF_SerialBaudrate(usbport):
        """
        Uses the provided usbport and tries to find a proper baudrate by testing for successful
        serial communication at up to all possible baudrates, beginning with the highest.
        return: returnBR = None     :   serial error
                returnBR = 0        :   No device found
                returnBR = <number> :   highest baudrate which worked
        """

        # NOTE: the device port can be opened without error at any baudrate permitted by the Python code,
        # even when no communication can be done, e.g. due to wrong baudrate. Therefore we test for
        # successful communication by checking for the return string for getVersion beginning with 'GQ-EMF'.

        defname = "getGEMF_SerialBaudrate: "
        dprint(defname, f"Testing by requesting device version at all baudrates from port: '{usbport}'")
        setIndent(1)

        baudrates = g.GEMFbaudrates[:]          # EMF devices are limited to single baudrate [115200]
        baudrates.sort(reverse=True)            # sort to start with highest baudrate

        foundit = False
        for baudrate in baudrates:
            dprint(defname, f"using baudrate: {baudrate}")

            try:
                with serial.Serial(usbport, baudrate=baudrate, timeout=0.3, write_timeout=0.5) as ABRser:
                    # calling getGEMF_Version may fail after plugging in of device. Somehow, calling GETCPM first
                    # breaks up this failure. Strange. Stranger: works also for GEMF! WTF??? (but sometimes not)
                    ABRser.write(b'<GETCPM>>')
                    getWaitBytes(ABRser)                        # just to clean pipeline

                    srec = getGEMF_Version(ABRser)              # get the GEMF device version as string. Can be real or simulated

            except OSError as e:
                exceptPrint(e, "")
                if e.errno == 13:
                    # no permission for port
                    msg  = "You have no permission to access Serial Port '{}'.".format(usbport)
                    msg += "<br>Please review Appendix C of the GeigerLog manual.<br>"
                else:
                    # non-13 errors
                    msg = "Serial Port {} not available".format(usbport)
                edprint(msg)
                efprint(msg)

                return None

            except Exception as e:
                errmessage1 = defname + "FAILURE: Reading from device"
                exceptPrint(e, errmessage1)
                efprint(errmessage1)
                setIndent(0)
                return None     # Python's None signals communication error


            if srec.startswith("GQ-EMF"):
                # it is a GEMF device
                foundit = True
                dprint(defname + f"Success - found GEMF device '{srec}' using baudrate {baudrate}")

                # now check for a Model definition if requested
                if g.GEMF_ID[0] is None:
                    # a GEMF device was found and a specific Model was NOT requested. You're done
                    break   # the baudrate-loop

                else:
                    if srec.startswith(g.GEMF_ID[0]):
                        # we found the specified Model
                        foundit = True
                        dprint(defname + "Success - matches configured Model '{}' ".format(g.GEMF_ID[0]))

                        # now check for a SerialNumber definition if requested
                        if g.GEMF_ID[1] is None:
                            # not requested
                            break
                        else:
                            serno = getGEMF_SerialNumber(usbport, baudrate)
                            if serno.startswith(g.GEMF_ID[1]):
                                # it is the specified SerialNo
                                foundit = True
                                dprint(defname + "Success - matches SerialNumber '{}' ".format(g.GEMF_ID[1]))
                                break   # the for loop
                            else:
                                # not the specified SerialNo
                                foundit = False

                    else:
                        # not the specified Model
                        rdprint(defname + "FAILURE - does NOT match configured Model '{}' ".format(g.GEMF_ID[0]))
                        foundit = False

                break # the baudrate-loop

            else:
                # not a GEMF device found; try next baudrate
                foundit = False

        # end baudrate-loop

        if foundit:
            g.GEMF_DeviceDetected = srec
            returnBR = baudrate
        else:
            returnBR = 0
            rdprint(defname + f"FAILURE - No matching device detected at port: {usbport}  baudrate: {baudrate}")

        setIndent(0)
        return returnBR

    ## end local defs ##################################################################################


    defname = "initGEMF: "
    dprint(defname)
    setIndent(1)

    g.GEMF_DeviceName = "EMF Device"        # full model name is set in later called g.GEMF_DeviceDetected

    # this sets the values defined in the GeigerLog config file
    if g.GEMF_usbport            == "auto":  g.GEMF_usbport            = None
    if g.GEMF_baudrate           == "auto":  g.GEMF_baudrate           = None
    if g.GEMF_timeoutR           == "auto":  g.GEMF_timeoutR           = 3.5    # long timeout; needed e.g. for SPIE
    if g.GEMF_timeoutR_getData   == "auto":  g.GEMF_timeoutR_getData   = 1.5    # shorter Timeout-Read used for data collection
    if g.GEMF_timeoutW           == "auto":  g.GEMF_timeoutW           = 1      # write is always rather fast
    if g.GEMF_ID                 == "auto":  g.GEMF_ID                 = (None, None)
    if g.GEMF_RTC_Offset         == "auto":  g.GEMF_RTC_Offset         = +1
    if g.GEMF_ClockCorrection    == "auto":  g.GEMF_ClockCorrection    = 30
    if g.GEMF_CustomCmd          == "auto":  g.GEMF_CustomCmd          = "None"
    ## g.GEMF_Variables to be set AFTER device detection!

    #
    # get the usbport and find the baudrate
    #
    if  g.GEMF_usbport is None:
        # user has NOT defined a port; now auto-find it and its baudrate

        port, baud = getGEMF_SerialSetting()
        # rdprint(defname + "port, baud: ", port, baud)

        if port is None or baud is None:
            g.Devices["GEMF"][g.CONN] = False
            msg = f"A device {g.GEMF_DeviceName} was not detected"
            setIndent(0)
            return msg
        else:
            g.GEMF_usbport          = port
            g.GEMF_baudrate         = baud
            g.Devices["GEMF"][0]    = g.GEMF_DeviceDetected                        # detected at getGEMF_Version()

            # Example fprint: 'EMF Device 'GQ-EMF390Re 1.00' detected at port: /dev/ttyUSB0 and baudrate: 57600'
            fprint("{} '{}' detected at port: {} and baudrate: {}".format(
                                                                                g.GEMF_DeviceName,
                                                                                g.GEMF_DeviceDetected,
                                                                                g.GEMF_usbport,
                                                                                g.GEMF_baudrate),
                                                                             )

    else:
        # user has defined a port; use it if it exists, return error if not; don't try anything else
        if not os.path.exists(g.GEMF_usbport):
            # edprint("den shit gibbes nich")
            return "The user defined port '{}' does not exist".format(g.GEMF_usbport)
        else:
            # use the port configured by the user
            # Example fprint:   A EMF Device was user configured for port: '/dev/ttyUSB0'
            fprint("A device {} was <b>user configured</b> for port: '{}'".format(
                                                                                g.GEMF_DeviceName,
                                                                                g.GEMF_usbport,))
            baudrate = getGEMF_SerialBaudrate(g.GEMF_usbport)
            if baudrate is not None and baudrate > 0:
                g.GEMF_baudrate = baudrate
                fprint("{} '{}' detected at port: {} and baudrate: {}".format(
                                                                                g.GEMF_DeviceName,
                                                                                g.GEMF_DeviceDetected,
                                                                                g.GEMF_usbport,
                                                                                g.GEMF_baudrate))
            else:
                return "A {} was not detected at user defined port '{}'.".format(
                                                                                g.GEMF_DeviceName,
                                                                                g.GEMF_usbport)

    ###
    ### if this point is reached, a serial connection does exist and the counter is connected and ID'd
    ###

    g.Devices["GEMF"][g.DNAME] = g.GEMF_DeviceDetected
    g.Devices["GEMF"][g.CONN]  = True

    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
    # get device details incl. GEMF_variables
    dprint(defname, f"Found device '{g.GEMF_DeviceDetected}', now getting Device Properties:")
    getGEMF_DeviceProperties()
    # PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

    # update the tooltip in the device toolbar incl device name
    g.exgg.dbtnGEMF.setToolTip("EMF Device<br><b>{}</b><br>Click Button for Device Info".format(g.GEMF_DeviceDetected))

    # enable / disable the History download options
    g.exgg.histGEMFDeviceAction.setEnabled(True if g.GEMF_HasHistory else False)

    # setting the variables
    defaultVars = "Temp:EF, Press:EMF, Humid:RF, Xtra:XF"
    defaultVMap = {}
    for gvar in defaultVars.split(","):
        gvarlist = gvar.replace(" ", "").split(":")
        defaultVMap.update({gvarlist[0] : gvarlist[1]})

    if g.GEMF_Variables == "auto":
        # auto config
        g.GEMF_Variables    = defaultVars
        g.GEMF_VariablesMap = defaultVMap

    else:
        # custom config
        try:
            for gvar in g.GEMF_Variables.split(","):
                gvarlist = gvar.replace(" ", "").split(":")
                g.GEMF_VariablesMap.update({gvarlist[0] : gvarlist[1]})
        except Exception as e:
            exceptPrint(e, defname + "set 'GEMF' variables")
            efprint(f"Could not set custom variables '{g.GEMF_Variables}'. Please, review config!")
            g.GEMF_Variables    = defaultVars
            g.GEMF_VariablesMap = defaultVMap

    # set variables string
    g.GEMF_Variables = setLoggableVariables("GEMF", ", ".join(g.GEMF_VariablesMap)) # join the keys; sets g.Devices["GEMF"][g.VNAMES]

    # reset all call durations
    g.GEMF_callDurMax = {"EF" : 0,
                         "EMF": 0,
                         "RF" : 0,
                         "XF" : 0}

    # set default commands
    g.GEMF_Commands = {"EF"   :b'<GETEF>>',                                        # EF  : b'EF = 163.7 V/m'
                       "EMF"  :b'<GETEMF>>',                                       # EMF : b'EMF = 3.6 mG'
                       "RF"   :b'<GETRFTOTALDENSITY>>',                            #
                       "XF"   :g.GEMF_CustomCmd.encode("utf-8", errors="replace"), # RFP : b'4886.6 mW/m2 (0.24-8G Peak)'
                      }

    # ydprint(defname, f"GEMF_Variables:    {g.GEMF_Variables}")
    # ydprint(defname, f"GEMF_VariablesMap: {g.GEMF_VariablesMap}")
    # ydprint(defname, f"GEMF_Commands:     {g.GEMF_Commands}")
    # ydprint(defname, "g.Devices['GEMF'][g.VNAMES]: ", g.Devices["GEMF"][g.VNAMES])
    # initGEMF: GEMF_Variables:    Temp, Press, Humid, Xtra
    # initGEMF: GEMF_VariablesMap: {'Temp': 'EF', 'Press': 'EMF', 'Humid': 'RF', 'Xtra': 'XF'}
    # initGEMF: GEMF_Commands:     {'EF': b'<GETEF>>', 'EMF': b'<GETEMF>>', 'RF': b'<GETRFTOTALDENSITY>>', 'XF': b'None'}
    # initGEMF: g.Devices['GEMF'][g.VNAMES]: ['Temp', 'Press', 'Humid', 'Xtra']


    # reset var values and last responses
    for vname in g.Devices["GEMF"][g.VNAMES]:
        g.GEMF_Value[vname] = g.NAN                         # reset all var values
        g.GEMF_lastResp.update({vname : "None"})            # reset Last Responses

    # do a clock correction at init, but only if so configured
    if g.GEMF_ClockCorrection > 0: makeClockCorrectionGEMF

    # get the config and set it up for GeigerLog
    rcfg, error, errmessage = getGEMF_RawConfig()

    if error >= 0:
        if g.debug:
            # make list of cfg for copy/paste to simulator
            ac = "["
            for i, a in enumerate(rcfg):
                if i % 20 == 0 and i > 0: ac += "\n "
                ac += "{:3d}, ".format(a)
            ac = ac[:-2] + "]"
            cdprint(defname, " Python list for copy/paste of config for use in simulation\n", ac)

        vprintGEMF_Config(defname, rcfg)
        setGEMF_Config4GL(rcfg)  # no return val

    dprint(defname, "power On:", setGEMFPowerIcon(getconfig=True))

    setIndent(0)

    # set Threading
    g.GEMF_ThreadRun     = True
    g.GEMF_Thread        = threading.Thread(target=GEMF_THREAD_Target, args=["Dummy"])     # auch tuple (args=("Dummy",)) möglich, aber NUR einzelnes Argument!
    g.GEMF_Thread.daemon = True
    g.GEMF_Thread.start()

    msgalive = "Yes" if g.GEMF_Thread.is_alive() else "No"
    # ydprint(defname + f"thread-status: alive: {msgalive}")

    return ""   # empty message signals "Ok"; only other useful msg is "SIM" (for simulated, like from Raspi devices)
#end initGEMF


def terminateGEMF():
    """close Serial connection if open, and reset some properties"""

    defname = "terminateGEMF: "

    dprint(defname )
    setIndent(1)

    # shut down thread
    dprint(defname, "stopping thread")
    g.GEMF_ThreadRun = False
    g.GEMF_Thread.join()                 # "This blocks the calling thread until the thread
                                         #  whose join() method is called is terminated."

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.GEMF_Thread.is_alive() and (time.time() - start) < 5:
        pass

    msgalive = "" if g.GEMF_Thread.is_alive() else "NOT"
    dprint(defname + f"thread-status: {msgalive} alive after:{1000 * (time.time() - start):0.1f} ms")

    # set the GEMF power icon to inactive state
    g.exgg.dbtnGEMFPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_on.png'))))
    g.exgg.dbtnGEMFPower.setEnabled(False)

    g.Devices["GEMF"][g.CONN] = False
    g.GEMF_Variables          = "auto"
    g.GEMF_usbport            = "auto"
    g.GEMF_baudrate           = "auto"

    if g.GEMFser is not None:
        try:        g.GEMFser.close()
        except:     edprint(defname + "Failed trying to close Serial Connection; terminating anyway")
        g.GEMFser = None

    dprint(defname, "Terminated")

    setIndent(0)


def getValuesGEMF(varlist):
    """Read data from the locally held vars; set them to NAN after readout"""

    start = time.time()

    defname = "getValuesGEMF: "
    # mdprint(defname, "varlist: ", varlist)

    alldata = {}
    keys    = g.GEMF_Value.keys()
    for vname in varlist:
        if vname in keys:
            alldata[vname]      = g.GEMF_Value[vname]   # g.GEMF_Value has already the scaled data - do not scale again!!
            g.GEMF_Value[vname] = g.NAN                 # reset g.GEMF_Value

    vprintLoggedValues(defname, varlist, alldata, 1000 * (time.time() - start))

    return alldata


def GEMF_THREAD_Target(args):
    """The thread to read the variables from the device"""

    # funny args issue: threading.Thread(target=GEMF_THREAD_Target, args=["Dummy"])
    #                   auch tuple (args=("Dummy",)) möglich, aber stets NUR einzelnes Argument!

    defname = "GEMF_THREAD_Target: "
    # rdprint(defname, "args: ", args)

    varlist     = g.Devices["GEMF"][g.VNAMES]
    GEMF_DurAllCalls = 0.3                   # 300 ms for the total of all calls

    # wait until logging has started
    while g.nexttime == 0:
        if not g.GEMF_ThreadRun: return
        time.sleep(0.1)

    THREAD_nexttime = g.nexttime - GEMF_DurAllCalls

    while g.GEMF_ThreadRun:

        # actions when logging and time is due
        if g.logging and time.time() >= THREAD_nexttime:

            # fetch the values
            g.GEMF_Value = THREAD_GEMF_fetchValues(varlist)           # gives error if doing when not logging

            # clock correction - if so configured
            if g.GEMF_ClockCorrection > 0 and (getMinute() == g.GEMF_NextCorrMin):
                makeClockCorrectionGEMF()

            # set time for next-cycle calls
            THREAD_nexttime = g.nextnexttime - GEMF_DurAllCalls - 0.01
            time.sleep(max(0, THREAD_nexttime - time.time()))

        time.sleep(0.01)    # idle period


def THREAD_GEMF_fetchValues(varlist):
    """get all data for vars in varlist for LOCAL storage"""

    totalstart   = time.time()

    defname = "THREAD_GEMF_fetchValues: "
    # mdprint(defname, varlist)
    # setIndent(1)

    THREAD_alldata = {}
    g.fSVStringSet = False

    # does the USB-Port exist?
    if not os.path.exists(g.GEMF_usbport):
        # den shit gibbes nich  -   kann passieren, wenn nach Start der USB Stecker gezogen wird!
        qmsg  = f"<br>{stime()} FAILURE: GEMF Serial Port '{g.GEMF_usbport}' does not exist.\n"
        qmsg += f"Is GEMF device '{g.GEMF_DeviceDetected}' still connected?"
        QueuefPrint(qmsg)
        QueueSound("burp")
        dprint(defname, BRED, f"FAILURE: Port '{g.GEMF_usbport}' does not exist", TDEFAULT)
        return THREAD_alldata

    else:
        # USB-Port does exist
        # try to make a serial connection and get values on success
        GEMF_DataSerial = None
        try:
            GEMF_DataSerial = serial.Serial(g.GEMF_usbport, baudrate=g.GEMF_baudrate, timeout=g.GEMF_timeoutR_getData, write_timeout=g.GEMF_timeoutW)
        except serial.SerialException as e:
            # no serial connection
            exceptPrint(e, "Device cannot be found or cannot be configured; Port may already be open.")
        except Exception as e:
            # no serial connection
            exceptPrint(e, "Unexpected Exception opening Serial Port")
        else:
            # serial connection had been made ok
            for vname in varlist:
                fSVstart    = time.time()
                fSV         = fetchSingleValueGEMF(GEMF_DataSerial, vname)
                fSVdur      = 1000 * (time.time() - fSVstart)
                # rdprint(defname, "fSVdur: {0:0.1f}".format(fSVdur))
                g.GEMF_calls += 1

                # fSV is a string only when an error had happened
                if type(fSV) is str:
                    mdprint(defname, f"{vname:6s} fsv: '{fSV}'")
                    g.fSVStringSet = True

                    if   "R_TIMEOUT" in fSV:
                            # QueuefPrint("{} {}".format(longstime(), emsg))
                            # dprint(defname, emsg)
                            # # g.SoundMsgQueue.append("doublebip")
                            # fSV = -1000 * g.GEMF_timeoutR_getData if g.GEMF_testing else g.NAN
                            fSV =  -999 if g.GEMF_testing else g.NAN

                    elif "EXTRABYTES" in fSV:
                            # wurde unter Windows einmal beobachtet. Nach einem timeout
                            # g.GEMF_callsExtrabyte += 1

                            emsg = "EXTRABYTES-FAIL: {:6s}".format(vname)
                            QueuefPrint(emsg)
                            cdlogprint(defname + emsg)
                            fSV =  -7000 if g.GEMF_testing else g.NAN

                    elif "WRONG_BYTECOUNT" in fSV:
                            # g.GEMF_callsWrongbyteCount += 1

                            emsg = "BYTECOUNT-FAIL: {:6s} got {} bytes, expected {}!".format(vname, fSV.split(" ")[1], g.GEMF_Bytes)
                            QueuefPrint(emsg)
                            cdlogprint(defname + emsg)
                            fSV =  -9000 if g.GEMF_testing else g.NAN

                    elif "USBPORT_MISSING" in fSV:
                            emsg = "USBPORT_MISSING-FAIL: Serial port '{}' does not exist. Cannot read variable: '{}'".format(g.GEMF_usbport, vname)
                            QueuefPrint(emsg)
                            cdlogprint(defname + emsg)
                            fSV = -10000 if g.GEMF_testing else g.NAN

                    elif "WRONG_VARNAME" in fSV:
                            emsg = "WRONG_VARNAME-FAIL: '{}' cannot be used".format(vname)
                            QueuefPrint(emsg)
                            cdlogprint(defname + emsg)
                            fSV = -11000 if g.GEMF_testing else g.NAN

                    elif "EXCEPTION" in fSV:
                            emsg = "EXCEPTION: getting value for '{}' on port: {}".format(vname, g.GEMF_usbport)
                            QueuefPrint(emsg)
                            cdlogprint(defname + emsg)
                            fSV = -12000 if g.GEMF_testing else g.NAN

                    else:
                            cdlogprint(defname, "UNCAUGHT fSV string: ", fSV)
                            fSV = -20000 if g.GEMF_testing else g.NAN
                # end if (message is str)

                ### fSV can be the original value or the negative error-string-modified-value.
                THREAD_alldata[vname] = fSV

            # end loop: 'for vname in varlist'

            GEMF_DataSerial.close()

    totaldur = 1000 * (time.time() - totalstart)                              # sum of durations of all actions in this def

# ### testing
# # get Deltatime and dur into var CPM3rd and CPS3rd
#     dt, dd = getGEMF_ClockDelta()
#     THREAD_alldata["CPM3rd"] = dt
#     THREAD_alldata["CPS3rd"] = dd
#     rdprint(defname, f"ClockDelta: {dt:0.3f} sec   {dd:0.3f} ms")
# ###

    vprintLoggedValues(defname + "   ", varlist, THREAD_alldata, totaldur)

    # get GEMFinfo during logging if requested
    #    as info requires multiple calls to counter, it can only be done when not
    #    interfering with calls for data. This place here is the ONLY one to assure this!
    if g.GEMF_getInfoFlag > 0:
        # NOTE: GEMF_getInfoFlag can be (0, 1, 2)
        extended = False if (g.GEMF_getInfoFlag == 1) else True
        g.GEMF_DatetimeMsg = getInfoGEMF(extended=extended,  force=True)
        g.GEMF_getInfoFlag = 0

    # setIndent(0)

    return THREAD_alldata


def fetchSingleValueGEMF(GEMF_DataSerial, vname):
    """Get value for a single, specific var, and return single value AFTER doing ValueFormula"""

    defname = "fetchSingleValueGEMF: "

    # find the wcommand to send to the EMF device
    cmd      = g.GEMF_VariablesMap[vname]
    wcommand = g.GEMF_Commands[cmd]
    # ydprint(defname, f"vname: {vname}  cmd: {cmd}  wcommand: {wcommand}")
    if wcommand == b'None': return g.NAN        # when 'GEMF_CustomCmd = auto'

    # does the USB-Port exist?
    if not os.path.exists(g.GEMF_usbport):  return "USBPORT_MISSING"                # can happen when plug is pulled aftr init

    # is the Port open?
    if GEMF_DataSerial is None:             return "GEMF Serial Port is not open"

    # get the value for variable 'vname'
    try:
        while g.GEMF_USBportBusy:
            time.sleep(0.1)

        getWaitBytes(GEMF_DataSerial)   # clean pipeline

        calldur   = g.NAN
        callstart = time.time()
        bwrt      = GEMF_DataSerial.write(wcommand)           # returns bwrt: Number of bytes written, type: <class 'int'>
        brec      = GEMF_DataSerial.read(1)                   # returns brec: data record of           type: <class 'bytes'>
        brec     += getWaitBytes(GEMF_DataSerial)
        calldur   = 1000 * (time.time() - callstart)          # duration of call in ms
        if calldur > g.GEMF_callDurMax[cmd]: g.GEMF_callDurMax[cmd] = calldur

    except Exception as e:
        g.GEMF_callsException += 1
        exceptPrint(e, defname + "getting data for {:6s} from port: {}".format(vname, g.GEMF_usbport))
        return "EXCEPTION"                                    # might happen, but I have not seen it yet

    # print brec and dur
    rdprint(defname, f"{vname:6s} Cmd: {str(wcommand):28s}  brec: {str(brec):37s} Dur: {calldur:6.1f} ms  DurMax: {g.GEMF_callDurMax[cmd]:6.1f} ms  Exceptions: {g.GEMF_callsException}")

    # check for read timeout
    if calldur >= g.GEMF_timeoutR_getData * 1000:     return "R_TIMEOUT"    # it is a timeout

    # make value
    try:
        value   = g.NAN
        brecstr = brec.decode("utf-8", errors="replace")
        value   = re.findall(r"(\d+(?:\.\d+)?)", brecstr)          # finds both floats and int
        if len(value) > 0:  value = float(value[0])
        else:               value = g.NAN
        g.GEMF_lastResp.update({vname:brec.decode("utf-8", errors="replace")})

    except Exception as e:
        exceptPrint(e, f"vname: {vname}  value: {value}")

    return applyValueFormula(vname, value, g.ValueScale[vname], info=defname)  # returns single number, int or float


def getGEMF_Version(GEMF_serial):
    # 1. Get hardware model and version
    # Command:  <GETVER>>
    # Return:   Version of the device. Ends char characters '\r' '\n' or 0x0D 0x0A in hex
    # 	  e.g.:  GQ-EMF380Re 1.00\r\n
    # NOTE: the CR & LF at the end!

    defname     = "getGEMF_Version: "
    errmessage  = "None"

    setIndent(1)

    # write to serial
    try:
        GEMF_serial.write(b'<GETVER>>')
    except Exception as e:
        errmessage = defname + "FAILURE writing to GEMF_serial"
        exceptPrint(e, errmessage)
        setIndent(0)
        return errmessage

    # read from serial
    try:
        brec  = GEMF_serial.read(10)   # may leave bytes in the pipeline
        brec += getWaitBytes(GEMF_serial)

    except Exception as e:
        errmessage = defname + f"FAILURE reading from GEMF_serial; brec: {brec}"
        exceptPrint(e, errmessage)
        setIndent(0)
        return errmessage

    else:
        brec = brec.strip()
        if len(brec) == 0:
            dprint(defname, "FAILURE: No data returned")
            GEMF_version = ""
        else:
            # convert to string
            GEMF_version = brec.decode("UTF-8", errors='replace')  # should never fail
            dprint(defname, f"rec: {brec} (len: {len(brec)} bytes), GEMF_version: '{GEMF_version}', errmessage: '{errmessage}'")

    setIndent(0)
    return GEMF_version


def cleanupGEMF(ctype = "Dummy"):    # ctype should be "before" or "after" (logging); is called from gsup_utils
    """clearing the pipeline, resetting values"""

    defname = "cleanupGEMF: "

    if g.Devices["GEMF"][g.CONN] :
        # clean pipeline
        dprint(defname, "'{}': Cleaning Pipeline '{}'".format(g.GEMF_DeviceDetected, ctype))
        getGEMF_ExtraByte()

        # reset all local values
        dprint(defname, "'{}': Reset local values '{}'".format(g.GEMF_DeviceDetected, ctype))
        for vname in g.VarsCopy:
            g.GEMF_Value[vname] = g.NAN


def getGEMF_VOLT():
    # 30. Gets the battery voltage
    # Command: <GETVOLT>>
    # Return: Battery Voltage in ascii (e.g.) 3.52 Volts

    defname = "getGEMF_VOLT: "
    dprint(defname)
    setIndent(1)

    rec, error, errmessage = serialGEMF_COMM(b'<GETVOLT>>', g.GEMF_voltagebytes, orig(__file__))
    try:                   dprint(defname, "VOLT: rec: {} (len:{})  as Dec:{}".format(rec, len(rec), BytesAsDec(rec)))
    except Exception as e: exceptPrint(e, f"Voltage format is not matching expectations, rec: {rec}")

    if error in (0, 1): rec = rec.decode('UTF-8', errors='replace')
    else:               rec = "FAILURE getting voltage"

    # dprint(defname, "Using config setting GEMF_voltagebytes={}:  Voltage='{}', err={}, errmessage='{}'".format(g.GEMF_voltagebytes, rec, error, errmessage))
    setIndent(0)

    return rec


def getGEMF_SPIR(address = 0, datalength = 4096):
    """Reads datalength (=4k) bytes from the internal flash memory at address to get history data"""

    # 33. read spi data (saved log)
    # Command: <SPIR[hi][mi][lo][b1][b0][>>
    # 			the [hi] [mi] [lo] parameters are three byte address and [b1][b0]
    # 			is the ammount of data you want.
    # 			e.g. (in hex) 3c 53 50 49 52 00 00 00 10 00 3e 3e
    # 			3c 53 50 49 52 	==>> is the "<SPIR" equivalent in hex
    # 			00 00 00 		==>> is the address in hex: 0
    # 			10 00			==>> the amount of bytes in hex: 4096 bytes
    # Return:
    # 			55 AA 12 09 06 0B 0B 0E AA 55 00 00 71 AE 9C 3D 42 8C 96 49
    # 			AA 55 00 00 06 D0 90 3D 42 8C 96 49 AA 55 00 00 0B F3 74 3D
    # 			42 8C 96 49 AA 55 00 00 0D 69 85 3D 42 8C 96 49 AA 55 00 00
    # 			71 AE 9C 3D 4D 87 BD 49 AA 55 00 00 9D D1 B5 3D 4D 87 BD 49
    # 			AA 55 00 00 DF 02 60 3D 4D 87 BD 49 AA 55 00 00 06 D0 90 3D
    # 			4D 87 BD 49 AA 55 00 00 06 D0 90 3D 4D 87 BD 49 AA 55 00 00
    # 			4E 04 A9 3D 4D 87 BD 49 AA 55 00 00 DF 02 60 3D 4D 87 BD 49
    # 			AA 55 00 00 0D 69 85 3D 3F 2B 6F 49 AA 55 00 00 0D 69 85 3D
    # 			3F 2B 6F 49 AA 55 00 00 71 AE 9C 3D 3F 2B 6F 49 AA 55 00 00
    # 			0D 69 85 3D (etc)
    #
    # 			// timestamp starts with 0x55 0xAA and is 8 bytes in total
    # 				e.g. 55 AA 12 09 06 0B 0B 0E ==>> 2018, September 6,  11:11:14
    # 			// data starts with 0xAA 0x55 and is 12 bytes long in total
    # 				e.g. AA 55 00 14 05 5A 43 3E 56 4E 70 48
    # 				Emf is 2 bytes. first 12 bits is the integer part and last 4
    # 						bits is decimal part. here is
    # 						00 14  ==>>> '001' is the integer part and '0' is dec.
    # 						00 14  ==>>> 1.4 mG
    # 				EF is 4 bytes float
    # 						05 5A 43 3E  ==>> these are the bytes of a floating point.
    # 											Need to use union data structure to
    # 											get the data
    # 				rf is 4 bytes float
    # 						56 4E 70 48  ==>> same as EF

    defname = "getGEMF_SPIR: "
    # dprint(defname)

    # address: pack into 4 bytes, big endian; then clip 1st byte = high byte! to have 3 bytes
    ad = struct.pack(">I", address)[1:]

    # datalength: pack into 2 bytes, big endian
    dl = struct.pack(">H", datalength)

    spirstart = time.time()
    # clean pipeline (before every(!) read of 4k)
    getGEMF_ExtraByte()

    # get SPIR data
    rec, error, errmessage = serialGEMF_COMM(b'<SPIR' + ad + dl + b'>>', datalength, orig(__file__)) # returns bytes
    spirdur   = 1000 * (time.time() - spirstart)
    if rec is not None :    rmsg = f"datalen:{len(rec):5d}"
    else:                   rmsg = f"ERROR: No data received!"

    msg  = f"requested: datalen:{datalength:5d} (0x{dl[0]:02x}{dl[1]:02x})"
    msg += f"  address:{address:7d} (0x{ad[0]:02x}{ad[1]:02x}{ad[2]:02x})"
    msg += f" --> received: {rmsg}  err={error}  errmsg='{errmessage}'  "
    msg += f"Dur: {spirdur:0.1f} ms"
    dprint(defname, msg)

    return (rec, error, errmessage)


def eraseGEMF_SPI():
    """Erase the History Data saved to memory"""

    # 34. Erases SPI chip
    # Command: <SPIE>>
    # Return: 0xAA

    start = time.time()
    defname = "eraseGEMF_SPI: "
    dprint(defname)
    setIndent(1)

    rec, error, errmessage = serialGEMF_COMM(b'<SPIE>>', 1, orig(__file__))
    cdprint(defname, f"SPIE rcvd: rec={rec}, err={error}, errmessage='{errmessage}'", "  Duration: {:0.1f} sec".format(time.time() - start))

    setIndent(0)

    return (rec, error, errmessage)


def getGEMF_ExtraByte(SerHandle = None):
    """Clearing the serial pipeline by reading all bytes from it"""

    defname = "getGEMF_ExtraByte: "

    setIndent(1)

    if SerHandle is None:
        # no SerHandle given as parameter; make new one
        if os.path.exists(g.GEMF_usbport):
            try:
                with serial.Serial( g.GEMF_usbport,
                                    g.GEMF_baudrate,
                                    timeout=g.GEMF_timeoutR_getData,                     # 0.5 sec ( a shorter value than default)
                                    write_timeout=g.GEMF_timeoutW)       as GEMF_serEB:
                    xrec = getWaitBytes(GEMF_serEB)

            except Exception as e:
                exceptPrint(e, defname + "Failure trying to establish serial connection")
                xrec = b""
        else:
            msg = f"USBport '{g.GEMF_usbport}' does not exist"
            rdprint(defname, msg)
            xrec = b""

    else:
        # a SerHandle was given as parameter, use it
        xrec = getWaitBytes(SerHandle)

    setIndent(0)

    return xrec


def getWaitBytes(serialHandle):
    """getting and returning waiting bytes"""

    brec = b""
    while True:
        time.sleep(0.01)
        bytesWaiting = serialHandle.in_waiting
        if bytesWaiting == 0: break
        brec += serialHandle.read(bytesWaiting)

    return brec


def getGEMF_RawConfig():
    """
    - get the config from the device
    - return cfg, error, errmessage
    """
    # 9. Get configuration data
    # Command:  <GETCFG>>
    # Return: The configuration data.  Total 256 bytes will be returned.

    defname = "getGEMF_RawConfig: "
    dprint(defname)
    setIndent(1)

    # get the config from the counter
    try:
        startGETCFG = time.time()
        cfg, error, errmessage = serialGEMF_COMM(b'<GETCFG>>', g.GEMF_configsize, orig(__file__))
        durGETCFG   = 1000 * (time.time() - startGETCFG)
    except Exception as e:
        exceptPrint(e, defname)
        return (b"", -1, "EXCEPTION reading config from counter")

    if cfg is not None:
        if len(cfg) == g.GEMF_configsize:
            # it has the right size
            dprint (defname + "Got config as {} bytes in {:5.1f} ms; first 20 B as hex: {}".format(len(cfg), durGETCFG, BytesAsHex(cfg[:20])))
        else:
            # the size is wrong - either empty or not expected config size
            edprint (defname + "FAILURE getting config - wrong byte count={} received in {:0.1f} ms".format(len(cfg), durGETCFG))
            QueuefPrint("ERROR: Could not load proper configuration from GEMF counter. Please, retry.")
            cfg, error, errmessage =  (b"", -1, f"FAILURE getting config - wrong size: {len(cfg)}")

    setIndent(0)

    return cfg, error, errmessage


def setGEMF_Config4GL(cfg):
    """
    Take configuration data and parse into dict
    parameter: cfg:  config data as read from device (real or simulated)
    return:    None
    """

    # local defs ########################################
    def convBytesToVals(cbytes):
        cval = ""
        cval = " ".join("%02X" % e for e in cbytes)
        return cval


    def getType(val):
        t = str(type(val))
        return t[8:-2]

    # end local defs ####################################


    start1 = time.time()

    defname = "setGEMF_Config4GL: "
    mdprint(defname)
    setIndent(1)

    cfgheader = "   {:20s} {:5s} : {:33s}{:8s} {}".format("key", "Index", "Value", "Type", "Bytes")

    # set low keys
    mdprint(defname, "cfgKeyLo")
    mdprint(cfgheader)

    # set endian
    if g.GEMF_endianness == "big": fcode = ">f"         # use big-endian ---   500er, 600er, 800er:
    else:                          fcode = "<f"         # use little-endian -- 3XX and 3XXS series

    try:
        for key in cfgKeyLo:
            index        = cfgKeyLo[key][1][0]
            width        = cfgKeyLo[key][1][1]
            cfgkeyBinVal = cfg [index : index + width]        # cut bytes out from config

            if   key == "ZeroCalibration"   : cfgKeyLo[key][0] = struct.unpack(fcode,   cfgkeyBinVal)[0]
            else:                             cfgKeyLo[key][0] = struct.unpack(">B",    cfgkeyBinVal)[0] # all other keys are single byte values

            mdprint("   {:20s} {:5d} : {:<33.10g}{:8s} {}".format(key, int(cfgKeyLo[key][1][0]), cfgKeyLo[key][0], getType(cfgKeyLo[key][0]), convBytesToVals(cfgkeyBinVal)))

    except Exception as e:
        exceptPrint(e, defname + "key: {}".format(key))


    DurWith  = 1000 * (time.time() - start1)
    dprint(defname, "Duration: {:0.0f} ms".format(DurWith))

    setIndent(0)


def writeGEMF_ConfigFull(config):
    """write a full config"""

    # 10. Erase all configuration data
    # Command:  <ECFG>>
    # Note: 	If <GETCFG>> is used after this command, you will get 256 bytes of 0xFF
    # Return: 0xAA

    # 11. Write configuration data
    # Command:  <WCFG[A1][A0][D0]>>
    #     A1 is the MSB of the address can only be 0x00
    #     A0 is the MLB can be 0x00 - 0xFF
    #     D0 is the data byte(hex).
    # Note:   Can't write a byte from 0 to 1. Changing a byte from 0 to 1 will require erasing the CFG
    #     So the proper way to use <WCFG>> is to:
    #     First <GETCFG>> to read 256 config bytes, modify the value from the 512 bytes, <ECFG>>, then <<WCFG>> each of the 256 byte to the config.
    # Return: 0xAA, returns 0x55 if failed


    start = time.time()

    defname = "writeGEMF_ConfigFull: "

    dprint(defname)
    setIndent(1)

    cfgcopy = copy.copy(config)

    doUpdate = 256

    # remove right side FFs; after erasing the config memory this will be the default anyway
    cfgstrip = cfgcopy.rstrip(b'\xFF')
    # dprint(defname + "Config right-stripped from FF: len:{}:\n".format(len(cfgstrip)), BytesAsHex(cfgstrip))

    # erase config on device
    startecfg = time.time()
    rec, error, errmessage = serialGEMF_COMM(b'<ECFG>>', 1, orig(__file__))
    cdprint(defname + "rec: {}  ECFG: Duration: {:0.3f} ms".format(rec, 1000 * (time.time() - startecfg)))

    # write the (modified) config to device
    dprint(defname + "Write new Config Data for Config Size: >>>>>>>>>>>>>>>> {} <<<<<<<<<<<<".format(doUpdate))
    startAllups = time.time()
    pfs = "addr:{:>3d} (0x{:03X})   cfgval:{:>3d} (0x{:02X})"
    with serial.Serial(g.GEMF_usbport, g.GEMF_baudrate, timeout=0.3) as GEMFserData:
        for i, cfgval in enumerate(cfgstrip):
            startsingle = time.time()

            Add = struct.pack(">H", i) # DOUBLE bytes: pack address into 2 bytes, big endian, for address writing config of up to 512 bytes

            D0 = bytes([cfgval])
            if D0 == ">": edprint("D0 == > !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            bwrt = GEMFserData.write(b'<WCFG' + Add + D0 + b'>>')      # bwrt: Number of bytes written, type: <class 'int'>
            brec = GEMFserData.read(1)                                 # brec: is always 0xaa; type: <class 'bytes'>

            duration   = 1000 * (time.time() - startsingle)
            extra      = "  Duration: {:0.1f} ms".format(duration)

            ### skip some printing
            min  = 7
            max  = len(cfgstrip) - min
            step = 1
            if i == max: print()
            else:
                if i > min and i < max:
                    if i % step == 0: print(".", end="", flush=True)
                    continue

            ix         = int.from_bytes(Add, byteorder="big")
            cx         = int.from_bytes(D0,  byteorder="big")
            mdprint(defname + pfs.format(i, ix, cfgval, cx), extra)

    dprint(defname + "Duration All Bytes: {:0.1f} sec".format(time.time() - startAllups))

    # activate new config on device
    updateGEMF_Config()

    # overall
    dprint(defname + "Duration Overall w. Update: {:0.1f} sec".format(time.time() - start))

    setIndent(0)


def updateGEMF_Config():
    # 15. Reload/Update/Refresh Configuration
    # Command: <CFGUPDATE>>
    # Return: 0xAA

    defname = "updateGEMF_Config: "
    dprint(defname)
    setIndent(1)

    rec = serialGEMF_COMM(b'<CFGUPDATE>>', 1, orig(__file__))

    dprint(defname + "rec: ", rec)

    setIndent(0)


#rep
def replaceGEMF_ConfigValues():
    """puts the config settings into cfg and writes it to the config memory"""
    # remember to NOT call 'setGEMF_Config4GL(cfg)' here: it resets all low and high keys !!!


    #### local defs #######################################################

    def replaceBytesInCFG(key, address, bytesrec):
        """write the bytes in byterec to the Python var cfg beginning at address"""

        defname = "replaceBytesInCFG: "

        # rdprint(defname, "key: {}  address:{} bytesrec: '{}'".format(key, address, bytesrec))

        for i in range(0, len(bytesrec)):
            gcfg[address + i] = bytesrec[i]

    #######################################################################

    defname = "replaceGEMF_ConfigValues: "

    setBusyCursor()
    dprint(defname, "Modified key settings")
    setIndent(1)

    cdprint(defname, "          Width:Key      Index:Width Value")

    gcfg = bytearray(g.GEMF_cfg)           # <class 'bytes'> --> CANNOT be modified, <class 'bytearray'> --> CAN be modified

    # set endian
    if g.GEMF_endianness == "big": fcode = ">f"                                            # use big-endian ---   500er, 600er:
    else:                          fcode = "<f"                                            # use little-endian -- other than 500er and 600er:

    # low keys as set by configuration dialog
    # "Alarm", "Speaker", "SaveDataType", "BackLightTOSec",
    #                                        "CalibCPM_0", "CalibuSv_0", "CalibCPM_1", "CalibuSv_1", "CalibCPM_2", "CalibuSv_2"
    # cfgKeyLo:
    #    key                    Value,     Index, width
    #   "Power"             : [ None,     [0,         1] ],     # Power state (read only, not settable!)

    for key in cfgKeyLo:
        cfgrec      = cfgKeyLo[key]
        indxfrom    = cfgrec[1][0]
        width       = cfgrec[1][1]
        cfgkeyVal   = cfgrec[0]

        cdprint(defname, " Lo: {:20s} {:4d}:{:2d}    {}".format(key, indxfrom, width, cfgkeyVal))

        if   width == 1: replaceBytesInCFG(key, indxfrom, struct.pack(">B",   cfgkeyVal))
        elif width == 2: replaceBytesInCFG(key, indxfrom, struct.pack(">H",   cfgkeyVal))
        elif width == 4: replaceBytesInCFG(key, indxfrom, struct.pack(fcode,  cfgkeyVal))

    cdprint()

    vprintGEMF_Config("Modified key settings: ", gcfg)

    fprint("Preparation completed, now writing to counter ...")
    QtUpdate()
    writeNewConfig(bytes(gcfg))

    # reread some settings
    setGEMFPowerIcon(getconfig=True)

    setIndent(0)
    setNormalCursor()


def writeNewConfig(newcfg):
    """Writes the modified config to the counter"""

    # write the new config data
    writeGEMF_ConfigFull(newcfg)
    fprint("Done. New configuration is transferred and activated.")
    QtUpdate()

    # verification of written data
    # PROBLEM:  the counter may overwrite some data (like date/time, MaxCPM) with new values, before verification is done!
    # print message but don't stop the programm
    rawcfg, _, _ = getGEMF_RawConfig()                          # read the raw config
    if verifyCFGwriting(newcfg, rawcfg):
        gdprint("compare is good")                              # ... and compare with intended config
        fprint("The Configuration was verified ok")
    else:
        rdprint ("compare is bad")                              # ... but ignore if comparison is bad
        qefprint("The Configuration did NOT verify ok!")
        qefprint("However, this could also result from a counter's change after the configuration had")
        qefprint("been written properly, like changing MaximumBytes. Verify manually by reloading the")
        efprint ("configuration.")


def verifyCFGwriting(old, new):
    """Compare a newly read CFG to a previous CFG"""

    # PROBLEM: some values in the config may be changed by the device between writing and
    # reading, resulting in non-identity. On an EMF390 none were identified so far

    defname  = "verifyCFGwriting: "
    verifyOK = True

    # check for same length
    if len(old) != len(new):
        errmsg  = "FAILURE trying to read from / write to the counter!\n"
        errmsg += "You can try to restart GeigerLog, but if the problem persists,\n"
        errmsg += "you may have to FACTORYRESET the counter!"
        edprint(errmsg)
        efprint(errmsg)
        verifyOK = False
    else:
        # length ok, check each byte
        for i in range(0, len(old)):
            if old[i] != new[i]:
                rdprint(defname + "Wrong byte at: addr:{:#05x} ({:3d}) written:{:#04x} read:{:#04x}".format(i, i, old[i], new[i]))
                verifyOK = False

    return verifyOK


#edit
def editGEMF_Configuration():
    """Edit the configuration from the GEMF config memory"""

    if not g.Devices["GEMF"][g.CONN] :
        g.exgg.showStatusMessage("No EMF Device Connected")
        return

    defname = "editGEMF_Configuration: "

    dprint(defname + "_" * 150)
    setIndent(1)

    # get a fresh config and show it
    cfg, error, errmessage = getGEMF_RawConfig()
    vprintGEMF_Config("Starting cfg", cfg)

    if error < 0 or cfg is None:
        efprint("Error:" + errmessage)
        setIndent(0)
        return

    # create GL dict
    setGEMF_Config4GL(cfg)

    # https://www.tutorialspoint.com/pyqt/pyqt_qlineedit_widget.htm
    # https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/

    setDefault = False      # i.e. False --> show what is read from device

    while True:
        fbox = QFormLayout()
        fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        # fbox.addRow(QLabel("<span style='font-weight:900;'>All GEMF Devices</span>"))

    # Power
        # changing the Power via the config is NOT possible!
        pmsg = "On" if isGEMF_PowerOn() == 'ON' else "Off"
        fbox.addRow(QLabel("Power State"), QLabel("<span style='font-weight:900;'>{}</span>".format(pmsg)))

    # Speaker
        r21 = QRadioButton("On")
        r22 = QRadioButton("Off")
        r21.setChecked(False)
        r22.setChecked(False)
        speakergroup = QButtonGroup()
        speakergroup.addButton(r21)
        speakergroup.addButton(r22)
        hbox2 = QHBoxLayout()
        hbox2.addWidget(r21)
        hbox2.addWidget(r22)
        hbox2.addStretch()
        fbox.addRow(QLabel("Speaker State           "), hbox2)
        if isGEMF_SpeakerOn() == 'ON':  r21.setChecked(True)
        else:                           r22.setChecked(True)

    # Saving State
        r31 = QRadioButton("On")
        r32 = QRadioButton("Off")
        r31.setChecked(False)
        r32.setChecked(False)
        alarmgroup = QButtonGroup()
        alarmgroup.addButton(r31)
        alarmgroup.addButton(r32)
        hbox1 = QHBoxLayout()
        hbox1.addWidget(r31)
        hbox1.addWidget(r32)
        hbox1.addStretch()
        fbox.addRow(QLabel("Saving State"), hbox1)
        # rdprint(defname, "cfgKeyLo['SpiSaveData'][0]: ", cfgKeyLo["SpiSaveData"][0], "  type:", type(cfgKeyLo["SpiSaveData"][0]))
        if cfgKeyLo["SpiSaveData"][0] == 1: r31.setChecked(True)
        else:                               r32.setChecked(True)

    # see: http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10559, Reply#4
    # EmfDev: "zero calibration feature has been removed."
    # # Zero Calibration
    #     zerotip   = "Enter a number 0.0 ... 4000.0"
    #     zerolimit = (0.0, 4000.0, 3)
    #     calzero   = cfgKeyLo["ZeroCalibration"][0]

    #     g.exgg.cal_zero = QLineEdit()
    #     g.exgg.cal_zero.setFont(g.fontstd)
    #     g.exgg.cal_zero.setValidator (QDoubleValidator(*zerolimit))
    #     g.exgg.cal_zero.setToolTip(zerotip)
    #     g.exgg.cal_zero.setText("{:0.6g}".format(calzero))

    #     fbox.addRow("Zero Calibration", g.exgg.cal_zero)

    ###############################################################################

    # create dialog
        dialog = QDialog()
        dialog.setWindowIcon(g.iconGeigerLog)
        dialog.setFont(g.fontstd)
        dialog.setWindowTitle("Edit Configuration of: {}".format(g.GEMF_DeviceDetected))
        dialog.setWindowModality(Qt.WindowModality.WindowModal)
        dialog.setMinimumWidth(400)

        # buttonbox: https://srinikom.github.io/pyside-docs/PySide/QtGui/QDialogButtonBox.html
        bbox = QDialogButtonBox()
        bbox.setStandardButtons(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        bbox.rejected.connect           (lambda: dialog.done(0))    # cancel, ESC key
        bbox.accepted.connect           (lambda: dialog.done(1))    # ok

        layoutV   = QVBoxLayout(dialog)
        layoutV.addLayout(fbox)
        layoutV.addWidget(bbox)

        popupdlg = dialog.exec()  # execute dialog #################################################################

        if   popupdlg == 0:
            setIndent(0)
            return                                  # reject (Cancel, ESC)
        elif popupdlg == 1:     break               # accept; end while
        elif popupdlg == 2:     setDefault = False  # help, Apply ... i.e. show what is read from device
        elif popupdlg == 3:     setDefault = True   # reset           i.e. show what is defined in the GeigerLog config

    # while loop ends here

    ndx = 0
    cfgKeyLo["Speaker"]        [ndx] = 1 if r21.isChecked() else 0
    cfgKeyLo["SpiSaveData"]    [ndx] = 1 if r31.isChecked() else 0

    ### begin local def ####################
    def getCalibValue(calibtext, type):
        """convert text to float or int"""

        defname = "getCalibValue: "

        # rdprint(defname, "calibtext: ", calibtext)
        if type == "float":
            try: val = float(calibtext)
            except Exception as e:
                exceptPrint(e, defname)
                val = g.NAN
        else:
            try:
                val = int(float(calibtext))
            except Exception as e:
                exceptPrint(e, defname)
                val = 0

        # rdprint(defname, "calibtext:{}, packstring:{}, val:{}".format(calibtext, type, val))
        return val

    ### end local def ####################

    # zerocalib = getCalibValue(g.exgg.cal_zero.text(), "float")
    # cfgKeyLo["ZeroCalibration"] [ndx] = zerocalib

    # fprint(header("Sending New Configuration to Counter"))
    fprint(header("Updating Device with New Configuration"))

    QtUpdate()
    replaceGEMF_ConfigValues()

    setIndent(0)


def getGEMF_SerialNumber(usbport, baudrate):
    # 13. get serial number
    # Command: <GETSERIAL>>
    # Return: serial number in 7 bytes.
    # NOTE: ist wohl falsch; mein Gerät zeigt 12 bytes an:
    #       5C 28 34 36 39 37
    #       14 00 48 36 37 31

    defname = "getGEMF_SerialNumber: "
    dprint(defname)
    setIndent(1)

    try:
        with serial.Serial(usbport, baudrate=baudrate, timeout=g.GEMF_timeoutR, write_timeout=g.GEMF_timeoutW) as ABRser:
            bwrt  = ABRser.write(b'<GETSERIAL>>')
            brec  = ABRser.read(7)                       # get the GEMF device serial number
            brec += getWaitBytes(ABRser)

    except Exception as e:
        errmessage1 = defname + "FAILURE: Reading Serial Number from device; returning None"
        exceptPrint(e, errmessage1)
        setIndent(0)
        return None

    hexbrec = " ".join(f"{byte:02X}" for byte in brec)
    dprint(defname, "brec: ", brec, " ", hexbrec)

    ###################################################################################
    # DSID - 2nd part of serial number sometimes needed when upgrading firmware
    # response scheint auf 8 char begrenzt zu sein?
    try:
        with serial.Serial(usbport, baudrate=baudrate, timeout=g.GEMF_timeoutR, write_timeout=g.GEMF_timeoutW) as ABRser:
            bwrt  = ABRser.write(b'<DSID>>')
            brec  = ABRser.read(6)        # if DSID is not supported, then the response is \x00 (up to 8 char when so requested)
            brec += getWaitBytes(ABRser)

    except Exception as e:
        exceptPrint(e, defname + "FAILURE: Reading DSID Serial Number from device")

    hexDSID = " ".join(f"{byte:02X}" for byte in brec)
    dprint(defname, "DSID: ", brec, "  ", hexDSID)
    ###################################################################################

    setIndent(0)

    return hexbrec + "  DSID: " + hexDSID


def getGEMF_Datetime(force=False):
    """Get DateTime from the GEMF device"""

    # 25. Get year date and time
    # command: <GETDATETIME>>
    # Return: Seven bytes data: YY MM DD HH MM SS 0xAA

    # return: date and time in the format:
    #           YYYY-MM-DD HH:MM:SS
    # e.g.:     2017-12-31 14:03:19
    #
    # <GETDATETIME>> yields: rec: b'\x12\x04\x13\x0c9;\xaa' , len:7
    #                for:         2018-04-19 12:57:59
    #
    # duration: calling <GETDATETIME>> :  < 45    ms        on GMC-300S @ 57600 baud
    #           1 print cmd            :  <  0.4  ms
    #           Other                  :  <  0.02 ms


    defname = "getGEMF_Datetime: "
    # cdprint(defname)
    setIndent(1)

    dtrec  = "2000-01-01 00:00:01" # default fake date to use on error

    if not force:
        if g.logging:
            emsg = "Cannot get GEMF DateTime when logging. Stop logging first"
            return (dtrec, -1, emsg)

    # this call takes < 45 ms
    # dstart  = time.time()
    rec, error, errmessage = serialGEMF_COMM(b'<GETDATETIME>>', 7, orig(__file__))
    # ddur1   = 1000 * (time.time() - dstart)

    if rec is None:
        dprint(defname + "ERROR: no DateTime received - ", errmessage)
    else:
        if error == 0 or error == 1:  # Ok or only-Warning
            try:
                dtrec = dt.datetime(rec[0] + 2000, rec[1], rec[2], rec[3], rec[4], rec[5])
            except Exception as e:
                # conversion of counter values to Python DateTime failed
                # dtrec       = "2099-09-09 09:09:09" # overwrite rec with fake date
                error       = -1
                errmessage  = "ERROR getting DateTime"
                if rec ==  [0, 1, 1, 0, 0, 80, 170]:    # the values found after first start! ??? sec is 80, das kann nicht sein???
                    errmessage  += " - Set at device first!"

        else:   # a real error
            dprint(defname, "ERROR getting DATETIME: ", errmessage)

        # cdprint(defname + "raw: len: {} rec: {}   parsed: {}  errmsg: '{}'".format(len(rec), str(rec), dtrec, errmessage))

    # ddur2  = 1000 * (time.time() - dstart)
    # rdprint(defname, "dur <GETDATETIME>>:{:0.3f}ms  dur total: +{:0.3f}ms  GEMF DateTime={} - {}=CompTime".format(ddur1, ddur2 - ddur1, dtrec, stime()[-5:]))

    setIndent(0)

    return (dtrec, error, errmessage)


def getGEMF_Mode():
    # 7. Get the current mode
    # Command:	<GETMODE>>
    # Return: 	Current Mode in text
    # 		e.g.:  64.00 - 108.00 MHz  MHz
    # 		e.g2: Vertical EMF/EF

    defname = "getGEMF_Mode: "
    dprint(defname)
    setIndent(1)

    rec, error, errmessage = serialGEMF_COMM(b'<GETMODE>>', 5, orig(__file__))
    dprint(defname + f"raw: rec={rec}, err={error}, errmessage='{errmessage}'")

    if error in (0, 1):             # Ok or Warning
        srec = rec.decode("UTF-8", errors="replace")
    else:
        srec = f"Failure getting MODE data:  rec='{rec}' errmsg='{errmessage}"

    dprint(defname, "(srec, error, errmessage): ", (rec, error, errmessage))
    setIndent(0)

    return (srec, error, errmessage)


def getGEMF_GYRO():
    # 26. Get gyroscope data
    # command: <GETGYRO>>
    # Return: Seven bytes gyroscope data in hexdecimal: BYTE1,BYTE2,BYTE3,BYTE4,BYTE5,BYTE6,BYTE7
    # 	Here: BYTE1,BYTE2 are the X position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    # 	      BYTE3,BYTE4 are the Y position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    # 	      BYTE5,BYTE6 are the Z position data in 16 bits value. The first byte is MSB byte data and second byte is LSB byte data.
    # 	      BYTE7 always 0xAA

    defname = "getGEMF_GYRO: "

    dprint(defname)
    setIndent(1)

    if not g.GEMF_HasGyroCommand:
        (rec, error, errmessage) = "Gyro not supported", -1, "Unsupported on this device"
        dprint(defname, "(rec, error, errmessage): ", (rec, error, errmessage))
        setIndent(0)
        return (rec, error, errmessage)

    rec, error, errmessage = serialGEMF_COMM(b'<GETGYRO>>', 7, orig(__file__))
    dprint(defname + "raw: rec={}, err={}, errmessage='{}'".format(rec, error, errmessage))

    if error in (0, 1):             # Ok or Warning
        x = rec[0] * 256 + rec[1]
        y = rec[2] * 256 + rec[3]
        z = rec[4] * 256 + rec[5]
        srec = "X=0x{:04x}, Y=0x{:04x}, Z=0x{:04x}   ({}, {}, {})".format(x, y, z, x, y, z)
    else:
        srec = "Failure getting Gyro data:  rec='{}' errmsg='{}".format(rec, errmessage)

    dprint(defname, "(srec, error, errmessage): ", (srec, error, errmessage))
    setIndent(0)

    return (srec, error, errmessage)


def setGEMF_POWEROFF():
    # 14. Power OFF
    # Command: <POWEROFF>>
    # Return: none (Turns off the device)

    # sleeping after Power OFF
    #   using 3 sec to be safe

    defname = "setGEMF_POWEROFF: "

    setBusyCursor()
    fprint(header("Switch Power OFF"))
    fprint("Please, wait ...")
    QtUpdate()

    rec  = serialGEMF_COMM(b'<POWEROFF>>', 0, orig(__file__))
    dprint("setGEMF_POWEROFF: ", rec)

    time.sleep(3)

    powerstate = setGEMFPowerIcon(getconfig=True)
    dprint(defname, "Device Power State:", powerstate)
    fprint("Device Power State:", powerstate)
    setNormalCursor()

    return rec


def setGEMF_POWERON():
    # 27. Power ON
    # Command: <POWERON>>
    # Return: none

    # sleeping after Power ON
    #   using 3 sec to be safe, as for setGEMF_POWEROFF

    defname = "setGEMF_POWERON: "

    setBusyCursor()
    fprint(header("Switch Power ON"))
    fprint("Please, wait ...")
    QtUpdate()

    rec  = serialGEMF_COMM(b'<POWERON>>', 0, orig(__file__))
    dprint("setGEMF_POWERON: ", rec)

    time.sleep(3)

    powerstate = setGEMFPowerIcon(getconfig=True)
    dprint(defname, "Device Power State:", powerstate)
    fprint("Device Power State:", powerstate)
    setNormalCursor()

    return rec


def setGEMFPowerIcon(getconfig=True):
    """Sets the GEMF Power-Icon in the toolbar"""

    # return isGEMF_PowerOn(getconfig=getconfig)           # includes the actual setting of the Power-Icon
    return isGEMF_PowerOn(getconfig=True)           # includes the actual setting of the Power-Icon


def toggleGEMFPower():
    """Toggle GEMF device Power ON / OFF"""

    if g.logging:
        g.exgg.showStatusMessage("Cannot change power when logging! Stop logging first")
        return

    if isGEMF_PowerOn(getconfig=True) == "ON":  setGEMF_POWEROFF()
    else:                                       setGEMF_POWERON()


def setGEMF_REBOOT():
    # 23. Reboot unit
    # command: <REBOOT>>
    # Return: REBOOT            # wirklich???

    defname = "setGEMF_REBOOT: "
    dprint(defname)
    setIndent(1)

    rec  = serialGEMF_COMM(b'<REBOOT>>', 0, orig(__file__))
    dprint(defname, rec)
    time.sleep(0.6)

    setIndent(0)
    return rec


def setGEMF_FACTORYRESET():
    # 22. Reset unit to factory default
    # command: <FACTORYRESET>>
    # Return: 0xAA

    defname = "setGEMF_FACTORYRESET: "
    dprint(defname)
    setIndent(1)

    rec  = serialGEMF_COMM(b'<FACTORYRESET>>', 1, orig(__file__))
    dprint(defname, rec)
    time.sleep(0.1)
    dprint(defname + "Done")
    setIndent(0)

    return rec


#
# Derived commands and functions
#

def getGEMF_DeltaTime(force=False):
    """reads the DateTime from both computer and device, converts into a number, and returns delta time in sec"""

    defname = "getGEMF_DeltaTime: "
    # cdprint(defname)
    # setIndent(1)
    time_delta = g.NAN

    recDateTime, error, errmessage = getGEMF_Datetime(force=force)       # recDateTime like: "2000-01-01 00:00:01"
    if error < 0:
        # error occurred
        edprint(defname + "recDateTime:{}, error:{}, errmessage:'{}'".format(recDateTime, error, errmessage))

    else:
        # ok or only Warning
        time_computer = longstime()
        time_device   = str(recDateTime)
        time_delta    = round((mpld.datestr2num(time_computer) - mpld.datestr2num(time_device)) * 86400, 3)
        if   time_delta > 0:  tmsg = "Device is slower"
        elif time_delta < 0:  tmsg = "Device is faster"
        else:                 tmsg = "same"
        cdprint(defname + "device:{}, computer:{}, Delta Comp ./. Dev: {:+0.1f} sec - {}".format(time_device, time_computer, time_delta, tmsg))

        # setIndent(0)

    return (time_delta, recDateTime)


def isGEMF_PowerOn(getconfig=False):
    """Checks Power status in the configuration
    returns: ON, OFF, or UNKNOWN as string"""

    # PowerOnOff byte:
    # 300 series
    #   at config offset  : 0       :    0 for ON and 255 for OFF
    #   http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=4948  Reply #14
    #   confirmed in Reply #17
    #

    defname = "isGEMF_PowerOn: "
    dprint(defname)
    setIndent(1)

    if getconfig:
        cfg, error, _ = getGEMF_RawConfig()      # get the raw config, be it real or simulated
        if error == 0:
            g.GEMF_cfg = cfg                     # set the cfg global value
            power     = g.GEMF_cfg[0]
        else:
            msg = "Failure reading the counter's config - Is counter connected?"
            rdprint(defname, msg)
            QueuefPrint(msg)
            power = -1                          # dummy value
    else:
        # use existing cfg
        power = g.GEMF_cfg[0]

    if   power == 0:        p = "ON"            # all counter
    elif power == 255:      p = "OFF"           # 300, 800 series
    elif power == 1:        p = "OFF"           # 500, 600 series
    else:                   p = "Unknown"
    dprint(defname, p)

    if   p == "ON":   g.exgg.dbtnGEMFPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_on.png'))))
    elif p == "OFF":  g.exgg.dbtnGEMFPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_off.png'))))
    else:             g.exgg.dbtnGEMFPower.setIcon(QIcon(QPixmap(os.path.join(g.resDir, 'icon_power-round_X.png'))))

    setIndent(0)
    return p


def isGEMF_AlarmOn():
    """Checks Alarm On status in the configuration.
    Alarm is at offset:1"""

    try:    c = g.GEMF_cfg[1]
    except: return "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    elif c == 255:          p = "ON"    # stimmt das so?
    else:                   p = c

    return p


def isGEMF_SpeakerOn():
    """Checks Speaker On status in the configuration.
    Speaker is at offset:2"""

    try:    c = g.GEMF_cfg[1]
    except: return "UNKNOWN"

    if   c == 0:            p = "OFF"
    elif c == 1:            p = "ON"
    elif c == 255:          p = "ON"        # stimmt das so?
    else:                   p = c

    return p


def getLightStatus():

    c =  g.GEMF_cfg[3]

    # if   c == 0     : p = "Light: OFF"
    # elif c == 1     : p = "Light: ON"
    # elif c is None  : p = "Light: Unknown"
    # else            : p = "Timeout: {} sec".format(c - 1)

    return c


def serialGEMF_COMM(sendtxt, RequestLength, caller=("", "", -1)):
    """open the port to make the serial call
    return: (brec, error, errmessage)
    """
    # brec:       bytes as received
    # error==0:   OK
    # error==1:   Warning
    # error==-1:  ERROR
    # errmessage: <string>

    defname = "serialGEMF_COMM: "
    # dprint(defname)
    setIndent(1)

    brec        = b""
    error       = -1
    errmessage  = "Error Message is Undefined"

    if g.GEMF_usbport is not None and os.path.exists(g.GEMF_usbport):
        while g.GEMF_USBportBusy:
            time.sleep(0.1)

        # USB port exists
        try:
            g.GEMF_USBportBusy = True
            with  serial.Serial(g.GEMF_usbport, g.GEMF_baudrate, timeout=g.GEMF_timeoutR, write_timeout=g.GEMF_timeoutW) as g.GEMFser:
                brec, error, errmessage = origserialGEMF_COMM(sendtxt, RequestLength, serhandle=g.GEMFser, caller=caller)

        except Exception as e:
            exceptPrint(e, defname + "'{}'".format(errmessage))

        finally:
            g.GEMF_USBportBusy = False

    else:
        # USB port is missing
        errmessage  = f"USB port '{g.GEMF_usbport}' does not exist"
        rdprint(defname, errmessage)

    setIndent(0)
    return (brec, error, errmessage)


def origserialGEMF_COMM(sendtxt, RequestLength, serhandle, caller=("", "", -1)):
    """write to and read from serial port, exit on serial port error
    return: (brec, error, errmessage)
        brec:       bytes sequence as received
        error:      ==0:OK,  ==1:Warning,  ==-1:ERROR
        errmessage: string
    """

    defname = "origserialGEMF_COMM: "
    # rdprint(defname + "sendtxt:{}  RequestLength:{}  caller:'{}', serhandle-Port:{}".format(sendtxt, RequestLength, caller, serhandle.port))
    setIndent(1)

    if not os.path.exists(g.GEMF_usbport):
        # edprint("den shit gibbes nich")
        return (brec, -1, f"FAILURE: The port '{g.GEMF_usbport}' does not exist. Is the device still plugged in?")

    brec        = b""
    error       = 0
    errmessage  = ""

    while True:

    #write sendtxt to serial port
        startwtime   = time.time()
        srcinfo      = ""
        writeSuccess = False
        try:
            bwrt         = serhandle.write(sendtxt)          # bwrt = no of bytes written
            writeSuccess = True

        except serial.SerialTimeoutException as e:
            # Exception that is raised ONLY on WRITE timeouts.
            srcinfo = f"SerialTimeoutException"
            srce    = e

        except serial.SerialException as e:
            srcinfo = f"SerialException"
            srce    = e

        except Exception as e:
            srcinfo = f"Exception"
            srce    = e

        # exit on write failure
        if not writeSuccess:
            srcinfo = defname + f"WRITE-to-Serial failed with {srcinfo} when writing {sendtxt}"
            exceptPrint(srce, srcinfo)
            terminateGEMF()
            brec       = b""
            error      = -1
            errmessage = defname + "FAILURE: WRITE-to-Serial failed. See log for details"
            break

        wdur = 1000 * (time.time() - startwtime)
        # cdprint(defname + f"WRITE: caller is: {caller[0]} in line no: {caller[2]} duration: {wdur:0.1f} ms")  # about 0.1 ms


    # read from serial port
        startrtime = time.time()

        readSuccess = False
        srcinfo     = ""
        srce        = ""

        try:
            brec  = serhandle.read(RequestLength)
            brec += getWaitBytes(serhandle)
            # mdprint(defname, "brec: ", brec)
            readSuccess = True

        except serial.SerialException as e:
            srcinfo = "SerialException"
            srce    = e

        except Exception as e:
            srcinfo = "Exception"
            srce    = e

        if not readSuccess:
            srcinfo = defname + f"READ-from-Serial failed with {srcinfo} when reading {RequestLength} bytes"
            exceptPrint(srce, srcinfo)
            terminateGEMF()
            brec        = b""
            error       = -1
            errmessage = defname + "FAILURE: READ-from-Serial. See log for details"
            break

        rdur = 1000 * (time.time() - startrtime)
        # cdprint(defname + f"READ:  caller is: {caller[0]} in line no: {caller[2]} duration: {rdur:0.1f} ms")

    # Retry loop - if len(brec) < RequestLength
        if len(brec) < RequestLength:
            efprint("{} Got {} data bytes, expected {} for call '{}'.".format(stime(), len(brec), RequestLength, cleanHTML(sendtxt)))

            # check for read timeout
            if rdur > (g.GEMF_timeoutR * 1000):
                # yes, a read timeout
                msg  = "{} GEMF TIMEOUT ERROR Serial Port; command {} exceeded {:3.1f}s".format(stime(), sendtxt, g.GEMF_timeoutR)
                qefprint(cleanHTML(msg)) # escaping needed as GEMF commands like b'<GETCPS>>' have <> brackets
                edprint(defname + msg, " - rdur:{:5.1f} ms".format(rdur))

            efprint("{} Got {} data bytes, expected {} for call '{}'.".format(stime(), len(brec), RequestLength, cleanHTML(sendtxt)))
            qefprint("{} Retrying.".format(stime()))
            QtUpdate()

            edprint(defname + "ERROR: Received length: {} is less than requested: {}".format(len(brec), RequestLength))
            # edprint(defname + "brec (len={}): {}".format(len(brec), BytesAsHex(brec)))

            # RETRYING
            count    = 0
            countmax = 3
            while True:
                count += 1
                errmsg = defname + "RETRY to get full return record, retrial #{}".format(count)
                dprint(errmsg)

                time.sleep(0.5)                         # extra sleep after not reading enough data
                extra = getWaitBytes(serhandle)         # just to make sure the pipeline is clean

                serhandle.write(sendtxt)

                rtime = time.time()
                brec   = serhandle.read(RequestLength)
                dprint("Timing (ms): Retry read:{:6.3f}".format(1000 * (time.time() - rtime)))

                if len(brec) == RequestLength:
                    bah = BytesAsHex(brec)
                    if len(bah) > 50: sbah = ", brec (1st 20 Bytes): " + bah[:20]
                    else:             sbah = ", brec:" + bah
                    dprint(defname + "RETRY: OK now. Length is {} bytes as requested. Continuing normal cycle".format(len(brec)), sbah)
                    errmessage += "; ok after {} retry".format(count)
                    extra = getWaitBytes(serhandle)   # just to make sure the pipeline is clean
                    fprint("<green>{} Retry successful.".format(stime()))
                    addGEMF_Error(errmessage)
                    break
                else:
                    dprint(u"RETRY:" + defname + "RequestLength is {} bytes. Still NOT ok; trying again".format(len(brec)))
                    pass

                if count >= countmax:
                    dprint(defname + "RETRY: Retried {} times, always failure, giving up. Serial communication error.".format(count))
                    error       = -1
                    errmessage  = "ERROR communicating via serial port. Giving up."
                    efprint(errmessage)
                    addGEMF_Error(errmessage)
                    break

                efprint("ERROR communicating via serial port. Retrying again.")

        break

    setIndent(0)

    # rdprint(defname, "(brec, error, errmessage): ", (brec, error, errmessage))
    return (brec, error, errmessage)


def makeClockCorrectionGEMF():
    """Correct the device clock with the GeigerLog clock"""

    GEMF_WriteDateTime()
    g.GEMF_NextCorrMin = (getMinute() + g.GEMF_ClockCorrection) % 60


def GEMF_setDateTime():
    """ set date and time on GEMF device to computer date and time"""

    defname = "GEMF_setDateTime: "
    dprint(defname)
    setIndent(1)

    fprint(header("Set DateTime of EMF Device"))
    fprint("Setting Device DateTime to GeigerLog DateTime")

    GEMF_WriteDateTime()

    tmsg = getDeltaTimeMessage(*getGEMF_DeltaTime())
    fprint(tmsg)

    dprint(defname, "GEMF Datetime was set")
    setIndent(0)


def getGEMF_ClockDelta():
    """Checking Clock Drift -
    return: Delta of time_computer minus time_device in seconds - negative: device is faster
            Duration of call in ms
    """

    cstart = time.time()

    defname = "getGEMF_ClockDelta: "
    # mdprint(defname)
    setIndent(1)

    clock_delta = g.NAN
    printFlag   = True
    brec        = b""
    try:
        with serial.Serial(g.GEMF_usbport, baudrate=g.GEMF_baudrate, timeout=1, write_timeout=0.5) as ABRser:
            bwrt = ABRser.write(b'<GETDATETIME>>')
            brec = ABRser.read(7)
            brec += getWaitBytes(ABRser)
            # ydprint(defname, "brec: ", brec, "  ", " ".join(f"{x:2d}" for x in brec))

    except Exception as e:
        exceptPrint(e, defname)

    else:
        # successful read
        if   brec == b'\x00\x00\x00\x00\x00\x00\xaa':
            # check for broken clock; in GMC-500:  --> brec = b'\x00\x00\x00\x00\x00\x00\xaa'
            rdprint(defname, f"Broken clock - brec: {brec}")

        elif brec == b'\x01\xf4\x01\xf4\x01\xf4\x01':
            # was observed; reason unknown
            rdprint(defname, f"FAILURE Clock reading - brec: {brec}")

        elif brec == b'ddddddd':
            # was observed; reason unknown
            rdprint(defname, f"FAILURE Clock reading - brec: {brec}")

        else:
            if len(brec) >= 6:
                try:
                    datetime_device    = str(dt.datetime(brec[0] + 2000, brec[1], brec[2], brec[3], brec[4], brec[5]))
                    timestamp_device   = mpld.datestr2num(datetime_device)                      # days

                    datetime_computer  = stime()
                    timestamp_computer = mpld.datestr2num(datetime_computer)                    # days
                    # ydprint(defname, "datetime_computer: ", datetime_computer, "  timestamp_computer: ", timestamp_computer)

                    timestamp_delta    = (timestamp_computer - timestamp_device) * 86400        # --> sec
                    # ydprint(defname, f"datetime_device: {datetime_device}  timestamp_device: {timestamp_device}   Delta: {timestamp_delta:0.1f} sec")

                    rounding           = 3 # count of decimals
                    clock_delta        = round(timestamp_delta, rounding)  # delta time in sec

                except Exception as e:
                    exceptPrint(e, "converting to time, and calculating clock delta")

                else:
                    printFlag = False
            else:
                rdprint(defname, "response is too short - brec: ", brec, "  len(brec): ", len(brec), "   ", " ".join(str(x) for x in brec))

    if printFlag: ydprint(defname, "brec: ", brec, "  ", " ".join(f"{x:2d}" for x in brec))

    cdur = 1000 * (time.time() - cstart)
    # mdprint(defname, f"Clock Delta is: {clock_delta} s   dur: {cdur:0.1f} ms")

    setIndent(0)
    return (clock_delta, cdur)


def GEMF_WriteDateTime():
    """Write DateTime to counter"""

    # 24. Set year date and time
    # command: <SETDATETIME[YYMMDDHHMMSS]>>
    # Return: 0xAA

    defname = "GEMF_WriteDateTime: "
    # ydprint(defname)

    # convert Computer DateTime to byte sequence format needed by device
    timelocal     = list(time.localtime())          # timelocal: 2018-04-19 13:02:50 --> [2018, 4, 19, 13, 2, 50, 3, 109, 1]
    timelocal[0] -= 2000
    btimelocal    = bytes(timelocal[:6])
    # rdprint(defname, "Setting DateTime:  now:", timelocal[:6], ", coded:", btimelocal)

    # write DATETIME as Byte-sequence to the device
    try:
        with serial.Serial(g.GEMF_usbport, baudrate=g.GEMF_baudrate, timeout=3, write_timeout=0.5) as ABRser:
            bwrt  = ABRser.write(b'<SETDATETIME' + btimelocal + b'>>')    # returns bwrt: Number of bytes written, type: <class 'int'>
            brec  = ABRser.read(1)                                        # returns brec: b'\xaa'                  type: <class 'bytes'>
            brec += getWaitBytes(ABRser)
            # rdprint(defname, "brec: ", brec)
    except Exception as e:
        msg = "DateTime could NOT be set!"
        exceptPrint(e, defname + msg)
        QueuefPrint(msg)
        QueueSoundDBG("burp")


def fprintGEMF_ConfigMemory():
    """prints the 256 or 512 bytes of device configuration memory to the NotePad"""

    defname = "fprintGEMF_ConfigMemory: "
    setBusyCursor()

    fprint(header("EMF Device Configuration"))
    dprint(defname)
    setIndent(1)

    cfg, error, errmessage = getGEMF_RawConfig()

    fText = ""
    if   cfg is None:
        msg = "FAILURE getting config from device. See log for details."
        dprint(defname + msg + " errmessage: " + errmessage)
        fText += msg
    else:
        lencfg = len(cfg)
        if error < 0 and lencfg not in (256, 512):
            msg = "FAILURE getting config from device. See log for details."
            dprint(defname + msg + " errmessage: " + errmessage)
            fText += msg
        else:
            # len(cfg) == 256 or == 512, even with error
            fText     += "The size of the configuration memory is: {} bytes\n".format(lencfg)
            fText     += "|Index | |------------ HEX -------------|   |------------------ DEC ------------------|\n"
            cfgcopy    = copy.copy(cfg)                 # use copy of cfg
            cfgstrp    = cfgcopy.rstrip(b'\xFF')        # remove the right-side FF values

            lencfgstrp = len(cfgstrp)
            if lencfgstrp == 0:
                fText += "ERROR: GEMF Configuration memory is empty. Try a factory reset!"
            else:
                rr = 10
                for i in range(0, lencfgstrp, rr):
                    pcfg = "{:3d}:{:03X}:  ".format(i, i)
                    for j in range(0, rr):
                        k = i + j
                        if j == 5: pcfg += " "
                        # if k < lencfgstrp:  pcfg += "{:02x} ".format(cfgstrp[k])
                        if k < lencfgstrp:  pcfg += "{:02X} ".format(cfgstrp[k])

                    pcfg += "    "
                    # print("k: ", k, "lencfgstrp % rr: ", lencfgstrp % rr)
                    if k >= lencfgstrp: pcfg += "   " * (rr - (lencfgstrp % rr))

                    for j in range(0, rr):
                        k = i + j
                        if j == 5: pcfg += "  "
                        if k < lencfgstrp:  pcfg += "{:3d} ".format(cfgstrp[k])

                    fText += pcfg + "\n"

                if lencfgstrp < lencfg:
                    # fText += "Remaining {} values up to address {} are all '0xff=255'\n".format(lencfg - lencfgstrp, lencfg - 1)
                    fText += "Remaining {} values up to address {} are all '0xFF=255'\n".format(lencfg - lencfgstrp, lencfg - 1)

                fText += "\nThe configuration as ASCII (byte 0xFF as 'F', other non-ASCII characters as '.'):\n"
                fText += cleanHTML(fBytesAsASCIIFF(cfgcopy))

    vprintGEMF_Config(defname, cfg)
    fprint(fText)

    setIndent(0)
    setNormalCursor()


def getInfoGEMF(extended=False, force=False):
    """builds string msg of basic or extended info on the GEMF device"""

    defname  = "getInfoGEMF: "
    dprint(defname)
    setIndent(1)

    tmp      = "{:30s}{}\n"
    gemfinfo  = ""
    gemfinfo += tmp.format("Configured Connection:", "Port:'{}' Baud:{} Timeouts[s]: R:{} W:{}".format(
        g.GEMF_usbport,
        g.GEMF_baudrate,
        g.GEMF_timeoutR,
        g.GEMF_timeoutW)
    )

    if not g.Devices["GEMF"][g.CONN]:
        msg = "Device is not connected"
        dprint(msg)
        setIndent(0)
        return gemfinfo + "<red>" + msg + "</red>"

    # device name
    gemfinfo += tmp.format("Connected Device:", g.GEMF_DeviceDetected)

    # GEMF_Variables
    gemfinfo += tmp.format("Configured Variables:", g.GEMF_Variables)

    # Tube sensitivities
    gemfinfo += getTubeSensitivities(g.GEMF_Variables)

    # handle info request when logging
    if g.logging and g.GEMF_getInfoFlag == 0:
        if extended :   g.GEMF_getInfoFlag = 2
        else:           g.GEMF_getInfoFlag = 1

        while g.GEMF_getInfoFlag > 0:
            time.sleep(0.01)

        setIndent(0)
        return g.GEMF_DatetimeMsg

    else:
        # not logging or g.GEMF_getInfoFlag > 0
        # time check
        gemfinfo += getDeltaTimeMessage(*getGEMF_DeltaTime(force=True))

        # read the cfg
        cfg, error, errmessage = getGEMF_RawConfig()
        g.GEMF_cfg = cfg
        vprintGEMF_Config(defname, cfg)
        setGEMF_Config4GL(cfg)

        # power state
        gemfinfo += tmp.format("Device Power State:", isGEMF_PowerOn(getconfig=False))
        gemfinfo += "\n"

        # Last Commands and Responses
        if not extended:
            for vname, response in g.GEMF_lastResp.items():
                gemfinfo += tmp.format("Device Last Data Response:", f"{vname:<6s}: {g.GEMF_VariablesMap[vname]:3s}: {response}")

    if extended:
        gemfinfo += tmp.format("Extended Info:", "")

        # Last Commands and Responses
        for vname, response in g.GEMF_lastResp.items():
            cmd  = g.GEMF_VariablesMap[vname]
            code = ((g.GEMF_Commands[cmd]).decode("utf-8", errors='replace') + " " * 30)[0:25]
            code = cleanHTML(code)
            gemfinfo += tmp.format("Device Last Data Response:", f"{vname:<6s}: {cmd:3s}: {code} {response}")
        gemfinfo += "\n"

        # saving history
        histstate = "ON" if cfgKeyLo["SpiSaveData"][0] == 1 else "OFF"
        gemfinfo += tmp.format("Device Saving History State:", histstate)

        # saving history SpiCircularAddress
        histmode = "Stop at 100%" if cfgKeyLo["SpiCircularAddress"][0] == 0 else "Circular"
        gemfinfo += tmp.format("Device Saving History Mode:", histmode)


        # Speaker state
        gemfinfo += tmp.format("Device Speaker State:", isGEMF_SpeakerOn())

        # # Alarm state
        # gemfinfo += tmp.format("Device Alarm State:", isGEMF_AlarmOn())

        # # Alarm level CPM
        # if g.GEMF_Model != "GMC-800":

        #     # CPMAlarmType = "Unknown"
        #     # try:
        #     #     AlarmCPM     = cfgKeyLo["AlarmCPMValue"][0]
        #     #     AlarmType    = cfgKeyLo["AlarmType"][0]
        #     #     CPMAlarmType = "Selected" if AlarmType == 0 else "NOT selected"
        #     # except Exception as e:
        #     #     exceptPrint(e, "Alarm level CPM")
        #     #     AlarmCPM = g.NAN

        #     if AlarmCPM is not None:
        #         try:
        #             gemfinfo += tmp.format("Device Alarm Level CPM:  ", "{:12s}: CPM:   {:<5.0f} (= µSv/h: {:5.3f})".format(CPMAlarmType, AlarmCPM, AlarmCPM / g.Sensitivity[0]))
        #         except Exception as e:
        #             exceptPrint(e, defname + "Alarmlevel" )
        #             rdprint(defname, "AlarmCPM: ", AlarmCPM)
        #             rdprint(defname, "g.Sensitivity[0]: ", g.Sensitivity[0])
        #             gemfinfo += tmp.format("Device Alarm Level CPM:  Undefined due to Exception")

        # else: # this is for GMC-800
        #     cfg, error, errmessage = getGEMF_RawConfig()
        #     ndx = 121 + 4 # single byte options?
        #     alarmcpm = struct.unpack(">I",    cfg [ndx: ndx + 4])[0]
        #     gemfinfo += tmp.format("Device Alarm Level CPM:  ", alarmcpm)


        # Alarm state
        gemfinfo += tmp.format("Device Alarm State EF:",   cfgKeyLoDefault["EFALARM"][0])
        gemfinfo += tmp.format("Device Alarm State EMF:",  cfgKeyLoDefault["EMFALARM"][0])
        gemfinfo += tmp.format("Device Alarm State RF:",   cfgKeyLoDefault["RFALARM"][0])

        # Zero calibration
        gemfinfo += tmp.format("Device Zero Calibration:", f"{cfgKeyLoDefault['ZeroCalibration'][0]:0.3f}")

        # Light state
        ls = getLightStatus()
        if   ls == 1:     sls = "Light ON"
        elif ls == 0:     sls = "Light OFF"
        else:             sls = str(ls -1) + " sec"
        gemfinfo += tmp.format("Device Backlight Timeout:", sls)


        # # get the current writing position in the History memory
        # try:
        #     wpos = getGEMF_HistWritePos()
        # except Exception as e:
        #     exceptPrint(e, "Getting HistWritePosition")
        # else:
        #     gemfinfo += tmp.format("Device Hist. Write position:", wpos)


        # Battery Voltage
        rec = getGEMF_VOLT()
        gemfinfo += tmp.format("Device Battery Voltage:", f"{rec}")

        # gyro
        rec, error, errmessage = getGEMF_GYRO()
        if error < 0: gemfinfo += tmp.format("Device Gyro Data:", errmessage)
        else:         gemfinfo += tmp.format("Device Gyro Data:", rec)

        # mode
        rec, error, errmessage = getGEMF_Mode()
        if error < 0: gemfinfo += tmp.format("Device Mode:", errmessage)
        else:         gemfinfo += tmp.format("Device Mode:", rec)

        # serial number of counter
        gemfinfo += "\n"
        gemfinfo += tmp.format("Device Serial Number:", "{}".format(getGEMF_SerialNumber(g.GEMF_usbport, g.GEMF_baudrate)))

        # Firmware settings
        fmt = "   {:27s}{}\n"
        ghc = "\nYour Configuration of GeigerLog for Counter's Firmware:\n"
        ghc += fmt.format("Memory (bytes):",                "{:,}".format(g.GEMF_memory))
        ghc += fmt.format("SPIRpage Size (bytes):",         "{:,}".format(g.GEMF_SPIRpage))
        ghc += fmt.format("Config Size (bytes):",           "{:}" .format(g.GEMF_configsize))
        ghc += fmt.format("Voltagebytes (1|5|None):",       "{:}" .format(g.GEMF_voltagebytes))
        ghc += fmt.format("Endianness (big | little):",     "{:}" .format(g.GEMF_endianness))

        gemfinfo += ghc

    setIndent(0)
    return gemfinfo


def eraseGEMF_HistoryData():
    """Erase all data in History memory"""

    defname = "eraseGEMF_HistoryData: "

    msg = QMessageBox()
    msg.setWindowIcon(g.iconGeigerLog)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("Erase History Data")
    msg.setText("All data saved into the device's <b>History memory</b> will be erased. A recovery is not possible.<br><br>Please confirm with OK, or Cancel")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
    msg.setEscapeButton(QMessageBox.StandardButton.Cancel)
    retval = msg.exec()

    if retval == QMessageBox.StandardButton.Ok:    # QMessageBox.StandardButton.Ok == 1024

        dprint(defname)
        setIndent(1)
        setBusyCursor()

        fprint(header("EMF Device Erase History Data"))
        fprint("Begin Erasing")
        QtUpdate()

        rec, err, errmessage = eraseGEMF_SPI()

        if err == 0 or err == 1:    fprint("Done Erasing")
        else:                       efprint("ERROR trying to Erase History Data: " + errmessage)

        setNormalCursor()
        setIndent(0)


def doREBOOT(force = False):
    """reboot the GEMF device"""

    if force:
        retval = QMessageBox.StandardButton.Ok
    else:
        msg = QMessageBox()
        msg.setWindowIcon(g.iconGeigerLog)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Reboot EMF Device")
        msg.setText("Rebooting your GEMF device.\n\nPlease confirm with OK, or Cancel")
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.setDefaultButton(QMessageBox.StandardButton.Cancel)
        msg.setEscapeButton(QMessageBox.StandardButton.Cancel)
        retval = msg.exec()

    if retval == QMessageBox.StandardButton.Ok:
        fprint(header("EMF Device Reboot"))
        QtUpdate()
        rec, err, errmessage = setGEMF_REBOOT()
        if err in (0, 1):    fprint("REBOOT completed")
        else:                fprint("ERROR in setGEMF_REBOOT: " + errmessage)


def doFACTORYRESET(force = False):
    """Does a FACTORYRESET of the GEMF device"""

    defname = "doFACTORYRESET: "

    d = QInputDialog()
    d.setWindowIcon(g.iconGeigerLog)
    warning ="""
<b>CAUTION</b> - You are about to reset the GEMF device to factory<br>
condition! All data and any changes of settings will be lost.<br><br>
If you want to proceed, enter the word <b>RESET</b> (in all capital)<br>
and press OK"""

    if force: text, ok = ("RESET", True)
    else:     text, ok = d.getText(None, 'RESET', warning)

    dprint(defname, "Entered text: ", text, ",  ok: ", ok)
    if ok:
        fprint(header("EMF Device FACTORYRESET"))
        QtUpdate()

        if text == "RESET":
            setBusyCursor()
            rec, err, errmessage = setGEMF_FACTORYRESET()
            if err in (0, 1): fprint("FACTORYRESET completed")
            else:             fprint("ERROR in setGEMF_FACTORYRESET: " + errmessage)

            time.sleep(3.5)     # some is needed, but how long???

            cfg, _, _ = getGEMF_RawConfig()
            setGEMF_Config4GL(cfg)
            setNormalCursor()
        else:
            fprint("Entry '{}' not matching 'FACTORYRESET' - Reset NOT done".format(text))


def getResponseAT(command):
    """communication with the ESP8266 chip in the counter"""

    defname = "getResponseAT: "

    print()
    dprint(defname + "for command: {}".format(command))
    setIndent(1)

    rec = g.GEMFser.write(command)  # rec = no of bytes written
    # print("bytes written: ", rec, "for command:", command)

    t0 = time.time()
    print("waiting for response ", end="", flush=True)
    while g.GEMFser.in_waiting == 0:
        print(".", end="", flush=True)
        time.sleep(0.2)
    print(" received after {:0.1f} sec".format(time.time() - t0))    #  ca 5 sec

    rec = b''
    t0 = time.time()
    while g.GEMFser.in_waiting > 0 or time.time() - t0 < 2:
        bw = g.GEMFser.in_waiting
        if bw > 0:
            # print("reading {:3d} bytes".format(bw), end="  ")
            newrec = g.GEMFser.read(bw)
            # print(newrec)
            rec += newrec
        else:
            print(".", end="", flush=True)
        time.sleep(0.2)
    print("\nfinal rec: ({} bytes) {}".format(len(rec), rec))

    setIndent(0)


def GEMF_TESTING():
    """put here any testing code, which can be called from the Devel menu"""

    defname = "GEMF_TESTING: "
    dprint(defname, "presently nothing is programmed in this function")


def vprintGEMF_Config(msg, cfg):
    """prints the GEMF memory config as Hex, Dec, ASCII to terminal"""

    defname = "vprintGEMF_Config: "

    # dprint(defname, " HEX    " + msg)
    dprint(msg, defname, " HEX    ")
    for ncfg in BytesAsHex(cfg).split("\n"):       dprint("   " + ncfg)

    dprint(msg, defname, " DEC    ")
    for ncfg in BytesAsDec(cfg).split("\n"):       dprint("   " + ncfg)

    dprint(msg, defname, " ASCII   ")
    dprint(defname, " print 0xFF as F, other non-printable ASCII as Blank")
    for ncfg in BytesAsASCIIFF(cfg).split("\n"):   dprint("   " + ncfg)


# def getGEMF_HistWritePos():
#     """Get the Write Position in the History memory"""

#     defname = "getGEMF_HistWritePos: "

#     dprint(defname)
#     setIndent(1)

#     RequestLength = 4
#     rec, error, errmessage = serialGEMF_COMM(b'<GetSPISA>>', RequestLength, orig(__file__))
#     writepos = (rec[0] << 16) | rec[1] << 8 | rec[2]        # rec[3] is always 0xaa, i.e. 3 valid bytes remain

#     dprint(defname + "GetSPISA: ReqLen={}  rcvd: rec={}  err={}  errmessage='{}'" .format(RequestLength, rec, error, errmessage))
#     dprint(defname + "GetSPISA: Write position: @Byte #{} (@{:0.3%} of memory)"   .format(writepos, writepos / g.GEMF_memory))

#     setIndent(0)

#     return "Byte #{} ({:0.3%} of memory)".format(writepos, writepos / g.GEMF_memory)


#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP

def getGEMF_DeviceProperties():
    """define a device and its parameters"""

    # NOTE: this def does NOT make any call to the device!

    # GETVER                    Model               nominal (observed)
    # GQ-EMF380Re 1.00,         EMF-380             ?.??    (?.??)
    # GQ-EMF390Re 1.00,         EMF-390             ?.??    (?.??)
    # GQ-EMF390v2Re 3.75        EMF-390             ?.??    (3.75)


    ## local begin ##############################################
    def showUnknownDeviceMsg(DeviceName, DModel, DFirmware):
        """call if any 'last resort' config had been reached"""

        defname = "showUnknownDeviceMsg: "

        msg  = f"<b>ATTENTION</b> A GEMF device '{DeviceName}' was detected, but of a so far unknown model / firmware!"
        msg += f"(Model: {DModel} Firmware: {DFirmware})"
        edprint(defname + msg)
        efprint(msg)
        qefprint("Review the 'Extended Info' for this GEMF device. You may have to edit the")
        qefprint("configuration file <b>geigerlog.cfg</b> to adapt the settings to this new device.")
    ## end local ################################################

    defname = "getGEMF_DeviceProperties: "
    dprint(defname)
    setIndent(1)


    #
    # default settings
    #
    GEMF_Variables               = "auto"
    GEMF_memory                  = 2**20                                 # 1 MByte
    GEMF_SPIRpage                = 4096                                  # 4k
    GEMF_HasGyroCommand          = True                                  # supports the command GETGYRO
    GEMF_HasRTC_Offset           = False                                 # EmfDef: From 1.04 for the S versions and 4.71 for the regular versions.
    GEMF_RTC_Offset              = +1                                    # correct 1 sec per hour as default; value is from -59 -> 59 seconds
    GEMF_HasHistory              = False                                 # True only for EMF-390 (state: July 2024)
    GEMF_endianness              = "little"
    # GEMF_endianness              = "big" # really can't be for EMF-390

    GEMF_DevDet                  = g.GEMF_DeviceDetected.split("Re")     # g.GEMF_DeviceDetected is set in function "getGEMF_Version()"
    GEMF_Model                   = GEMF_DevDet[0].strip()
    try:    GEMF_FWVersion       = float(GEMF_DevDet[1].strip())
    except: GEMF_FWVersion       = 0.0

    cdprint(defname, "GEMF_DeviceDetected: >{}<   GEMF_Model: >{}<   GEMF_FWVersion: >{}< (type: {})".
             format(g.GEMF_DeviceDetected, GEMF_Model, GEMF_FWVersion, type(GEMF_FWVersion)))


# EMF-360
    # full version e.g.: GQ-EMF360 ... (unknown)
    if "GQ-EMF360" in GEMF_Model:
        # ydprint(defname, f"###1### GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
        GEMF_configsize           = 256
        GEMF_voltagebytes         = 5
        GEMF_HasHistory           = False

        if   0 <= GEMF_FWVersion:           # so far the same for any version
            pass

        else:
            # last resort for "EMF-360" devices
            # ydprint(defname, f"###2###    GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
            showUnknownDeviceMsg(g.GEMF_DeviceDetected, GEMF_Model, GEMF_FWVersion)


# EMF-380
    # full version e.g.: GQ-EMF380Re 1.00
    elif "GQ-EMF380" in GEMF_Model:
        # ydprint(defname, f"###1### GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
        GEMF_configsize           = 256
        GEMF_voltagebytes         = 5
        GEMF_HasHistory           = False

        if   0 <= GEMF_FWVersion:           # so far the same for any version
            pass

        else:
            # last resort for "EMF-380" devices
            # ydprint(defname, f"###2###    GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
            showUnknownDeviceMsg(g.GEMF_DeviceDetected, GEMF_Model, GEMF_FWVersion)


# EMF-390
    # my test device:  GQ-EMF390v2Re 3.75   (9.7.2024)
    elif "GQ-EMF390" in GEMF_Model:
        # ydprint(defname, f"###3### GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
        GEMF_configsize           = 256
        GEMF_voltagebytes         = 5
        GEMF_HasHistory           = True

        if   0 <= GEMF_FWVersion:           # so far the same for any version
            pass

        else:
            # last resort for "EMF-390" devices
            # ydprint(defname, f"###4### GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
            showUnknownDeviceMsg(g.GEMF_DeviceDetected, GEMF_Model, GEMF_FWVersion)


# last resort
    else:
        # The very last resort:  If none of the above match, then this place will be reached.
        # Allows integrating unknown new (and also old) devices
        # ydprint(defname, f"###5### GEMF_Model: {GEMF_Model}  GEMF_FWVersion: {GEMF_FWVersion}")
        showUnknownDeviceMsg(g.GEMF_DeviceDetected, GEMF_Model, GEMF_FWVersion)

        GEMF_configsize           = 256              # all EMF are 256 bytes config memory
        GEMF_voltagebytes         = 5                # like in 500 series
        GEMF_HasGyroCommand       = True             # looks like all EMF support Gyro
        GEMF_HasRTC_Offset        = False            # ???
        GEMF_HasHistory           = False            # True only for EMF-390 (state: July 2024)



    # overwrite any "auto" values with defaults
    if g.GEMF_memory             == "auto" : g.GEMF_memory           = GEMF_memory
    if g.GEMF_SPIRpage           == "auto" : g.GEMF_SPIRpage         = GEMF_SPIRpage
    if g.GEMF_configsize         == "auto" : g.GEMF_configsize       = GEMF_configsize
    if g.GEMF_voltagebytes       == "auto" : g.GEMF_voltagebytes     = GEMF_voltagebytes
    if g.GEMF_endianness         == "auto" : g.GEMF_endianness       = GEMF_endianness
    if g.GEMF_HasGyroCommand     == "auto" : g.GEMF_HasGyroCommand   = GEMF_HasGyroCommand
    if g.GEMF_HasRTC_Offset      == "auto" : g.GEMF_HasRTC_Offset    = GEMF_HasRTC_Offset
    if g.GEMF_RTC_Offset         == "auto" : g.GEMF_RTC_Offset       = GEMF_RTC_Offset
    if g.GEMF_Variables          == "auto" : g.GEMF_Variables        = GEMF_Variables
    if g.GEMF_HasHistory         == "auto" : g.GEMF_HasHistory       = GEMF_HasHistory


    g.GEMF_Model              = GEMF_Model                # Model Name like 'GMC-500+'; extracted from g.GEMF_DeviceDetected
    g.GEMF_FWVersion          = GEMF_FWVersion            # Firmware Version like '1.18'; extracted from g.GEMF_DeviceDetected

    dpformat = defname + "  {:20s} : {}"
    dprint(dpformat.format("Detected device",        g.GEMF_DeviceDetected))
    dprint(dpformat.format("--> Model",              g.GEMF_Model))
    dprint(dpformat.format("--> Firmware Version",   g.GEMF_FWVersion))
    dprint(dpformat.format("GEMF_configsize",        g.GEMF_configsize))
    dprint(dpformat.format("GEMF_memory",            g.GEMF_memory))
    dprint(dpformat.format("GEMF_HasHistory",        g.GEMF_HasHistory))
    dprint(dpformat.format("GEMF_SPIRpage",          g.GEMF_SPIRpage))
    dprint(dpformat.format("GEMF_voltagebytes",      g.GEMF_voltagebytes))
    dprint(dpformat.format("GEMF_HasGyroCommand",    g.GEMF_HasGyroCommand))
    dprint(dpformat.format("GEMF_endianness",        g.GEMF_endianness))
    dprint(dpformat.format("GEMF_HasRTC_Offset",     g.GEMF_HasRTC_Offset))
    dprint(dpformat.format("GEMF_RTC_Offset",        g.GEMF_RTC_Offset))
    dprint(dpformat.format("GEMF_Variables",         g.GEMF_Variables))

    setIndent(0)

#### end getGEMF_DeviceProperties PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP
#PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP


#hhh
###############################################################################
### HISTORY stuff
###############################################################################


def fprintGEMF_HistDetails(hist=False):
    """prints byte count info to the NotePad, either on a hist given in the call
    parameter, or by reading the database"""

    defname = "fprintGEMF_HistDetails: "
    #print(defname, "hist:", hist)

    if hist == False:
        if g.hisConn is None:
            g.exgg.showStatusMessage("No data available")
            return

        fprint(header("Show History Binary Data Details"))
        fprint("from: {}\n".format(g.hisDBPath))

        hist    = gsup_sql.DB_readBinblob(g.hisConn)
        if hist is None:
            efprint("No binary data found in this database")
            return

    histlen     = len(hist)                  # Total length; could be any length e.g. when read from file
    histFF      = hist.count(b'\xFF')        # total count of FF bytes
    histAA      = hist.count(b'\xAA')        # total count of AA bytes

    histRC      = hist.rstrip(b'\xFF')       # after right-clip FF (removal of all trailing 0xff)
    histRClen   = len(histRC)                # total byte count
    histRCFF    = histRC.count(b'\xFF')      # total count of FF in right-clipped data

    fpformat = "{:40s} {} Bytes"
    fprint(fpformat.format("Binary data total byte count:"              , histlen))
    fprint(fpformat.format("Count of data bytes - w/o trailing 0xFF:"   , histRClen))
    fprint(fpformat.format("Count of 0xAA bytes - @Tags: Time, Data"    , histAA))
    fprint(fpformat.format("Count of 0xFF bytes - Total:"               , histFF))
    fprint(fpformat.format("Count of 0xFF bytes - Trailing:"            , histlen - histRClen))
    fprint(fpformat.format("Count of 0xFF bytes - Within data:"         , histRCFF))


def saveGEMF_HistBinaryData():
    """get the binary data from the database and save to *.bin file"""

    if g.hisConn is None:
        g.exgg.showStatusMessage("No data available")
        return

    fprint(header("Save History Binary Data to File"))
    fprint("from: {}\n".format(g.hisDBPath))

    hist    = gsup_sql.DB_readBinblob(g.hisConn)
    if hist is None:
        efprint("No binary data found in this database")
        return

    newpath = g.hisDBPath + ".bin"
    writeBinaryFile(newpath, hist)

    fprint("saved as file: " + newpath)


def makeGEMF_History(sourceHist):
    """make the History by reading data either from file or from device,
    parse them, sort them by date&time, and write into files"""

    # sourceHist can be only: ("GEMFDevice", "GEMFBinFile") in ggeiger.py

    defname = "makeGEMF_History: "

    str_data_origin = u"Downloaded {} from device '{}'"

    #
    # get binary HIST data - either from file or from device
    #
    if   sourceHist == "CSV File":
        return (0, "")

    elif sourceHist == "Database":
        return (0, "")

    elif sourceHist == "GEMFBinFile":
        hist    = readBinaryFile(g.binFilePath)

        if b"ERROR" in hist[:6]: # hist contains error message
            error = -1
            return (error, "ERROR: Cannot Make History: " + hist)

        if hist[0:11] == b"DataOrigin:":
            data_origin   = hist[11:128].rstrip(b' ').decode('UTF-8', errors='replace')
            data_originDB = (data_origin[11:30], data_origin[30+12:])
            dprint("DataOrigin: len:{}: {}".format(len(data_origin), data_origin))
            hist = hist[128:]

        else:
            data_origin   = str_data_origin.format("<Date Unknown>", "<Device Unknown>")
            data_originDB = ("<Date Unknown>", "<Device Unknown>")
            dprint("No Data-Origin label found")
            fprint("No Data-Origin label found")

            # Test auf die Bin File Länge. Wenn mit GQ's DV eingelesen
            # dann sind 256 Bytes zuviel eingelesen!!
            # Problem: wenn mit anderen Programmen eingelesen, irgendwelche
            # Werte können resultieren, wenn die Programme bei vielen FFs abschalten.
            lenhistold = len(hist)
            #print("len(hist):", lenhistold)
            if   len(hist) == 2**20 + 512:   hist = hist[0: 2**20]
            elif len(hist) == 2**16 + 256:   hist = hist[0: 2**16]

            msg = "Removed {} bytes from end of orginal binary file of {} bytes".format(lenhistold - len(hist), lenhistold)
            dprint(msg)
            fprint(msg)

    elif sourceHist == "GEMFDevice":
        data_origin   = str_data_origin.format(stime(), g.GEMF_DeviceDetected)
        data_originDB = (stime(), g.GEMF_DeviceDetected)

        if not os.path.exists(g.GEMF_usbport):
            # edprint("den shit gibbes nich")
            return (-1, f"FAILURE: The port '{g.GEMF_usbport}' does not exist. Is the device still plugged in?")

        fprint(f"Reading data from connected device: {g.GEMF_DeviceDetected}")

        hist    = b""
        page    = g.GEMF_SPIRpage           # 4096 bytes, see: getGEMF_DeviceProperties
        FFpages = 0                         # counting successive pages having only FF

        # # Cleaning pipeline BEFORE reading history
        # dprint(defname + "Cleaning pipeline BEFORE reading history")
        # extra = getGEMF_ExtraByte()

        start = time.time()
        cdprint(defname, f"GEMF_memory: {g.GEMF_memory}  page: {page}")
        for address in range(0, g.GEMF_memory, page): # prepare to read all memory
            spirstart = time.time()
            rec, error, errmessage = getGEMF_SPIR(address, page)
            spirdur   = 1000 * (time.time() - spirstart)
            try:    spirbpsec = page / spirdur
            except: spirbpsec = g.NAN
            fprint(f"Reading page of size {page} @address:{address:9d}  took{spirdur:6.1f} ms  kBytes/sec: {spirbpsec:6.1f}")
            QtUpdate()

            if error in (0, 1):
                hist += rec
                if error == 1: fprint("Reading error:", "Recovery succeeded")

                if rec.count(b'\xFF') == page:
                    gdprint (defname, "rec.count(b'\xFF'):", rec.count(b'\xFF'))
                    FFpages += 1
                else:
                    FFpages  = 0

                if not g.fullhist and FFpages * page >= 8192: # 8192 is 2 pages of 4096 byte each
                    txt = f"Found {FFpages} successive pages of {page} B (total {FFpages * page} B), as 'FF' only - ending reading"
                    dprint(txt)
                    fprint(txt)
                    break

            else: # error = -1
                # non-recovered error occured
                edprint(defname + "ERROR: ", errmessage, "; exiting from ", defname)
                return (error, "FAILURE: Cannot Get History: " + errmessage)

        stop = time.time()
        dtime = (stop - start)
        timing = "Total time: {:0.1f} sec, Total Bytes: {:1n} --> {:0.2f} kBytes/s ({:0.3f} MBits/s)".format(dtime, len(hist), len(hist) / dtime / 1000, len(hist) / dtime / 1E6 * 8)
        dprint(timing)
        fprint(timing)
        QtUpdate()

        # # Cleaning pipeline AFTER reading history
        # dprint(defname + "Cleaning pipeline AFTER reading history")
        # extra = getGEMF_ExtraByte()

    ### end if   sourceHist==    #################################################

    fprintGEMF_HistDetails(hist)

    # Parsing binary HIST data
    msg = "Parsing binary HIST data"
    fprint(msg)
    dprint(msg)
    g.HistoryDataList      = []
    g.HistoryParseList     = []
    g.HistoryCommentList   = []
    parseGEMF_HIST(hist)

    dbhisClines    = [None] * 2
    #                  ctype    jday modifier (using time unmodified)
    dbhisClines[0] = ["HEADER", "0 hours", "File created from History Download Binary Data"]
    dbhisClines[1] = ["ORIGIN", "0 hours", "{}".format(data_origin)]

# creating Database
    msg = "Writing HIST data to Database"
    fprint(msg)
    dprint(msg)

# write to database
    gsup_sql.DB_insertBin           (g.hisConn, hist)
    gsup_sql.DB_insertDevice        (g.hisConn, *data_originDB)
    gsup_sql.DB_insertComments      (g.hisConn, dbhisClines)
    gsup_sql.DB_insertComments      (g.hisConn, g.HistoryCommentList)
    gsup_sql.DB_insertData          (g.hisConn, g.HistoryDataList)
    gsup_sql.DB_insertParse         (g.hisConn, g.HistoryParseList)

# Done
    msg = "All done"
    fprint(msg)
    dprint(msg)

    return (0, "")


def parseGEMF_HIST(hist):
    """Parse history hist"""

    defname = "parseGEMF_HIST: "

    i               = 0     # counter for starting point byte number
    first           = 0     # byte index of first occurence of datetimetag
    cpms            = 0     # counter for CPMs read, so time can be adjusted

    # set endian
    if g.GEMF_endianness == "big": fcode = ">f"         # use big-endian ---   500er, 600er, 800er:
    else:                          fcode = "<f"         # use little-endian -- 3XX and 3XXS series

    # search for first occurence of a DateTime tag
    # must include re.DOTALL, otherwise a \x0a as in time 10h20:30 will
    # be considered as newline characters and ignored!
    DateTimeTag      = re.compile(b"\x55\xaa\x00......\x55\xaa[\x00\x01\x02\x03]", re.DOTALL)

    DateTimeTagList  = DateTimeTag.finditer(hist)
    for dtt in DateTimeTagList:
        first = dtt.start()
        break

    i    = first                    # the new start point for the parse
    hist = hist + hist[:i]          # concat with the part missed due to overflow
    rec  = hist.rstrip(b'\xff')     # right-clip FF (removal of all trailing 0xff)
    lh   = len(rec)
    dprint(defname, f"Byte index of first DateTime tag: {first} TotalBytes: {lh}")

    # NOTE: ###################################################################
    # After reading the DateTime tag the next real count is assumed to come at
    # the time of this DateTime tag. That is why the cpms += 1 command comes
    # as last command for each condition
    # may not be true; CPM save every minute seems to be off by ~30sec!

    rectimestamp = 0
    savetext     = ""
    saveinterval = 1
    cpms         = 0

    while i < lh:       #  range is: 0, 1, 2, ..., (lh - 1)
        durstart = time.time()
        r = rec[i]
        # 55 AA - Datetime - is found every approx 3 min or earlier (1 min seen)
        if r == 0x55:
            if rec[i+1] == 0xaa:
                if not g.GEMF_ClockIsDead:
                    YY = rec[i+2]
                    MM = rec[i+3]
                    DD = rec[i+4]
                    hh = rec[i+5]
                    mm = rec[i+6]
                    ss = rec[i+7]
                    rectime = f"20{YY:02d}-{MM:02d}-{DD:02d} {hh:02d}:{mm:02d}:{ss:02d}"
                    rectimestamp = datestr2num(rectime)

                else:
                    rectime = "1970-01-01 00:00:00"
                    parseGEMF_CommentAdder(i, rectime, "Clock is dead")

                msg55 = " ".join(f"{r55:02x}" for r55 in rec[i : i + 8])
                gdprint(defname, f"index: {i:6d}  {msg55} {rectime}    {rectimestamp}")
                i   += 8
                cpms = 0


        # AA 55 - datarecord - found every 1 sec
        # aa 55   00 25   9a 99 2b 43   62 90 58 49   5a 08   aa 55   - what is the extra 5a 08 /also seen: 5a 06, 5a 07
        # wasted space, to be ignored, see: EmfDev comment: "it is for the possible source. you can ignore it."
        # reply#1 in:  http://www.gqelectronicsllc.com/forum/topic.asp?TOPIC_ID=10550
        elif r == 0xaa:
            msgAA = " ".join(f"{raa:02x}" for raa in rec[i : i + 14])
            if rec[i + 1] == 0x55:
                try:
                    lrec         = rec[i + 2 : i + 14]
                    emfbytes     = lrec[0] * 256 + lrec[1]
                    emf          = round(float(emfbytes >> 4) + float((emfbytes & 0x000f)) / 10, 3)
                    ef           = round(struct.unpack(fcode, lrec[2:6]  )[0]      , 3)
                    rf           = round(struct.unpack(fcode, lrec[6:10] )[0] / 1E5, 3) # apparently pW/cm², while display is mW/m²
                    # xf         = round(struct.unpack(">H",  lrec[10:12])[0]      , 3) # this would be big-endian, while all else is little?
                    xf           = round(                     lrec[11]             , 3) # last byte; ignoring 2nd to last byte
                    parsecomment = ""

                except Exception as e:
                    exceptPrint(e, defname + "FAILED Getting Data Record")
                    ef, emf, rf, xf = g.NAN, g.NAN, g.NAN, g.NAN
                    parsecomment = "FAILED Getting Data Record"

                parseGEMF_ValueAdder(i, ef, emf, rf, xf, rectimestamp, cpms, saveinterval, parsecomment, savetext)

                tstmp = dt.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
                dur = 1000 * (time.time() - durstart)
                mdprint(defname, f"index: {i:6d}  {msgAA}  ef:{ef:7.3f}   emf:{emf:7.3f}   rf:{rf:10.3f}   xf:{xf:4.0f}   DateTime: {tstmp}  Dur: {dur:0.2f} ms")
                i    += 14
                cpms += 1

        # FF
        elif r == 0xff:
            rdprint(defname, f"FF position  r:{r:X}  i:{i}  cpms:{cpms}")
            i    += 1

        # all else
        else:
            rdprint(defname, f"else position  r:{r:X}  i:{i}  cpms:{cpms}")
            i    += 1


# code for julianday w/o localtime
def parseGEMF_ValueAdder(i, ef, emf, rf, xf, rectimestamp, cpms, saveinterval, parsecomment, savetext):
    """Add the parse results to the *.his list and commented *.his.parse list"""

    defname = "parseGEMF_ValueAdder: "

    # mdprint(defname, f"rectimestamp: {rectimestamp} cpms: {cpms}  saveintervall: {saveinterval}")

    datalist     = [None] * (g.datacolsDefault + 1)         # 13 x None
    datalist[0]  = i
    datalist[1]  = dt.datetime.fromtimestamp(rectimestamp + cpms * saveinterval).strftime('%Y-%m-%d %H:%M:%S')
    # datalist[2]= # CPM

    # GEMF_VariablesMap: {'CPS1st': 'RF', 'Humid': 'EMF', 'Xtra': 'XF', 'Temp': 'EF'}
    # VarsIndex = {"DateTime":0, "CPM":1, "CPS":2, "CPM1st":3, "CPS1st":4, "CPM2nd":5, "CPS2nd":6, "CPM3rd":7, "CPS3rd":8, "Temp":9, "Press":10, "Humid":11, "Xtra":12}
    for vname, cmd in g.GEMF_VariablesMap.items():
        dlindex = g.VarsIndex[vname]
        if   cmd == "EF":   datalist[dlindex + 1] = ef
        elif cmd == "EMF":  datalist[dlindex + 1] = emf
        elif cmd == "RF":   datalist[dlindex + 1] = rf
        elif cmd == "XF":   datalist[dlindex + 1] = xf

    g.HistoryDataList .append(datalist)
    g.HistoryParseList.append([i, parsecomment + savetext])

    # rdprint(defname, "Length of g.HistoryDataList: ", len(g.HistoryDataList))


def parseGEMF_CommentAdder(i, rectime, dbtype):

    datalist     = [None] * 3   # 3 x None
    datalist[0]  = i            # byte index
    datalist[1]  = rectime      # DateTime
    datalist[2]  = dbtype       # DateTime Stamp Info
    #print("#{:5d}, {:19s}, {:}".format(i, rectime, dbtype))

    g.HistoryCommentList.append(datalist)


def addGEMF_Error(errtext):
    """Adds ERROR info from gdev_gemf as comment to the current log"""

    logPrint("#GEMF_ERROR, {}, {}".format(stime(), errtext))   # to the LogPad

    if not g.logConn is None:                                  # to the DB
        cJulianday  = getTimeJulian()
        gsup_sql.DB_insertComments(g.logConn, [["DevERROR", cJulianday, errtext]])



# #######################################################################################
# ### Commands for use with GQ EMF devices
# #######################################################################################
# ### wird das überhaupt genutzt????????????????????
# def GEMF(command, port):
#     """Code to read an GQ EMF Device"""
#     # command: like: "GETEMF", for uses as: <GETEMF>>
#     # port:    like: "COM3"     on Windows
#     #                "USB0"     on Linux
#     #            or: "ttyUSB0"  on Linux

#     defname = "GEMF: "

#     # define the port
#     if 'win32' in sys.platform:
#         ### Windows
#         usbport = port
#     else:
#         ### Linux, Mac
#         if   "tty" in port:   usbport = "/dev/"    + port
#         elif "TTY" in port:   usbport = "/dev/tty" + port[3:]
#         else:                 usbport = "/dev/tty" + port

#     bcommand = (f"<{command}>>").encode("ASCII")
#     baudrate = 115200
#     timeoutR = 0.5
#     timeoutW = 1
#     rdprint(defname, f"Calling: {command:8s}  port: '{usbport}'  baudrate: {baudrate}  timeout: R:{timeoutR} W:{timeoutW}")

#     try:
#         with serial.Serial(usbport, baudrate=baudrate, timeout=timeoutR, write_timeout=timeoutW) as gemfser:
#             bwrt = gemfser.write(bcommand)           # returns bwrt: Number of bytes written, type: <class 'int'>
#             brec = b""
#             while True:
#                 brec += gemfser.read()               # returns brec: data record of           type: <class 'bytes'>
#                 if gemfser.in_waiting == 0: break

#     except OSError as e:
#         exceptPrint(e, "")
#         # edprint(defname + "OSError: ERRNO:{} ERRtext:'{}'".format(e.errno, e.strerror))
#         if e.errno == 13:
#             # no permission for port
#             msg  = f"You have no permission to access Serial Port '{usbport}'."
#             msg += "<br>Please review Appendix C of the GeigerLog manual.<br>"
#         else:
#             # any error number but 13
#             msg = "Serial Port {} not available".format(usbport)
#         edprint(msg)
#         efprint(msg)
#         return None

#     except Exception as e:
#         errmessage1 = defname + "FAILURE: Reading from device"
#         exceptPrint(e, "")

#         edprint(defname, errmessage1)
#         efprint(errmessage1)
#         setIndent(0)
#         return None     # Python's None signals communication error

#     # ydprint(defname, f"brec: {brec}")

#     try:
#         if   command == "GETVER":
#             msg = brec.decode("ascii", errors='replace')
#             gdprint(defname, f"command: {command:10s}  value: {msg}")
#             QueuefPrint(msg)
#             return g.NAN

#         elif command == "GETCPM":
#             value = brec[0] << 8 | brec[1]
#             gdprint(defname, f"command: {command:10s}  value: {value}")
#             return value

#         elif command == "GETCPS":
#             value = brec[0] << 8 | brec[1]
#             value = value & 0x3fff
#             gdprint(defname, f"command: {command:10s}  value: {value}")
#             return value

#         elif command == "GETEMF":
#             # e.g. : EMF = 3.5 mG
#             try:
#                 value = "EMF = 3.5 mG"
#                 # value = float((brec.split(" "))[0])
#             except Exception as e:
#                 exceptPrint(e, "GETEF")

#             gdprint(defname, f"command: {command:10s}  value: {value}")
#             return value

#         elif command == "GETEF":
#             # e.g.: EF = 33.9 V/m
#             try:
#                 value = "EF = 33.9 V/m"
#                 # value = float((brec.split(" "))[0])
#             except Exception as e:
#                 exceptPrint(e, "GETEF")

#             gdprint(defname, f"command: {command:10s}  value: {value}")
#             return value

#         else:
#             msg = f"Unknown Command: {command:10s}"
#             rdprint(defname, msg)
#             QueuefPrint(msg)
#             return g.NAN

#     except Exception as e:
#         exceptPrint(e, defname)


# #######################################################################################
# ### ENDE    Commands for use with GQ EMF devices
# #######################################################################################

