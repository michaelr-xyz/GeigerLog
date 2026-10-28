#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
gdev_radpro.py - GeigerLog module to handle devices with the RadPro firmware.
                 see: https://github.com/Gissio/radpro
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

### RadPro Devices:
#
# Dev#1:  Yellow FNIRSI GC-01:
# Chip:   CH32F103
#         R8T6
#         401546C10
#         WCH
# Tube:   J321     2022  12
# Batt:   JHCY703048  3.7V   1100 mAh   4.07 Wh   22/12
# Voltage Test:
#         Setting to 56.07kHz, 50% --> Voltage = 231 V
# Messung Logiksignal PWM:
#         Ich hab das PWM Signal an Widerstand R9 (an dessen Tube-Seite) gefunden. Oszi sagt ok
# Schaltung:
#         https://github.com/Gissio/radpro/blob/main/docs/devices/FNIRSI%20GC-01/schematics.pdf
#
# Tube as desklamp; lightning, fireworks
# https://www.youtube.com/watch?v=avdHJTEzvmQ
#
# neue Messung 2024-11-06:
#   A-Volt: setting by GeigerLog: 400V
#   A-Volt: 323 Volt (via 1GOhm and OW18E#1)
#   PWM-F:  169.03 Hz
#   Duty:   50%
#
# NOTE: user Alf has:  FNIRSI GC-01 (APM32F103CB)
#       he also has:   Bosean FS-5000
#       both on RadPro 2.0.2
#-----------------------------------------------------------------------------------------------
# Dev#2:  Blue FNIRSI GC-01:
# Chip:   Geehy
#         APM32
#         F103RBT6
#         NTRN7      D1
#         3141     2306
#                   arm
# Tube:   J321     2024 1
# Batt:   JHCY 703048  3.7V   1100 mAh   4.07 Wh  23/11
# A-Volt: 689 V (Factory default)
# Messung Logiksignal PWM:
#     same position as with yellow device
# PWM F:  56.07 kHz
#     D:  50.0 %
#
# neue Messung 2024-11-06:
#   A-Volt: 489 Volt (via 1GOhm and OW18E#1)
#   PWM-F:  56.2 kHz
#   Duty:   50%
#-----------------------------------------------------------------------------------------------
#
# Dev#3:  Yellow FNIRSI GC-01: Deutlich anderer Aufbau!
# Chip:   ???? Beschriftung von IC1 ist entfernt
#
# Tube:   j613
# Batt:   Rundzelle, keine Beschriftung
# A-Volt: 456V  (Factory Default)
# Messung Logiksignal PWM:
# PWM:    An R22 unsauberes Signal von 2.0kHz, Duty: 20.0%
# USB:    Only for Charging? Are Data-Pins even connected?


from gsup_utils import *
import gsup_sql

__author__      = "ullix"
__copyright__   = "Copyright 2024 - 2025"
__credits__     = ["Gissio"]            # original code
__license__     = "GPL3"


def initRadPro():
    """Find serial device by USB-manufactuerer and check it for being a RadPro device"""

    defname = "initRadPro: "
    dprint(defname)
    setIndent(1)

    if not findRadProDevice():
        # did NOT find a RadPro
        initresponse = "A RadPro device was not detected"
        g.RadProPort = "auto"           # prepare for trying again

    else:
        # DID find a RadPro
        initresponse = ""
        dprint(f"On port: '{g.RadProPort}'  found RadPro device with Hardware Id: '{g.RadProHardwareId}' and Software Id: '{g.RadProSoftwareId}'")

        # mark device as connected and named 'RadPro'
        g.Devices["RadPro"][g.CONN]  = True
        g.Devices["RadPro"][g.DNAME] = "RadPro "   # not used anywhere

        if g.RadProVoltageDefault    == "auto":  g.RadProVoltageDefault     = 500
        if g.RadProHVControl         == "auto":  g.RadProHVControl          = [False, 100, 0.425]
        if g.RadProVoltageGeneration == "auto":  g.RadProVoltageGeneration  = "GLdefault"
        if g.RadProClockCorrection   == "auto":  g.RadProClockCorrection    = 30
        if g.RadProVariables         == "auto":  g.RadProVariables          = "CPM3rd, CPS3rd"

        g.RadProScanType = "Off"

        # determine all configured vars and set to NAN in local values holder
        g.RadProVariables = setLoggableVariables("RadPro", g.RadProVariables)
        for vname in g.Devices["RadPro"][g.VNAMES]: g.RadProValues[vname] = g.NAN

        # determine the HV parameter
        g.RadProHVparameter = getRadProHVparameter()

        # set the default Anode voltage
        setRadProVoltage(g.RadProVoltageDefault)

        dprint(defname, "RadProPort:            ", g.RadProPort)
        dprint(defname, "RadProVoltageDefault:  ", g.RadProVoltageDefault)
        dprint(defname, "RadProHVFormula:       ", g.RadProVoltageConfigStr)
        dprint(defname, "RadProHVControl:       ", g.RadProHVControl)
        dprint(defname, "RadProClockCorrection: ", g.RadProClockCorrection)
        dprint(defname, "RadProVariables:       ", g.RadProVariables)

        # record the clockdrift
        getClockDrift()
        dprint(defname, f"Observed Clockdrift: {g.RadProClockDrift:+0.0f} sec, from: {g.RadProClockDriftFrom}  {g.RadProClockDriftMsg}")

        # do a clock correction by setting time of counter to that of computer, but only if so configured
        if g.RadProClockCorrection > 0:
            setRadProDateTime(verbose=False)
            g.RadProClockNextCorrMin = (getMinute() + g.RadProClockCorrection) % 60

        # init Threading
        g.RadProThreadRun     = True
        g.RadProThread        = threading.Thread(target=ThreadTargetRadPro, args=["Dummy"]) # auch tuple (args=("Dummy",)) möglich, aber NUR einzelnes Argument!
        g.RadProThread.daemon = True
        g.RadProThread.start()

    dprint(defname, "Done")
    setIndent(0)
    return initresponse


def findRadProDevice():
    """Find a RadPro device by checking response to command  "GET deviceId"
    return:         True when found, False otherwise
    data are in:    g.RadProHardwareId, g.RadProSoftwareId, g.RadProDeviceId
    """

    defname = "findRadProDevice: "

    if (g.RadProPort == "auto"):
        # check all USB ports and make list of all qualifying ones.
        # Frustratingly, Windows overwrites both product and manufacturer :-((
        newPortList  = []
        for port in getPortList(symlinks=False):
            # cdprint(defname, f"Port: {port.device}   Product: {port.product:40s}   Manufacturer: {port.manufacturer}")
            if 'win32' in sys.platform:
                ### Windows
                if queryRadPro("GET deviceId", port=port.device) > "":  newPortList.append(port)
            else:
                ### Linux, Mac
                if port.product == "Rad Pro":                           newPortList.append(port)

        ports = [port.device for port in newPortList]
        dprint(defname, "Port-Candidates for RadPro are: ", ports)

    else:
        # use user defined port
        ports = [g.RadProPort]
        msg   = f"RadPro uses <b>user-configured</b> port: '{g.RadProPort}'"
        dprint(defname, msg)
        fprint(msg)

    # check ports for proper RadPro device response; (yielding Hardware, Software, Device -ID)
    # break on first qualifying port
    foundDevice = False
    for g.RadProPort in ports:
        qresp = queryRadPro("GET deviceId")         # return like: FNIRSI GC-01 (CH32F103C8);Rad Pro 2.0.1beta3;88eb5698
        # ydprint(defname, qresp)
        if qresp > "":
            g.RadProHardwareId, g.RadProSoftwareId, g.RadProDeviceId = qresp.split(";")
            foundDevice = True
            break
        else:
            g.RadProHardwareId, g.RadProSoftwareId, g.RadProDeviceId = None, None, None

    return foundDevice


