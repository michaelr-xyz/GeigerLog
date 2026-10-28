#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
WiFiServer - calling external WiFiServer Devices
NOTE: the external device acts as a http-server: you have to 'browse' it for data
      Examples: Tasmota-Plug, GLDS (see GeigerLog Manual)
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
import gsup_sql


def initWiFiServer():
    """Initialize WiFiServer"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    ### set device name
    g.Devices["WiFiServer"][g.DNAME] = "WiFiServer"

    ### set configuration
    ### bisher braucht nur Ufs bei der 16 MB version bis zu 702 ms!
    # g.WiFiServerTimeout = 0.5  # sec                                   # with Tasmotaplug: it averages ~140 ms, tops 450 ms,
    # g.WiFiServerTimeout = 1.0  # sec                                   # with Tasmotaplug: it averages ~140 ms, tops 450 ms,
                                                                       # except when it fails, then even 2 sec is not enough???
    # g.WiFiServerTimeout = 0.7  # sec                                   # is 0.5 perhaps too short for regular fluctuations?
    g.WiFiServerTimeout = 10.0  # sec                                   # is 0.5 perhaps too short for regular fluctuations?


    ### count of connected Server
    connectedSrv = 0

    ### write Berry Code to file
    saveBerryGeigerCode(writefile=True)

    # assemble WiFiServerList
    for wslIndex in range(len(g.WiFiServerList)):
        if g.WiFiServerList[wslIndex]["DevActiv"]:                     # is WiFiServer activated?
            DevCat      = g.WiFiServerList[wslIndex]["DevCat"]
            DevType     = g.WiFiServerList[wslIndex]["DevType"]
            DevName     = g.WiFiServerList[wslIndex]["DevName"]
            DevUrl      = geturl(wslIndex)
            currentWS   = f"#{wslIndex} {DevCat} {DevType}: "

            dprint(defname, f"{currentWS}Trying url: {DevUrl}")        # like:  Device #0:  Name: Tasmota  url: http://10.0.0.58:80

            defnameW = defname + f"#{wslIndex} {DevCat} {DevType}: "

            ### checking server response on its root url, like: http://10.0.0.58:80
            trials = 2
            for trial in range(trials):
                response, rmsg, rdur = getTasmotaResponse(DevUrl, "")               # check root - is server present?
                if response > "":                                               # found a device at url; is it the right one?
                    ### init device
                    success, imsg, DevName, DevID = initWiFiServerDev(wslIndex)
                    if success:
                        g.WiFiServerList[wslIndex]["DevName"] = DevName
                        g.WiFiServerList[wslIndex]["DevID"]   = DevID
                        msg = f"Success - Found: Name: '{DevName}'  ID: '{DevID}'   at {DevUrl}"
                        gdprint(defnameW, msg)
                        fprint(f"{currentWS:20s}{msg}")

                        g.WiFiServerList[wslIndex]["DevConnect"] = True
                        connectedSrv += 1

                        break   # get out of trial for-loop
                    else:
                        msg = f"FAILURE - {imsg}"
                        # rdprint(defnameW, msg)
                        efprint(f"{currentWS:20s}{msg}")
                        g.WiFiServerList[wslIndex]["DevConnect"] = False
                        break

                else:
                    ### did NOT find a server
                    g.WiFiServerList[wslIndex]["DevConnect"] = False

                    if trial < trials - 1:
                        rdprint(defnameW, f"{currentWS} Re-Trying")
                        time.sleep(0.1)
                    else:
                        DevID = "Undefined"
                        msg   = f"{currentWS:20s}FAILURE - Found no server in {trial + 1} of {trials} trials  @ {DevUrl}"
                        rdprint(defname, msg)
                        efprint(msg)
            ### end for trials loop
            print()

    # rdprint(defnameW, "g.WiFiServerList:", g.WiFiServerList)


    ### combine variables from all CONNECTED WiFiServers
    VarsCombo = ""
    for wsl in g.WiFiServerList:
        if wsl["DevConnect"]:    VarsCombo += wsl["DevVars"] + ","
    # dprint(defnameW, f"VarsCombo:  '{VarsCombo}'  {type(VarsCombo)}")

    ### sort Vars in GeigerLog order into list; ignore "None"
    g.WiFiServerVariables = []
    for vname in g.VarsCopy:
        # iydprint(defnameW, f"vname: {vname}")
        if vname in VarsCombo.split(","):
            g.WiFiServerVariables.append(vname)
    # cdprint(defnameW, f"{currentWS} WiFiServerVariables: {g.WiFiServerVariables}")

    if connectedSrv > 0:   # at least 1 connected?
        # connected
        g.Devices["WiFiServer"][g.CONN] = True
        msg = ""
        dprint(defname, f"Init complete with {connectedSrv} WiFiServer connected")
        WFSVars = ",".join(v for v in g.WiFiServerVariables)
        g.WiFiServerVariables = setLoggableVariables("WiFiServer", WFSVars)
        # gdprint(defnameW, f"Overall Variables: {g.WiFiServerVariables}")

        dprint(defnameW, f"WiFiServer List:")
        chunk = 125
        for wslIndex, wsl in enumerate(g.WiFiServerList):
            swsl = str(wsl)
            if wsl["DevConnect"]:
                dprint(f"{" "*3}WiFiServer #{wslIndex} connected  {swsl[0:chunk]}")
                loop = 1
                while True:
                    newstart = chunk * loop
                    newstop  = chunk * (loop + 1)
                    print(f"{" "*60}{swsl[newstart : newstop]}")
                    if newstop > len(swsl):  break
                    loop += 1

            else:
                dprint(f"{" "*3}WiFiServer #{wslIndex} NOT CNCTD  {swsl[0:chunk]}")
                loop = 1
                while True:
                    newstart = chunk * loop
                    newstop  = chunk * (loop + 1)
                    print(f"{" "*60}{swsl[newstart : newstop]}")
                    if newstop > len(swsl):  break
                    loop += 1

    else:
        # none connected
        g.Devices["WiFiServer"][g.CONN] = False
        msg = "No connection to any WiFiServer Device"
        rdprint(defname, msg)

    setIndent(0)

    return msg


def initWiFiServerDev(wslIndex):
    """
    Initialize the designated external device
    return: success, initMsg, DevName, DevID
    """

    defname  = gd(sys._getframe().f_code.co_name)
    success  = False
    initMsg  = ""

    DevCat   = g.WiFiServerList[wslIndex]["DevCat"]
    DevType  = g.WiFiServerList[wslIndex]["DevType"]
    DevUrl   = geturl(wslIndex)
    DevName  = "NAME UNDEFINED"
    DevID    = "ID UNDEFINED"

    defname += f"#{wslIndex} {DevCat} {DevType}: "

    try:
        ### Tasmota Plug
        if DevCat == "Tasmota" and DevType == "Plug":
            ### Difference to other Tasmota only in:
            #    "StatusSNS": {
            #       "Time": "2025-12-13T10:13:15",
            #       "ENERGY": {
            #          "TotalStartTime": "2025-11-12T08:56:02",
            #          "Total": 0.46,
            #          "Yesterday": 0.016,
            #          "Today": 0.006,
            #          "Power": 0.0,
            #          "ApparentPower": 0.0,
            #          "ReactivePower": 0.0,
            #          "Factor": 0.0,
            #          "Voltage": 232.4,
            #          "Current": 0.0
            #       }
            #    },
            try:
                ### getting status0
                response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=status0")
                try:
                    jresponse = json.loads(response)
                    # iydprint(defname, "\n", json.dumps(jresponse, indent=3))  # pretty print
                    DevName = jresponse["Status"]["DeviceName"]
                    DevID   = jresponse["Status"]["Topic"]
                    if "Energy" in response:    Energy = jresponse["StatusSNS"]["ENERGY"]
                    else:                       Energy = None
                    # iydprint(defname, f"Energy: {Energy}")
                except Exception as e:
                    exceptPrint(e, defname + f"Getting JSON")
                    success = False
                    initMsg    += " - FAILURE to get Identifiers"
                else:
                    if Energy is None:
                        success = False
                        initMsg    += f" - Found a Tasmota device, but NOT a Tasmota Plug at {DevUrl}"
                    else:
                        success = True
                        initMsg = "Found a Tasmota Plug"

                        ### set power switch to On (just in case it isn't!)
                        response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=power%20On")

                        ### switch off the network scans
                        ### from:  https://tasmota.github.io/docs/Commands/#setoptions
                        ### "SetOption57: Wi-Fi network re-scan every 44 minutes with alternate to +10dB stronger
                        ###  signal if detected(only visible networks) 0 = disable; 1 = enable (default)"
                        ### Not needed for this Plug device
                        # response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=SetOption57%20Off")

            except Exception as e:
                exceptPrint(e, f"FAILURE in {defname}")
                success = False
                initMsg    += " - FAILURE in Init"


        ### Tasmota Geiger
        elif DevCat == "Tasmota" and DevType == "Geiger":
            ### getting status0
            response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=status0")
            if response > "":
                jresponse = json.loads(response)
                # iydprint(defname, "\n", json.dumps(jresponse, indent=3))          # pretty print
                DevName   = jresponse["Status"]["DeviceName"]
                DevID     = jresponse["Status"]["Topic"]                            # like: "Topic":"tasmota_E1E2F4"
                success   = True
                initMsg   = f"Found a '{DevName}'"
            else:
                success   = False
                initMsg   = f"Could not initialize the device '{DevCat} {DevType}'"



        ### Tasmota Poisson
        elif DevCat == "Tasmota" and DevType == "Poisson":
            DevName = "P-Calls"
            DevID   = "Simul"


        ### Tasmota GDK101 devices
        elif DevCat == "Tasmota" and DevType == "GDK101":
            # {
            # "Time": "2025-11-29T17:23:45",
            # "GDK101": {
            #     "Firmware": 1.6,
            #     "RadiationAvg10Min": 0.02,
            #     "RadiationAvg1Min": 0.05,
            #     "Status": 2,
            #     "Vibration": 0,
            #     "Measurement": "00:05"
            # }
            # }
            response, rmsg, rdur = getTasmotaResponse(DevUrl, "")
            if response > "":
                ### getting Devicename
                response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=status")         # 'status' is needed for the devicename
                jresponse = json.loads(response)
                # iydprint(defname, "\n", json.dumps(jresponse, indent=3))
                DevName = jresponse["Status"]["DeviceName"]                     # like:  Tasmota
                DevID   = jresponse["Status"]["Topic"]                          # like:  tasmota_E1E2F4


            ### get the firmware
            response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=STATUS%2010")         # get the 'status 10' data
            if response > "":
                try:
                    jresponse   = json.loads(response)
                    iydprint(defname, "\n", json.dumps(jresponse, indent=3))
                    firmware    = jresponse["StatusSNS"]["GDK101"]["Firmware"]
                    DevID      += f" {firmware}"
                except Exception as e:
                    exceptPrint(e, f"{DevType} getting jresponse and firmware")
                    response    = ""
                    DevID      += f" {'No FW'}"


    ### GLDS devices
        elif DevCat == "GLDS" and (DevType == "GMCserver"   or
                                   DevType == "SimulServer" or
                                   DevType == "PulseServer" or
                                   DevType == "RaspiServer")   :
            ### getting DeviceName
            response, rmsg, rdur = getTasmotaResponse(DevUrl, "")
            if response > "":   DevName = getGLDSdevicename(response)
            else:               DevName = "No Name"

            ### getting ID
            response, rmsg, rdur = getTasmotaResponse(DevUrl, "/id")
            if response > "":   DevID = response
            else:               DevID = "No ID"

        else:
            DevName = f"No DevType: {DevType}"
            DevID   = f"No ID"

        ### gilt für alle devices
        # gdprint(defname, f"Initialized: DevType: {DevType}  DevName: {DevName}  DevID: {DevID}")

    except Exception as e:
        exceptPrint(e, defname)

    return success, initMsg, DevName, DevID


def geturl(wslIndex):

    IP     = g.WiFiServerList[wslIndex]["DevIP"]
    port   = g.WiFiServerList[wslIndex]["DevPort"]
    url    = f"http://{IP}:{port}"

    return url


def getGLDSdevicename(response):
    """extract the DevName from a GLDS response"""

    defname = gd(sys._getframe().f_code.co_name)

    try:
        index1, index2 = -1, -1
        index1 = response.find("<h1 DeviceName>")
        if index1 >= 0:
            index2  = response.find("</h1>", index1)
            if index2 >= 0:
                DevName = response[index1 + 15: index2 ]
        # iydprint(defname, f"index1: {index1}  index2: {index2}")
    except Exception as e:
        exceptPrint(e, "Extract GLDS DeviceName")

    return DevName


def terminateWiFiServer():
    """terminating all connections"""
    # nothing has to be done; the httpserver is off by default

    defname     = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    g.Devices["WiFiServer"][g.CONN] = False

    dprint(defname + "Terminated")
    setIndent(0)


def getTasmotaResponse(url, GET):
    """get response on url + GET; response is string; it is empty on failure"""

    defname   = gd(sys._getframe().f_code.co_name)
    FullURL   = url + GET
    errortext = ""              # aka no error

    start   = time.time()

    try:
        response = ""
        with urllib.request.urlopen(FullURL, timeout=g.WiFiServerTimeout) as page:
            response = page.read().strip().decode("UTF-8", errors='replace')       # type(response) = <class 'str'>
            # irdprint(defname, f"type(response): {type(response)}")
    except urllib.error.URLError as e:
        exceptPrint(e, defname + f"URLError  {FullURL}")
        errortext = f"URLError '{e.reason}'"
    except TimeoutError as e:
        exceptPrint(e, defname + f"Timeout Error  {FullURL}")
        errortext = f"TimeoutError  '{e}'"
    except urllib.error.HTTPError as e:
        exceptPrint(e, defname + f"HTTPError {FullURL}")
        errortext = f"HTTPError '{e.reason}'"
    except OSError as e:
        exceptPrint(e, defname + f"OSError   {FullURL}")
        errortext = f"OSError '{e.reason}'"
    except Exception as e:
        exceptPrint(e, defname + f"{FullURL}")
        errortext = f"Exception '{e.reason}'"

    Dur     = 1e3 * (time.time() - start)

    ### printing to log
    chunk = 80
    lenrs = len(response)
    if   lenrs > chunk: presponse = f"{response[0:chunk]} ... (showing {chunk} of {lenrs} chars)"
    elif lenrs == 0   : presponse = "<empty>"
    else:               presponse = response

    lenfu = len(FullURL)
    if   lenfu > chunk: pFullURL = f"{FullURL[0:chunk]} ... (showing {chunk} of {lenfu} chars)"
    elif lenfu == 0   : pFullURL = "<empty>"
    else:               pFullURL = FullURL

    cdprint(defname, f"command:  {pFullURL} Dur: {Dur:0.0f} ms")
    cdprint(defname, f"response: {presponse}")

    ### reporting errors
    if errortext > "":
        if "Timeout" in errortext :
            color = "<red>"
            QueueSound("alarm")
        elif "timed out" in errortext :
            color = "<magenta>"
            QueueSound("cocoo")
        else:
            color = "<black>"

        QueuefPrint(f"{stime()} ERR: {Dur:0.0f} ms  {errortext}  {FullURL}", color=color)

    return response, FullURL, Dur


# get ALL data from ALL WiFiServer devices
def getValuesWiFiSrvAll(varlist):
    """Read data from all connected WiFiServer devices"""
    # NOTE: varlist is ignored; individual vars for devices is used

    defname = gd(sys._getframe().f_code.co_name)
    alldata = {}

    for wslIndex in range(len(g.WiFiServerList)):
        device = g.WiFiServerList[wslIndex]
        # irdprint(defname, f"device: {device}")
        cat    = device["DevCat"]
        dtype  = device["DevType"]
        url    = geturl(wslIndex)
        vars   = device["DevVarsList"]
        if device["DevConnect"]:  alldata = {**alldata, **getValuesWFS(DevCat=cat, DevType=dtype, url=url, varlist=vars, wslIndex=wslIndex)}

    return alldata


# get data from single WiFiServer device
def getValuesWFS(DevCat, DevType, url, varlist, wslIndex):
    """Read all WiFiServer data from a single device"""

    gVstart  = time.time()

    defname  = gd(sys._getframe().f_code.co_name)[0:-4]
    defname  = defname[0:12] + f" #{wslIndex} {DevType[0:6]}: "
    alldata  = {}                                                         # dict for return data
    datalist = []
    response = ""
    rmsg     = ""

    while True: ########################################################### to allow break statements
    ### Tasmota plug devices
        if DevCat == "Tasmota" and DevType == "Plug":
            response, rmsg, rdur = getTasmotaResponse(url, "/cm?cmnd=Status%2010")   # takes 145 ms avg, range 50...400 ms on NOUS A8T Tasmota plug
            if response > "":
                try:
                    jresponse   = json.loads(response)
                    # iydprint(defname, "\n", json.dumps(jresponse, indent=3))
                    Eresponse   = jresponse["StatusSNS"]["ENERGY"]
                except Exception as e:
                    exceptPrint(e, f"{DevType} getting jresponse, Eresponse")
                    response = ""
                    break

                try:    volt        = Eresponse["Voltage"]
                except: volt        = g.NAN
                try:    curr        = Eresponse["Current"]
                except: curr        = g.NAN
                try:    powr        = Eresponse["Power"]
                except: powr        = g.NAN
                try:    etotal      = Eresponse["Total"]
                except: etotal      = g.NAN
                try:    apppowr     = Eresponse["ApparentPower"]
                except: apppowr     = g.NAN
                try:    rctpowr     = Eresponse["ReactivePower"]
                except: rctpowr     = g.NAN
                try:    factor      = Eresponse["Factor"]               # is always same as: powr / apppowr
                except: factor      = g.NAN
                # iydprint(defname, f"Tasmota Factor: {factor}  Calculated Factor: {powr / apppowr:0.2f}")

                datalist = [volt, curr, powr, etotal, apppowr, rctpowr, factor, rdur]


    ### Tasmota Geiger devices
        elif DevCat == "Tasmota" and DevType == "Geiger":
            ### response like: 17:51:34.316 RSL: RESULT = {"geiger":{"CPM":8172,"CPS":160}}

            response, rmsg, rdur = getTasmotaResponse(url, "/cm?cmnd=geiger")   # get the data

            ### got data?
            if response == "":
                # no, failure to get data
                iydprint(defname, "Breaking, because response is empty")
                break                                                           # exit while loop

            ### yes, got data
            try:
                jresponse   = json.loads(response)
                # iydprint(defname, "\n", json.dumps(jresponse, indent=3))      # pretty print
                Cresponse   = jresponse["geiger"]                               # class 'dict'; like: Cresponse: {'CPS': 48, 'CPM': 3170}
            except Exception as e:
                exceptPrint(e, f"{DevCat} {DevType} bad response getting data: '{response}")
                response = ""
                break                                                           # exit while loop on misformed response

            ### set counts
            try:
                cpm = Cresponse["CPM"]      # CPM
                cps = Cresponse["CPS"]      # CPS
                dlt = Cresponse["Dlt"]      # Delta time [ms]
                # svg = Cresponse["Svg"]      # Saving flag 0 or 1

                if cpm is None: cpm = g.NAN
                if cps is None: cps = g.NAN
                if dlt is None: dlt = g.NAN
                # if svg is None: svg = g.NAN

                if cpm > g.WiFiServerCPMlimit:  cpm = g.NAN  # data can't be real!
                if cps > g.WiFiServerCPSlimit:  cps = g.NAN  # data can't be real!

            except Exception as e:
                exceptPrint(e, f"Setting CPM, CPS, dlt from Cresponse: {Cresponse}")
                cpm = g.NAN
                cps = g.NAN
                dlt = g.NAN
                # svg = g.NAN

            # datalist = [cpm, cps, rdur, dlt, svg]
            datalist = [cpm, cps, rdur, dlt]


    ### Tasmota Poisson devices - simulating Geiger counts from exponential distr of time between pulses
        elif DevCat == "Tasmota" and DevType == "Poisson":
            ### duration is <1 ms

            response, rmsg, rdur = "Dummy", "Dummy", g.NAN
            cpsraw      = 0
            deltat      = 0
            records     = 1     #
            mean        = 100   # cps

            cps         = int(np.random.poisson(mean, 1))
            g.WiFiServerList[wslIndex]["CPSlist"].append(int(cps))
            cpm = sum(g.WiFiServerList[wslIndex]["CPSlist"])

            cycleStd    = 5.0
            cycleStdDev = 0.1
            cycle       = cycleStd #+ np.random.normal(cycleStdDev, cycleStdDev, size=records)
            while True:
                dtevent = np.random.exponential(1 / mean, size=records) # duration before next pulse in sec
                deltat += dtevent
                if deltat < cycle: cpsraw += 1
                else:              break

            cps1st      = round(float(cpsraw / cycle), 0)

            datalist = [cpm, cps, cps1st, round(float(cpsraw), 0), float(deltat), float(cycle) ]


    ### Tasmota GDK101 devices
        elif DevCat == "Tasmota" and DevType == "GDK101":
            # {
            # "Time": "2025-11-29T17:23:45",
            # "GDK101": {
            #     "Firmware": 1.6,
            #     "RadiationAvg10Min": 0.02,
            #     "RadiationAvg1Min": 0.05,
            #     "Status": 2,
            #     "Vibration": 0,
            #     "Measurement": "00:05"
            # }
            # }

            response, rmsg, rdur = getTasmotaResponse(url, "/cm?cmnd=STATUS%2010")            # get the data
            if response > "":
                try:
                    jresponse   = json.loads(response)
                    iydprint(defname, "\n", json.dumps(jresponse, indent=3))
                    r1min       = jresponse["StatusSNS"]["GDK101"]["RadiationAvg1Min"]
                    r10min      = jresponse["StatusSNS"]["GDK101"]["RadiationAvg10Min"]
                    status      = jresponse["StatusSNS"]["GDK101"]["Status"]
                    vibration   = jresponse["StatusSNS"]["GDK101"]["Vibration"]
                    measurement = jresponse["StatusSNS"]["GDK101"]["Measurement"]

                except Exception as e:
                    exceptPrint(e, f"{DevType} getting jresponse and data")
                    response = ""
                    break

                iydprint(defname, "r1min, r10min, status, vibration, measurement:  ", r1min, r10min, status, vibration, measurement)

                datalist = [r1min, r10min, status, vibration, measurement]


    ### GLDS devices
        elif DevCat == "GLDS" and (DevType == "GMCserver"   or
                                   DevType == "SimulServer" or
                                   DevType == "PulseServer" or
                                   DevType == "RaspiServer")   :
            response, rmsg, rdur = getTasmotaResponse(url, "/data")
            if response > "":
                try:
                    rlist = response.split(",")
                    for rl in rlist:
                        try:
                            if rl > ""  :   val = float(rl)
                            else:           val = g.NAN
                        except Exception as e:
                            exceptPrint(e, f"{DevType} data")
                            val = g.NAN
                        datalist.append(val)

                except Exception as e:
                    exceptPrint(e, f"getting {DevType} values")


    ### UNDEFINED - any other DevType
        else:
            response, rmsg, rdur = "", f"DevType '{DevType}' is UNDEFINED", g.NAN


    ### checking response
        # cdprint(defname, f"Checking: DevType: {DevType}  response: {response}   datalist: {datalist}  type(datalist): {type(datalist)}  rmsg: {rmsg}")
        if response > "":
            ### ok, got good response
            try:
                ### fill alldata with vname from varlist
                for vindex, vname in enumerate(varlist):
                    # irdprint(defname, f"vindex: {vindex}  vname: {vname}")
                    if vindex > len(datalist) - 1: break                                    # datalist exhaustet
                    if vname in g.VarsCopy:     alldata.update({vname: datalist[vindex]})   # update alldata by vname
            except Exception as e:
                exceptPrint(e, f"checking response: '{response}'")

        else:
            # FAIL, got empty response
            g.LogReadingsFail += 1
            msg  = f"NO DATA {DevType} " + rmsg                                                 # need DevType for GUI mesg
            msg += " - Failed readings: {:0.3%}".format(g.LogReadingsFail / (g.LogReadings + 1))
            if g.debug: QueuefPrint(longstime() + " " + msg, color="red", error=True)
            edprint(defname, msg)

    ### must have final break to exit while loop
        break

    ### while loop has ended ################################################################

    gVdurAfter = 1e3 * (time.time() - gVstart)  # is some <0.3 ms longer than the getTasmotaResponse call alone
    vprintLoggedValues(defname, varlist, alldata, gVdurAfter)

    return alldata


def getInfoWiFiServer(extended=False):
    """Info on the WiFiServer Device"""

    defname  = gd(sys._getframe().f_code.co_name)

    WiFiInfo           = "Configured Connection:        GeigerLog PlugIn\n"

    if not g.Devices["WiFiServer"][g.CONN]:
        # not connected
        WiFiInfo      += "<red>Device is not connected</red>"
    else:
        # is connected     N     url    CNCT  CAT   TYPE   id     Name   Vars
        wtmplt         = "#{:1s} {:26s} {:4s} {:9s} {:11s} {:17s} {:22s} {}\n"

        WiFiInfo      += "Connected Device:             {}\n".format(g.Devices["WiFiServer"][g.DNAME])
        WiFiInfo      += "\n"
        WiFiInfo      += wtmplt.format('N', "Activated Devices (URL)", "Cnct", "Category", "Type", "ID", "Name", "Vars")

        for i, wsl in enumerate(g.WiFiServerList):
            DevCat     = wsl["DevCat"] .strip()
            DevType    = wsl["DevType"].strip()
            vars       = wsl["DevVars"].strip()
            name       = wsl["DevName"].strip()
            id         = wsl["DevID"]  .strip()
            url        = geturl(i)
            connect    = "YES" if wsl["DevConnect"] else "NO"
            WiFiInfo  += wtmplt.format(str(i), url, connect, DevCat, DevType, id, name, vars)

        WiFiInfo      += "\n"
        WiFiInfo      += "Active Variables:             {}\n"        .format(g.WiFiServerVariables)
        WiFiInfo      += getTubeSensitivities(g.WiFiServerVariables)

    if extended:
        oldWiFiServerTimeout = g.WiFiServerTimeout
        g.WiFiServerTimeout  = 1.0                                                     # temporarily change Timeout

        WiFiInfo      += "\n"
        WiFiInfo      += "Extended Info:\n"
        WiFiInfo      += "#N Activated Devices (URL):\n"
        fail           = "FAIL"

        for i, wsl in enumerate(g.WiFiServerList):
            if not wsl["DevConnect"]: continue

            DevCat     = wsl["DevCat"]
            DevType    = wsl["DevType"]
            DevUrl     = geturl(i)
            # iydprint(defname, f"{DevCat}  {DevType}  {DevUrl}")

            if wsl["DevConnect"]:
                ### all status details
                response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=status0")      # 'status0' gets everything
                if response > "":
                    try:
                        jresponse = json.loads(response)
                        # iydprint(defname, "\n", json.dumps(jresponse, indent=3))      # pretty print
                        version   = jresponse["StatusFWR"]["Version"]                   # like: "StatusFWR": {"Version": "15.1.0(release-tasmota32)", ...
                        cpufreq   = jresponse["StatusFWR"]["CpuFrequency"]              # like: "StatusFWR": {"CpuFrequency": 160,
                        hardware  = jresponse["StatusFWR"]["Hardware"]                  # like: "StatusFWR": {"Hardware": "ESP32-D0WD-V3 v3.0"
                        progsize  = jresponse["StatusMEM"]["ProgramSize"] / 1e3         # like: "StatusMEM":{"ProgramSize":2082,"Free":797,
                        progfree  = jresponse["StatusMEM"]["Free"]        / 1e3         # like: "StatusMEM":{"ProgramSize":2082,"Free":797,
                        TSleep    = jresponse["StatusSTS"]["Sleep"]                     # should be 1 [ms]

                    except Exception as e:
                        exceptPrint(e, defname + f"getting json")
                        version   = fail
                        cpufreq   = g.NAN
                        hardware  = fail
                        progsize  = g.NAN
                        progfree  = g.NAN
                else:
                    version   = fail
                    cpufreq   = g.NAN
                    hardware  = fail
                    progsize  = g.NAN
                    progfree  = g.NAN

                progmax     = progsize + progfree                                   # Est for total space available???
                pcprogfree  = progfree / progmax                                    # max prog size possible

                ### module info
                response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=Module")
                if response > "":
                    try:
                        jresponse = json.loads(response)
                        # iydprint(defname, "\n", json.dumps(jresponse, indent=3))      # pretty print
                        TModule   = jresponse["Module"]
                    except Exception as e:
                        exceptPrint(e, defname + f"getting json on module")
                        TModule = fail
                else:
                    TModule = fail


                ### all Ufs (Universal File System) details
                response, rmsg, rdur = getTasmotaResponse(DevUrl, "/cm?cmnd=Ufs")
                if response > "":
                    try:
                        jresponse = json.loads(response)
                        # iydprint(defname, "\n", json.dumps(jresponse, indent=3))      # pretty print
                        ufssize   = jresponse["Ufs"]["Size"] / 1e3                      # UfsSize 	Filesystem size in kb
                        ufsfree   = jresponse["Ufs"]["Free"] / 1e3                      # UfsFree 	Filesystem free size in kb
                        ufstype   = jresponse["Ufs"]["Type"]                            # UfsType 	Get filesystem type
                    except Exception as e:
                        exceptPrint(e, defname + f"getting json")
                        ufssize   = g.NAN
                        ufsfree   = g.NAN
                        ufstype   = 4
                else:
                    ufssize   = g.NAN
                    ufsfree   = g.NAN
                    ufstype   = 4

                prcfree   = ufsfree / ufssize                                            # % Ufsfree
                fstype    = ["None", "SD card", "Flash file", "LittleFS", fail][ufstype] # 0=none, 1=SD card, 2=Flash file, 3=LittleFS, 4=FAILURE


                FlashSizB  = getBerryFlashSize(DevCat, DevUrl)
                FlashSizMB = FlashSizB / 2**20
                HistSize   = getBerryHistSize(DevCat, DevType, DevUrl)
                WiFiInfo  += f"#{str(i):1s} {DevUrl:26s} {'Tasmota Version'  :20s}: {version}\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Tasmota Sleep'    :20s}: {TSleep} ms\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Tasmota Module'   :20s}: {TModule}\n"

                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'ESP32 Hardware'   :20s}: {hardware}\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'ESP32 Frequency'  :20s}: {cpufreq} MHz\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'ESP32 Flash Size' :20s}: {FlashSizMB:0.3f} MB ({FlashSizB:<0,.0f} Bytes)\n"

                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Flash Prog Size'  :20s}: {progsize:0.3f} MB (Max: {progmax:0.3f} MB)\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Flash Prog Free'  :20s}: {progfree:0.3f} MB ({pcprogfree:0.1%})\n"

                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Flash Ufs Type'   :20s}: {fstype}\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Flash Ufs Size'   :20s}: {ufssize:0.3f} MB\n"
                WiFiInfo  += f"#{str(i):1s} {''    :26s} {'Flash Ufs Free'   :20s}: {ufsfree:0.3f} MB ({prcfree:0.1%})\n"

                if  DevCat == "Tasmota" and DevType == "Geiger":                    # only for 'Tasmota Geiger Counter'
                    WiFiInfo  += f"#{str(i):1s} {'' :26s} {'Current History' :20s}: {HistSize:<0,.0f} Bytes\n"

                WiFiInfo  += "\n"

        ### reset the timeout set for extended
        g.WiFiServerTimeout = oldWiFiServerTimeout

    return WiFiInfo


# ping
def pingWiFiServer():
    """Ping the WiFiServer"""
    # NOTE: Remember that a host may choose to not respond to a ping (ICMP)
    #       request even if the host name is valid and the host exists!

    setBusyCursor()

    fprint(header("Pinging WiFiServer"))
    QtUpdate()

    for i in range(len(g.WiFiServerList)):
        if g.WiFiServerList[i]["DevConnect"]:                                     # ping connected devices only
            IP = g.WiFiServerList[i]["DevIP"]
            pr = f"Ping Result: IP:{IP}"

            presult, ptime = ping(IP)
            if presult:
                fprint ("<green>" + pr, "Success in ", ptime)
                bip()
            else:
                efprint(pr, "Failure - ", ptime)

    setNormalCursor()

#his
###
### History download #####################################################################################
###
### Schätzungen Speicherung Daten
# ESP32 Flash max: 16 MB = 2^24 Byte.
# Speicherung CPS mit 2 Byte pro CPS, plus 16 Byte jede Stunde:
#   Byte:      2^24 / (2 * 3600 + 16) => 2325 h => 96.9 Tage => 3.2 Monate
# Speicherung CPS mit 1 Byte pro CPS, plus 16 Byte jede Stunde:
#   Byte:      2^24 / (1 * 3600 + 16) => 4640 h => 193 Tage => 6.4 Monate
# Speicherung CPS mit 13 Bit pro CPS, plus 16 * 8 Bit = 128 Bit jede Stunde:
#   Bit:       2^24 * 8 = 134 MBit / (13 * 3600 +128 ) => 2860.1 h => 119.2 Tage => 4.0 Monate
# Es gibt auch 32 MByte!!!
# --> Verdopplung --> bis 1 Jahr
#
# 32M
# Speicherung CPM mit 3 Byte pro CPM, plus 16 Byte jede Stunde:
#   Byte:32MB: 2^25 / (3 * 60 + 16) => 171196 h => 7133 Tage => 20 Jahre
#
# Shit, vergessen, den Prog Space abzurchnen :-((( #######################################################
#  4 MB: Flash für FS:  0.320 MB
#  8 MB: Flash für FS:  4.416 MB
# 16 MB: Flash für FS: 12.608 MB
#
# Rechnung für CPS: 2 Bytes pro CPS; Speicherung von 13 bit statt 16 Bit: +23%
#  4 MB:  0.320 E6  / (2 * 86400) =  1.8 Tage
#  8 MB:  4.416 E6  / (2 * 86400) = 25.5 Tage => >3 Wochen; bei 13 bit: ~4.5 Wochen
# 16 MB: 12.608 E6  / (2 * 86400) = 73.0 Tage => >2 Monate; bei 13 bit: ~3   Monate
#
# Rechnung für CPM: 3 Bytes pro CPM;
# 16 MB: 12.608 E6  / (3 * 1440)  = 2916 Tage => 97 Monate => 8 Jahre
#
# Mischung: 1 Jahr CPM, Rest für CPS:
# ( 3 Byte/min * 1440 min/d * 365 d/y ) = 1 576 800 Byte/y  (2^21 = 2 097 152)
# 12 MB - 2 MB = 10 MB bleibt für CPS
# ( 2 Byte/sec * 86400 sec/d * 30 d/monat ) =  5 184 000 Byte/Monat  --> 2 Monate möglich

### Extended Info:
#N Activated Devices (URL):
###  8 MB Flash system
#0 http://10.0.0.104:80       Tasmota Version     : 15.1.0(release-tasmota32)
#0                            ESP32 Hardware      : ESP32-D0WD-V3 v3.0
#0                            ESP32 Frequency     : 160 MHz
#0                            ESP32 Flash Size    : 8.000 MB (8,388,608 Bytes)
#0                            Flash Prog Size     : 2.082 MB (Max: 2.879 MB)
#0                            Flash Prog Free     : 0.797 MB (27.7%)
#0                            Flash Ufs Type      : LittleFS
#0                            Flash Ufs Size      : 4.416 MB
#0                            Flash Ufs Free      : 2.192 MB (49.6%)
#0                            Current History Size: 2,243,538 Bytes

###  4 MB Flash system
#0 http://10.0.0.102:80       Tasmota Version     : 15.1.0(release-tasmota32)
#0                            ESP32 Hardware      : ESP32-D0WD-V3 v3.0
#0                            ESP32 Frequency     : 160 MHz
#0                            ESP32 Flash Size    : 4.000 MB (4,194,304 Bytes)      !!! different
#0                            Flash Prog Size     : 2.082 MB (Max: 2.879 MB)
#0                            Flash Prog Free     : 0.797 MB (27.7%)
#0                            Flash Ufs Type      : LittleFS
#0                            Flash Ufs Size      : 0.320 MB                        !!! different
#0                            Flash Ufs Free      : 0.272 MB (85.0%)                !!! different
#0                            Current History Size: 25,367 Bytes

###  16 MB Flash system
#0 http://10.0.0.103:80       Tasmota Version     : 15.1.0(release-tasmota32)
#0                            ESP32 Hardware      : ESP32-D0WD-V3 v3.0
#0                            ESP32 Frequency     : 160 MHz
#0                            ESP32 Flash Size    : 16.000 MB (16,777,216 Bytes)    !!! different
#0                            Flash Prog Size     : 2.082 MB (Max: 2.879 MB)
#0                            Flash Prog Free     : 0.797 MB (27.7%)
#0                            Flash Ufs Type      : LittleFS
#0                            Flash Ufs Free      : 12.548 MB (99.5%)               !!! different
#0                            Current History Size: 36,893 Bytes

### Preise:
# https://de.aliexpress.com/item/1005005429891414.html?spm=a2g0o.productlist.main.9.6344H3doH3doqo&algo_pvid=8d3e577e-580a-46c8-b483-d451c6715ea0&algo_exp_id=8d3e577e-580a-46c8-b483-d451c6715ea0-8&pdp_ext_f=%7B%22order%22%3A%2218%22%2C%22eval%22%3A%221%22%2C%22fromPage%22%3A%22search%22%7D&pdp_npi=6%40dis%21EUR%212.39%211.79%21%21%212.74%212.05%21%40211b6a7a17655364832871417eefce%2112000033509756662%21sea%21DE%212579164188%21X%211%210%21n_tag%3A-29919%3Bd%3A4f864d32%3Bm03_new_user%3A-29895&curPageLogUid=ALmBfEofNjdE&utparam-url=scene%3Asearch%7Cquery_from%3A%7Cx_object_id%3A1005005429891414%7C_p_origin_prod%3A&gatewayAdapt=glo2deu
# ESP32-WROOM-32U 4 MB 8 MB 16 MB,  US $3.08, US $3.32, US $3.61, Versand US $3.77

def loadHistoryWiFiServer(sourceHist):
    """
    Download History from device (ONLY for Tasmota Geiger!) and create database
    return: error, message
    """
    ### aka: load the data file from device's flash

    setNormalCursor()   # quiet cursor;is set busy in ggeiger.py

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname, f" - sourceHist: '{sourceHist}'")
    setIndent(1)

    ### which WiFiServer?
    d = QInputDialog()
    d.setWindowIcon(g.iconGeigerLog)
    label = "Select WiFiServer to load History from"
    items = []
    for i, wsl in enumerate(g.WiFiServerList):
        items.append(f"#{i:<3d}: {wsl["DevIP"]}  {wsl["DevName"]}")
    selItem, ok = d.getItem(None, "Load History from WiFiServer", label, items, 0, editable=False)
    # iydprint(defname, f"selItem: {selItem}  ok: {ok}")
    if ok:
        msg = f"Selected WiFiServer: {selItem}"
        dprint(defname, msg)
        fprint(msg)
        QtUpdate()
    else:
        fprint("Loading History was canceled")
        setIndent(0)
        return 0, ""

    sndxl    = selItem.find("#")
    sndxr    = selItem.find(":")
    wslIndex = int(selItem[sndxl + 1 : sndxr])
    # iydprint(defname, f"wslIndex: {wslIndex}  ok: {ok}")

    DevCat  = g.WiFiServerList[wslIndex]["DevCat"]
    DevType = g.WiFiServerList[wslIndex]["DevType"]
    DevID   = g.WiFiServerList[wslIndex]["DevID"]
    DevUrl  = geturl(wslIndex)

    ### works only for  Tasmota Geiger devices
    if not (DevCat == "Tasmota" and DevType == "Geiger"):
        msg = "A download can be made only from 'Tasmota Geiger' devices!"
        rdprint(defname, msg)
        fprint(msg, error=True, color="<red>")
        setIndent(0)
        return 0, ""

    ### run download
    dstart  = time.time()

    setBusyCursor()

    ### how much Timeout is really needed?
    oldTimeOut = g.WiFiServerTimeout
    g.WiFiServerTimeout = 1.0
    response, rmsg, rdur = getTasmotaResponse(DevUrl, "/ufsd?download=/hist.dat")
    g.WiFiServerTimeout = oldTimeOut

    dur     = (time.time() - dstart) # in sec
    size    = len(response)
    msg     = f"Downloaded {size:,d} Bytes in {dur:0.1f} sec  ({size/dur/1e3:0.1f} kBytes/sec)"
    cdprint(defname, msg)
    fprint(msg)
    QtUpdate()

    ### got data?
    if response == "":
        ### Failure
        msg = f"NO DATA!  {DevCat} {DevType}:  response: \n{response[0:150]}   \nrmsg:{rmsg}"
        iydprint(defname, msg)
        setIndent(0)
        return 0, msg

    ### yes, got data! Now extract DB records  ########################################################################
    historyDB = extractWFSRecords(response)

    ### make DB
    updateWFSHistDB(historyDB, response, DevCat, DevType, DevID)

    setNormalCursor()

    setIndent(0)
    return 0, ""


def extractWFSRecords(response):
    """Get the data from the Hist downlaod"""

    start = time.time()
    defname = gd(sys._getframe().f_code.co_name)

    # get Hist as list
    Hist = response.split("\n")
    icdprint(defname, f"Total number of downloaded lines: {len(Hist)}")

    # save data to database
    historyDB = []
    ts, cps, cpm, cdur = 0, 0, 0, 0
    for i, HistLine in enumerate(Hist):
        # HistRecord: #3       ['nil', '64', '3E1']       dt: 2025-12-18 11:10:35  cpm: nan  cps: 100
        # HistRecord: #4       ['nil', '60', '3E8']       dt: 2025-12-18 11:10:36  cpm: nan  cps: 96
        # ...
        # HistRecord: #4204    ['162E', '5F', '3E8']      dt: 2025-12-18 12:20:54  cpm: 5678  cps: 95
        # HistRecord: #4205    ['163C', '66', '3E8']      dt: 2025-12-18 12:20:55  cpm: 5692  cps: 102

        try:
            HistRecord = HistLine.split(",")
            if len(HistRecord) == 1:
                Tts = HistRecord[0]                                   # Tasmota timestamp
                if Tts  != "nil": ts = int(Tts, 16) - 1               # -1 to allow +1 in cpm,cpc extractrs
                else:             ts = 0                              # to allow removal later
                continue

            elif len(HistRecord) == 2:
                ts += 1                                               # increase ts by 1 sec
                cpm, cps = HistRecord
                if cpm != "nil": cpm = int(cpm, 16)
                else:            cpm = g.NAN

                if cps != "nil": cps = int(cps, 16)
                else:            cps = g.NAN

                if cpm > g.WiFiServerCPMlimit:
                    rdprint(defname, f"Skipping:   #{i:<6d}  {str(HistRecord):25s}  because CPM > {g.WiFiServerCPMlimit}")
                    continue

                if cps > g.WiFiServerCPSlimit:
                    rdprint(defname, f"Skipping:   #{i:<6d}  {str(HistRecord):25s}  because CPS > {g.WiFiServerCPSlimit}")
                    continue

            elif len(HistRecord) == 3:
                ts += 1                                               # increase ts by 1 sec
                cpm, cps, cdur = HistRecord
                if cpm != "nil":  cpm = int(cpm, 16)
                else:             cpm = g.NAN

                if cps != "nil":  cps = int(cps, 16)
                else:             cps = g.NAN

                if cdur != "nil": cdur = int(cdur, 16)
                else:             cdur = g.NAN

                if cpm > g.WiFiServerCPMlimit:
                    rdprint(defname, f"Skipping:   #{i:<6d}  {str(HistRecord):25s}  because CPM > {g.WiFiServerCPMlimit}")
                    continue

                if cps > g.WiFiServerCPSlimit:
                    rdprint(defname, f"Skipping:   #{i:<6d}  {str(HistRecord):25s}  because CPS > {g.WiFiServerCPSlimit}")
                    continue

            if ts > 1e8:                                                # 1e8: Saturday March 3 1973 09:46:40 GMT
                dt = num2datestr(ts)
            else:
                rdprint(defname, f"Skipping:   #{i:<6d}  {str(HistRecord):25s}  because of 1970s Timestamp: {ts}")
                continue

        except Exception as e:
            exceptPrint(e, defname + f"get dt,cpm,cps from {HistRecord}")
            continue

        ### create DB record
        historyDB.append(
            [i,
             dt,               # DateTime str
             cpm,              # CPM:  counts per min
             cps,              # CPS:  counts per sec
             None,
             None,
             None,
             None,
             None,
             None,
             None,
             None,
             None,
             cdur,              # Xtra: deltaTime between calls
            ]
        )

        ### limited printing in for loop
        if i < 5 or i > len(Hist) - 6: iydprint(defname, f"HistRecord: #{i:<6d}  {str(HistRecord):25s}  dt: {dt}  cpm: {cpm:0.0f}  cps: {cps:0.0f}")
        elif i == 6:                   print("...")

    ### For loop on Hist has ended #############################

    lenhist  = len(historyDB)                   # no of records
    duration = time.time() - start              # dur in sec
    recRate  = lenhist   / duration             # records / sec
    msg      = f"Extracting {lenhist:,d} records in {duration:0.3f} s  ({recRate:0,.1f} rec/s)"
    dprint(defname, msg)
    fprint(msg)

    return historyDB


def updateWFSHistDB(historyDB, response, DevCat, DevType, DevID):
    """Update the Hist DB with Hist Data"""

    start = time.time()
    defname = gd(sys._getframe().f_code.co_name)

    ### updating database - SQL Data
    gsup_sql.DB_insertData(g.hisConn, historyDB)

    ### updating database - SQL Device
    gsup_sql.DB_insertDevice(g.hisConn, stime(), f"{DevCat} {DevType} {DevID}")

    ### updating database - SQL Comments
    gsup_sql.DB_insertComments(g.hisConn, [
                                            ["HEADER",  None, "File created by reading history from device"],
                                            ["ORIGIN",  None, "Download from device"],
                                            ["DEVICE",  None, f"{DevCat} {DevType} {DevID}"],
                                            ["COMMENT", None, "Values: CPM, CPS"],
                                          ])

    ### updating database - SQL Bin (saving text file as blob)
    gsup_sql.DB_insertBin (g.hisConn, response)

    lenhist  = len(historyDB)                   # no of records
    duration = time.time() - start              # dur in sec
    recRate  = lenhist   / duration             # records / sec
    msg      = f"Created DB of {lenhist:,d} records in {duration:0.3f} s  ({recRate:0,.1f} rec/s)"
    dprint(defname, msg)
    fprint(msg)


def showHistDetails():
    """Print filename and filesize in Bytes"""

    defname = gd(sys._getframe().f_code.co_name)

    msg = "Show History Details"
    QueuefPrint(header(msg))

    if g.hisConn is None:
        msg = f"A History database is not loaded"
        QueuefPrint(msg, error=True, color="<red>")
        return

    response = gsup_sql.DB_readBinblob(g.hisConn)
    filename = os.path.join(getPathToDataDir(), g.hisDBPath)
    if response is None: return

    bytecount = len(response)
    msg = f"Filename: {filename}"
    fprint(msg)
    dprint(defname, msg)
    msg = f"Total Byte Count: {bytecount:<8,d} Bytes"
    fprint(msg)
    dprint(defname, msg)


def saveHistoryData():
    """Save the History data as they are rfead from the db blob into a CSV file"""

    defname = gd(sys._getframe().f_code.co_name)

    msg = "Save History Data to CSV"
    QueuefPrint(header(msg))

    if g.hisConn is None:
        msg = f"A History database is not loaded"
        QueuefPrint(msg, error=True, color="<red>")
        return

    response = gsup_sql.DB_readBinblob(g.hisConn)

    try:
        filename = os.path.join(getPathToDataDir(), g.hisDBPath + ".csv")
        with open(filename, "wt", encoding="UTF-8", errors='replace', buffering = 1) as f:
            f.write(response)
        msg = f"CSV file: {filename}"
        dprint(defname, msg)
        QueuefPrint(msg)
    except Exception as e:
        exceptPrint(e, "writing local CSV History file")


def showHistData(Flag=""):
    """Print data as text"""

    defname = gd(sys._getframe().f_code.co_name)

    msg = "Show History Data"
    if Flag > "" : msg += " Excerpt"
    QueuefPrint(header(msg))

    if g.hisConn is None:
        msg = f"A History database is not loaded"
        QueuefPrint(msg, error=True, color="<red>")
        return

    QueuefPrint(f"Database: {g.hisDBPath}")

    response = gsup_sql.DB_readBinblob(g.hisConn)

    try:
        plimit      = 10
        lresponse   = response.split("\n")
        size        = len(lresponse)
        if Flag == "" :
            # fprint(response)
            for i, rec in enumerate(lresponse):
                QueuefPrint(f"#{i:<6d} {rec}")

        else:
            for i, rec in enumerate(lresponse):
                if   i < 10 or i > size - (plimit + 1 ): QueuefPrint(f"#{i:<6d} {rec}")
                elif i == 11:                            QueuefPrint("...")

    except Exception as e:
        exceptPrint(e, defname)

### end History stuff ###################################################################

# def resetWiFiDevices(select=""):
def resetWiFiDevices(select=None):
    """Reset all WiFiServer Devices - but only when connected - and not the WiFiServer"""

    rstart = time.time()

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    selector = "Selected" if select == "select" else "All"
    fprint(header(f"Resetting {selector} WiFiServer Devices (if connected)"))
    QtUpdate()

    # if select == "select":
    if select is not None:
        d = QInputDialog()
        d.setWindowIcon(g.iconGeigerLog)
        label = "Select WiFiServer to Reset"
        items = []
        for i, wsl in enumerate(g.WiFiServerList):
            items.append(f"#{i:<3d}: {wsl["DevIP"]}  {wsl["DevName"]}")
        selItem, ok = d.getItem(None, "Reset Selected WiFiServer Device", label, items, 0, editable=False)
        # iydprint(defname, f"selItem: {selItem}  ok: {ok}")
        if ok:
            sndxl     = selItem.find("#")
            sndxr     = selItem.find(":")
            selIndex = int(selItem[sndxl + 1 : sndxr])
            # iydprint(defname, f"selIndex: {selIndex}  ok: {ok}")
        else:
            fprint("Resetting was canceled")
            setIndent(0)
            return

    setBusyCursor()

    for wslIndex, wsl in enumerate(g.WiFiServerList):
        if select is not None:                            # on not None do only a single server
            if wslIndex != selIndex:  continue

        if not g.WiFiServerList[wslIndex]["DevConnect"]:  continue          # must be connected for resetting!

        DevCat  = g.WiFiServerList[wslIndex]["DevCat"]
        DevType = g.WiFiServerList[wslIndex]["DevType"]
        DevUrl     = geturl(wslIndex)
        msg     = f"Resetting WiFiServer #{wslIndex}  {DevCat}  {DevType}  @ url: {DevUrl}"
        fprint(msg)

        if DevCat == "Tasmota" and DevType == "Geiger":
            ### need this:? :  DevCat == "Tasmota": command = "/cm?cmnd=SetOption57%20Off" # switch "On" the network scans
            ### resetting Tasmota Geiger by delketing history
            msg = deleteBerryHist(DevCat, DevType, DevUrl)
            dprint(defname, f"msg: {msg}")
        else:
            if   DevCat == "GLDS":    command = "/reset"                     # maybe a dummy reset
            elif DevCat == "Tasmota": command = ""                           # maybe a dummy reset
            else:                     command = "/reset"                     # all new devices should have it

            if command > "":
                response, rmsg, rdur = getTasmotaResponse(DevUrl, command)
                if response == "":  msg = "FAILURE"
                else:               msg = "Success"
            else:
                msg = "Device has no Reset Option"

        fprint(msg)

    rdur = 1000 *(time.time() - rstart)
    dprint(defname, f"dur: {rdur:0.1f} ms")

    setNormalCursor()

    setIndent(0)


def deleteBerryHist(DevCat, DevType, url):
    """Send History Delete Command to Tasmota Geiger"""

    BHstart = time.time()
    defname = gd(sys._getframe().f_code.co_name)

    if not(DevCat == "Tasmota" and DevType == "Geiger"):  return "No Action"

    cmd = \
"""
var f = open('hist.dat', 'r')
var Hsize = f.size()
f.close()

