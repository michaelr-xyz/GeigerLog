#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Simul_GEMF.py - GeigerLog's Simulator for a GQ EMF device

use with GeigerLog to simulate responses of a GQ EMF Device. See more in
the header of file gdev_gemf.py located in the GeigerLog folder.

- MUST start as SUDO (!):
- pyserial must have been installed as root:   sudo python -m pip install -U pyserial
- socat must have been installed as root:      sudo apt install socat
- GeigerLog must have been started with command: 'simulgemf'
- GeigerLog's configuration file 'custom.cfg' must contain usbport setting:
        [GEMF_Device]
        GEMF_Activation = yes
        # NOTE:    for a simulation use: /dev/ttyS90
        GEMF_usbport = /dev/ttyS90

The communication between GeigerLog and the Pseudo device is logged into file
Simul_GEMF.log
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


# check ports with:  stty -F /dev/pts/5
#                    stty -F /dev/ttyS90
#
# cstopb=<bool>  Sets two stop bits, rather than one.    # How to use?
#
# socat -d -d -d -d tcp-listen:4141,reuseaddr,fork file:/dev/ttyUSB0,nonblock,cs8,b9600,cstopb=0,raw,echo=0
# socat -d -d  pty,b9600,cs8,raw,echo=0    # cs8 ok, cs7 geht nicht
#
# use sudo to make links
    # sudo socat -d -d  pty,b9600,raw,echo=0,link=/dev/ttyS90    pty,b9600,raw,echo=0,link=/dev/ttyS91
# but then it needs these commands:
#   sudo chmod 777 /dev/ttyS91
#   sudo chmod 777 /dev/ttyS90
# obgleich das schon erfüllt sein sollte:
#   lrwxrwxrwx 1 root root       10 Sep  7 11:56 /dev/ttyS90 -> /dev/pts/2
#   lrwxrwxrwx 1 root root       10 Sep  7 11:56 /dev/ttyS91 -> /dev/pts/4


__author__          = "ullix"
__copyright__       = "Copyright 2016 - 2025"
__credits__         = [""]
__license__         = "GPL3"
__version__         = "1.2"

import sys, os, io, time
import datetime                  as dt
import subprocess
import serial                               # serial port
import serial.tools.list_ports              # allows listing of serial ports
import numpy                     as np      # for Poisson values
import struct
import getopt                               # parsing command line options


TDEFAULT            = '\033[0m'             # default, i.e greyish
TRED                = '\033[91m'            # red
BGREEN              = '\033[92m'            # light green
TYELLOW             = '\033[93m'            # yellow
TBLUE               = '\033[94m'            # blue (dark)
TMAGENTA            = '\033[95m'            # magenta
TCYAN               = '\033[96m'            # cyan
TWHITE              = '\033[97m'            # high intensity white

INVMAGENTA          = '\033[45m'            # invers magenta looks ok
INVBOLDMAGENTA      = '\033[45;1m'          # invers magenta with bold white

# BOLDxyz are brighter colors
BRED                = '\033[91;1m'          # bold red
BGREEN              = '\033[92;1m'          # bold green
BYELLOW             = '\033[93;1m'          # bold yellow
BBLUE               = '\033[94;1m'          # bold blue
BMAGENTA            = '\033[95;1m'          # bold magenta
BCYAN               = '\033[96;1m'          # bold cyan
BWHITE              = '\033[97;1m'          # bold white


class globalvars():
    NAN                 = float("nan")
    GEMF_Version        = "EMF390"          # "GQ-EMF390Re 1.00"
    GEMF_cfg            = None
    GEMF_powerIsON      = True

    helpOptions         = """
            Usage:  Simul_GEMF.py [Options]

            Start:  Simul_GEMF.py
            Stop:   CTRL-C

            Options:
                -h, --help          Show this help and exit
                -V, --Version       Show version status and exit
                -E, --EMF           Set the device name (EMF-390)                                   Default: EMF-390

            Example: starting Simul_GEMF.py with options:
                                 Simul_GEMF.py --EMF=EMF-390
            or with same result: Simul_GEMF.py -E EMF-390
    """

# instantiate class vars
g = globalvars

### function code ##############################################################################################################

def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?

    print(longstime(), "EXCEPTION: '{}' in file: '{}' in line {}".format(e, fname, exc_tb.tb_lineno))
    if srcinfo > "": print(longstime(), srcinfo)


