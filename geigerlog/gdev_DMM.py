#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gdev_DMM.py      -  a utility which gets readings from a DMM (Digital Multi Meter).
                    Supported are: 'OWON OW18E' and 'Voltcraft VC850'
                    The latter only via Formula Interpreter
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

############################################################################################################
# ATTENTION:   This Bluetooth code works ONLY with an OWON OW18E DMM device with Bluetooth identifier 'BDM'.
#              Presently only the functions Volt, milliVolt, Frequency, and Duty Cycle are supported.
#
#              The Voltcraft VC850 code is called from the Formula Interpreter as:  DMMCALL("VC850", PORT).
#              PORT is the serial port, to which it is connected (like: '/dev/ttyUSB1', or 'COM3').
#              All DMM functions are supported.
#
# The Bluetooth code uses simplepyble, which "... works on Windows, Linux and MacOS".
# Install with:
#           pip install simplepyble
#
# Please take into consideration that when using this library on Linux, you
# will need to have the following dependencies installed:
#           sudo apt-get install libdbus-1-dev
#
# https://simpleble.readthedocs.io/en/latest/simplepyble/usage.html
#
# OWON Meter Decoding:
#    see: https://github.com/sercona/Owon-Multimeters/blob/main/owon_multi_cli.c)
#
#
# MAC-Adresse (Media Access Control) ... Alle Bluetooth-Geräte müssen eine eindeutige MAC-Adresse enthalten.
# 2 x 3 Paare hex => 255^3 = 16 581 375 Varianten - einmal für Manufacturer, plus einmal für Gerät.
#
# Die ersten drei Paare (00-0C-29) sind als Organizationally Unique Identifier (OUI) bekannt. Sie
# identifizieren den Hersteller des Geräts. Die OUIs werden dabei von einer Organisation namens
# Institute of Electrical and Electronics Engineers (IEEE) zugewiesen, die für jeden Hersteller
# eine einmalige Kombination aus Buchstaben und Ziffern vergibt. Dadurch wird sichergestellt, dass
# jede MAC-Adresse eindeutig ist.
#
# Die letzten drei Paare (20-4A-E4) werden als Individual Identifiers (einmalige Identifizierer)
# bezeichnet. Sie werden vom Hersteller zugewiesen und sind für jedes Gerät einzigartig. Somit
# können zwei Geräte niemals die gleiche MAC-Adresse haben.
#
# Online search:
# https://www.dein-ip-check.de/tools/macfinder?oui=A6%3AC0%3A80%3AE3%3A80%3A78&page=1
#
# Bluetooth Adapter:
# local_device.allDevices(): list name: amd7        address: 40:9C:A7:05:76:54  (built-in to ACE computer,  ID:'hci0' --> Hardware Vendor 'CHINA DRAGON TECHNOLOGY LIMITED'
# local_device.allDevices(): list name: amd7 #2     address: 8C:88:2B:60:37:72  (Dongle ORICO)
# local_device.allDevices(): list name: amd7 #3     address: F4:4E:FC:D8:10:75  (Dongle BT 5.3)
# on computer AI370:
#    ID: hci1   MAC-Addr: DC:97:BA:3F:D9:5E

# Bluetooth Device - Other
# 38:F5:54:3D:AF:F2  'HISENSE ELECTRIC CO.,LTD, No. 218, Qianwangang Rd, Qingdao  Shandong  266555, CN'  (TV???):
# DC:23:4F:27:CC:0B  'TY' kein hersteller mit der OUI DC:23:4F             ??????????????????
# 66:96:A9:49:72:44  ???? kein hersteller mit der OUI 66:96:A9             ??????????????????
#
# Bluetooth Devices 'OWON OW18E':
# ADDRESS = "A6:C0:80:E3:85:9D"  ID:'BDM'   --> Hardware Vendor unknown!    # my first device OW18E#1 - Yellow
# ADDRESS = "A6:C0:80:E3:80:78"  ID:'BDM'   --> Hardware Vendor unknown!    # my secnd device OW18E#2 - Blue
#
# Output from code in BTsetupDMM() (line 346) for Device 'OWON OW18E':
#   for i, pair in enumerate(service_characteristic_pair):
#         dprint(defname, f"   #{i}  Finding service.uuid: {pair[0]},  characteristic.uuid: {pair[1]}")
#
# BTsetupDMM: #0  service.uuid: 00001801-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a05-0000-1000-8000-00805f9b34fb # Generic Attribute
# BTsetupDMM: #1  service.uuid: 0000180a-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a29-0000-1000-8000-00805f9b34fb # Device Information
# BTsetupDMM: #2  service.uuid: 0000180a-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a24-0000-1000-8000-00805f9b34fb # Device Information
# BTsetupDMM: #3  service.uuid: 0000180a-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a26-0000-1000-8000-00805f9b34fb # Device Information
# BTsetupDMM: #4  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff1-0000-1000-8000-00805f9b34fb # Unknown
# BTsetupDMM: #5  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff2-0000-1000-8000-00805f9b34fb # Unknown
# BTsetupDMM: #6  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff3-0000-1000-8000-00805f9b34fb # Unknown
# BTsetupDMM: #7  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff4-0000-1000-8000-00805f9b34fb # Output: like: 23 f0 04 00 5b 0f     # this is choice #7 !
# BTsetupDMM: #8  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff5-0000-1000-8000-00805f9b34fb # Unknown
# BTsetupDMM: #9  service.uuid: 00010203-0405-0607-0809-0a0b0c0d1911,  characteristic.uuid: 00010203-0405-0607-0809-0a0b0c0d2b12 # Proprietary
##############################################################################################################################