# empty the file
var f = open('hist.dat', 'w')
f.close()

return Hsize
"""

    urlcmd = urllib.parse.quote_plus(cmd)
    # iydprint(defname, f"urlcmd: '{urlcmd}'")
    response, rmsg, rdur = getTasmotaResponse(url, f"/cm?cmnd=Br%20{urlcmd}") # get like: response: '{"Br":"2065381"}, or:' '{"Br":"nil"}'
    if response == "":
        msg = "FAILURE"
    else:
        msg = "Success"
        try:
            jresponse   = json.loads(response)
            # iydprint(defname, "\n", json.dumps(jresponse, indent=3))          # pretty print
            HistSize   = int(jresponse["Br"])                                   # class 'str'; like: '{"Br":"8310"}'
        except Exception as e:
            exceptPrint(e, f"{DevCat} {DevType} bad response: '{response}")
            response = ""
            HistSize = g.NAN

        BHdur = 1e3 * (time.time() - BHstart)
        msg  += f" - Deleted History of {HistSize} Bytes in {BHdur:0.0f} ms"

    return msg


def getBerryHistSize(DevCat, DevType, url):
    """Get History Size from Tasmota"""

    defname = gd(sys._getframe().f_code.co_name)

    if not (DevCat == "Tasmota" and DevType == "Geiger"):   # only for Tasmota Geiger Counter
        HistSize = g.NAN
    else:
        cmd = \
"""
var f = open('hist.dat', 'r')
var Hsize = f.size()
f.close()
return Hsize
"""

        urlcmd = urllib.parse.quote_plus(cmd)
        response, rmsg, rdur = getTasmotaResponse(url, f"/cm?cmnd=Br%20{urlcmd}")
        if response == "":
            HistSize = g.NAN
        else:
            try:
                jresponse = json.loads(response)                               # class 'str'; like: '{"Br":"8310"}'
                # iydprint(defname, "\n", json.dumps(jresponse, indent=3))     # pretty print
                respBR    = jresponse["Br"]                                    # missing file: '{"Br":"[io_error] cannot open file 'hist.dat'"}
                try:    HistSize  = int(respBR)
                except: HistSize  = g.NAN
            except Exception as e:
                exceptPrint(e, f"{DevCat} {DevType} bad response for History size: '{response}")
                HistSize = g.NAN

    return HistSize


def getBerryFlashSize(DevCat, url):
    """get size of Tasmota Flash"""

    defname = gd(sys._getframe().f_code.co_name)

    if not (DevCat == "Tasmota"):
        FlashSize = g.NAN
        msg = f"Can get Flash size only for {DevCat} devices !"
        rdprint(defname, msg)
        QueuefPrint(msg, error=True, color="<red>")
    else:
        cmd = \
"""
import flash
var Fsize = flash.size()
return Fsize
"""

        urlcmd = urllib.parse.quote_plus(cmd)
        response, rmsg, rdur = getTasmotaResponse(url, f"/cm?cmnd=Br%20{urlcmd}")
        if response == "":
            FlashSize = g.NAN
        else:
            try:
                jresponse   = json.loads(response)
                # iydprint(defname, "\n", json.dumps(jresponse, indent=3))       # pretty print
                FlashSize   = int(jresponse["Br"])                               # class 'str'; like: '{"Br":"8310"}'
            except Exception as e:
                exceptPrint(e, f"getting flash size bad response: '{response}")
                FlashSize = g.NAN

    return FlashSize


def setBerryCounterConfig(url):
    """Configure ESP32 with Counter class"""

    defname = gd(sys._getframe().f_code.co_name)

    cmdcode = saveBerryGeigerCode()

    ### print Counter code to log with line numbers
    for i, cl in enumerate(cmdcode.split("\n")):
        icdprint(defname, f"{i + 1:3d}   {cl}")

    ### orig length
    dprint(defname, f"orig              - len(cmdcode): {len(cmdcode)}")

    ### strip all line

    newCmdCode = ""
    for i, ccl in enumerate(cmdcode.split("\n")):
        newCmdCode += ccl.strip().replace("  ", " ").replace(" : ", ":").replace(" = ", "=").replace(" > ", ">") + "\n"
    print(newCmdCode)
    dprint(defname, f"strip code         - len(newCmdCode): {len(newCmdCode)}")



    # ### replace multi space with single space
    # cmdrepl = newCmdCode.strip().replace("  ", " ").replace("  ", " ").replace("  ", " ")
    # dprint(defname, f"clean space       - len(cmdrepl): {len(cmdrepl)}")

    # ### replace " = " with "=",  " += " with "+=",
    # cmdrepl = cmdrepl.replace(" = ", "=").replace(" += ", "+=")
    # dprint(defname, f"clear spaces in fomula:           {len(cmdrepl)}")

    # iydprint(defname, f"cmdrepl: {cmdrepl}")

    # ### replace LF= " with " "
    # cmdrepl = cmdrepl.replace("\n", " ")
    # dprint(defname, f"replace LF with ' ':           {len(cmdrepl)}")

    # iydprint(defname, f"cmdrepl: {cmdrepl}")

    ### prepare code for url
    cmdrepl = urllib.parse.quote_plus(newCmdCode)
    dprint(defname, f"parse.quote_plus  - len(urlcmd):  {len(cmdrepl)}")

    iydprint(defname, f"cmdrepl: {cmdrepl}")

    # urlcmd = urlcmd.replace("%0A", "+")
    # dprint(defname, f"change %0A to '+' - len(urlcmd):  {len(urlcmd)}")
    # imdprint(defname, f"command: '{urlcmd}'")

    ### send geiger code to Tasmota
### testing use either line
    response, rmsg, rdur = sendCommand(url, f"Br+{cmdrepl}")
    # response, rmsg, rdur = "inactiv", "inactiv", g.NAN
### end testing

    return response, rmsg, rdur


def sendCommand(url, command):
    """prep command for web and send"""

    defname = gd(sys._getframe().f_code.co_name)

    urlcmd  = urllib.parse.quote_plus(command)                      # prep for HTTP transmission
    response, rmsg, rdur = getTasmotaResponse(url, f"/cm?cmnd={urlcmd}")

    return response, rmsg, rdur

#gg
def saveBerryGeigerCode(writefile=False):
    """Create Berry Code for Tasmota Geiger Counter"""

    defname = gd(sys._getframe().f_code.co_name)

    cmdcode = \
"""
class geiger
var cpm,cps,name,cpslist,tmax,dt,oldmts, oldcount, wlist, skip1
def init()
    self.name = classname(self)
    self.close()
    self.wlist = []
    self.tmax = 60
    self.cps = 0
    self.cpm = 0
    self.dt  = "---"
    self.oldmts = tasmota.millis()
    import math
    self.cpslist = []
    for i : 1..60
        self.cpslist.push(math.nan)
    end
    self.skip1 = true
    gpio.counter_set(0,0)
    tasmota.add_driver(global.geiger_instance := self)
    import json
    tasmota.add_cmd(self.name, /cmd,idx,payload ->
    tasmota.resp_cmnd(json.dump({self.name: {"CPS" : self.cps, "CPM" : self.cpm}})))
