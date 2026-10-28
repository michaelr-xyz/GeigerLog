 #! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
DMM_OWON.py      -  a utility which gets a reading from an OWON OW18E DMM.
                    It exchanges the last reading with GeigerLog by either
                    file (default) or memory (not reommended).

see: 'helpOptions' below for usage information
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

__author__              = "ullix"
__copyright__           = "Copyright 2016 - 2025"
__credits__             = [""]
__license__             = "GPL3"
__version__             = "1.4"


# module imports
import sys, os, time                            # basic modules
import datetime         as dt                   # date and time
import getopt                                   # parsing command line options
import simplepyble                              # the Bluetooth lib
from multiprocessing import shared_memory       # to allow saving to memory
import subprocess                               # used for cli
import serial                                   # used for VC850

# from wifi
import urllib.request                           # making Web calls
import socket                                   # for finding the IP address
import ipaddress                                # for checking for valid IP address

# colors
TDEFAULT                = '\033[0m'             # default, i.e greyish
TRED                    = '\033[91m'            # red
BRED                    = '\033[91;1m'          # bold red
TGREEN                  = '\033[92m'            # light green
BGREEN                  = '\033[92;1m'          # bold green
TYELLOW                 = '\033[93m'            # yellow
TCYAN                   = '\033[96m'            # cyan

INVMAGENTA              = '\033[45m'            # invers magenta looks ok
INVBOLDMAGENTA          = '\033[45;1m'          # invers magenta with bold white

##############################################################################################################################
# This code uses simplepyble: "... works on Windows, Linux and MacOS."
# Install with:
#           pip install simplepyble
#
# Please take into consideration that when using this library on Linux, you
# will need to have the following dependencies installed:
#           sudo apt-get install libdbus-1-dev
#
# https://simpleble.readthedocs.io/en/latest/simplepyble/usage.html
#
#
# ATTENTION:              This code works ONLY with an OWON OW18E DMM device with Bluetooth identifier 'BDM'
#                         Presently only the functions Volt, milliVolt, Frequency, and Duty Cycle are supported
#
# specific for my first device OW18E#1
#
# ADDRESS = "A6:C0:80:E3:85:9D"
# CHARACTERISTIC_UUID = "0000fff4-0000-1000-8000-00805f9b34fb"      # Output: 23 f0 04 00 5b 0f     # this is choice #7 !
# CHARACTERISTIC_UUID = "00001801-0000-1000-8000-00805f9b34fb"      # Generic Attribute
# CHARACTERISTIC_UUID = '00001800-0000-1000-8000-00805f9b34fb'      # Generic Access
# CHARACTERISTIC_UUID = '0000180a-0000-1000-8000-00805f9b34fb'      # Device Information
# CHARACTERISTIC_UUID = '0000fff0-0000-1000-8000-00805f9b34fb'      # Unknown
# CHARACTERISTIC_UUID = '00010203-0405-0607-0809-0a0b0c0d1911'      # Proprietary
#
# Output from:
#   for i, pair in enumerate(service_characteristic_pair):
#         dprint(defname, f"   #{i}  Finding service.uuid: {pair[0]},  characteristic.uuid: {pair[1]}")
#
# BTsetupDMM: #0  service.uuid: 00001801-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a05-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #1  service.uuid: 0000180a-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a29-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #2  service.uuid: 0000180a-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a24-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #3  service.uuid: 0000180a-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 00002a26-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #4  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff1-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #5  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff2-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #6  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff3-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #7  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff4-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #8  service.uuid: 0000fff0-0000-1000-8000-00805f9b34fb,  characteristic.uuid: 0000fff5-0000-1000-8000-00805f9b34fb
# BTsetupDMM: #9  service.uuid: 00010203-0405-0607-0809-0a0b0c0d1911,  characteristic.uuid: 00010203-0405-0607-0809-0a0b0c0d2b12
##############################################################################################################################

# globals
class Globals:
    """A class with the only task to make some variables global"""

    # constants
    NAN                 = float("nan")              # use as g.NAN

    # WiFi Settings (change via command line options)
    WiFiTargetIP        = "0.0.0.0"                 # IP of computer to RECEIVE data from this DMMWiFiClient
    WiFiTargetPort      = 4000                      # for GeigerLog the TargetPort should be 4000 (range: 1024...65535)
    WiFiClientType      = "GENERIC"                 # so far "GMC" and "GENERIC" are the only options

    # Cycle
    CycleTime           = 1                         # default = 1 sec


    # Saving via file or memory?
    saveflag            = "FILE"                          # alternatives: "FILE" (default) or -taken from command line-  "MEM" or "WIFI"

    # Flags
    verify              = False                           # Verify data?

    # Trackers
    counter             = 1                               # waiting for data ...
    ScanDuration        = 1000                      # ms
    lastnow             = time.time()
    lastlastnow         = time.time()
    lasttime            = time.time()
    handlings           = 1