def ThreadTargetRadPro(args):
    """The thread to read the variables from the device"""

    defname = "ThreadTargetRadPro: "
    # rdprint(defname, "args: ", args)

    varlist  = g.Devices["RadPro"][g.VNAMES]
    while g.RadProThreadRun:
        if not g.logging:
            needtime = True
            # rdprint(defname, "not logging")
        else:
            # gdprint(defname, "logging")
            if needtime:
                time.sleep(0.005)

                # fill CPS-deque
                g.RadProLast60CPS = deque([], 60)                                   # default deque list with a single CPS=0
                lastMin           = 2                                               # to get last 5 min of records
                try:
                    Hist, _, _    = getHistRadPro(time.time() - (lastMin * 60))
                    if len(Hist) <= 2:
                        dprint(defname,  f"No Hist data in the last {lastMin} min")
                        # rdprint(defname, f"g.RadProLast60CPS: {g.RadProLast60CPS}")
                    else:
                        sumHistCPS = 0
                        counter    = 0
                        for i, rec in enumerate(Hist[-lastMin * 60:]):
                            # rdprint(defname, "rec: ", rec)
                            if i == 0: continue
                            hTime       = rec[0]
                            hCPM        = rec[1]
                            sumHistCPS += hCPM
                            counter    += 1

                        avgCPM = sumHistCPS / counter
                        avgCPS = avgCPM / 60
                        # rdprint(defname, f"avgCPM: {avgCPM}   avgCPS: {avgCPS}")

                        if not np.isnan(avgCPS):
                            poissval = []
                            cdprint(defname, f"Making 60 CPS Poisson values averaging CPM={avgCPM:0.3f} --> CPS={avgCPS:0.3f}")
                            for p in np.random.poisson(avgCPS, 60):
                                poissval.append(int(p))                 # conversion from numpy 64bit to Python int()
                            g.RadProLast60CPS = deque(poissval, 60)     # deque list filled with CPS in all 60 places for CPS averaging avgCPS

                        dprint(defname, f"Got History for last {lastMin} min with {len(Hist)} records; last one from '{num2datestr(hTime)}', averaging CPM={avgCPM:0.3f} --> CPS={avgCPS:0.3f}")
                        # gdprint(defname, f"Creating fake 'last 60sec' record: {g.RadProLast60CPS}")

                except Exception as e:
                    exceptPrint(e, defname + "Getting Hist Data for CPS deque; continuing with empty deque")

                # rdprint(defname, f"Current 'last 60sec' CPS record: {g.RadProLast60CPS}")

                nexttime = time.time()
                needtime = False


### this fetches the values
            if time.time() >= nexttime:
                THREAD_RadPro_fetchValues(varlist)      # fetch the values
                nexttime += 1                           # always use 1 sec cycle; everything else gives Non-Poisson CPS!
                ### done fetching values

                # now scanning if needed
                updateScanRadPro()

            #
            # set some RadPro properties (at this place cannot be a conflict for double-calling via Serial)
            #

            # clock correction
            if g.RadProClockCorrection > 0 and (getMinute() == g.RadProClockNextCorrMin):
                setRadProDateTime(verbose=False)
                g.RadProClockNextCorrMin = (g.RadProClockNextCorrMin + g.RadProClockCorrection) % 60
                # rdprint(defname, f"CurrentMinute: {getMinute()}  RadProClockCorrection: {g.RadProClockCorrection}  RadProClockNextCorrMin: {g.RadProClockNextCorrMin}" )

            # printing RadPro info
            if g.RadProFlagInfo > 0:
                rdprint(defname, "printing radpro info")
                if g.RadProFlagInfo == 1: info = getInfoRadPro(extended=False)      # g.RadProFlagInfo == 1
                else:                     info = getInfoRadPro(extended=True)       # g.RadProFlagInfo == 2
                QueuefPrint(info)
                g.RadProFlagInfo = 0

            # setting RadPro time
            if g.RadProFlagDateTime:
                g.RadProFlagDateTime = False
                setRadProDateTime(verbose=False)

        time.sleep(0.005)  # last command still in while loop


def updateScanRadPro():
    """Execute a Scan if so commanded"""

    defname = "updateScanRadPro: "

    if g.RadProScanType in ("Freq", "Duty", "Volt"):
        if (g.LogReadings % g.RadProScanUpdate) == 0:

        # Freq Scan
            if g.RadProScanType == "Freq":
                ## scan of freq @ fixed duty

                if g.RadProScanUp:  g.RadProFrequency *= g.RadProScanFstep
                else:               g.RadProFrequency /= g.RadProScanFstep

                # # sinewave change
                # g.RadProFrequency = 100 + 250 + (np.sin(g.LogReadings / 5) * 250)
                # ydprint(defname, f"g.RadProFrequency: {g.RadProFrequency:0.2f}")

                if g.RadProFrequency >= g.RadProScanFmax:
                    g.RadProScanFindex += 1
                    if g.RadProScanFindex >= len(g.RadProScanFselect):
                        g.STOPlogging = True
                        setRadProVoltage(g.RadProVoltageDefault)
                        g.RadProScanType = "Off"
                        return

                    g.RadProScanFindex  = g.RadProScanFindex % len(g.RadProScanFselect)
                    g.RadProScanFduty   = g.RadProScanFselect[g.RadProScanFindex]
                    g.RadProFrequency   = g.RadProScanFmin
                    g.RadProDutycycle   = g.RadProScanFduty
                    # ydprint(defname, "g.RadProScanFindex: ", g.RadProScanFindex)
                    # ydprint(defname, "g.RadProScanFduty:  ", g.RadProScanFduty)
                    # ydprint(defname, "g.RadProFrequency:  ", g.RadProFrequency)
                    # ydprint(defname, "g.RadProDutycycle:  ", g.RadProDutycycle)
                    msg = "Step Change"
                    ydprint(defname, msg)
                    QueuefPrint(f"{stime()}  " + msg)

                setRadProPWM()

                msg = f"Scanning: Freq: {getRadProFreq():6.6g} Hz   @Duty: {getRadProDuty():0.6g}%"

        # Duty Scan
            elif g.RadProScanType == "Duty":
                ## for scan of duty @ fixed freq

                if g.RadProScanUp:  g.RadProDutycycle += g.RadProScanDstep
                else:               g.RadProDutycycle -= g.RadProScanDstep

                if g.RadProDutycycle >= g.RadProScanDmax:
                    g.RadProScanDindex += 1
                    if g.RadProScanDindex >= len(g.RadProScanDselect):
                        g.STOPlogging = True
                        setRadProVoltage(g.RadProVoltageDefault)
                        g.RadProScanType = "Off"
                        return
                    g.RadProScanDindex  = g.RadProScanDindex % len(g.RadProScanDselect)
                    g.RadProScanDfreq   = g.RadProScanDselect[g.RadProScanDindex]
                    g.RadProDutycycle   = g.RadProScanDmin
                    g.RadProFrequency   = g.RadProScanDfreq
                    # ydprint(defname, "g.RadProScanDindex: ", g.RadProScanDindex)
                    # ydprint(defname, "g.RadProScanDfreq:  ", g.RadProScanDfreq)
                    # ydprint(defname, "g.RadProFrequency:  ", g.RadProFrequency)
                    # ydprint(defname, "g.RadProDutycycle:  ", g.RadProDutycycle)
                    msg = "Step Change"
                    ydprint(defname, msg)
                    QueuefPrint(f"{stime()}  " + msg)

                setRadProPWM()

                msg = f"Scanning: Duty: {g.RadProDutycycle:6.6g} %   @Freq: {g.RadProFrequency:0.6g} Hz"

        # Volt Scan
            elif g.RadProScanType == "Volt":
                ## for scan of voltage; compare with measurement

                if g.RadProScanUp:  g.RadProVoltage += g.RadProScanVstep
                else:               g.RadProVoltage -= g.RadProScanVstep

                if   g.RadProVoltage >= g.RadProScanVmax: g.RadProScanUp = False
                elif g.RadProVoltage <= g.RadProScanVmin:
                    ydprint(defname, "elif g.RadProVoltage <= g.RadProScanVmin")
                    g.STOPlogging = True
                    setRadProVoltage(g.RadProVoltageDefault)
                    g.RadProScanType = "Off"
                    g.RadProScanUp = True
                    return

                setRadProVoltage(g.RadProVoltage)
                msg = f"Scanning: Voltage: Target:{g.RadProVoltage:0.6g} V   @PWM:({g.RadProFrequency:0.6g} Hz / {g.RadProDutycycle:0.6g} %)"


            icdprint(defname, msg)
            QueuefPrint(f"{stime()}  " + msg)