end
def close()
    tasmota.remove_driver(global.geiger_instance)
    tasmota.remove_cmd(self.name)
end
def web_sensor()
    import string
    var msg = string.format("{s}DateTime{m}%s{e}""{s}CPM{m}%i{e}""{s}CPS{m}%i{e}",self.dt,self.cpm,self.cps)
    tasmota.web_send(msg)
end
def every_second()
    var mts  = tasmota.millis()
    var dmts = mts - self.oldmts
    self.oldmts = mts

    var cr = gpio.counter_read(0)
    gpio.counter_set(0,0)

    if self.skip1
        self.skip1 = False
        print(f"Skipping first record - deltat: {dmts}ms - dumping counter_read: {cr}")
        return
    end

    self.cps = cr
    self.cpslist.insert(0,cr)
    if size(self.cpslist) > self.tmax
        self.cpslist.pop()
    end

    self.cpm = 0
    for cs : self.cpslist
        self.cpm += cs
    end

    print(f"self.cpm: {self.cpm}  self.cps: {self.cps}")
    print(f"self.cpslist: {self.cpslist}")

    import string
    var ts  = tasmota.rtc()['local']
    self.dt = string.replace(f"{tasmota.time_str(ts)}","T"," ")

    var b = bytes(-2)
    b.set(0, 6666, 2)
    print(b)
    print(b[0], b[1])
    print(b.tostring())

    var hexrec = f"{string.hex(ts)},{string.hex(self.cpm)},{string.hex(self.cps)}{string.char(10)}"
    var decrec = f"CNT: #{size(self.wlist)}  cpm: {self.cpm} cps: {self.cps} deltat: {dmts}ms"

    self.wlist.push(hexrec)
    print(decrec)

    if size(self.wlist) >= 60
        var fd  = open('hist.dat','a')
        for wls : self.wlist
            fd.write(wls)
        end
        fd.close()
        self.wlist = []
        self.skip1 = true
        print("wrote file -----------------------------")
    end