#from wifi
    lastupload          = time.time()
    SumGETcalls         = 0
    DurTotal            = 0


    # Which OWON device?
    owondevice = "default"                       # alternatives: "owon#1" ([A6:C0:80:E3:85:9D] BDM),
                                                 #               "owon#2" ([A6:C0:80:E3:80:78] BDM)

    # Bluetooth device
    peripheral = None

    # For data exchange via MEMORY; same name must be used in GeigerLog
    shm        = None
    DMMshmName = None

    # For data exchange via FILE; same name must be used in GeigerLog
    filename   = ".dmmOW18E.data"

    # Help
    helpOptions = """
            Usage:  DMM_OWON.py [Options] [Commands]

            Start:  DMM_OWON.py
            Stop:   CTRL-C

            Options:
                -h, --help          Show this help and exit
                -V, --Version       Show version and exit
                -v, --verify        Verify data by reading back what had been saved
                -c, --cycle         Set the cycle time in sec (default 1 sec)
                -s, --Scan          Bluetooth max scan duration in ms (default=1000)
                -I, --TargetIP      WiFi: Set the IP of the target computer
                -P, --TargetPort    WiFi: Set the Port of the target computer (default 8000)
                -T, --Type          WiFi: Set the Type of client to 'GENERIC' (default) or 'GMC'

            Commands:
                file                Exchanging data via file.
                                    In GeigerLog call in Formula Interpreter
                                    as:     DMMCALL("OW18E_FILE")

                mem                 Exchanging data via memory.
                                    In GeigerLog call in Formula Interpreter
                                    as:     DMMCALL("OW18E_MEM")

                wifi                Exchanging data via WiFi, using GeigerLog's
                                    WiFiClient device.

                <device>            Can be 'ow18e', 'ow18e#1', or 'ow18e#2'; nothing else

            Examples:
                DMM_OWON.py         Run DMM_OWON and exchange data with
                                    GeigerLog via file

                DMM_OWON.py -v mem  Run DMM_OWON and exchange data with GeigerLog
                                    via memory and verify data by reading back

                DMM_OWON.py -I 10.0.0.46 wifi
                                    Run DMM_OWON and exchange data with GeigerLog
                                    as a WiFiClient. GeigerLog listens on IP 10.0.0.46
                                    (using default Port 4000).

            ATTENTION:              This code works only with an OWON OW18E device
                                    with Bluetooth identifier 'BDM'.

                                    Presently only the functions DC-Volt, DC-milliVolt,
                                    Frequency, and Duty Cycle are supported                           .
    """
# end globals class


# initiate global vars
g = Globals



def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def dprint(*args):
    tag = ""
    for arg in args: tag += str(arg)
    if tag > "": tag = f"{longstime():23s} " + tag
    print(tag)


def rdprint(*args):
    args = (BRED,) + args + (TDEFAULT,)
    dprint(*args)