__author__              = "ullix"
__copyright__           = "Copyright 2016 - 2025"
__credits__             = [""]
__license__             = "GPL3"

from gsup_utils   import *            # all utilities


# Try importing the Bluetooth module
try:
    import simplepyble
    g.BTfoundsimplepyble = True
    g.versions["simplepyble"] = simplepyble.get_simpleble_version()
    # irdprint("gdev_dmm.py ", "DID find simplepyble")
except Exception as e:
    g.BTfoundsimplepyble = False
    exceptPrint(e, "Failure to import Bluetooth module 'simplepyble'; cannot run DMM")
    sys.exit(999)



#init
def initDMM():
    """Start the device"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    ### check if importing the Bluetooth module simplepyble has FAILED
    if not g.BTfoundsimplepyble:
        msg = "Cannot find required Bluetooth module 'simplepyble'!"
        setIndent(0)
        return msg
    else:
        msg = "DID find Bluetooth module 'simplepyble' !"
        # irdprint(defname, msg)


    ### turn Bluetooth Off, then On
    try:
        os.system("rfkill   block bluetooth")
        os.system("rfkill unblock bluetooth")
        time.sleep(1)
    except Exception as e:
          msg = "Failure turning Bluettoth Off +On via os.system call"
          exceptPrint(e, defname + msg)
          return msg

    ### is BT enabled on the computer?
    ### NOTE: with above os.system commands, BT should always be enabled
    try:
        msg = "A Bluetooth adapter is NOT enabled on this Computer!"
        if not simplepyble.Adapter.bluetooth_enabled():
            g.BTsetupMsg += msg + "\n"
            cdprint(msg)
            setIndent(0)
            return msg
    except Exception as e:
        exceptPrint(e, defname)
        setIndent(0)
        return msg

    ### set Device Name
    g.Devices["DMM"][g.DNAME] = "DMM"

    ### set configs
    if g.DMMDevice       == "auto":     g.DMMDevice     = "BDM"    # else: DMMDevice = Label1:A6:C0:80:E3:80:78, Label2:A6:C0:80:E3:85:9D, ...
    if g.DMMVariables    == "auto":     g.DMMVariables  = "Xtra"
    # mdprint(defname, f"g.DMMDevice: {g.DMMDevice}")

    ### set variables
    g.DMMVariables     = setLoggableVariables("DMM", g.DMMVariables)
    g.DMMVariablesList = (g.DMMVariables.replace(" ", "")).split(",", 11)

    ### set all active g.DMMValues to nan, as well as selected devices
    for vname in g.Devices["DMM"][g.VNAMES]:
        g.DMMValues[vname] = g.NAN
        g.BTDevices[vname] = {"dev" : None, "Label" : None, "Stuff" : None}                     # defines ONLY the devices in varlist!
        # irdprint(defname, f"g.BTDevices['{vname}']['Label']:  {g.BTDevices[vname]['Label']}")

    icdprint(defname, f"init g.DMMValues:  {g.DMMValues}")
    icdprint(defname, f"init g.BTDevices:  {g.BTDevices}")

    ### is there a BT adapter?
    g.BTsuccessAdapter = BTsetupAdapter()
    # irdprint(defname, f"g.BTsuccessAdapter: {g.BTsuccessAdapter}")
    if g.BTsuccessAdapter[0]:                                              # success or fail on finding a BT adapter
        # a BT adapter was found and was selected
        msg = f"Success: Bluetooth Adapter was found"
        gdprint(defname, msg)
        fprint(msg)
        fprint(" "*9 + g.BTsuccessAdapter[1])
        QtUpdate()

    else:
        # a BT adapter was NOT found
        msg = f"Failure: Bluetooth Adapter was NOT found"
        dprint(defname, msg)
        efprint(msg)
        QtUpdate()
        g.Devices["DMM"][g.CONN] = False
        msg = f"{g.BTsuccessAdapter[1]}"
        setIndent(0)
        return msg

    cdprint(defname, "Scanning for Bluetooth Devices")
    ### are there any BT devices?
    g.BTAdapter.scan_for(g.BTscanDur)                               # Scan for Bluetooth devices for 'g.BTscanDur' millisec
    g.BTperipherals = g.BTAdapter.scan_get_results()                # the scanning-code will print the peripherals via their callbacks
    # irdprint(defname, f"g.BTperipherals:  {g.BTperipherals}")

    cdprint(f"Count of Bluetooth devices:  {len(g.BTperipherals)}")
    if len(g.BTperipherals) == 0:
        msg = f"No Bluetooth Devices were found"
        setIndent(0)
        return msg
    else:
        msg = f"Success: Bluetooth Devices were found"
        fprint(msg)


    ### are any of the devices matching configuration?
    BTdevsuccess = BTsetupDMM()
    if BTdevsuccess[0]:
        # a matching BT device was found and is connected
        try:
            # irdprint(defname, f"All BT DMM devices: {g.BTDevices}")
            for vname in g.BTDevices:
                icdprint(defname, f"vname: {vname}")
                if g.BTDevices[vname]["dev"] is not None:
                    id    = g.BTDevices[vname]["dev"].identifier()
                    addr  = g.BTDevices[vname]["dev"].address()
                    label = g.BTDevices[vname]["Label"]
                    icdprint(defname, f"dev: {addr}   ID: {id}  Label: {label}")
                    msg   = f"Bluetooth Device:             ID: {id:8s}  Label: {label:6s}  MAC-Addr: [{addr}]\n"
                    fprint(msg)
        except Exception as e:
            exceptPrint(e, defname + f"on disconnection of Bluetooth devices for : {vname}")
            msg =          "Bluetooth Device:             unknown (Bluetooth Discovery Failure; Try repeating)\n"
            fprint(msg)

        g.Devices["DMM"][g.CONN] = True
        msg = ""
    else:
        # a BT device was found but it is NOT matching
        g.Devices["DMM"][g.CONN] = False
        msg = f"a Bluetooth Device matching configuration was NOT found"

    setIndent(0)
    return msg  # empty means no errmsg for return


def BTsetupAdapter():
    """Find the Bluetooth Adapters, and setup the Bluetooth Environment"""

    ############################################################################################
    def AddBTsetupMsg(msg):
        """Needed in the BT callbacks"""
        if msg is None: return
        # g.BTsetupMsg += msg + "\n"
        cdprint(msg)
    ############################################################################################

    defname = gd(sys._getframe().f_code.co_name)
    cdprint(defname)
    setIndent(1)

    g.BTsetupMsg     = ""

    ### search for BT adapters
    adapters     = simplepyble.Adapter.get_adapters()
    adapters_len = len(adapters)
    if adapters_len == 0:
        msg = f"A Bluetooth Adapter was NOT found!"
        setIndent(0)
        return False, msg

    ### at least 1 BT Adapter was found, now select only adapters with its ID starting with hci
    msg = f"Found {len(adapters)} Bluetooth Adapters"
    g.BTsetupMsg += msg + "\n"
    cdprint(defname, msg)
    hciIndex = []
    for i, adapter in enumerate(adapters):
        id   = None
        addr = "unknown"
        try:
            id   = adapter.identifier()
            if id.startswith("hci"):  hciIndex.append(i)
            addr = adapter.address()
        except Exception as e:
            exceptPrint(e, defname)

        msg = f"   #{i + 1}  ID: {id:5s}     MAC-Addr: {addr}"
        cdprint(msg)

        g.BTsetupMsg += msg + "\n"

    msg = f"   Bluetooth Adapter Search complete, finding {len(hciIndex)} hci adapters"
    cdprint(msg)
    g.BTsetupMsg += msg + "\n"

    ### select first hci* adapter
    g.BTAdapter  = adapters[hciIndex[0]]
    msg = f"Selected Adapter: ID: {g.BTAdapter.identifier():5s}  MAC-Addr: {g.BTAdapter.address()}"
    cdprint(msg)
    g.BTsetupMsg    += msg + "\n"

    g.BTAdapter.set_callback_on_scan_start(lambda:              AddBTsetupMsg(None))                                # no printout on start
    g.BTAdapter.set_callback_on_scan_stop (lambda:              AddBTsetupMsg("   Bluetooth Device Scan complete"))
    g.BTAdapter.set_callback_on_scan_found(lambda peripheral:   AddBTsetupMsg("   " + foundBTDevice(peripheral)))

    setIndent(0)

    return True, msg


def BTsetupDMM():
    """Setup the DMM for Notify"""

    defname = gd(sys._getframe().f_code.co_name)
    icdprint(defname)
    setIndent(1)

    BTmatches     = 0

    if g.DMMDevice == "BDM":
        # use only the first found 'BDM' device
        vname = g.DMMVariablesList[0]
        for g.BTperipheral in g.BTperipherals:
            if g.BTperipheral.identifier() == "BDM":
                BTmatches +=1
                g.BTDevices[vname] = {"dev" : g.BTperipheral, "Label" : "BDM"}
                irdprint(defname, f"DMMdevAddress: {g.BTperipheral.address()}   ID: {g.BTperipheral.identifier()}")
                irdprint(defname, g.BTDevices)
                break  # ignore any other following BDMs

    else:
        # find all BR devices matching configured MAC addresses
        DMMDevsCfg = g.DMMDevice.split(",", 11)
        ### cycle through all configured BT devices
        for i, DMMdevCfg in enumerate(DMMDevsCfg):
            if "|" in DMMdevCfg:   Label, DMMdev = DMMdevCfg.split("|", 1)
            else:                  Label, DMMdev = f"Label#{i}", DMMdevCfg
            # icdprint(defname, f"{Label}, {DMMdev}")
            vname = g.DMMVariablesList[i]

            ### found periphs matching configured ones?
            ### For each found BT device, compare with all configured BT devices
            for g.BTperipheral in g.BTperipherals:
                # irdprint(defname, f"Compare: Config devices: {DMMdev}  real Peripheral: {g.BTperipheral.address()}")
                if DMMdev == g.BTperipheral.address():
                    BTmatches +=1
                    icdprint(defname, f"Found match for '{DMMdev}' in real devices; configured label is: '{Label}'")
                    g.BTDevices[vname] = {"dev" : g.BTperipheral, "Label" : Label}

    if BTmatches == 0 :
        msg = "No BT DMM found"
        irdprint(defname, msg)
        setIndent(0)
        g.BTperipheral = None

        return False, "Configured BT Device(s) not found"

    else:
        msg = "Connecting found devices: "
        icdprint(defname, msg)

        for vname in g.DMMVariablesList:
            if g.BTDevices[vname]["dev"] is None: continue      # ignore non-existent devices

            msg = f"{vname} : Connecting to: {foundBTDevice(g.BTDevices[vname]["dev"])}"
            icdprint(defname, msg)

            try:
                g.BTDevices[vname]["dev"].connect()
            except Exception as e:
                msg = f"Failed connection to device: '{g.BTDevices[vname]["dev"]}'"
                exceptPrint(e, msg)
                g.BTDevices[vname]["dev"] = None

    # NOTIFY
    choice = 7
    icdprint(defname, f"Setting Notify on pair: #{choice}")
    g.DMMlasttime = time.time()   # needed ???????

    # service_uuid, characteristic_uuid = service_characteristic_pair[choice]
    for vname in g.DMMVariablesList:
        # icdprint(defname, f"vname: {vname}")

        if g.BTDevices[vname]["dev"] is None: continue      # ignore non-existent devices

        ### odd pairing
        service_characteristic_pair = []
        for service in g.BTDevices[vname]["dev"].services():
            for characteristic in service.characteristics():
                service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

        service_uuid, characteristic_uuid = service_characteristic_pair[choice]

        try:
            if   vname == "CPM"    : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPM(data))
            elif vname == "CPS"    : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPS(data))

            elif vname == "CPM1st" : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPM1st(data))
            elif vname == "CPS1st" : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPS1st(data))

            elif vname == "CPM2nd" : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPM2nd(data))
            elif vname == "CPS2nd" : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPS2nd(data))

            elif vname == "CPM3rd" : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPM3rd(data))
            elif vname == "CPS3rd" : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyCPS3rd(data))

            elif vname == "Temp"   : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyTemp(data))
            elif vname == "Press"  : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyPress(data))
            elif vname == "Humid"  : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyHumid(data))
            elif vname == "Xtra"   : g.BTDevices[vname]["dev"].notify(service_uuid, characteristic_uuid, lambda data: BTnotifyXtra(data))

        except Exception as e:
            exceptPrint(e, defname)

    icdprint(defname, f"Summary:  g.BTDevices:")
    for btdev in g.BTDevices:
        icdprint(defname, f" - {btdev}")

    g.BTsetupMsg += "\n"
    g.BTsetupMsg += f"Found {len(g.BTperipherals)} Bluetooth devices:\n"

    if g.BTperipherals is not None:
        for i, g.BTperipheral in enumerate(g.BTperipherals):
            g.BTsetupMsg += f"   #{i} Adress: {g.BTperipheral.address()}   ID: {g.BTperipheral.identifier()}\n"
    else:
        msg = f"Bluetooth peripherals have not yet been detected"
        dprint(defname, msg)
        efprint(msg)
        setIndent(0)
        return False

    setIndent(0)
    return True, ""


def BTnotifyCPM(data):      getValueFromBTData(data, "CPM")
def BTnotifyCPS(data):      getValueFromBTData(data, "CPS")

def BTnotifyCPM1st(data):   getValueFromBTData(data, "CPM1st")
def BTnotifyCPS1st(data):   getValueFromBTData(data, "CPS1st")

def BTnotifyCPM2nd(data):   getValueFromBTData(data, "CPM2nd")
def BTnotifyCPS2nd(data):   getValueFromBTData(data, "CPS2nd")

def BTnotifyCPM3rd(data):   getValueFromBTData(data, "CPM3rd")
def BTnotifyCPS3rd(data):   getValueFromBTData(data, "CPS3rd")

def BTnotifyTemp(data):     getValueFromBTData(data, "Temp")
def BTnotifyPress(data):    getValueFromBTData(data, "Press")
def BTnotifyHumid(data):    getValueFromBTData(data, "Humid")
def BTnotifyXtra(data):     getValueFromBTData(data, "Xtra")


def getValueFromBTData(data, vname):
    """Take the data from the DMM, convert to value, and store in 'g.DMMValues[vname]'"""

    ### g.BTinterval is duration in ms between 2 notifications; get it in Formula as 'BTNOTIFYDELTA()'
    ### BTinterval range: 94 ... 540 ms
    nowtime          = time.time()
    g.BTinterval     = 1000 * (nowtime - g.DMMlasttime)
    g.DMMlasttime    = nowtime

    # ignore everything coming when not logging
    if not g.logging: return

    defname = gd(sys._getframe().f_code.co_name)

    ### convert bytes to 'reading' array
    reading    = [0, 0, 0]
    reading[0] = data[1] << 8 | data[0]
    reading[1] = data[3] << 8 | data[2]
    reading[2] = data[5] << 8 | data[4]
    # icdprint(defname, reading)

    ### construct paramteres from the reading array
    function = (reading[0] >> 6) & 0x0f
    scale    = (reading[0] >> 3) & 0x07
    decimal  =  reading[0]       & 0x07

    ########################################################################################
    ### Extract items from first reading field
    ### Get the label and factors acc. to setting
    ### Total of 14 functions
    ffactor = 1 / 10**decimal
    if   function == 0b00000000 :
                                    fmode   = "DC_VOLTS"
                                    if scale == 3:
                                        fmode   = "DC_milliVOLTS"

    elif function == 0b00000001 :
                                    fmode = "AC_VOLTS"
                                    if scale == 3:
                                        fmode   = "AC_milliVOLTS"

    elif function == 0b00000010 :
                                    fmode = "DC_AMPS"
                                    if   scale == 2: ffactor /= 1E6              # µA
                                    elif scale == 3: ffactor /= 1E3              # mA
                                    elif scale == 4: ffactor /= 1                # A

    elif function == 0b00000011 :
                                    fmode = "AC_AMPS"
                                    if   scale == 2: ffactor /= 1E6              # µA
                                    elif scale == 3: ffactor /= 1E3              # mA
                                    elif scale == 4: ffactor /= 1                # A

    elif function == 0b00000100 :
                                    fmode = "OHMS"
                                    if   scale == 4: ffactor *= 1                # Ohm
                                    elif scale == 5: ffactor *= 1e3              # kOhm
                                    elif scale == 6: ffactor *= 1e6              # MOhm

    elif function == 0b00000101 :   fmode = "CAPACITANCE"
    elif function == 0b00000110 :
                                    fmode   = "FREQUENCY"
                                    if   scale == 4: ffactor *= 1
                                    elif scale == 5: ffactor *= 1000
    elif function == 0b00000111 :
                                    fmode   = "PERCENT"
                                    if   scale == 4: ffactor *= 1
                                    elif scale == 5: ffactor *= 1000

    elif function == 0b00001000 :   fmode = "TEMP_C"
    elif function == 0b00001001 :   fmode = "TEMP_F"
    elif function == 0b00001010 :   fmode = "DIODE"
    elif function == 0b00001011 :   fmode = "CONTINUITY"
    elif function == 0b00001100 :   fmode = "HFE"
    elif function == 0b00001101 :   fmode = "NCV"
    ########################################################################################

    # Extract and convert measurement value (consider sign!)
    if (reading[2] <= 0x7fff):      measurement = reading[2]
    else:                           measurement = -1 * (reading[2] & 0x7fff)
    value = measurement * ffactor

    ### testing
    msg = f"value: {value}  reading[2]: {reading[2]}  reading[2]&0x7fff: {reading[2]&0x7fff}  measurement: {measurement}  ffactor: {ffactor}  scale: {scale}  decimal: {decimal}"
    # irdprint(defname, msg)
    if value < 10000:
          irdprint(defname, msg)
          QueuefPrint(msg, color="<red>", error=True)
          irdprint(defname, f"Negative reading ----------------------------------------------------------------------------")
    ### end testing

    ### printout of each notify call (1 ... 3 per sec)
    # BTpstuff  = ""
    # BTpstuff += f"g.BTDevices[{vname}]: "
    # BTpstuff += f"ΔBT: {g.BTinterval:4.0f} ms  data: '{data.hex(' ')}'  "
    # BTpstuff += f"Raw: {measurement:>5.0f}  func: {function}  fmode: {fmode:10s}  scale: {scale}  dec: {decimal}"
    # BTpstuff += f" --> {value:6.{5}g} {fmode}"
    # irdprint(defname, f"{BTpstuff}")

    g.DMMValues[vname] = value


def getValuesDMM(varlist):
    """get the values"""

    defname = gd(sys._getframe().f_code.co_name)

    start = time.time()

    alldata = {}
    for vname in varlist:
        alldata[vname]     = applyValueFormula(vname, g.DMMValues[vname], g.ValueScale[vname], info=defname)
        if not np.isnan(g.DMMValues[vname]):
            g.DMMValues[vname] = g.NAN                                      # reset value to NAN after read-out

    vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)

    return alldata


def terminateDMM():
    """Stop all DMM devices and the GL DMM Device"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    try:
        pass
        # for vname in g.BTDevices:
        #     if g.BTDevices[vname]["dev"] is not None:
        #         dprint(defname, f"vname: {vname:6s}  dev: {g.BTDevices[vname]["Label"]}")
        #         g.BTDevices[vname]["dev"].disconnect()
        #     g.BTDevices[vname]["dev"] = None
        # time.sleep(1)

    except Exception as e:
        exceptPrint(e, defname + f"on disconnection of Bluetooth devices for : {vname}")

    os.system("rfkill   block bluetooth")
    os.system("rfkill unblock bluetooth")

    g.Devices["DMM"][g.CONN]  = False

    dprint(defname, "Terminated")
    setIndent(0)