def THREAD_RadPro_fetchValues(varlist):
    """get all data for vars in varlist for LOCAL storage"""

    ### CPM by RadPro:                  - is now done via formula RADPROCPM()
    ### clock drift                     - is now done via formula RADPROCLOCKDRIFT()
    ### get Hist to obtain its len      - is now done via formula RADPROHISTLEN()

    start   = time.time()
    defname = "THREAD_RadPro_fetchValues: "
    # rdprint(defname)

    ### CPS: get from (cumulative) tubePulseCount
    # 1) find the delta-counts
    #    takes 2 ... 7 ms
    command                     = "GET tubePulseCount"
    try:
        qstr                    = queryRadPro(command)
        if qstr > "": cpsPulseCount = int(qstr)
        else:         cpsPulseCount = g.NAN
    except Exception as e:
        exceptPrint(e, defname + f"Failure with query command: {command}")
        cpsPulseCount = g.NAN

    cpsPulseCountDelta          = cpsPulseCount - g.RadProLastCPSPulseCount
    g.RadProLastCPSPulseCount   = cpsPulseCount

    # 2) find the delta-time
    CPSTime                     = time.time()
    CPSTimeDelta                = CPSTime - g.RadProLastCPSTime     # in sec; ideally would be exactly 1 sec, no decimals
    g.RadProLastCPSTime         = CPSTime
    CPScorr                     = round(cpsPulseCountDelta / CPSTimeDelta, 0)
    # rdprint(defname, f"CPSTimeDelta: {CPSTimeDelta:0.4f}  CPScorr: {CPScorr}  cpsPulseCountDelta: {cpsPulseCountDelta}")

    if CPScorr == float(cpsPulseCountDelta):    # the correction for time difference was not big enough to change the value
        CPS = cpsPulseCountDelta
        g.RadProLast60CPS.append(CPS)
        if len(g.RadProLast60CPS) > 10:          # if less than 10 data in last 60 sec do not plot
            CPM = float(round(np.nansum(g.RadProLast60CPS) / len(g.RadProLast60CPS) * 60, 0))
        else:
            CPM = g.NAN
        # rdprint(defname, f"CPS: {CPS:0.4f}  CPM: {CPM}  len(RadProLast60CPS): {len(g.RadProLast60CPS)}")

    else:
        CPS = g.NAN
        CPM = g.NAN
        if g.LogReadings > 1:   # ignore the first reading; it will always be NAN
            QueuefPrint(f"{stime()}  RadPro Cycle Dur ≠ 1 sec: {CPSTimeDelta:0.3f} sec  CPM:{CPM}   CPS:{CPS}")

    # fill local RadProValues
    for vname in varlist:
        if   vname == "CPM":        val = CPM
        elif vname == "CPS":        val = CPS
        elif vname == "CPM1st":     val = CPM
        elif vname == "CPS1st":     val = CPS
        elif vname == "CPM2nd":     val = CPM
        elif vname == "CPS2nd":     val = CPS
        elif vname == "CPM3rd":     val = CPM
        elif vname == "CPS3rd":     val = CPS

        elif vname == "Temp":
                                    val = getRadProFreq()
                                    g.VarsCopy[vname][6] = "Freq"

        elif vname == "Press":
                                    val = getRadProDuty()
                                    g.VarsCopy[vname][6] = "Duty"
        elif vname == "Humid":
                                    val = g.RadProVoltage if (g.RadProScanType in ("Off", "Volt")) else g.NAN
                                    g.VarsCopy[vname][6] = "Volt"
        elif vname == "Xtra":
                                    val = g.NAN
                                    g.VarsCopy[vname][6] = " "

        if   "CPM" in vname:        g.VarsCopy[vname][6] = "CPM"
        elif "CPS" in vname:        g.VarsCopy[vname][6] = "CPS"

        g.RadProValues[vname] = val

    vprintLoggedValues(defname + " ", varlist, g.RadProValues, (time.time() - start) * 1000)


#control
    # set the Voltage to compensate drop by CPS (if enabled); mimic PI control
    if g.RadProHVControl[0] and (g.RadProScanType == "Off"):
        if not np.isnan(CPS):
            newvoltage                 = g.RadProVoltageDefault + g.RadProHVControl[2] * CPS
            deltavoltage               = g.RadProVoltage - newvoltage
            g.RadProHVControlDeltaSum += deltavoltage
            msg = f"Current Voltage: {g.RadProVoltage}  PI-Voltage: {newvoltage}   Delta: {deltavoltage:+0.2f}  SumDelta: {g.RadProHVControlDeltaSum:0.6g}"
            if abs(g.RadProHVControlDeltaSum) > g.RadProHVControl[1]:
                mdprint(defname, msg,  f" --> change to newvoltage: ", newvoltage)
                g.RadProHVControlDeltaSum = 0
                setRadProVoltage(newvoltage)
                msg = f"Set Voltage: {g.RadProVoltage:0.2f} V  using Freq: {g.RadProFrequency:0.2f} Hz  Duty: {g.RadProDutycycle:0.2f} %"
                mdprint(defname, msg)
                QueuefPrint(f"{stime()} {msg}", color="<blue>")
                QueueSoundDBG("geiger")
            else:
                mdprint(defname, msg,  f" -->  NOT changing voltage")


def terminateRadPro():
    """Close device"""

    defname = "terminateRadPro: "
    dprint(defname)
    setIndent(1)

    errmsg = ""
    g.Devices["RadPro"][g.CONN] = False
    g.RadProPort                = "auto"
    g.RadProLastCPSTime         = g.NAN
    g.RadProLastCPSPulseCount   = g.NAN

    g.RadProThreadRun = False
    g.RadProThread.join()

    # verify that thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.RadProThread.is_alive() and (time.time() - start) < 5:
        pass

    msgalive = "is alive" if g.RadProThread.is_alive() else "NOT alive"
    dprint(defname, f"thread-status: {msgalive} after:{1000 * (time.time() - start):0.3f} ms")

    dprint(defname, "Terminated")
    setIndent(0)

    return errmsg


def queryRadPro(request, port="default"):
    """Query the RadPro device with a command 'request'"""
    # return: str of scrubbed, downloaded byte-data; empty str on failure

    ### begin local defs #################################################################################################

    def verifyData(DataStr):
        """Check the data for validity, and return:
        on ok:  cleaned data (without ok at Start and LF at end)
        else:   empty string ("")
        """

        if g.debug: printQueryDetails(DataStr)

        if DataStr      == "":          return ("",                  f"Bad data - Empty DataStr: '{DataStr}'")       # empty DataStr
        # if DataStr[-2:] != "\r\n":      return ("",                  f"Bad data - No CRLF ending:'{DataStr[-50:]}'") # no CR+LF ending
        if DataStr.startswith("OK"):    return (DataStr.strip()[3:], f"Good Data: '{DataStr}'")                      # skip the initial "OK "
        else:                           return ("",                  f"Bad data - No initial OK:  '{DataStr[:50]}'") # missing initial OK


    def printQueryDetails(DataStr):
        """print some query details on size, dur, speed"""

        global wdur, rdur, tdur

        # rdprint(defname, f"wdur: {wdur:0.2f}  rdur: {rdur:0.2f}  tdur: {tdur:0.2f}")

        lendata = len(DataStr)
        wspeed  = g.NAN if wdur == 0 else wcnt    / wdur
        rspeed  = g.NAN if rdur == 0 else lendata / rdur
        tspeed  = g.NAN if tdur == 0 else lendata / tdur
        plimit  = 60    # print-length limit
        breclim = brec[:plimit] + (b"..." if len(brec) > plimit else b"")
        msg     = f"{request:28s} [B]:W:{wcnt:<3d} R:{lendata:<3d}  Dur[ms]:W:{wdur:<5.2f} R:{rdur:<5.2f} Ttl:{tdur:<5.2f} "
        msg    += f"[kB/s]:W:{wspeed:<3.0f} R:{rspeed:<3.0f} Ttl:{tspeed:<3.0f}  resp:{breclim}"
        #
        # mdprint(defname, msg)
        #

    ### end local defs #################################################################################################


    global wdur, rdur, tdur

    tstart      = time.time()
    defname     = "queryRadPro: "
    # mdprint(defname, f"request: '{request}' ")

    endchars    = "\r\n"
    endcharslen = len(endchars)
    response    = ""   # default response on failure

    if port == "default":  port = g.RadProPort
    # mdprint(defname, "port: ", port, "   ", type(port))

    try:
        ### using serial port with context manager ######################################################################
        with serial.Serial( port          = port,
                            baudrate      = g.RadProBaud,
                            timeout       = g.RadProTimeoutRHist,
                            write_timeout = g.RadProTimeoutW,
                            ) as RPser:
        # write
            try:
                wstart   = time.time()
                wcnt     = g.NAN
                brequest = (request + endchars).encode("ascii", errors='replace')   # are there ever errors on encoding?
                wcnt     = RPser.write(brequest)                                    # wcnt= no of Bytes written
                # rdprint(defname, f"writing: >{brequest}<  response: >{wcnt}<")
            except serial.SerialTimeoutException as e:                              # this exception ONLY on WRITE timeout !
                exceptPrint(e, defname + f"FAILURE Timeout on WRITING; request: '{request}'")
            except Exception as e:
                exceptPrint(e, defname + f"FAILURE writing to serial; request: '{request}'")
            wdur = 1000 * (time.time() - wstart)                                    # in ms

        # wait for data in the pipeline but wait no longer than tmax sec - takes 0 ... 3 ms
            beginwait = time.time()     # sec
            dtime     = 0               # sec
            tmax      = 3               # sec; wait no longer than these
            while RPser.in_waiting == 0:
                dtime = time.time() - beginwait
                if (dtime) > tmax:
                    rdprint(defname, f"Waited: {dtime:0.3f} sec")
                    setIndent(0)
                    return response
                # rdprint(defname, f"Waited: {1000 * dtime:0.3f} ms")

        # read
            rstart = time.time()
            try:
                brec = RPser.readline()  # waits for LF; timeoutR when no LF received, but download Hist takes > 2 sec, yet works?
                # rdprint(defname, f"request: >{request}<  response: >{brec}<")
                brec = brec[:-endcharslen]                                       # remove LF-only  or CRLF ending
                # rdprint(defname, f"request: >{request}<  response: >{brec}<")

            except Exception as e:
                exceptPrint(e, defname + f"FAILURE reading serial request: '{request}'")
                brec     = b""
            rdur = 1000 * (time.time() - rstart)                                    # in ms
        ### serial port is now CLOSED again ####################################################################################

    except Exception as e:
        emsg = f"FAILURE using serial: '{request}'"
        exceptPrint(e, defname + emsg)
        QueuefPrint("RadPro Failure: " + str(e))

    else:
        # rdprint(defname, "brec: ", brec)
        if rdur >= g.RadProTimeoutRHist * 1000:                           # timeout R; brec kann trotzdem ok sein, siehe datalog!
            rdprint(defname, f"requ:'{request}' --- EXCEEDED READ-TIMEOUT --- dur: {rdur:0.3f} ms")

        tdur        = 1000 * (time.time() - tstart)
        response, _ = verifyData(brec.decode("ascii", errors='replace'))  # with errors='replace' no further exception possible(?)

    # mdprint(defname, f"returning: '{response}'")
    return response     # response is type str; it is ascii-decoded brec