def init():
    """Init the Simul_GEMF device"""

    print("\n------------------------ Simul_GEMF.py -------------------------------")
    print("File:                 ", __file__)

    # parse command line options
    try:
        # sys.argv[0] is progname
        opts, args = getopt.getopt(sys.argv[1:], "hdVE:", ["help", "debug", "Version", "EMF="])
    except getopt.GetoptError as e :
        # print info like "option -x not recognized", then exit
        msg = "For Help use: './Simul_GEMF.py -h'"
        exceptPrint(e, msg)
        return 1

    # process the options
    for opt, optval in opts:

        if   opt in ("-h", "--help"):                       # show the help info
            print(g.helpOptions)
            return 1

        elif opt in ("-V", "--Version"):                    # show the Simul_WiFiClient.py version
            print("Simul_GEMF.py Version:", __version__)
            return 1

        elif opt in ("-E", "--EMF"):                        # set the device name
            g.GEMF_Version = optval.strip()


    print("Executing subprocess.Popen with socat command: ")

    # mypopen = subprocess.Popen([
    #                             "socat",
    #                             '-d',
    #                             '-d',
    #                             'pty,b4000000,CSIZE=CS8,PARENB=0,PARODD=0,raw,echo=0,link=/dev/ttyS90',
    #                             'pty,b4000000,CSIZE=CS8,PARENB=0,PARODD=0,raw,echo=0,link=/dev/ttyS91'
    #                             ])

    mypopen = subprocess.Popen([
                                "socat",
                                'pty,link=/dev/ttyS90',
                                'pty,link=/dev/ttyS91'
                                ])

    print("   subprocess.Popen: mypopen:           ", mypopen)
    print("   subprocess.Popen: mypopen.args:      ", mypopen.args)
    print("   subprocess.Popen: mypopen.pid:       ", mypopen.pid)

    time.sleep(0.005) # socat needs ~0.001 sec to complete its action; but then keeps running

    print("\nFound permissions:")
    try:
        print("   /dev/ttyS90: ", oct(os.stat('/dev/ttyS90')[0]))
        print("   /dev/ttyS91: ", oct(os.stat('/dev/ttyS91')[0]))
    except Exception as e:
        print("Listing permissions failed with Exception: ", e)
        print()
        print("??????????   FAILURE - Forgot to start program with 'sudo'  ???????????\n\n")
        print()
        sys.exit()

    print("\nChanging permission with os.chmod on: ", '/dev/ttyS90', '/dev/ttyS91', 'to 0o777')
    start = time.time()
    while True:
        try:
            os.chmod('/dev/ttyS90', 0o777)
            os.chmod('/dev/ttyS91', 0o777)
            break
        except:
            pass
    print("   success after {:0.3f} ms".format((time.time() - start) * 1000))

    print("\nChanged permissions:")
    print("   /dev/ttyS90: ", oct(os.stat('/dev/ttyS90')[0]))
    print("   /dev/ttyS91: ", oct(os.stat('/dev/ttyS91')[0]))

    print("\nList of Ports found on system (including linked ports): ")
    lps = serial.tools.list_ports.comports(include_links=True)
    lps.sort()
    for lp in lps:  print(" ", lp)
    print()


    print("Config:")
    print("   EMF:               ", g.GEMF_Version)
    print("   Power is ON:       ", g.GEMF_powerIsON)
    print()

    g.GEMF_Version    = getVersion()
    g.GEMF_cfg        = getCFG()

    print()
    print("EMF Version found:")
    print("   Version:           ", g.GEMF_Version)
    print("   CFG: len:          ", len(g.GEMF_cfg))
    print("   CFG:")
    print(g.GEMF_cfg)
    print()

    start           = time.time()
    counter         = -1
    portsim         = "/dev/ttyS91"

    # create serial connection
    # for use of spy see: https://pyserial.readthedocs.io/en/latest/url_handlers.html
    # wser        = serial.serial_for_url("spy://{}?file=Simul_GEMF.log".format(portsim), baudrate=0, timeout=0.1, bytesize=8, parity="N")
    wser        = serial.Serial(portsim, baudrate=115200, timeout=0.05)
    print("\nSerial Instance: ", wser)
    print()
    getSPIR(b"<SPIR\x00\x00\x00\x00\x00>>")
    print("Looping:")

    while True:
        wstart   = time.time()
        counter += 1

        brec = b""
        while True:
            cnt = wser.in_waiting
            if cnt > 0:     brec += wser.read(cnt)
            else:           break

        if brec > b"":
            # print(" ")
            print("\nReceived : {:30s}  on port '{}'".format(str(brec), portsim ))
            print("           ", end="")

            counter = 0

            if   brec.startswith(b"<GETEF>>")                    : tag = getValues("EF")
            elif brec.startswith(b"<GETEMF>>")                   : tag = getValues("EMF")
            elif brec.startswith(b"<GETRFTOTALDENSITY>>")        : tag = getValues("RF")
            elif brec.startswith(b"<GETRFTOTALDENSITYPEAK>>")    : tag = getValues("XF")
            elif brec.startswith(b"<GETVER>>")                   : tag = getVersion()
            elif brec.startswith(b"<GETCFG>>")                   : tag = getCFG()
            elif brec.startswith(b"<GETDATETIME>>")              : tag = getDatetime()        # return the counter's Datetime
            elif brec.startswith(b'<POWERON>>')                  : tag = setPower("ON")
            elif brec.startswith(b'<POWEROFF>>')                 : tag = setPower("OFF")
            elif brec.startswith(b'<GETVOLT>>')                  : tag = b"3.52 Volts"        # as defined in the doc
            elif brec.startswith(b'<<GETGYRO>>')                 : tag = b"1234567"           # 7 bytes per doc
            elif brec.startswith(b"<GETSERIAL>>")                : tag = b"FAKE SN"
            elif brec.startswith(b"<DSID>>")                     : tag = b"FAKE DSID"
            elif brec.startswith(b"<CFGUPDATE>>")                : tag = b"\xaa"
            elif brec.startswith(b"<SETDATETIME")                : tag = setDatetime(brec)    # set the counter's Datetime (has no effect here)
            elif brec.startswith(b'<SPIR')                       : tag = getSPIR(brec)
            elif brec.startswith(b"<ECFG>>")                     : tag = b"\xaa"
            elif brec.startswith(b"<WCFG")                       : tag = b"\xaa"
            elif brec.startswith(b"<GetSPISA>>")                 : tag = b"\x01\x04\x6a\xaa"  # dummy answer

            else                                                 : tag = b"SIMUL UNDEFINED"

            wser.write(tag)
            if brec.startswith(b'<SPIR'): print("Answered : {} \n          NOTE: all following FF removed".format(tag.rstrip(b"\xFF")))
            else:                         print("Answered : {}".format(tag.rstrip(b"\xFF")))
            print("Exec in  : {:0.1f} ms".format(1000 * (time.time() - wstart) ))

        else:
            loopcount = 30000
            if counter % loopcount == 0 and counter > 0:
                dur = 1000 * (time.time() - start)
                print("   Loops: {} in {:0.1f} ms per loop".format(loopcount,  dur / loopcount), flush=True)
                start = time.time()
            else:
                print("\033[#D", end="", flush=True) # printing ANSI codes  https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797

        time.sleep(0.001) # 1 ms resolution