def foundBTDevice(peripheral):
    """Detailing the peripheral properties"""

    defname = gd(sys._getframe().f_code.co_name)

    ### is always: Tx Power: -32768 dBm
    ### From SimpleBLE docs: tx power:
    ### "If the field has not been advertised by the peripheral, the returned value will be -32768."
    # icdprint(f'   Tx Power: {peripheral.tx_power()} dBm') # always: Tx Power: -32768 dBm

    ### is all empty on OWON OW18E
    # manufacturer_data = peripheral.manufacturer_data()
    # icdprint(defname, f"manuf data: {manufacturer_data}")
    # for manufacturer_id, value in manufacturer_data.items():
    #     icdprint(f"    Manufacturer ID: {manufacturer_id}    Manufacturer data: {value}")

    ### data is all empty (b'') on OWON OW18E
    # services = peripheral.services()
    # for service in services:
    #     icdprint(f"    Service UUID:    {service.uuid()}     Service data: {service.data()}")

    if peripheral is not None:
        try:
            pif = peripheral.identifier()
            if peripheral.identifier().strip() == "":  pid = "<empty>"
            else:                                      pid = peripheral.identifier().strip()
        except Exception as e:
            exceptPrint(e, defname)
            ydprint(defname, f"peripheral: {peripheral}")
            msg = "bummer"
        else:
            connectable_str   = "Connectable    " if peripheral.is_connectable() else "Non-Connectable"
            msg = f"ID {pid:10s}  MAC-Addr: [{peripheral.address()}] - {connectable_str}   {peripheral.address_type()}"
    else:
        msg = f"Requested 'peripheral' is undefined"

    return msg