def getClockDrift():
    """check the Device Clock Drift"""

    if not g.logging:
        g.RadProClockDrift     = getRadProDeltaTime()
        g.RadProClockDriftFrom = num2datestr(time.time())

    if   np.isnan(g.RadProClockDrift):
                                       msg = f"<red>Device Clock cannot be read"
                                       QueueSoundDBG("burp")
    elif abs(g.RadProClockDrift) <= 1: msg = f"Device Clock is same as Computer's within 1 sec"
    elif     g.RadProClockDrift  >  1: msg = f"Device Clock is slower than Computer's by {abs(g.RadProClockDrift):0.0f} sec"
    else:                              msg = f"Device Clock is faster than Computer's by {abs(g.RadProClockDrift):0.0f} sec"

    g.RadProClockDriftMsg = msg


#info
def getInfoRadPro(extended=False):
    """Return RadPro info"""

    defname = "getInfoRadPro: "

    if g.logging:
        if  g.RadProFlagInfo == 0:
            if extended: g.RadProFlagInfo    = 2
            else:        g.RadProFlagInfo    = 1
            return "Please Wait ..."

    info = ""
    if g.RadProHardwareId is not None:
        info += "Configured Connection:        Port:'{}' Baud:{} Timeouts[s]: R:{} W:{}\n".format(
                                                                                                    g.RadProPort,
                                                                                                    g.RadProBaud,
                                                                                                    g.RadProTimeoutR,
                                                                                                    g.RadProTimeoutW,
                                                                                                 )

    if not g.Devices["RadPro"][g.CONN]:
        info += "<red>Device is not connected.</red>\n"
    else:
        chiptype = "GEEHY" if "APM32" in g.RadProHardwareId else "WCH"
        info += f"Connected Device:             {g.RadProHardwareId}  Chip:'{chiptype}'\n"
        info += f"Firmware Version:             {g.RadProSoftwareId}\n"
        getClockDrift()
        info +=  "Device Clock Drift:           {:0.0f} sec  (checked @ Computer Time: {})\n".format(g.RadProClockDrift, g.RadProClockDriftFrom)
        info +=  "                              {}\n".format(g.RadProClockDriftMsg)
        info += f"Configured Anode Voltage:     {g.RadProVoltageDefault:0.6g} V\n"
        info +=  "Configured Variables:         {}\n".format(g.RadProVariables)
        info +=  getTubeSensitivities(g.RadProVariables)

### for testing
        if g.debug: extended = True
###

        if extended:
            info += "\n"
            info += "Extended:\n"
            try:
                info += "Anode Voltage under Control:\n"
                if g.RadProHVControl[0]:
                    TargetVolt      = f"{g.RadProVoltage:0.6g} V"    if g.RadProScanType == 'Off' else 'inactive during scanning'
                    ControlTime     = f'{g.RadProHVControl[1]:0.6g}' if g.RadProScanType == 'Off' else 'inactive during scanning'
                    ControlStrength = f'{g.RadProHVControl[2]:0.6g}' if g.RadProScanType == 'Off' else 'inactive during scanning'
                else:
                    TargetVolt      = "Off"
                    ControlTime     = "Off"
                    ControlStrength = "Off"

                info += f"   Voltage controlled:        {TargetVolt}\n"
                info += f"   Voltage Control Time Cnst: {ControlTime}\n"
                info += f"   Voltage Control Strength:  {ControlStrength}\n"

                if   g.RadProScanType == "Off":  info += f"Scanning:                     {g.RadProScanType}\n"
                elif g.RadProScanType == "Freq": info += f"Scanning:                     On: '{g.RadProScanType}'   {g.RadProScanFmin}...{g.RadProScanFmax} Hz  @{g.RadProScanFduty} %\n"
                elif g.RadProScanType == "Duty": info += f"Scanning:                     On: '{g.RadProScanType}'   {g.RadProScanDmin}...{g.RadProScanDmax} %  @{g.RadProScanDfreq} Hz\n"
                elif g.RadProScanType == "Volt": info += f"Scanning:                     On: '{g.RadProScanType}'   {g.RadProScanVmin}...{g.RadProScanVmax} V  \n"

                info += f"Tube Freq(Volt) @ DC=50%:     {g.RadProVoltageConfigStr}\n"
                info += f"Tube PWM Frequency:           {float(queryRadPro('GET tubeHVFrequency'))      :0.6g} Hz\n"
                info += f"Tube PWM Duty Cycle:          {float(queryRadPro('GET tubeHVDutyCycle')) * 100:0.6g} % \n"
            except Exception as e:
                exceptPrint(e, "Failure getting PWM Settings")

            try:
                dtimestmp = int(queryRadPro("GET deviceTime"))     # convert to int from str
            except Exception as e:
                exceptPrint(e, "no timestamp from device")
                dtimestmp = g.NAN

            try:
                info += f"Device Time:                  {num2datestr(dtimestmp)}  timestamp: {dtimestmp}\n"
                info += f"Device ID:                    {g.RadProDeviceId}\n"
                info += f"Device Battery Voltage:       {queryRadPro('GET deviceBatteryVoltage')} V\n"
                info += f"Tube life time:               {queryRadPro('GET tubeTime')}\n"
                info += f"Tube life pulse count:        {queryRadPro('GET tubePulseCount')}\n"
                info += f"Tube rate:                    {queryRadPro('GET tubeRate')} CPM\n"
                info += f"Tube conversion factor:       {queryRadPro('GET tubeConversionFactor')} CPM/(µSv/h)\n"
                info += f"Tube dead time:               {queryRadPro('GET tubeDeadTime')} s\n"
                info += f"Tube dead-time compensation:  {queryRadPro('GET tubeDeadTimeCompensation')} s\n"
                info += f"Tube background compensation: {queryRadPro('GET tubeBackgroundCompensation')} CPM\n"
            except Exception as e:
                msg   = "Failure getting Extended Info"
                info += msg + "\n"
                exceptPrint(e, defname + msg)

    return info


def getCPMRadPro():
    """get CPM from RadPro's command 'GET tubeRate'"""

    defname = "getCPMRadPro: "

    try:
        qstr = queryRadPro("GET tubeRate")
        if qstr > "":   cpmTR = float(qstr)                             # will except when qstr == ""
        else:           cpmTR = g.NAN
    except Exception as e:
        exceptPrint(e, defname)
        cpmTR = g.NAN

    # mdprint(defname, "CPM: ", cpmTR)
    return cpmTR


def getValuesRadPro(varlist):
    """Read data from the locally held vars; set them to NAN after readout"""

    start   = time.time()
    defname = "getValuesRadPro: "

    # rdprint(defname, "g.RadProValues: ", g.RadProValues)
    alldata = {}
    for vname in varlist:
        if vname in g.RadProValues.keys():
            alldata[vname]        = applyValueFormula(vname, g.RadProValues[vname], g.ValueScale[vname])
            g.RadProValues[vname] = g.NAN   # reset g.RadProValues to NAN after reading

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def loadHistoryRadPro(sourceHist):
    """Load history from device"""

    start = time.time()

    defname = "loadHistoryRadPro: "

    fprint(f"Loading data from source {sourceHist} ...")
    QtUpdate()

    # get Hist as list
    Hist, bytecount, _ = getHistRadPro(0)

    # save data to database
    historyDB = []
    for i, HisRecord in enumerate(Hist):
        # rdprint(defname, "HisRecord: ", HisRecord)    # loadHistoryRadPro: HisRecord: [1713345208, 1263.0, 60,         1263]
                                                        # loadHistoryRadPro: HisRecord: [1713345268, 1221.0, 60,         1221]
                                                        # loadHistoryRadPro: HisRecord: [1713345328, 1233.0, 60,         1233]
                                                        # HistData.append(             [record_time, cpm,    delta_time, delta_pulse_count])
                                                        #                                                    between     pulse delta betw.
                                                        #                                                    2 records   2 records
                                                        #                                                                same as CPM
                                                        #                                                                if dt==60

        historyDB.append(
            [i,
             num2datestr(HisRecord[0]), # DateTime str

             HisRecord[1],              # CPM:  counts per min
             None,
             None,
             None,

             None,
             None,
             None,
             None,

             HisRecord[2],              # Temp: delta_time to previous record in sec
             None,
             None,
             None,
            ]
        )

    # updating database - SQL Device
    gsup_sql.DB_insertDevice(g.hisConn, stime(), str(g.RadProHardwareId))

    # updating database -  SQL Comments
    gsup_sql.DB_insertComments(g.hisConn, [
                                            ["HEADER",  None, "File created by reading history from device"],
                                            ["ORIGIN",  None, "Download from device"],
                                            ["DEVICE",  None, str(g.RadProHardwareId)],
                                            ["COMMENT", None, "CPM: Counts per 1 min; Temp: Delta t[sec] to prev. record"],
                                          ])

    # updating database - SQL Data
    gsup_sql.DB_insertData(g.hisConn, historyDB)

    lenhist  = len(historyDB)                   # no of records
    duration = time.time() - start              # sec
    rec_rate = lenhist   / duration             # records / sec
    byterate = bytecount / duration / 1000      # kilobytes / sec
    msg      = "Done. Got {} records in {:0.1f} s;  {:0.0f} rec/s  ({:0.1f} kB/s)".format(lenhist, duration, rec_rate, byterate)
    dprint(defname, msg)
    fprint(msg)

    return (0, "")