def ydprint(*args):
    args = (TYELLOW,) + args + (TDEFAULT,)
    dprint(*args)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which filename?

    print(TYELLOW, end="")
    dprint("EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno), "  ", srcinfo, TDEFAULT)


def clearTerminal():
    """clear the terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')    # os.name:  posix (on Linux); nt (on Windows)


def getIP():
    """get the IP of the computer running GLrelay.py"""

    defname = "getGeigerLogIP: "

    try:
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        st.connect(('8.8.8.8', 80))
        IP = st.getsockname()[0]
    except Exception as e:
        IP = '127.0.0.1'
        srcinfo = "Bad socket connect, IP set to:" + IP
        exceptPrint(e, defname + srcinfo)
    finally:
        st.close()

    return IP


def isValidIP(ip):
    """determine validity of given IP address"""

    defname = "isValidIP: "

    try:
        ipaddress.ip_address(ip)
        return True
    except Exception as e:
        exceptPrint(e, defname)
        return False


#main
def main():
    """setup"""

    defname = "main: "

    # clear screen
    clearTerminal()

    # header
    dprint(BGREEN + "Starting: " + __file__ + "   " +"*" * 75, TDEFAULT)
    rdprint("Help:     Exit with: CRTL-C")
    rdprint("Help:     Get help on usage with option '-h'")

    # parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdVvc:I:P:T:s:", ["help", "debug", "Version", "verify", "cycle=", "TargetIP=", "TargetPort=", "Type=", "Scan="])
    except getopt.GetoptError as e :
        # print info like "option -x not recognized", then exit
        exceptPrint(e, "For Help use: './DMM_OWON.py -h'")
        return False

    # process the options
    for opt, optval in opts:
        if   opt in ("-h", "--help"):                       # show the help info and exit
            print(g.helpOptions)
            return  False

        elif opt in ("-V", "--Version"):                    # show the version and exit
            print(f"\n        Version: {__version__} of {__file__}\n")
            return  False

        elif opt in ("-v", "--verify"):                     # flag to verify saved data by reading back from file or mem
            g.verify = True
            dprint(defname, f"Verify: {g.verify}")

        elif opt in ("-c", "--cycle"):                      # set the cycle time in sec
            try:    ct = float(optval)
            except: ct = 1
            if ct > 0:
                g.WiFiCycleTime = ct
            else:
                print("The configured cycle time of '{}' sec is not valid.".format(optval))
                print("It can be any number greater than zero")
                return False

        elif opt in ("-I", "--TargetIP"):                   # re-define the Target IP address
            if isValidIP(optval):
                g.WiFiTargetIP = optval
            else:
                print("The configured Target IP address '{}' is not valid. See: https://en.wikipedia.org/wiki/IP_address".format(optval))
                print("As an example, this computer has the IP address: '{}'".format(g.WiFiTargetIP))
                return False

        elif opt in ("-P", "--TargetPort"):                 # re-define the Target Port number
            try:    pnum = int(float(optval))
            except: pnum = -1
            if pnum >= 1 and pnum <= 65535:
                g.WiFiTargetPort = pnum                     # valid port
                if g.WiFiTargetPort < 1024:
                    msg = f"As TargetPort {g.WiFiTargetPort} is privileged you must be running DMM_WiFiClient with ADMINISTRATIVE RIGHTS!"
            else:
                print("The configured Target Port number '{}' is not valid".format(optval))
                print("Allowed range for Port numbers is 1 ... 65535 (incl.)")
                return False

        elif opt in ("-T", "--Type"):                       # re-define the Client Type as "GMC" or "GENERIC"
            if optval in ("GMC", "GENERIC"):
                g.WiFiClientType = optval
            else:
                print("The configured Client Type '{}' is not valid".format(optval))
                print("Only 'GMC' and 'GENERIC' are allowed")
                return False

        elif opt in ("-s", "--Scan"):                       # ScanDuration; default = 1000 ms
            try:    sd = float(optval)
            except: sd = 1000
            if sd > 0:
                g.ScanDuration = sd
            else:
                print("The configured Scan Duration time of '{}' sec is not valid.".format(optval))
                print("It can be any number greater than zero; default=1000")
                return False


    # process the args
    for arg in args:
        arg = arg.lower()
        if   arg == "mem":   g.saveflag   = "MEM"
        elif arg == "file":  g.saveflag   = "FILE"
        elif arg == "wifi":  g.saveflag   = "WIFI"
        elif "ow18e" in arg: g.owondevice = arg

    tmplt = "Info:     {:20s}: {} {}"
    dprint(tmplt.format('Command line',         sys.argv,          ""))
    dprint(tmplt.format('Transfer data by',     g.saveflag,        ""))
    dprint(tmplt.format('Transfer filename',    g.filename,        ""))
    dprint(tmplt.format('WiFi Target IP',       g.WiFiTargetIP,    ""))
    dprint(tmplt.format('WiFi Target Port',     g.WiFiTargetPort,  ""))
    dprint(tmplt.format('WiFi Client Type',     g.WiFiClientType,  ""))
    dprint(tmplt.format('Cycle time',           g.CycleTime,       "sec"))
    dprint(tmplt.format('BT Scan Duration',     g.ScanDuration,    "ms"))
    dprint(tmplt.format('Device',               g.owondevice,      ""))
    dprint(tmplt.format('Verify data',          g.verify,          ""))
    print()

    return True


def BTsetupDMM():
    """Setup the DMM for Notify"""

    defname = "BTsetupDMM: "
    # dprint(defname)

    # is BT enabled on the computer?
    if not simplepyble.Adapter.bluetooth_enabled():
        rdprint(defname, "Bluetooth adapter is NOT enabled! Exiting")
        return False

    # get the adapters
    dprint(defname, f"Searching Bluetooth adapters:")
    adapters = simplepyble.Adapter.get_adapters()
    adapters_len = len(adapters)
    for i, adapter in enumerate(adapters):
        try:
            dprint(defname, f"   Found Bluetooth adapter: #{i} of {adapters_len}    ID: '{adapter.identifier()}'  mac: [{adapter.address()}]")
        except Exception as e:
            rdprint(defname, f"   Found Bluetooth adapter: #{i} of {adapters_len}    ID: '{adapter.identifier()}'  adapter: '{adapter}")
            # rdprint(defname, f"   Found Bluetooth adapter: #{i} of {adapters_len}    ID: '{adapter.identifier()}'  mac: [{adapter.address()}]")

    adapter  = adapters[0]
    dprint(defname, f"   Selected Bluetooth adapter: ID: '{adapter.identifier()}'  mac: [{adapter.address()}]")

    adapter.set_callback_on_scan_start(lambda: dprint(defname, "Scanning for Bluetooth devices"))
    adapter.set_callback_on_scan_stop (lambda: dprint(defname, "   Bluetooth Scan complete"))
    adapter.set_callback_on_scan_found(lambda peripheral: dprint(defname, f"   Found device: ID: '{peripheral.identifier()}'  mac: [{peripheral.address()}]"))

    adapter.scan_for(g.ScanDuration)                        # Scan for Bluetooth devices for g.ScanDuration millisec
    peripherals = adapter.scan_get_results()                # the scan code will print the peripherals via the callback
    # rdprint(defname, "peripherals: ", peripherals, " len: ", len(peripherals))

    if len(peripherals) == 0:
        rdprint(defname, "   No Bluetooth devices found. Please check setup. Exiting.")
        return False


    BDMfound = False
    if   g.owondevice == "default":
        if len(peripherals) > 1:
            # Query the user to pick a peripheral from multiple found
            print()
            print("Found multiple devices, please select:")
            print("Index: ID     Address              Device")

            for i, tmpperipheral in enumerate(peripherals):
                print(f"    {i}: {tmpperipheral.identifier():6s} [{tmpperipheral.address()}]", end="  ")
                if   tmpperipheral.address() == "A6:C0:80:E3:85:9D": print(f"local#1")
                elif tmpperipheral.address() == "A6:C0:80:E3:80:78": print(f"local#2")
                else:                                                print(f"unknown")


            while True:
                ec = input("Enter index of device: ")
                if ec == "":
                    choice = 0
                else:
                    try:    choice = int(ec)
                    except: choice = 0

                if choice < len(peripherals): break
                else:                         print("Not available!")
        else:
            # there is only a single peripheral
            choice = 0

        g.peripheral = peripherals[choice]

        if g.peripheral.identifier() == "BDM":
            BDMfound   = True
            g.DMMshmName = "ow18e"
            g.filename   = ".dmmOW18E.data"

    else:
        for g.peripheral in peripherals:
            if g.peripheral.identifier() == "BDM":
                dprint(defname, "A 'BDM' device was found")

                if g.owondevice == "ow18e#1":
                    if g.peripheral.address() == "A6:C0:80:E3:85:9D":
                        BDMfound   = True
                        g.DMMshmName = "ow18e#1"
                        g.filename   = ".dmmOW18E.data" + "#1"
                        break

                elif g.owondevice == "ow18e#2":
                    if g.peripheral.address() == "A6:C0:80:E3:80:78":
                        BDMfound   = True
                        g.DMMshmName = "ow18e#2"
                        g.filename   = ".dmmOW18E.data" + "#2"
                        break

                elif g.owondevice == "ow18e":
                    BDMfound   = True
                    g.DMMshmName = "ow18e"
                    g.filename   = ".dmmOW18E.data"
                    break

    if not BDMfound:
        g.peripheral = None
        dprint(defname, "Peripheral BDM not found - giving up")
        return False

    if   g.peripheral.address() == "A6:C0:80:E3:85:9D": device = f"local#1"
    elif g.peripheral.address() == "A6:C0:80:E3:80:78": device = f"local#2"
    else:                                               device = f"Unknown"
    dprint(defname, f"Connecting to: {g.peripheral.identifier()}  [{g.peripheral.address()}]  Device: '{device}'")
    try:
        g.peripheral.connect()
    except Exception as e:
         exceptPrint(e, f"Failed connection to device: '{g.owondevice}'")
         return False
    print()

    services = g.peripheral.services()
    service_characteristic_pair = []
    for service in services:
        for characteristic in service.characteristics():
            service_characteristic_pair.append((service.uuid(), characteristic.uuid()))

    for i, pair in enumerate(service_characteristic_pair):
        dprint(defname, f"   #{i}  Finding service.uuid: {pair[0]},  characteristic.uuid: {pair[1]}")

    choice = 7
    dprint(defname, f"Setting Notify on: #{choice}")
    g.lasttime = time.time()
    try:
        service_uuid, characteristic_uuid = service_characteristic_pair[choice]
        g.peripheral.notify(service_uuid, characteristic_uuid, lambda data: handleData(data))
    except Exception as e:
        exceptPrint(e, defname)

    dprint(defname, "Done Setup")
    print()

    return True


def handleData(data):
    """Extract Voltage values from Owon meter response"""

    defname = "handleData: "
    # ydprint(defname, data)

    nowtime         = time.time()
    g.DMMduration   = 1000 * (nowtime - g.lasttime)     # duration in ms between 2 notifications
    g.lasttime      = nowtime
    g.counter       = 1
    g.handlings    += 1


    # Owon meter logic (from: https://github.com/sercona/Owon-Multimeters/blob/main/owon_multi_cli.c)
    # convert bytes to 'reading' array
    reading    = [0, 0, 0]
    reading[0] = data[1] << 8 | data[0]
    reading[1] = data[3] << 8 | data[2]
    reading[2] = data[5] << 8 | data[4]
    # ydprint(defname, reading)

    # Extract data items from first field
    function = (reading[0] >> 6) & 0x0f
    scale    = (reading[0] >> 3) & 0x07
    decimal  =  reading[0]       & 0x07


    ########################################################################################
    # Get the label and factors acc. to setting
    # 14 functions
    ffactor  = 1
    if   function == 0b00000000 :
                                    fmode   = "DC_VOLTS"
                                    ffactor = 1 / 10**decimal
                                    if scale == 3: ffactor /= 1000              # millivolt
    elif function == 0b00000001 :   fmode = "AC_VOLTS"
    elif function == 0b00000010 :   fmode = "DC_AMPS"
    elif function == 0b00000011 :   fmode = "AC_AMPS"
    elif function == 0b00000100 :   fmode = "OHMS"
    elif function == 0b00000101 :   fmode = "CAPACITANCE"
    elif function == 0b00000110 :
                                    fmode   = "FREQUENCY"
                                    ffactor = 1 / 10**decimal
                                    if   scale == 4: ffactor *= 1
                                    elif scale == 5: ffactor *= 1000
    elif function == 0b00000111 :
                                    fmode   = "PERCENT"
                                    ffactor = 1 / 10**decimal
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
    if (reading[2] < 0x7fff):       measurement = reading[2]
    else:                           measurement = -1 * (reading[2] & 0x7fff)
    g.DMMvalue = measurement * ffactor

    # printout
    pstuff  = ""
    pstuff += f"{defname}#{g.handlings:<4d} dBT:{g.DMMduration:4.0f} ms  BT:'{data.hex(' ')}'  "
    pstuff += f"Raw: {measurement:4.0f}  func: {function}  fmode: {fmode}  scale: {scale}  dec: {decimal}"
    pstuff += f" --> {g.DMMvalue:6.5g} {fmode}  smpls/sec: {1 / ((nowtime - g.lastlastnow) / 2):2.0f} (Return for LF)  "
    g.lastlastnow = g.lastnow
    g.lastnow     = nowtime
    print(f"\r{longstime():23s} {pstuff}", end="")          # stays on the same terminal line

    uploadData(fmode)


def uploadData(fmode):
    """fmode is unit of value, like: DC_VOLTS
    3 options are supported:
            - WiFi
            - File
            - Memory
    """

    defname = "uploadData: "

    now     = time.time()
    if now - g.lastupload < (g.CycleTime - 0.51):                           # in 15 min keine "Missing File" Meldungen
        return            # deltaT between 2 notifications is up to 510 ms
    g.lastupload = now

# WiFi
    if g.saveflag == "WIFI":

        # prepare data as needed for url
        numbers     = [g.NAN] * 12                  # reset numbers to all NAN
        numbers[10] = round(g.DMMduration, 3)       # --> Humid   # the duration between 2 notification calls
        numbers[11] = round(g.DMMvalue,  3)         # --> Xtra    # the Volt value

        dataURL     = "/GENERIC?M={}&S={}&M1={}&S1={}&M2={}&S2={}&M3={}&S3={}&T={}&P={}&H={}&X={}".format(*numbers)
        fullURL     = f"http://{g.WiFiTargetIP}:{g.WiFiTargetPort}" + dataURL
        resp        = ""
        status      = -1

        # make GET call
        try:
            ustart = time.time()
            with urllib.request.urlopen(fullURL) as response:
                resp   = str(response.read())                            # type(resp): <class 'bytes'>
                status = response.status
            udur   = 1000 * (time.time() - ustart)

            g.DurTotal    += udur
            g.SumGETcalls += 1
            DurAvg         = g.DurTotal / g.SumGETcalls                  # g.SumGETcalls is at least==1

            msg = f"{g.SumGETcalls:4d} req: {fullURL:115s}  resp: {TGREEN}{resp:27s}{TDEFAULT}  status:{status}  dur:{udur:0.1f} ms  durAvg:{DurAvg:0.1f} ms"
            print(f"\n{longstime():23s} {defname}{msg}")      # make a new line

        except Exception as e:
            # exceptPrint(e, "")
            stre = str(e)
            if "connection without response" in stre or "Connection refused" in stre:
                msg = f"{INVMAGENTA}No WiFi connection to GeigerLog; it must be both Running AND Logging!{TDEFAULT} (using URL: {fullURL})"
                rf  = "\r"
                print(f"{rf}{longstime()} {defname}{msg}")
            else:
                exceptPrint(e, "")

# FILE
    elif g.saveflag == "FILE":
        dataline   = f"{longstime()}, {g.DMMvalue:0.5g}, {fmode}\n"
        with open(g.filename, "w") as fd:
            fd.write(dataline)

        # check by reading back from File
        if g.verify:
            with open(g.filename, "r") as fd:
                print("Verify: ", fd.readline(), end="")  # line is ending with LF

# MEM
    elif g.saveflag == "MEM":
        dataline   = f"{longstime()}, {g.DMMvalue:0.5g}, {fmode}\n"

        # check for shm and make if needed
        try:
            # ydprint(defname, "g.shm: ", g.shm)
            if g.shm is None:
                g.shm = shared_memory.SharedMemory(name=g.DMMshmName, create=True, size=50)     # type(g.shm): <class 'memoryview'> print(type(g.shm.buf))
                print()
                ydprint(defname, "g.shm: ", g.shm)
        except Exception as e:
            exceptPrint(e, "create shared-mem issue")

        try:
            bdataline                   = dataline.encode("ascii")
            g.shm.buf[0:len(bdataline)] = bdataline

            # check by reading back from memory
            if g.verify:
                buffer = bytes(g.shm.buf)
                print("Verify:", (buffer.decode("ascii", errors = "ignore").replace("\0", "").strip()))

        except Exception as e:
            exceptPrint(e, "shared mem buffer writing/reading")


##################################################################################################################################################

if __name__ == "__main__":

    defname = __name__ + ": "

    try:
        setup_success = False
        resp = main()
        if resp:
            setup_success = BTsetupDMM()
            while setup_success:
                if g.counter % 300 == 0: print("\nwaiting for data ...", end="")
                g.counter += 1
                time.sleep(0.01)

    except KeyboardInterrupt:
        dprint()
        dprint(defname, "Exit by CTRL-C")
        print(f"{longstime()} {defname}Disconnecting BDM: ", end=" ", flush=True)
        try:
            if g.peripheral is not None:
                 g.peripheral.disconnect()
            print("Done")
        except Exception as e:
            exceptPrint(e, "on disconnection of Bluetooth device: BDM")

    finally:
        if g.saveflag == "MEM":
            if g.shm is not None :
                try:                    g.shm.close()
                except Exception as e:  exceptPrint(e, "shm.close()")
                try:                    g.shm.unlink()
                except Exception as e:  exceptPrint(e, "shm.unlink()")
            else:
                if setup_success:      print("ATTENTION: shm is None!")

        try:
            if os.path.exists(g.filename): os.remove(g.filename)
        except Exception as e:
            exceptPrint(e, f"Failure deleting Bluetooth Data File '{g.filename}'")


##################################################################################################################################################
##################################################################################################################################################
##################################################################################################################################################
#
# following is from gsup_utils.py
#

def DMMCALL(MODEL, PORT=""):
    """Read Values from DMM Multimeter Voltcraft VC850, OW18E by
    using in Formula interpreter, e.g.:  DMMCALL("OW18E_FILE_2")
    """

    if   MODEL == "VC850":     return getVC850Value()              # Voltcraft VC850 with serial interface

    elif MODEL == "OW18E":     return getOW18EValue("any")     # any device which identifies itself with 'BDM'
    elif MODEL == "OW18E_1":   return getOW18EValue("#1")      # my OW18E #1
    elif MODEL == "OW18E_2":   return getOW18EValue("#2")      # my OW18E #2

    else:                      return g.NAN


def getOW18EValue(device="any"):
    """get a single value from FS file saved by the code DMM_FILE.py"""
    # currently supported: Voltage, Frequency, Duty Cycle

    ostart   = time.time()
    defname  = "getOW18EValue: "

    # if   device == "any": filename = g.DMMDataFile               # default: ".dmmOW18E.data"
    # elif device == "#1":  filename = g.DMMDataFile + device      #
    # elif device == "#2":  filename = g.DMMDataFile + device      #

    val             = g.DMMvalue
    unit            = g.DMMunit
    g.DMMvalue      = g.NAN
    g.DMMunit       = "<empty>"
    g.Bluetoothdur  = round(1000 * (time.time() - ostart), 3)

    rdprint(defname, f"val: {val:5.3f} {unit:10s}  Dur:{g.Bluetoothdur:5.3f} ms" )

    return val


# def getOW18EValue(device="any"):
#     """get a single value from FS file saved by the code DMM_FILE.py"""
#     # currently supported: Voltage, Frequency, Duty Cycle
#     # dur is 0.45 ms, marginally slower than via memory with 0.44 ms

#     ostart   = time.time()
#     defname  = "getOW18EValue: "

#     if   device == "any": filename = g.DMMDataFile               # default: ".dmmOW18E.data"
#     elif device == "#1":  filename = g.DMMDataFile + device      #
#     elif device == "#2":  filename = g.DMMDataFile + device      #

#     try:
#         # read file, then remove it
#         if os.path.exists(filename):
#             with open(filename, "r") as fd:
#                 rawdata = fd.readline().strip()
#             os.remove(filename)
#         else:
#             rawdata = f"DMM DataFile {filename} missing"

#     except Exception as e:
#         exceptPrint(e, defname + "Cannot open DMM data file")
#         rawdata = "Exception - Cannot open DMM data file"
#         unit    = "Exception - Cannot open DMM data file"
#         val     = g.NAN

#     else:
#         # file was read successfully
#         rawvals = rawdata.split(",")
#         # at least 3 entries: DateTime, Value, Unit
#         # like: 2024-11-27 13:18:06.350, 2.962, DC_VOLTS
#         if len(rawvals) >= 3:
#             unit        = rawvals[2].strip()
#             try:    val = float(rawvals[1])
#             except: val = g.NAN
#         else:
#             unit = "NoUnit"
#             val  = g.NAN

#     g.Bluetoothdur = round(1000 * (time.time() - ostart), 3)
#     if np.isnan(val):  rdprint(defname, f"val: {val:5.3f} {unit:10s}  Dur:{g.Bluetoothdur:5.3f} ms  Raw: '{rawdata}'" )
#     else:              cdprint(defname, f"val: {val:5.3f} {unit:10s}  Dur:{g.Bluetoothdur:5.3f} ms  Raw: '{rawdata}'" )

#     return val


# def getOW18EValueMEM(device="any"):
#     """get a single value from in-memory saved data by the OWON OW18E DMM with code DMM_MEM.py"""
#     # currently supported: Voltage, Frequency, Duty
#     # dur is 0.44 ms, marginally faster than via File system with 0.45 ms

#     from multiprocessing import shared_memory

#     #########################################################################################################
#     def getBuffer(DMMshmName):

#         defname = "getBuffer: "
#         try:
#             DMMshm        = shared_memory.SharedMemory(name=DMMshmName, create=False)   # works ok
#             rawbuffer     = bytes(DMMshm.buf)                                           # has 50 Bytes; filled up with '\x00'
#             DMMshm.buf[0] = 0                                                           # reset content to "empty"
#             # DMMshm.close()                                                              # close shared mem, but do NOT unlink
#         except Exception as e:
#             exceptPrint(e, defname + "FAILURE getting shared memory content")
#             rawbuffer = b"NoData"
#             DMMshm    = None

#         return DMMshmName, rawbuffer, DMMshm, str(DMMshm)
#     #########################################################################################################

#     ostart  = time.time()
#     defname = "getOW18EValueMEM: "
#     val     = g.NAN
#     unit    = "NoData"

#     # Name for shared memory used for DMM must be same as used in DMM_OWON.py
#     if   device == "any":  name, rawbuffer, g.DMMshm0, shmCfg = getBuffer("ow18e")
#     elif device == "#1":   name, rawbuffer, g.DMMshm1, shmCfg = getBuffer("ow18e#1")
#     elif device == "#2":   name, rawbuffer, g.DMMshm2, shmCfg = getBuffer("ow18e#2")
#     else:                  return g.NAN

#     clipbuffer = rawbuffer.rstrip(b"\x00")                                  # eliminate trailing \x00
#     sbuffer    = clipbuffer.decode("ascii", errors = "ignore").strip()      # decode
#     vals       = sbuffer.split(",")
#     if len(vals) > 1:
#         try:
#             vals = sbuffer.split(",")
#             unit = vals[2].strip()
#             try:    val = float(vals[1])
#             except: val = g.NAN
#         except Exception as e:
#             exceptPrint(e, defname)

#     g.Bluetoothdur = round(1000 * (time.time() - ostart), 3)
#     mdprint(defname, f" val: {val:5.3f} {unit:10s}  Dur:{g.Bluetoothdur:5.3f} ms  Name: '{name}'  shm: {shmCfg}  Raw: {rawbuffer}" )

#     return val


# not in use; keep
def getOW18EValueCLI():
    """Query the OWON OW18E DMM via Bluetooth using owon_multi_cli code for a single Value"""

    # start with cmd: owon_multi_cli -a A6:C0:80:E3:85:9D -t ow18e

    defname  = "getOW18EValueCLI: "

    bstart      = time.time()
    scmd        = ["gtools/u3owon_multi_cli", '-a', 'A6:C0:80:E3:85:9D', '-t', 'ow18e']
    try:
        if g.DMMproc is None:
            g.DMMproc = subprocess.Popen(scmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=False)

    except Exception as e:
        emsg = defname + f"Bluetooth FAILURE: "
        exceptPrint(e, emsg)
        # QueuePrint(emsg + str(e))
        value = g.NAN
        time.sleep(0.1)

    else:
        dstart = time.time()
        while True:
            dout = g.DMMproc.stdout.readline()[:-1]             # assuming CR still present, but LF is gone
            data = dout.strip().split(" ")
            print(f"{str(time.time()):19s}  out: {dout}")

            try:
                if abs(time.time() - float(data[0]) ) < 0.5:    # less than 500 ms apart
                    value = float(data[1])
                    break
            except:
                value = g.NAN
                break

            if (time.time() - dstart) > 3:  # try no longer than 3 sec
                break

    bdur = 1000 * (time.time() - bstart)
    dprint(defname,  f"Dur:{bdur:0.1f} ms  out: '{dout}'   Volt: {value:0.3f}")

    g.Bluetoothdur = round(bdur, 3)

    return value



def getVC850Value():
    """Query the Voltcraft VC850 DMM via RS232 Serial for a single Value"""

    rstart   = time.time()

    defname  = "getVC850Value: "

    try:
        port     = "/dev/ttyUSB0"
        # port     = "/dev/ttyUSB1"
        rtimeout = 1.0
        wtimeout = 1.0
        prefix   = ""
        unit     = "NoData"
        brec     = "NoData"
        TOflag   = False

        # sercall  = time.time()
        # opening takes 0.2 ... 2.0 ms, mostly 0.8 ms
        with serial.Serial( port          = port,
                            baudrate      = 2400,
                            timeout       = rtimeout,
                            write_timeout = wtimeout,
                            ) as RPser:
            # sdur   = time.time() - sercall                      # in sec
            # ydprint(defname + f"opening serial: {sdur * 1000:0.1f} ms")

            try:
                # ydprint(defname, "Begin waiiting")
                sercall = time.time()
                while True:            # kann bis zu mehrere 100 ms dauern! sammelt alle records; mid 14 in einem record
                    if RPser.in_waiting >= 14: break
                    waitperiod = 0.8
                    if time.time() - sercall > waitperiod:           # exit after no data within waitperiod sec
                        rdprint(defname, f"Exiting as no data within last {waitperiod} sec")
                        return g.NAN
                    time.sleep(0.010)

                rawbrec = RPser.read(RPser.in_waiting)      # read all from the pipeline
                index   = rawbrec.rindex(b"\n") + 1         # find the last LF
                brec    = rawbrec[index - 14 : index]       # get the 14 chars up to the last LF
                # rdprint(defname, "rawbrec: ", rawbrec, "  index:   ", index, "  brec:    ", brec)

            except Exception as e:
                sdur   = time.time() - sercall                      # in sec
                TOflag = True if sdur >= rtimeout else False        # True on Timeout
                TOmsg = "Timeout " if TOflag else " "
                exceptPrint(e, defname + f"FAILURE {TOmsg}reading serial ")

            sdur   = time.time() - sercall                      # in sec
            # rdprint(defname + f"reading serial: {sdur * 1000:0.1f} ms")

            ### the '+' sign is missing when brec is only 13 long
            ### fix by adding a blank at the beginning; odd, so far always working!
            if (len(brec) == 13) and not (brec[0] in (b"+", b"-")):
                brec = b" " + brec

            rdur = 1000 * (time.time() - rstart)                  # in ms

            if (len(brec) == 14) and (brec[5] == 0x20):           # must make sure to have a blank char at pos 5
                try:
                    val = float(brec[0:5].decode("ascii", errors='replace'))
                    if   brec[6] == 0x31:       val /= 1000       # == 1
                    elif brec[6] == 0x32:       val /= 100        # == 2
                    elif brec[6] == 0x33:       val /= 10         # == 3
                    elif brec[6] == 0x34:       val /= 10         # == 4
                except:
                    val = g.PINF

                if   (brec[9] & 0x80) != 0:     prefix = "µ"
                elif (brec[9] & 0x40) != 0:     prefix = "m"
                elif (brec[9] & 0x20) != 0:     prefix = "k"
                elif (brec[9] & 0x20) != 0:     prefix = "M"
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

            else:
                msgTO = "Response with incorrect format - " if rdur <= rtimeout * 1000 else "Timeout @Reading - "
                rdprint(defname, f"{TDEFAULT} {TYELLOW}{msgTO} brec:{brec}  len:{len(brec)} (expct:14)")
                val = g.NAN

    except Exception as e:
        emsg = f"FAILURE getting VC850 values; bred: {rawbrec}"
        exceptPrint(e, defname + emsg)
        val = g.NAN

    rdur = round(1000 * (time.time() - rstart), 3)
    dprint(defname, f"    val: {val:10.3f} {prefix + unit:10s}  Dur:{rdur:7.3f} ms  Raw: {rawbrec} len:{len(rawbrec)} (expct:14)")

    return val      # float value