#inf
def getInfoDMM(extended=False):
    """Info on settings of the DMM device"""

    defname = gd(sys._getframe().f_code.co_name)

    DMMInfo  =          "Configured Connection:        Bluetooth\n"
    if not g.Devices["DMM"][g.CONN]: return DMMInfo + "<red>Device is not connected</red>"

    DMMInfo +=          "Connected Device:             {}\n"                            .format(g.Devices["DMM"][g.DNAME])
    DMMInfo +=          "............................. ID        Label     [MAC-Addr]\n"
    DMMInfo +=          "Bluetooth Adapter:            {:8s}  ---       [{}]\n"         .format(g.BTAdapter.identifier(), g.BTAdapter.address())

    try:
        for vname in g.BTDevices:
            if g.BTDevices[vname]["dev"] is not None:
                id    = g.BTDevices[vname]["dev"].identifier()
                addr  = g.BTDevices[vname]["dev"].address()
                label = g.BTDevices[vname]["Label"]
                DMMInfo += f"Bluetooth Device:             {id:8s}  {label:8s}  [{addr}]\n"
                icdprint(defname, f"vname: {vname}  dev: {addr}   ID: {id}  Label: {label}")

    except Exception as e:
        exceptPrint(e, defname + f"on disconnection of Bluetooth devices for : {vname}")
        DMMInfo +=      "Bluetooth Device:             unknown (Bluetooth Discovery Failure; Try repeating)\n"

    DMMInfo +=          "Configured Variables:         {}\n"                            .format(g.DMMVariables)
    DMMInfo +=          getTubeSensitivities(g.DMMVariables)
    DMMInfo +=          "\n"

    if extended:
        DMMInfo +=      "\n"

    return DMMInfo