def setPower(newpowerstate):
    """Set Power to ON or OFF; return nothing"""

    defname = "setPower: "
    print(defname, "New Powerstate: ", newpowerstate)

    if newpowerstate == "ON":  g.GEMF_powerIsON = True
    else:                      g.GEMF_powerIsON = False

    print("getCFG: ", getCFG())

    return b""


def getVersion():
    """Available GEMF version"""
    # GEMF_version = b"GQ-EMF380Re 1.00"

    if   g.GEMF_Version == "EMF390":   GEMFdevice = b"GQ-EMF390Re 1.00"
    else:                              GEMFdevice = b"GQ-EMF380Re 1.00"

    return GEMFdevice


def getCFG():
    """CFG from counter; by version"""
    # 256 == configsize

    defname = "getCFG: "

    # print(" "*10, defname, "g.GEMF_powerIsON: ", g.GEMF_powerIsON)
    # print(defname, "g.GEMF_powerIsON: ", g.GEMF_powerIsON)

    if 1 or b"GQ-EMF380Re 1.00" in g.GEMF_Version :
        # First 0 indicates that power is ON
        cfgEMF390 = [ 0,   0,   1,   1, 255,   1,  10, 255,  10,   1,   0,   1,  10,  30, 216,   3,   1, 255, 255, 255,
                    255, 255, 255, 255,  10,   2,   1,   1,   1,   0,   1,   0,   0,   0,   1,   0,   0,   0,   0,   0,
                      0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0, 100,
                    100,   1,   2,   0, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,   0,   0,   0,   0,   0,   0,
                      0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   1, 244,   1, 244,   1, 244,
                      1, 244,   1, 244,   1, 244,   1, 244,   1, 244,   1, 244,   1, 244,   0,   0,   0,   0, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255,
                    255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255]

        if g.GEMF_powerIsON: cfg = [0]    # power is ON
        else:                cfg = [1]    # power is OFF
        cfg += cfgEMF390[1:]
        # cfg  = bytes(cfg)

    # return cfg
    return bytes(cfg)