end
end
gg = geiger()
return "Ok"
"""

######################################################

######################################################

    ### remove white space at beginning and end
    cmdcode = cmdcode.strip()

    if 0 and writefile:
        ### write code as 'geiger.be' to local file in GeigerLog subfolder 'berry'
        try:
            filename = os.path.join(getPathToProgDir(), "berry", "geiger.be")
            with open(filename, "wt") as fc:
                fc.write(cmdcode)
            msg = f"Tasmota Geiger Code - see file: '{filename}'"
            dprint(defname, msg)
            fprint(msg)
        except Exception as e:
            exceptPrint(e, "writing 'geiger.be' file")

    return cmdcode


#su
# not in use see ggeiger near line 802
def startupWiFiConfig(select=None):
    """Apply the startup configuration for all devices"""

    # return # now that we TAPP, we don't need this startup!

    rstart = time.time()

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    fprint(header("Setting Startup Configurations"))
    if g.logging:
        efprint(f"Cannot apply startup config while logging. Stop logging first!")
        return

    msg = QMessageBox()
    msg.setWindowIcon(g.iconGeigerLog)
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("WARNING:  Applying Config may change System!")
    msg.setText("If you continue all devices will be first disconnected, and then configured! \
                To finish you'll have to reconnect all devices.\
                \n\nSome devices may reboot, and it may take some seconds before they recover; \
                please, be patient.")
    msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
    msg.setDefaultButton  (QMessageBox.StandardButton.Cancel)
    msg.setEscapeButton   (QMessageBox.StandardButton.Cancel)
    retval = msg.exec()

    if retval != QMessageBox.StandardButton.Ok:
        fprint("Setting Startup Config was cancelled")
        return


    for wslIndex, wfs in enumerate(g.WiFiServerList):

        DevCat  = wfs["DevCat"]
        DevType = wfs["DevType"]
        DevUrl  = geturl(wslIndex)
        msg     = f"Setting Template to WiFiServer #{wslIndex}  {DevCat} {DevType}  @ url: {DevUrl}"
        fprint(msg)

        if DevCat == "Tasmota" and DevType == "Geiger":
            ### setting template --> results in Reboot
            # original = 'Template {"NAME":"GeigerLog\'s","GPIO":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,  1,  1,1,0,1,1,1,0,0,0,0,1,1,1,1,1,0,0,1],"FLAG":0,"BASE":1}'
            # template = 'Template {"NAME":"GeigerLog\'s","GPIO":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,  1,352,1,0,1,1,1,0,0,0,0,1,1,1,1,1,0,0,1],"FLAG":0,"BASE":1}'
            template   = 'Template {"NAME":"GeigerLog\'s","GPIO":[1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,353,352,1,0,1,1,1,0,0,0,0,1,1,1,1,1,0,0,1],"FLAG":0,"BASE":1}'
            response, rmsg, rdur = sendCommand(DevUrl, template)

            ### activating template after setting it
            # 12:27:39.027 CMD: modules
            # 12:27:39.029 RSL: RESULT = {"Modules":{"0":"GeigerLog","1":"ESP32-DevKit"}}
            response, rmsg, rdur = sendCommand(DevUrl, "Modules")
            try:
                jresponse   = json.loads(response)
                # iydprint(defname, "\n", json.dumps(jresponse, indent=3))          # pretty print
                modules     = jresponse["Modules"]
                # iydprint(defname, f"modules = {modules}")
            except Exception as e:
                exceptPrint(e, f"{DevCat} {DevType} bad response: '{response}")
                response = ""
                setNormalCursor()
                setIndent(0)
                return
            else:
                modulIndex = None
                for i in range(len(modules)):
                    if "GeigerLog" in modules[f"{i}"] :
                        modulIndex = i
                        break

                if modulIndex is None:
                    msg = f"   Module 'GeigerLog' is missing. Did you run 'Set Startup Configuration?'"
                    efprint(msg)
                    edprint(defname, msg)
                    setNormalCursor()
                    setIndent(0)
                    return

                response, rmsg, rdur = sendCommand(DevUrl, f"Module {modulIndex}")
                iydprint(defname, f"Activating module response: {response}")

                try:
                    jresponse   = json.loads(response)
                    iydprint(defname, "\n", json.dumps(jresponse, indent=3))          # pretty print

                except Exception as e:
                    exceptPrint(e, f"{DevCat} {DevType} bad response '{response}' on cmd: 'Module {modulIndex}' ")


                if response > "": fprint (f"   Module 'GeigerLog' is activated")
                else:             efprint(f"   FAILURE activating module 'GeigerLog'")

        else:
            msg = f"No Startup Action for WiFiServer #{wslIndex}  {DevCat}  {DevType}  @ url: {DevUrl}"
            dprint(defname, f"msg: {msg}")
            fprint(msg)

    rdur = 1000 *(time.time() - rstart)
    dprint(defname, f"dur: {rdur:0.1f} ms")

    g.exgg.switchAllDeviceConnections("OFF")

    setNormalCursor()

    setIndent(0)