def showBTenvironment():
    """check for adapter and devices"""

    defname = gd(sys._getframe().f_code.co_name)

    fprint(header("Show Bluetooth Environment"))
    QtUpdate()

    if not g.Devices["DMM"][g.CONN]:
        msg = "Device is not connected"
        QueuefPrint(msg, color="<red>")
        return msg

    # check if importing the Bluetooth module has FAILED
    if not g.BTfoundsimplepyble:
        msg = "Cannot find Bluetooth module!"
        QueuefPrint(msg)
        return msg

    # is BT available on the computer?
    if not simplepyble.Adapter.bluetooth_enabled():
        QueuefPrint("This computer's Bluetooth adapter is NOT enabled!")
        return

    ### not relevant any more
    # if 0 and g.Devices["DMM"][g.CONN]:
    #     QueuefPrint("Cannot show BT environment with an activ connection to it!", error=True)
    #     QueuefPrint("Please, disconnect first.", color="<red>", error=False)
    #     return
    #
    # BTsetupAdapter()
    # BTsetupDMM()

    QueuefPrint(g.BTsetupMsg)


def connectDMM():

    defname = gd(sys._getframe().f_code.co_name)
    g.exgg.switchSingleDeviceConnection ("DMM", new_connection="ON")


def disconnectDMM():

    defname = gd(sys._getframe().f_code.co_name)
    g.exgg.switchSingleDeviceConnection ("DMM", new_connection="OFF")
    g.BTperipheral = None