def getHistRadPro(startTime):
    """Download History from Counter"""
    # return: - List of Hist records
    #         - count of downloaded bytes
    #         - duration of full processing

    # - high count rates
    # - run: /RadPro-Hist-Len check_#2.logdb
    #    143, 2024-04-11 18:19:57,  2367.000
    #    144, 2024-04-11 18:20:00,  1861.000  delta = 506   /8 = 63.25

    # Quote: "Data logging can store up to 5060 data points. At normal radiation levels, this allows for
    #         3 days of data at 1-minute intervals, 8 days at 5-minute intervals, 17 days at 10-minute
    #         intervals, 52 days at 30-minute intervals, and 105 days at 60-minute intervals."

    ###################################################################################################
    def printRecordInfo():
        # print only first, last records, and those different from delta_time==60

        global sixty, sixtyplus, sixtyminus, sixtyall

        if    delta_time == 60:     sixty        += 1
        elif  np.isnan(delta_time): pass
        elif  delta_time >  60:     sixtyplus    += 1
        else:                       sixtyminus   += 1
        sixtyall = sixty + sixtyplus + sixtyminus
        sixtypct = sixtyplus / sixtyall if sixtyall > 0 else g.NAN

        ilimit      = 6 #11
        conditionLo = index < ilimit                            # first and last ilimit records
        conditionHi = index > (len(records) - ilimit)           # first and last ilimit records
        conditionM  = False                                     # records where deltaTime is not == 60
        if conditionLo or conditionHi or conditionM:
            msg  = f"index:{index:4d}  time:{record_time:10d} {num2datestr(record_time):19s}  pulse_count:{record_pulse_count:7d}  "
            msg += f"delta_time:{delta_time:4.0f}  delta_pulse_count:{delta_pulse_count:<4.0f}  "
            msg += f". sixty:{sixty:<5.0f}  >:{sixtyplus:<4.0f} {sixtypct:<4.0%}   <:{sixtyminus:<3.0f}  . CPM:{cpm}"
            if index == (len(records) - ilimit + 1): cdprint(defname, "...")
            if conditionLo or conditionHi:  cdprint(defname, msg)
            else:                           mdprint(defname, msg)
    ###################################################################################################

    global sixty, sixtyplus, sixtyminus, sixtyall

    defname = "getHistRadPro: "
    # setIndent(1)
    # cdprint(defname)
    # setIndent(1)

    sixty               = 0
    sixtyplus           = 0
    sixtyminus          = 0
    sixtyall            = 0

    # get records since "startTime" - with startTime==0 to fetch all records
    Hstart  = time.time()
    qstr    = queryRadPro(f"GET datalog {int(startTime)}")          # MUST NOT have decimals in starttime!
    # like:  qstr: time,tubePulseCount;1730710711,2784668;1730710712,2784670;...
    # ydprint(defname, "qstr: ", qstr)
    setIndent(1)
    cdprint(defname)
    setIndent(1)
    Hdur1   = 1000 * (time.time() - Hstart)                         # Got 3036 records in 3.1 s;  967 rec/s  (19.4 kB/s)

    records = qstr.split(";")                                       # recs like: '1713200682,12713637;' format: (timestamp, cum-count)
    cdprint(defname, f"Total no of records: {len(records) - 1} (+ 1 for header)", )


    # parse the records and create list of HistData records
    last_time           = g.NAN
    last_pulse_count    = g.NAN
    HistData            = []
    for index, record in enumerate(records):
        if index == 0:                                                  # skipping the header line: 'time,tubePulseCount;'
            cdprint(defname, f"index:{index:4d}  header: '{record}'")
            continue

        values = record.split(",")                                      # 'values' are strings!
        if len(values) != 2:
            rdprint(defname, f"Record '{record}' malformed (too many commas)")
            continue

        try:
            record_time         = int(values[0])                            # unix time stamp
            record_pulse_count  = int(values[1])                            # cumulative counts

            delta_time          = record_time        - last_time            # in sec
            delta_pulse_count   = record_pulse_count - last_pulse_count     # in counts

            last_time           = record_time
            last_pulse_count    = record_pulse_count

            cpm = round(delta_pulse_count / delta_time * 60, 0)             # to correct for delta_time != 60; kills Poissonian!
            if g.debug: printRecordInfo()

            HistData.append([record_time, cpm, delta_time, delta_pulse_count])

        except Exception as e:
            exceptPrint(e, defname + "Error while parsing records")

    Hdur2 = 1000 * (time.time() - Hstart)                               # 20 ... 30 ms länger als Hdur1
    cdprint(defname, f"Hist: get Dur:{Hdur1:0.1f} ms  processing: plus:{Hdur2 - Hdur1:0.1f} ms")

    setIndent(0)
    setIndent(0)

    return (HistData, len(qstr), (Hdur1, Hdur2))


def getRadProDeltaTime():
    """
    reads the timestamp from device and computer
    return: on success: delta time 'Computer minus Device' in sec with 1 sec resolution
            on failure: NAN
    """

    defname = "getRadProDeltaTime: "

    dtimestamp = queryRadPro("GET deviceTime")
    # rdprint(defname, f"devtimestmp: '{dtimestamp}'")

    try:
        time_computer = int(time.time())
        if dtimestamp > "": time_device   = int(dtimestamp)
        else:               time_device   = g.NAN
    except Exception as e:
        exceptPrint(e, defname + f"FAILURE getting timestamps; computer: '{time_computer}'  RadPro: '{dtimestamp}'")
        time_device = g.NAN

    time_delta = time_computer - time_device
    # gdprint(defname, f"Clock: computer:{time_computer}, device:{time_device}, Delta CD:{time_delta:+0.3f}"

    return time_delta


def setRadProDateTime(verbose=False):

    defname = "setRadProDateTime: "

    if g.logging:
        if not g.RadProFlagDateTime:
            g.RadProFlagDateTime = True
            return

    ctime = int(time.time())                                         # cut off the decimals from time.time() by int()
    resp  = queryRadPro(f"SET deviceTime {ctime}")

    msg = "RadPro Datetime was set to Computer DateTime"
    if verbose:
        QueuefPrint(header("Setting RadPro DateTime"))
        QueuefPrint(msg)
    dprint(defname, msg)


def getRadProDuty():
    """get the Duty Cycle in %"""

    defname = "getRadProDuty: "

    hvdc = queryRadPro('GET tubeHVDutyCycle')
    try:
        if hvdc > "": fhvdc = float(hvdc) * 100
        else:         fhvdc = g.NAN
    except Exception as e:
        exceptPrint(e, defname)
        fhvdc = g.NAN

    return fhvdc


def getRadProFreq():
    """get the Freq in Hz"""

    defname = "getRadProFreq: "

    hvfreq = queryRadPro('GET tubeHVFrequency')
    try:
        if hvfreq > "": fhvfreq = float(hvfreq)
        else:           fhvfreq = g.NAN

    except Exception as e:
        exceptPrint(e, defname)
        fhvfreq = g.NAN

    return fhvfreq