def getSPIR(brec):

    defname = f"getSPIR: "
    print(defname, brec, " ".join(f"{s:02X}" for s in brec))

    demospir = b"""55 AA 12 09 06 0B 0B 1E AA 55 02 14 71 AE 9C 3D 42 8C 96 49
AA 55 02 74 06 D0 90 3D 42 8C 96 49 AA 55 02 15 0B F3 74 3D
42 8C 96 49 AA 55 02 16 0D 69 85 3D 42 8C 96 49 AA 55 02 17
71 AE 9C 3D 4D 87 BD 49 AA 55 02 18 9D D1 B5 3D 4D 87 BD 49
AA 55 02 54 DF 02 60 3D 4D 87 BD 49 AA 55 02 14 06 D0 90 3D
4D 87 BD 49 AA 55 02 19 06 D0 90 3D 4D 87 BD 49 AA 55 02 1a
4E 04 A9 3D 4D 87 BD 49 AA 55 02 1B DF 02 60 3D 4D 87 BD 49
AA 55 02 34 0D 69 85 3D 3F 2B 6F 49 AA 55 02 1C 0D 69 85 3D
3F 2B 6F 49 AA 55 02 1D 71 AE 9C 3D 3F 2B 6F 49 AA 55 02 1E
0D 69 85 3D 6F 49 6F 49"""

    spirdata = demospir.replace(b"\n", b" ").split(b" ")
    # print(spirdata)

    bspirdata = b"".join(bytes([int(v, 16)]) for v in spirdata)
    # print(bspirdata)

    print(defname, " ".join(f"{s:3d}" for s in bspirdata[:12]))
    bspirdata = bspirdata [0:6] + bytes([bspirdata[6] + 1]) + bspirdata [7:]
    print(defname, " ".join(f"{s:3d}" for s in bspirdata[:12]))

    # Command: <SPIR[hi][mi][lo][b1][b0]>>
    #          01234 5   6   7   8   9  AB
    # n4k pages of 4k each:
    n4k = 3
    if brec[6] >  (n4k * 4096 / 256):
        bspirdata = b""  # if SPIR address is greater than 00 10 00 then send FF only

    newb = bspirdata + b"\xFF" * (4096 - len(bspirdata))
    print(newb[:100])

    return newb


def getValues(vtype):

    defname = f"getValues({vtype}): "

    if   vtype == "EF":         bval = b'EF = 163.7 V/m SIMUL'
    elif vtype == "EMF":        bval = b'EMF = 3.6 mG SIMUL'
    elif vtype == "RF":         bval = b'1234.5 mW/m2 (0.24-8G) SIMUL'
    elif vtype == "XF":         bval = b'4886.6 mW/m2 (0.24-8G Peak) SIMUL'

    print(defname, "bval: {} --> {}".format(bval, ", ".join(str(b) for b in bval)))

    return bval


def getDatetime():
    """return a Datetime as the counter would"""

    defname = "getDatetime: "

    # convert Computer DateTime to byte sequence format needed by counter
    timelocal     = list(time.localtime())                          # timelocal: 2018-04-19 13:02:50 --> [2018, 4, 19, 13, 2, 50, 3, 109, 1]
    print(defname, "timelocal: ", timelocal)
    timelocal[0] -= 2000
    dtrec         = dt.datetime(timelocal[0] + 2000, timelocal[1], timelocal[2], timelocal[3], timelocal[4], timelocal[5])

    btimelocal    = b''
    for i in range(0, 6):  btimelocal += bytes([timelocal[i]])
    print(defname, "creating Datetime:  now:", timelocal[:6], ", coded:", btimelocal, "  ", dtrec)

    return btimelocal + b"\xaa"


def setDatetime(dt):
    """send the Datetime to Simul decice as created by GeigerLog; does not change anything"""

    defname = "setDatetime: "
    print(defname, "receiving: ", dt, end="")

    return b"\xaa"


def clearTerminal():
    """clear the terminal"""

    os.system('cls' if os.name == 'nt' else 'clear')
    # print("os.name: ", os.name) # os.name:  'posix' (on Linux)


### end function code ################################################################################################

if __name__ == '__main__':

    try:
        clearTerminal()
        init()

    except KeyboardInterrupt:
        print()
        print("Exit by CTRL-C")
        print()
        os._exit(0)