##################################################################################################################
####  OWON OW18E DMM via Bluetooth                                                ################################
####  Call via Formula Interpreter as:    DMMCALL(MODEL, PORT)    (see in utils)  ################################
##################################################################################################################
def getOW18EValue():
    """
    Query the OWON OW18E DMM via Bluetooth for a single Value  in whatever unit selected at the DMM
    return: value as float
    """
    defname = gd(sys._getframe().f_code.co_name)

    value           = g.DMMcallValue
    g.DMMcallValue  = g.NAN                 # reset to NAN to avoid double-calling same value

    return value


##################################################################################################################
####  VOLTCRAFT VC850 DMM VIA SERIAL PORT                                         ################################
####  Call via Formula Interpreter as:    DMMCALL(MODEL, PORT)    (see in utils)  ################################
##################################################################################################################
def getVC850Value(PORT):
    """
    Query the Voltcraft VC850 DMM via RS232 Serial for a single Value in whatever unit selected at the DMM
    return: value as float
    """

    # Coding:
    # doc:  see: VC850-Encoding.pdf under ~/Hardware -> DMM
    # response of DMM is:  b'+2962 11\x04\x00\x80\x1d\r\n'
    # HEX:                  2B 32 39 36 32 20 31 31 04 00 80 1D 0D 0A
    # ASCII:                 +  2  9  6  2 Sp  1  1  4  0 XX BG CR LF  # Sp = Space; XX = Bin code; BG = Bar Graph
    # index:                 0  1  2  3  4  5  6  7  8  9 10 11 12 13
    #                       +-____value____ Space
    #                                         Factor
    #                                            SB1 - see doc
    #                                               SB2 - see doc
    #                                                  Prefix
    #                                                    Unit (80 = Volt)
    #                                                        Bar Graph Byte - see doc
    #                                                            CR LF
    #
    # A proper response is NOT returned in some 5%(!) -or even more- of calls!

    # defname       = "getVC850Value: "
    defname = gd(sys._getframe().f_code.co_name)

    rstart        = time.time()
    g.VC850Count += 1

    try:
        port     = PORT.replace("/DEV/TTYUSB", "/dev/ttyUSB")           # for Linux; in Win it is COM anyway
        rtimeout = 1.0
        wtimeout = 1.0
        prefix   = "NoPrefix"
        unit     = "NoUnit"

        # opening Serial (takes 5 ... 7 ms)
        # sercall  = time.time()
        with serial.Serial( port          = port,
                            baudrate      = 2400,
                            timeout       = rtimeout,
                            write_timeout = wtimeout,
                            ) as RPser:
            # ydprint(defname, f"opening serial: {(time.time() - sercall) * 1000:0.1f} ms")

            try:
                # waiting for >14 bytes; takes 50 ... 700 ms! sammelt bytes von allen transmits in einem record
                sercall    = time.time()
                waitperiod = 0.8
                while True:
                    if RPser.in_waiting >= 14: break
                    if time.time() - sercall > waitperiod:           # exit if no data within waitperiod sec
                        rdprint(defname, f"Exiting as no data within last {waitperiod} sec")
                        return g.NAN
                    time.sleep(0.010)

                # got >= 14 bytes; now read them and evaluate
                rawbrec = RPser.read(RPser.in_waiting)        # read all bytes from the pipeline
                # ydprint(defname, f"rawbrec: {rawbrec}  [{' '.join("%02X" % e for e in rawbrec)}]  len: {len(rawbrec)}")

                index   = rawbrec.rfind(b"\r\n")              # find the last CRLF (-1 if not found)
                # ydprint(defname, "index: ", index)

                # check record for errors
                error = False
                if index < 12:                                # need at least 12 chars for data (+ CRLF -> 14)
                    error = True
                else:
                    brec = rawbrec[index - 12 : index]        # get the 12 chars up to before the last CRLF
                    # ydprint(defname, f"brec:    {brec}  [{' '.join("%02X" % e for e in brec)}]  len: {len(brec)}")

                    if len(brec)    != 12 :                     error = True
                    if brec[0]      not in (0x2B, 0x2D):        error = True
                    if brec[1]      not in range(0x30, 0x36):   error = True    # 6000 counts: 5999
                    if brec[2]      not in range(0x30, 0x3A):   error = True
                    if brec[3]      not in range(0x30, 0x3A):   error = True
                    if brec[4]      not in range(0x30, 0x3A):   error = True
                    if brec[5]      != 0x20 :                   error = True
                    if brec[6]      >  0x33 :                   error = True    # observed: value=0xF1 (instead of 0x31)

            except Exception as e:
                TOmsg  = "Timeout " if (time.time() - sercall) >= rtimeout else " "
                exceptPrint(e, defname + f"FAILURE {TOmsg}reading serial ")
                error = True

            if error:
                g.VC850ErrCount += 1
                val = g.NAN
                # QueueSoundDBG("cocoo")
            else:
                val = float(brec[0:5].decode("ascii", errors='replace'))
                if   brec[6] == 0x30:           val /= 1
                elif brec[6] == 0x31:           val /= 1000
                elif brec[6] == 0x32:           val /= 100
                elif brec[6] == 0x33:           val /= 10

                if   (brec[9] & 0x80) != 0:     prefix = "µ"
                elif (brec[9] & 0x40) != 0:     prefix = "m"
                elif (brec[9] & 0x20) != 0:     prefix = "k"
                elif (brec[9] & 0x10) != 0:     prefix = "M"
                else:                           prefix = ""

                if   (brec[10] & 0x80) != 0:    unit = "V"
                elif (brec[10] & 0x40) != 0:    unit = "A"
                elif (brec[10] & 0x20) != 0:    unit = "Ω"
                elif (brec[10] & 0x10) != 0:    unit = "hFE"
                elif (brec[10] & 0x08) != 0:    unit = "Hz"
                elif (brec[10] & 0x04) != 0:    unit = "F"
                elif (brec[10] & 0x02) != 0:    unit = "℃"
                elif (brec[10] & 0x01) != 0:    unit = "℉"
                else:                           unit = ""

    except Exception as e:      # Exception über alles. sinnvoll?
        exceptPrint(e, defname + f"FAILURE getting VC850 values; rawbrec: {rawbrec}")
        val = g.NAN

    rdur = round(1000 * (time.time() - rstart), 3)
    rbs  = [{" ".join("%02X" % e for e in rawbrec)}]
    errpc= g.VC850ErrCount / g.VC850Count
    msg  = f"val: {val:6.3f} {prefix + unit:<4s}  Dur:{rdur:4.0f} ms  len:{len(rawbrec)} (expect:14)  Raw: {rawbrec} {rbs}  Err%: {errpc:0.1%}"

    if error: rdprint(defname, "ERROR: " + msg)
    else:     mdprint(defname, msg)

    return val      # type float