def editRadProPWM():
    """Enter values for Freqency and Duty Cycle"""

    defname = "editRadProPWM: "

    dprint(defname)
    setIndent(1)

    fbox = QFormLayout()
    fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

    ftitle = QLabel("Frequency [Hz]\n(100 Hz ... 100 kHz)      ")
    QfreqL = QLineEdit()
    QfreqL.setToolTip("The PWM Frequency of the HV Generator")
    # QfreqL.setText(f"{g.RadProFrequency:0.2f}")
    QfreqL.setText(f"{g.RadProFrequency:0.5g}")
    fbox.addRow(ftitle, QfreqL)

    dtitle = QLabel("Duty Cycle [%]\n(0 ... 100%)")
    QdutyL = QLineEdit()
    QdutyL.setToolTip("The PWM Duty Cycle of the HV Generator")
    # QdutyL.setText(f"{g.RadProDutycycle:0.2f}")
    QdutyL.setText(f"{g.RadProDutycycle:0.5g}")
    fbox.addRow(dtitle, QdutyL)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set RadPro PWM Values")
    d.setWindowModality(Qt.WindowModality.WindowModal)
    d.setMinimumWidth(200)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(fbox)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE key or Cancel Button pressed
        dprint(defname + "Canceling; no changes made")

    else:
        # OK pressed
        QueuefPrint(header("RadPro Device PWM Settings"))

        try:
            fval = clamp(float(QfreqL.text().strip().replace(",", ".")), 100, 100000)   # freq
            dval = clamp(float(QdutyL.text().strip().replace(",", ".")),   0,    100)   # duty
        except Exception as e:
            msg = "getting freq and duty values"
            exceptPrint(e, msg)
            QueuefPrint("FAILURE " + msg)
            fval = g.RadProFrequencyDefault
            dval = g.RadProDutycycleDefault

        g.RadProFrequency = round(fval, 2)
        g.RadProDutycycle = round(dval, 2)

        fmsg = f"{'PWM Frequency  - Attempted setting:      ':30s} {g.RadProFrequency:0.2f} Hz"
        dmsg = f"{'PWM Duty Cycle - Attempted setting:      ':30s} {g.RadProDutycycle:0.2f} %"
        QueuefPrint(fmsg)
        QueuefPrint(dmsg)
        dprint(defname, fmsg)
        dprint(defname, dmsg)

        setRadProPWM()

        fmsg = f"{'PWM Frequency  - RadPro reported setting:':30s} {getRadProFreq():0.2f} Hz"
        dmsg = f"{'PWM Duty Cycle - RadPro reported setting:':30s} {getRadProDuty():0.2f} %"
        QueuefPrint(fmsg)
        QueuefPrint(dmsg)
        dprint(defname, fmsg)
        dprint(defname, dmsg)

    setIndent(0)


def editRadProVoltage():
    """Set the voltage by defining PWM Freqency and Duty Cycle"""

    defname = "editRadProVoltage: "

    dprint(defname)
    setIndent(1)

    fbox = QFormLayout()
    fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

    Vtitle = QLabel("Anode-Voltage [V]\n(200 ... 800 Volt)      ")
    QVoltL = QLineEdit()
    QVoltL.setToolTip("The Anode-Voltage")
    # QVoltL.setText(f"{g.RadProVoltage:0.2f}")
    QVoltL.setText(f"{g.RadProVoltage:0.5g}")
    fbox.addRow(Vtitle, QVoltL)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set RadPro Voltage")
    d.setWindowModality(Qt.WindowModality.WindowModal)
    d.setMinimumWidth(200)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(-1))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(fbox)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval != 1:
        # ESCAPE key or Cancel Button pressed
        dprint(defname + "Canceling; no changes made")

    else:
        # OK pressed
        QueuefPrint(header("RadPro Device Anode Voltage"))

        try:
            volt = clamp(float(QVoltL.text().strip().replace(",", ".")), 200, 800)
        except Exception as e:
            msg = "getting volt value"
            exceptPrint(e, msg)
            QueuefPrint("FAILURE " + msg)

        g.RadProVoltage        = round(volt, 2)
        g.RadProVoltageDefault = g.RadProVoltage

        Vmsg = f"{'Voltage  - Attempted setting:        ':30s} {g.RadProVoltage:0.2f} V"
        QueuefPrint(Vmsg)
        dprint(defname, Vmsg)

        setRadProVoltage(g.RadProVoltageDefault)

        Vmsg = f"{'         - RadPro reported  PWM Freq:':30s} {g.RadProFrequency:0.2f} Hz"
        QueuefPrint(Vmsg)
        dprint(defname, Vmsg)

        Vmsg = f"{'         - RadPro reported  PWM Duty:':30s} {g.RadProDutycycle:0.2f} Hz"
        QueuefPrint(Vmsg)
        dprint(defname, Vmsg)

    setIndent(0)


def setRadProPWM():
    """set freq: in Hz,  duty: in %"""

    if g.RadProHardwareId is None: return g.NAN

    defname = "setRadProPWM: "

    queryRadPro(f"SET tubeHVFrequency {f'{g.RadProFrequency      :0.2f}'}")       # queryRadPro return is here always==""
    queryRadPro(f"SET tubeHVDutyCycle {f'{g.RadProDutycycle / 100:0.4f}'}")       # queryRadPro return is here always==""

    # msg  = f"Current PWM Setting: freq: {getRadProFreq():0.2f} Hz  duty: {getRadProDuty():5.2f}%"
    # rdprint(defname, msg)

#hv
def getRadProHVparameter():
    """get the parameter of a 1st or 3rd order parabola to fit Freq(Volt)"""

    defname = "getRadProHVparameter: "

    a, b, c, d = g.RadProHVparameter                                   # does this work as a dummy setting?????

    if g.RadProVoltageGeneration == "GLdefault":
        # take GL function; no custom defined formula

    # option #1 (auto - with either WCH or GEEHY chip)
        # YELLOW with WCH chip -  FNIRSI GC-01 CH32F103 #R8T6 #401546C10 #WCH
        if "FNIRSI GC-01 (CH32F103" in g.RadProHardwareId:

            # from run 12.12.24, BACKGROUND radiation level
            # 4 param fit
        #   a, b, c, d = -1044.49, 6.90631, -0.0134878, 1.09938e-05     # Target: 400V -> Result: 401       Delta: +1
                                                                        # Target: 450V -> Result: 450       Delta:  0
                                                                        # Target: 500V -> Result: 497       Delta: -3
                                                                        # Target: 550V -> Result: 546       Delta: -4
                                                                        # Target: 600V -> Result: 598       Delta: -2

            # 2 param fit (using 350...600V, r2= 0.992)
            a, b, c, d = -390.309, 1.62782, 0, 0                        # Target: 400V -> Result: 399       Delta: -1
                                                                        # Target: 450V -> Result: 455       Delta: +5
                                                                        # Target: 500V -> Result: 503       Delta: +3
                                                                        # Target: 550V -> Result: 546       Delta: -4
                                                                        # Target: 600V -> Result: 584       Delta: -16
            # manuelle Korrektur:
            a += 0.8



            # high CPS is not adequat!
            # from run 12.12.24, CPS=60 radiation level
            # 1st order fit,  r2 : 0.991
        #   a, b, c, d = -496.309, 1.93584, 0, 0                        # Target: 400V -> Result: 396       Delta: -4
                                                                        # Target: 450V -> Result: 455       Delta: +5
                                                                        # Target: 500V -> Result: 505       Delta: +5
                                                                        # Target: 550V -> Result: 548       Delta: -2
                                                                        # Target: 600V -> Result: 589       Delta: -11


            # F: 150 ... 500 Hz
            # WCH  Freq = -317.174 + 1.52174 * AVoltage
            # a, b, c, d = -317.174, 1.52174, 0, 0

        # BLUE with GEEHY chip -  FNIRSI GC-01 (Geehy APM32 #F103RBT6 #NTRN7 D1 #3141     2306
        elif "FNIRSI GC-01 (APM32" in g.RadProHardwareId:
            # 4 param fit
            a, b,c, d = 6911.97, -42.8945, 0.0909529, 0

            # 2 param fit; F: 2800 ... 10000 Hz
            # GEEHY Freq = -10463.2 + 37.8947 * AVoltage
            a, b, c, d = -10463.2, 37.8947, 0, 0


    else:
        # custom defined formula

        rpcfg = g.RadProVoltageGeneration.split(",")                    # gives 2 or 4 components

        # option #2 (4 components)
        if len(rpcfg) == 4:
            try:
                a = float(rpcfg[0])
                b = float(rpcfg[1])
                c = float(rpcfg[2])
                d = float(rpcfg[3])
            except Exception as e:
                exceptPrint(e, defname + "RadProVoltageGeneration")

        # option #3 (2 components)
        elif len(rpcfg) == 2:
            # Option #3: 'Flo=Vlo,FHi=VHi'

            # YELLOW: WCH     RadProVoltageGeneration = 150=307,500=537     # Freq = -317.174 + 1.52174 * Volt + 0 * Volt² + 0 * Volt³
            # BLUE:   GEEHY   RadProVoltageGeneration = 2800=350,10000=540  # Freq = -10463.2 + 37.8947 * Volt + 0 * Volt² + 0 * Volt³
            # #  ### Blue with about 20 fold higher freq ???? Relevant?????

            f0, v0 = rpcfg[0].split("=")
            f1, v1 = rpcfg[1].split("=")
            try:
                f0 = float(f0)
                v0 = float(v0)
                f1 = float(f1)
                v1 = float(v1)
            except Exception as e:
                exceptPrint(e, defname)

            ydprint(defname, f"f0: {f0}, v0: {v0} --- f1: {f1}  v1: {v1}")
            d = 0
            c = 0
            b = (f1 - f0) / (v1 - v0)
            a = f0 - b * v0

    g.RadProVoltageConfigStr = f"Freq = {a:0.6g} + {b:0.6g} * Volt + {c:0.6g} * Volt² + {d:0.6g} * Volt³"        #

    return [a, b, c, d]


#volt
def setRadProVoltage(NewVoltage):
    """set Anode Voltage in Volt"""
    # on yellow GC1: counts erst ab 308V gemessen!
    # on blue   GC1: counts erst ab 342V gemessen, @: F=2480 Hz, DC=50%

    ###########################################
    def getPWM(Volt):
        """Sets the Pulse Width Modulation by calculating Freq from fitted curve parameters with a fixed Duty cycle of 50%"""

        a, b, c, d = g.RadProHVparameter
        Freq       = ((d * Volt + c) * Volt + b) * Volt + a
        Duty       = 50                                        # Duty Cycle fix @ 50%

        return Freq, Duty
    ##########################################

    defname = "setRadProVoltage: "

    if g.RadProHardwareId is None: return g.NAN

    g.RadProVoltage                      = NewVoltage
    g.RadProFrequency, g.RadProDutycycle = getPWM(g.RadProVoltage)

    if g.RadProFrequency > 1E5:
        msg = f"Target Frequency {g.RadProFrequency:0.1f} exceeds max limit 100 kHz; Clamping to 100 kHz!"
        g.RadProFrequency = 1E5
        edprint(defname, msg)
        QueuefPrint(msg)

    elif g.RadProFrequency < 1E2:
        msg = f"Target Frequency {g.RadProFrequency:0.1f} is below min limit 100 Hz; Clamping to 100 Hz!"
        g.RadProFrequency = 1E2
        edprint(defname, msg)
        QueuefPrint(msg)

    queryRadPro(f"SET tubeHVFrequency {f'{g.RadProFrequency      :0.2f}'}")     # queryRadPro return is here always: ""
    queryRadPro(f"SET tubeHVDutyCycle {f'{g.RadProDutycycle / 100:0.4f}'}")     # queryRadPro return is here always: ""


#con
def setRadProVoltageControl():
    """Set the voltage control level"""

    defname = "setRadProVoltageControl: "

    dprint(defname)
    setIndent(1)

    fbox = QFormLayout()
    fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

    Atitle = QLabel("Activate Control:         ")
    Abox   = QCheckBox()
    Abox.setChecked(g.RadProHVControl[0])
    Abox.setTristate (False)
    Abox.setToolTip("Activate Control")
    fbox.addRow(Atitle, Abox)

    Vtitle = QLabel("Control Time Constant:\n(Default: 100=Medium)")
    QVoltL = QLineEdit()
    QVoltL.setToolTip("The Anode-Voltage Control Time Constant (1=VeryFast ... 10=Fast ... 100=Medium ... 1000=Slow)")
    QVoltL.setText(f"{g.RadProHVControl[1]:0.5g}")
    fbox.addRow(Vtitle, QVoltL)

    CFtitle = QLabel("Control Strength: \n(Default: 0.425)")
    CFL = QLineEdit()
    CFL.setToolTip("The Anode-Voltage Control Strength  (0.1 ... 1.0)")
    CFL.setText(f"{g.RadProHVControl[2]:0.5g}")
    fbox.addRow(CFtitle, CFL)

    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set RadPro Anode Voltage Control")
    d.setWindowModality(Qt.WindowModality.WindowModal)
    d.setMinimumWidth(300)

    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(fbox)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval == 0:
        # ESCAPE key or Cancel Button pressed
        dprint(defname + "Canceling; no changes made")

    else:
        # OK pressed
        QueuefPrint(header("RadPro Device Anode Voltage Control Level"))

        if Abox.isChecked():            g.RadProHVControl[0] = True
        else:                           g.RadProHVControl[0] = False

        Vmsg = f"{'Voltage Control Activation:':29s} {'Yes' if g.RadProHVControl[0] else 'No'}"
        QueuefPrint(Vmsg)
        dprint(defname, Vmsg)

        try:
            value = float(QVoltL.text().strip().replace(",", "."))
        except Exception as e:
            msg = "getting Anode-Voltage control value"
            exceptPrint(e, msg)
            QueuefPrint("FAILURE " + msg)
            value = 0  # --> OFF

        if value < 0:
            msg = f"A negative Speed is not permitted; keeping old value {g.RadProHVControl[1]}"
            QueuefPrint(msg)
            QueueSound("burp")
            dprint(defname, msg)
        else:
            g.RadProHVControl[1] = value
            Vmsg = f"{'Voltage Control Speed:':29s} {g.RadProHVControl[1]:0.6g}"
            QueuefPrint(Vmsg)
            dprint(defname, Vmsg)

        try:
            value = float(CFL.text().strip().replace(",", "."))
        except Exception as e:
            msg = "getting Anode-Voltage Factor value"
            exceptPrint(e, msg)
            QueuefPrint("FAILURE " + msg)
            value = 0.425

        if value <= 0:
            msg = f"A Strength of 0 or negative is not permitted; keeping old value {g.RadProHVControl[2]}"
            QueuefPrint(msg)
            QueueSound("burp")
            dprint(defname, msg)
        else:
            g.RadProHVControl[2] = value
            Vmsg = f"{'Voltage Control Strength:':29s} {g.RadProHVControl[2]:0.6g}"
            QueuefPrint(Vmsg)
            dprint(defname, Vmsg)

    setIndent(0)


#tab
def editRadProScanTab():
    """make the Scan settings"""

    defname = "editRadProScanTab: "

    dprint(defname)
    setIndent(1)

    fbox = QFormLayout()
    fbox.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)

    # # Select Scan type
    # r20 = QRadioButton("Off")
    # r21 = QRadioButton("Freq")
    # r22 = QRadioButton("Duty")
    # r23 = QRadioButton("Volt")
    # r20.setChecked(True)
    # r21.setChecked(False)
    # r22.setChecked(False)
    # r23.setChecked(False)
    # speakergroup = QButtonGroup()
    # speakergroup.addButton(r20)
    # speakergroup.addButton(r21)
    # speakergroup.addButton(r22)
    # speakergroup.addButton(r23)
    # hbox2 = QHBoxLayout()
    # hbox2.addWidget(r20)
    # hbox2.addWidget(r21)
    # hbox2.addWidget(r22)
    # hbox2.addWidget(r23)
    # hbox2.addStretch()
    # if   g.RadProScanType == 'Off':   r20.setChecked(True)
    # elif g.RadProScanType == 'Freq':  r21.setChecked(True)
    # elif g.RadProScanType == 'Duty':  r22.setChecked(True)
    # elif g.RadProScanType == 'Volt':  r23.setChecked(True)
    # fbox.addRow(QLabel("Scan Type"), hbox2)

    # renew
    QupdateL = QLineEdit()
    QupdateL.setToolTip("Apply one Step Change every Nth log cycle")
    QupdateL.setText(f"{g.RadProScanUpdate:0.5g}")
    fbox.addRow(QLabel("Scan step change every Nth log cycle        N:"), QupdateL)

    # Blank
    # fbox.addRow(QLabel(""), QLabel(""))

    # Initialize tab widget - tabs for:  Off, Freq, Duty, Volt
    tab0 = QWidget()
    tab0.layout = QVBoxLayout()

    tab1 = QWidget()
    tab1.layout = QVBoxLayout()

    tab2 = QWidget()
    tab2.layout = QVBoxLayout()

    tab3 = QWidget()
    tab3.layout = QVBoxLayout()

    # Add tabs
    tabs = QTabWidget()
    # tabs.resize(300,200)
    tabs.addTab(tab0,"Off")
    tabs.addTab(tab1,"Freq")
    tabs.addTab(tab2,"Duty")
    tabs.addTab(tab3,"Volt")


    # Off - Create tab 0
    fboxOff = QFormLayout()
    fboxOff.setFieldGrowthPolicy (QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
    fboxOff.addRow(QLabel("No Scanning; regular use"), QLabel(""))
    tab0.layout.addLayout(fboxOff)
    tab0.setLayout(tab0.layout)


    # Freq - Create tab 1
    fboxFreq = QFormLayout()
    fboxFreq.addRow(QLabel("<b>Frequency</b> Scan (100 Hz ... 100 kHz)"), QLabel(""))

    ftitle1 = QLabel("- Frequency Min [Hz]")
    QfreqL1 = QLineEdit()
    QfreqL1.setToolTip("The PWM Frequency of the HV Generator")
    QfreqL1.setText(f"{g.RadProScanFmin:0.6g}")
    fboxFreq.addRow(ftitle1, QfreqL1)

    ftitle1a = QLabel("- Frequency Max [Hz]")
    QfreqL1a = QLineEdit()
    QfreqL1a.setToolTip("The PWM Frequency of the HV Generator")
    QfreqL1a.setText(f"{g.RadProScanFmax:0.6g}")
    fboxFreq.addRow(ftitle1a, QfreqL1a)

    ftitle1b = QLabel("- Frequency Step [fold] (1.01 ... 1.1)")
    QfreqL1b = QLineEdit()
    QfreqL1b.setToolTip("The change of the PWM Frequency of the HV Generator as factor")
    QfreqL1b.setText(f"{g.RadProScanFstep:0.6g}")
    fboxFreq.addRow(ftitle1b, QfreqL1b)

    dtitle1 = QLabel("- @Duty Cycle [%] (0 ... 100)")
    QdutyL1 = QLineEdit()
    QdutyL1.setToolTip("The PWM Duty Cycle of the HV Generator; on 'auto' a default list will be used in succession.")
    QdutyL1.setText(", ".join(f"{a:0.6g}" for a in g.RadProScanFselect))
    fboxFreq.addRow(dtitle1, QdutyL1)

    tab1.layout.addLayout(fboxFreq)
    tab1.setLayout(tab1.layout)


    # Duty - Create tab 2
    fboxDuty = QFormLayout()
    fboxDuty.addRow(QLabel("<b>Duty</b> Scan (0 ... 100%)"), QLabel(""))

    dtitle2 = QLabel("- Duty Cycle Min [%]")
    QdutyL2 = QLineEdit()
    QdutyL2.setToolTip("The PWM Duty Cycle of the HV Generator")
    QdutyL2.setText(f"{g.RadProScanDmin:0.6g}")
    fboxDuty.addRow(dtitle2, QdutyL2)

    dtitle2a = QLabel("- Duty Cycle Max [%]")
    QdutyL2a = QLineEdit()
    QdutyL2a.setToolTip("The PWM Duty Cycle of the HV Generator")
    QdutyL2a.setText(f"{g.RadProScanDmax:0.6g}")
    fboxDuty.addRow(dtitle2a, QdutyL2a)

    dtitle2b = QLabel("- Duty Cycle Step [%]")
    QdutyL2b = QLineEdit()
    QdutyL2b.setToolTip("The change of the PWM Duty Cycle of the HV Generator in %-Points")
    QdutyL2b.setText(f"{g.RadProScanDstep:0.6g}")
    fboxDuty.addRow(dtitle2b, QdutyL2b)

    ftitle2 = QLabel("- @Frequency [Hz] (100 ... 100 000)")
    QfreqL2 = QLineEdit()
    QfreqL2.setToolTip("The PWM Frequency of the HV Generator; on 'auto' a default list will be used in succession.")
    QfreqL2.setText(", ".join(f"{a:0.6g}" for a in g.RadProScanDselect))
    fboxDuty.addRow(ftitle2, QfreqL2)

    tab2.layout.addLayout(fboxDuty)
    tab2.setLayout(tab2.layout)


    # Volt - Create tab 3
    fboxVolt = QFormLayout()
    fboxVolt.addRow(QLabel("<b>Volt</b> Scan (200 V ... 1200 V)"), QLabel(""))

    vtitle3 = QLabel("- Volt Min [V]")
    QVoltL3 = QLineEdit()
    QVoltL3.setToolTip("The Minimum of the Anode Voltage")
    QVoltL3.setText(f"{g.RadProScanVmin:0.5g}")
    fboxVolt.addRow(vtitle3, QVoltL3)

    vtitle3a = QLabel("- Volt Max [V]")
    QVoltL3a = QLineEdit()
    QVoltL3a.setToolTip("The Maximum of the Anode Voltage")
    QVoltL3a.setText(f"{g.RadProScanVmax:0.5g}")
    fboxVolt.addRow(vtitle3a, QVoltL3a)

    vtitle3b = QLabel("- Volt Step [V]")
    QVoltL3b = QLineEdit()
    QVoltL3b.setToolTip("The change in the Anode Voltage as [V]")
    QVoltL3b.setText(f"{g.RadProScanVstep:0.5g}")
    fboxVolt.addRow(vtitle3b, QVoltL3b)

    tab3.layout.addLayout(fboxVolt)
    tab3.setLayout(tab3.layout)


    # Dialog box
    d = QDialog()
    d.setWindowIcon(g.iconGeigerLog)
    d.setFont(g.fontstd)
    d.setWindowTitle("Set RadPro for Scanning")
    d.setWindowModality(Qt.WindowModality.WindowModal)
    d.setMinimumWidth(900)


    # Buttons
    bbox = QDialogButtonBox()
    bbox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok )
    bbox.accepted.connect(lambda: d.done(1))
    bbox.rejected.connect(lambda: d.done(0))

    layoutV = QVBoxLayout(d)
    layoutV.addLayout(fbox)
    layoutV.addWidget(tabs)
    layoutV.addWidget(bbox)

    retval = d.exec()
    #print("reval:", retval)

    if retval == 0:
        # ESCAPE key or Cancel Button pressed
        dprint(defname + "Canceling; no changes made")

    else:
        # OK pressed
        QueuefPrint(header("RadPro Device Scan Settings"))

        # renew interval
        try:    g.RadProScanUpdate = float(QupdateL .text().strip().replace(",", "."))
        except: pass

        # Off - no scan
        if tabs.currentIndex() == 0:
            g.RadProScanType = "Off"

            g.RadProScanUp   = True
            setRadProVoltage(g.RadProVoltageDefault)

            msg = f"Scanning is Off"
            QueuefPrint(msg)
            ydprint(defname, msg)


        # Freq scan
        elif tabs.currentIndex() == 1:
            g.RadProScanType    = "Freq"
            g.RadProScanFmin    = clamp(float(QfreqL1 .text().strip().replace(",", ".")), 100, 100000)   # freq
            g.RadProScanFmax    = clamp(float(QfreqL1a.text().strip().replace(",", ".")), 100, 100000)   # freq
            g.RadProScanFstep   = clamp(float(QfreqL1b.text().strip().replace(",", ".")),  1.01, 1.10)   # freq
            g.RadProScanFindex  = 0

            g.RadProScanFselect = []
            ccc = QdutyL1 .text().strip().split(",")
            for a in ccc:
                try:                    g.RadProScanFselect.append(float(a))
                except Exception as e:  pass

            g.RadProScanFduty = g.RadProScanFselect[0]

            ydprint(defname, "g.RadProScanFselect: ", g.RadProScanFselect)
            msg0 = f"Scanning type:'{g.RadProScanType}'  Range:{g.RadProScanFmin:0.6g}...{g.RadProScanFmax:0.6g} Hz, Step:{g.RadProScanFstep:0.6g} [fold], renew every {g.RadProScanUpdate:0.0f} log cycles"
            msg1 = f"@Dutycycle[%]: {', '.join(f'{a:0.6g}' for a in g.RadProScanFselect)}"
            ydprint(defname, msg0)
            ydprint(defname, msg1)
            QueuefPrint(msg0)
            QueuefPrint(msg1)

            g.RadProFrequency = g.RadProScanFmin
            g.RadProDutycycle = g.RadProScanFduty
            setRadProPWM()


        # Duty scan
        elif tabs.currentIndex() == 2:
            g.RadProScanType    = "Duty"
            g.RadProScanDmin    = clamp(float(QdutyL2 .text().strip().replace(",", ".")), 0.0, 100)         # duty
            g.RadProScanDmax    = clamp(float(QdutyL2a.text().strip().replace(",", ".")), 0.0, 100)         # duty
            g.RadProScanDstep   = clamp(float(QdutyL2b.text().strip().replace(",", ".")), 0.1,  10)         # duty
            g.RadProScanDindex  = 0

            g.RadProScanDselect = []
            ccc = QfreqL2 .text().strip().split(",")
            for a in ccc:
                try:                    g.RadProScanDselect.append(float(a))
                except Exception as e:  pass

            g.RadProScanDfreq = g.RadProScanDselect[0]

            msg0 = f"Scanning type:'{g.RadProScanType}'  Range:{g.RadProScanDmin:0.6g}...{g.RadProScanDmax:0.6g} %, Step:{g.RadProScanDstep:0.6g} %, renew every {g.RadProScanUpdate:0.0f} log cycles"
            msg1 = f"@Freq[Hz]: {', '.join(f'{a:0.6g}' for a in g.RadProScanDselect)}"
            ydprint(defname, msg0)
            ydprint(defname, msg1)
            QueuefPrint(msg0)
            QueuefPrint(msg1)

            g.RadProFrequency = g.RadProScanDfreq
            g.RadProDutycycle = g.RadProScanDmin
            setRadProPWM()


        # Volt scan
        elif tabs.currentIndex() == 3:
            g.RadProScanType  = "Volt"
            g.RadProScanVmin  = clamp(float(QVoltL3 .text().strip().replace(",", ".")), 100, 100000)   # freq
            g.RadProScanVmax  = clamp(float(QVoltL3a.text().strip().replace(",", ".")), 100, 100000)   # freq
            g.RadProScanVstep = clamp(float(QVoltL3b.text().strip().replace(",", ".")), 0.1, 100)      # freq

            msg = f"Scanning type:'{g.RadProScanType}', Range:{g.RadProScanVmin:0.6g}...{g.RadProScanVmax:0.6g} V, Step:{g.RadProScanVstep:0.6g} V, renew every {g.RadProScanUpdate:0.0f} log cycles"
            ydprint(defname, msg)
            QueuefPrint(msg)

            g.RadProScanUp   = True
            setRadProVoltage(g.RadProScanVmin)

    setIndent(0)

