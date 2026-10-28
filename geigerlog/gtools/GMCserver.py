#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
GMCserver -  GeigerLog Data Server for GMC Geiger Counter
                A Python webserver running as a GeigerLog WiFiServer device
                enabling various external devices to send data by WiFi.

                It responds with 16 vars of random values from a Poisson distribution
                like: 12, 0, 117, 2, 207, 2, 309, 3, 12, 988, 79, 48, ...

Start with: path/to/GMCserver.py
Stop  with: CTRL-C

Requires Python 3.7 or later (threading HTTP-Server)
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


###############################################################################
####################       CUSTOMIZE HERE        ##############################
#
## Port Number
#  On which Port number shall the WiFiServer listen
#  Options:      1024 ... 65535
#  Default     = 7777
WiFiServerPort = 7777

## Display name
DisplayName    = "GMCServer"

## Filename of log file
Logfile        = ""                             # if left empty a log file will NOT be written
# Logfile      = "GMCserver.log"                # the log file will be in the directory from
                                                # where you started GMCserver

## GMC_ID:
# Specifying a GMC Device ID forces GeigerLog to connect only when that specified GMC
# device is present. The specification can be a version of the model name given at any
# length (GMC-5, GMC-500, GMC-500+Re 1.27) and can in addition be followed by the
# serial number of the counter.
#
# Examples:
#   GMC_ID = "None", "None"       # use the first found GMC counter whatever the model and serial No
#   GMC_ID = "GMC-300", "None"    # use the first found GMC-300 counter whatever the serial No
#   GMC_ID = "GMC-5", "12774E"    # use the first found GMC-500 or GMC-510 counter but only when
#                                 # its serial No begins with '12774E'
# GMC-800:  12004E*
# GMC-300s: F7F4C3*
#
# Options:      < "<Model>" | "None",  "<Serial Number>" | "None" >
# NOTE: if a Serial Number is given, then a Model MUST also be given!
# like:         GMC_ID = "GMC-300", "None"
#               GMC_ID = "GMC-800", "12004E"
#
# Default     = "None", "None"
# cGMC_ID       = "None", "None"
cGMC_ID       = "GMC-3", "None"


####################   END of CUSTOMIZATION   ##################################
################## NO USER CHANGES BELOW THIS LINE ! ###########################


import sys, os, io, time                        # basic modules
import datetime             as dt               # needed for longstime()
import traceback                                # see exceptPrint()
import platform                                 # to find OS
import socket                                   # finding IP Adress
import http.server                              # web server
import threading                                # higher-level threading interfaces
import numpy                as np               # for fudging some numbers

import serial                                   # required for GMC counter
import serial.tools.list_ports                  # required for serial ports

__author__                  = "ullix"
__copyright__               = "Copyright 2016 - 2025"
__credits__                 = [""]
__license__                 = "GPL3"
__version__                 = "2.0"                       # of this script
__script__                  = os.path.basename(__file__)  # exclude the path, give just the filename


# colors for terminal
TDEFAULT                    = '\033[0m'             # default, i.e greyish
TYELLOW                     = '\033[93m'            # yellow
INVYELLOW                   = '\033[90;1;103m'      # black on yellow BG
BRED                        = '\033[91;1m'          # bold red

# if "WINDOWS" in platform.platform().upper():    # Windows does not support terminal colors
#     TDEFAULT              = ""
#     TYELLOW               = ""



class GlobalVars():
    # Default settings
    NAN                     = float('nan')          # 'not-a-number'; used as 'missing value'
    xprintcounter           = 0                     # the count of dprint, dprint, dprint, xdprint commands

    # WiFi Server
    dogetmsg                = ""                    # web server msg
    color                   = TDEFAULT              # used also as flag for color printout in Linux terminal
    index                   = 0                     # number of WiFi calls
    WiFiServer              = None                  # the HTTP Web server
    WiFiServerThread        = None                  # thread handle
    WiFiServerThreadStop    = None                  # flag to stop thread

    LastCall                = 0                     # time of last data call
    LastRec                 = ""                    # last 'lastrec'

    iconGeigerLogWeb        = None                  # holds the icon svg code

    GMCPortsList            = []                    # List with all GMC matching ports; to handle multiple GMCs
    GMCser                  = None                  # pointer to Serial for GMC
    GMCport                 = "auto"                # this program does NOT allow manual settings!
    GMCbaudrate             = "auto"                # this program does NOT allow manual settings!
    GMCtimeout              = "auto"                # this program does NOT allow manual settings!
    GMCtimeoutR             = "auto"                # this program does NOT allow manual settings!
    GMCtimeoutW             = "auto"                # this program does NOT allow manual settings!
    GMC_ID                  = cGMC_ID[0],cGMC_ID[1].replace(" ", "") # remove blanks from serial no

    GMCbytes                = 4                     # 2 or 4 bytes
    GMCtubeCount            = 1                     # 1 or 2
    GMCcounterversion       = ""                    # to be filled with e.g.: GMC-800Re1.18
    GMCvariables            = ""                    # fixed to: CPM1st, CPS1st, (plus for 2-tube counter: CPM2nd, CPS2nd)
    GMCSerialNumber         = "None"                # the counter's serial number
    GMCmaxdur               = 0                     # longest duration of a GMC call


### make defaults global
g = GlobalVars

##############################################################################################################



def gd(name):
    """gt the defname in proper format from 'defname = gd(sys._getframe().f_code.co_name)'"""
    return f"{name + ': ':20s}"


def stime():
    """Return current time as YYYY-MM-DD HH:MM:SS"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S") # sec resolution


def longstime():
    """Return current time as YYYY-MM-DD HH:MM:SS.mmm, (mmm = millisec)"""

    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # ms resolution


def commonPrint(ptype, *args):
    """Printing function
    ptype : DEBUG, ERROR, RED, YELLOW
    args  : anything to be printed, print args as single line
    return: nothing
    """

    g.xprintcounter += 1

    tag = f"{longstime():23s}  {g.xprintcounter:.>6d} "

    for arg in args: tag += str(arg)
    if   ptype == "ERROR":      print(TYELLOW   + tag + TDEFAULT)
    elif ptype == "RED":        print(BRED      + tag + TDEFAULT)
    elif ptype == "YELLOW":     print(TYELLOW   + tag + TDEFAULT)
    elif ptype == "INVYELLOW":  print(INVYELLOW + tag + TDEFAULT)
    else:                       print(tag)                          # ptype=DEBUG


def dprint  (*args):    commonPrint("DEBUG",        *args)
def edprint (*args):    commonPrint("ERROR",        *args)
def rdprint (*args):    commonPrint("RED",          *args)
def ydprint (*args):    commonPrint("YELLOW",       *args)
def iydprint(*args):    commonPrint("INVYELLOW",    *args)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname                     = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # the filename

    dprint(TYELLOW + f"EXCEPTION: {srcinfo} ({e}) in file: {fname} in line: {exc_tb.tb_lineno}", TDEFAULT)
    # dprint(traceback.format_exc())


def getMyIP():
    """get the IP of the computer running this program"""

    defname = gd(sys._getframe().f_code.co_name)

    st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        st.connect(('10.255.255.255', 1))
        IP = st.getsockname()[0]
    except Exception as e:
        IP = '127.0.0.1'
        srcinfo = "Bad socket connect, IP:" + IP
        exceptPrint(defname + str(e), srcinfo)
    finally:
        st.close()

    return IP


def initWiFiServer():
    """Initialize WiFiServer"""

    defname = gd(sys._getframe().f_code.co_name)

    g.iconGeigerLogWeb = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00F\x00\x00\x00F\x08\x06\x00\x00\x00q.\xe2\x84\x00\x00\txeXIfII*\x00\x08\x00\x00\x00\n\x00\x0b\x00\x02\x00\x0e\x00\x00\x00\x86\x00\x00\x00\x00\x01\t\x00\x01\x00\x00\x00F\x00\x00\x00\x01\x01\t\x00\x01\x00\x00\x00F\x00\x00\x00\x12\x01\t\x00\x01\x00\x00\x00\x01\x00\x00\x00\x1a\x01\t\x00\x01\x00\x00\x00H\x00\x00\x00\x1b\x01\t\x00\x01\x00\x00\x00H\x00\x00\x00(\x01\t\x00\x01\x00\x00\x00\x02\x00\x00\x002\x01\x02\x00\x14\x00\x00\x00\x94\x00\x00\x00\x13\x02\t\x00\x01\x00\x00\x00\x01\x00\x00\x00i\x87\x04\x00\x01\x00\x00\x00\xa8\x00\x00\x00\xf6\x00\x00\x00gThumb 3.12.7\x002025:11:22 16:14:04\x00\x06\x00\x00\x90\x07\x00\x04\x00\x00\x000221\x01\x91\x07\x00\x04\x00\x00\x00\x01\x02\x03\x00\x00\xa0\x07\x00\x04\x00\x00\x000100\x01\xa0\t\x00\x01\x00\x00\x00\x01\x00\x00\x00\x02\xa0\t\x00\x01\x00\x00\x00F\x00\x00\x00\x03\xa0\t\x00\x01\x00\x00\x00F\x00\x00\x00\x00\x00\x00\x00\x06\x00\x03\x01\x03\x00\x01\x00\x00\x00\x06\x00\x00\x00\x1a\x01\t\x00\x01\x00\x00\x00H\x00\x00\x00\x1b\x01\t\x00\x01\x00\x00\x00H\x00\x00\x00(\x01\t\x00\x01\x00\x00\x00\x02\x00\x00\x00\x01\x02\x04\x00\x01\x00\x00\x00D\x01\x00\x00\x02\x02\x04\x00\x01\x00\x00\x004\x08\x00\x00\x00\x00\x00\x00\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x05\x03\x04\x04\x04\x03\x05\x04\x04\x04\x05\x05\x05\x06\x07\x0c\x08\x07\x07\x07\x07\x0f\x0b\x0b\t\x0c\x11\x0f\x12\x12\x11\x0f\x11\x11\x13\x16\x1c\x17\x13\x14\x1a\x15\x11\x11\x18!\x18\x1a\x1d\x1d\x1f\x1f\x1f\x13\x17"$"\x1e$\x1c\x1e\x1f\x1e\xff\xdb\x00C\x01\x05\x05\x05\x07\x06\x07\x0e\x08\x08\x0e\x1e\x14\x11\x14\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\x1e\xff\xc0\x00\x11\x08\x00F\x00F\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1b\x00\x00\x03\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x08\x05\x07\x04\x03\x02\xff\xc4\x009\x10\x00\x01\x03\x03\x01\x05\x04\t\x03\x02\x07\x00\x00\x00\x00\x00\x01\x02\x03\x04\x00\x05\x11\x06\x07\x12!1AQaq\x81\x08\x13\x14"2BR\x91\xb1\x15\xc1\xd1#\xa1\x163Sbs\xa2\xe1\xff\xc4\x00\x1b\x01\x00\x02\x02\x03\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\x03\x04\x01\x06\x07\x02\xff\xc4\x000\x11\x00\x01\x03\x03\x02\x04\x04\x03\t\x00\x00\x00\x00\x00\x00\x00\x01\x00\x02\x03\x04\x05\x11!1\x06\x12q\x812Aa\xb1\x13\x91\xd1\x14\x15"3Qb\xc1\xf0\xf1\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\x8c\xab\xeb\x123\xd2\x9fK1\xdbS\x8b<\x80\xa2$weIDvS\xbc\xb5\x9c\x01O\xd6\x8bs\x16\xe8\xc1\xa6\x80+?\x1b\x98\xe2\xa3\xfcwP\x85\x95m\xd2\xec6\x90\xb9\xce\x17W\xf4 \xe1#\xcf\x99\xad\xb8\xf0\xa2G\x18b3M\xf8$g\xefZvkl\xeb\xc5\xd25\xae\xdb\x19rfIXm\xa6\x93\xcdG\xf6\x1dI\xe8\x05R\xdb=\xd8\x9e\x9d\xb2GjN\xa1i\xbb\xdd\xc8\x80T\x95\x82c\xb4{\x12\x8f\x9b\xc5\\\xfb\x05*\xba^i\xad\xad\x06S\x92v\x03\x7f\xf1X\x82\x99\xf3\x9f\xc3\xb2\x97\x90\x82\xef\x06\xd0\\\xeeJw\xbf\x15\xe3\x99j\x80\xf9(\x91\r\xb0\xb3\xfe\xdd\xc5\x7fn5C\xedCk\xee\xe9\xeb\xdb\xbawDC\xb6\xc7n\x12\xbd\\\x89>\xce\x92\x92\xe0\xe6\x84$``r$\xe7\'8\xe5\xc5\xd7fw{v\xd4t2\xe4jK%\xbaD\x86_Ti)S\x00\xa1D\x00\xa0\xb4\xe7\x8ar\x149\x1e\x04R\xe9\xaf\xb5\x14\xf4\xed\xaa\x96\x9f\x0c?\xbbQ\x9d\x8e1\xfc\xa9\x9bH\xc7\xbc\xb1\xaf\xd7\xa2\x88\xae\xbaa\xc6\xc1v\x02\xcb\xa9\x1cKj\xf8\xbc\x8fZ\\P)QJ\x81\x04\x1c\x10zU\xe1u\xd8\xde\xccm\xed\x99W\x07e@aK\xdd\nz\xe9\xea\xd0\t\xc9\t\x05_\x8c\xf4\xa9\xdf\xd2#E\xe9{n\xa3i\x1a2Jd\xb5\xeciu\xc5&P\x7f}{\xca\x04o\x0e\xb8\x03\x85[\xb7\xdf\xa9\xab\xe4\xf8q\x07w\x1a|\xf2\xa3\x9a\x91\xf0\x8c\xb8\x85\xc5\xa8\xa2\x8av\xaa\xa6\xed\x15\x047\x19s\x96=\xf7\tJ;\x929\xfd\xcf\xe2\x98\xab\xe1ndG\x80\xc3\x03\xe4l\x0f<q\xfe\xf5\xf7\xa1\x0b\xb9z&Z\xa3\xbds\xbe^\x9cBT\xfcf\xdb\x8c\xc9?&\xfe\xf2\x96G\x88H\x1fz\xed;A\xbd+N\xe8\x8b\xc5\xe9\xb3\xfdX\xb1\x16\xa6\xbf\xe4>\xea?\xecEM[\x08\xd7q\xb4^\xa2}\xbb\x9e\xf8\xb5\xdcP\x94>\xb4\x8c\x96V\x92w\\\xc0\xe68\x90q\xc7\x07=*\x81\xda$\x11\xad\xf6as\x89\xa7eG\x9c\xa9l\xa5q\x96\xcb\xa1HqHZU\xbb\xbc8\x0c\xe3\x1cy\x1eu\xcd8\x82\x99\xe2\xee\xd9\'\xfc\xb7\x16\xeb\xe5\x8d2=\xfd\xd3\xba7\x8f\xb3\x90\xcf\x10\xca\x8eT\xa5-eKQZ\xd4r\xa5\x1ed\x9ef\xaa\xcfF\xcbC\x96\xbd\x98G\x90\xf2JWr\x90\xe4\xb0\x0f\xd0p\x84}\xc2s\xe7\\sC\xecsV\xde\xaf\x8d3y\xb5J\xb4[P\xb0d\xbc\xf8\tZ\x929\xa5\t\xceJ\x8f,\xf2\x1c\xf3Tn\xa1\xd5\x1aWF[[j\xe7r\x89\x01\xb6\x1a\x08f*U\xbc\xe9JF\x02R\xd8\xf7\x8f\x00\x052\xe2\x9b\x83*X\xca:c\xce\xe2ryu\xe84\xfe\xe8\xa1\xa0\x84\xb0\x99\x1f\xa0\xf5I~\x94r\x18kfi\x8e\xee\xe9rE\xc1\x90\xd0<\xf2\x9d\xe5(\xfd\xbf5.\x00\x07!\x8f\nt\xda\xde\xbd\x95\xae\xaf\xc8\x91\xea\x95\x1a\xdb\x14\x14C\x8e\xa3\x92\x01\xe6\xb5c\x86\xf2\xb0<\x00\x03\xc5.\x9fp\xfd\x04\x944M\x8eO\x11$\x9fL\xf9*\x95\x93\te.n\xc9\'WA\x11n^\xb9\xb1\x86\xdf\x1b\xc0v+\xaf\xf3\xe7E1jH>\xdd\r\xb4\x0f\x89\x0ed\x1e\xec\x1c\xfe\xd4S\xb5Uj\x02\x08\x04r"\x8a\xf1\xd9$\t6\xa8\xcfg$\xa0%^#\x81\xfcW\xb2\x84.\xcb\xb0m\x96\xdb\xf54\x0f\xf1.\xa0R\xdd\x82\x97\x94\xd4xhQHx\xa7\xe2R\xc8\xe3\xbb\x9e\x1b\xa3\x9e\x0eM<\xed\xbfK\xeb\x07\xed\x96\x96\xb4\x1aW\x1a\xdf\x04,\xb9\x06\xdc\xe7\xb3\xaf\x7f#u`$\x8d\xe0\x06F3\x9c\xf1\xe3\x9a\xcb\xf4x^\xbb\xb3\xda\xbfM\x9d\xa5\xa4\x1b\x13\xae\x17\xda\x92\xfb\xa9\x8e\xb67\xbe"\x12\xb2\n\x90q\x9eC\x1ck\xa6\xc1\xd7\x1a:u\xc5v\xe8\x9a\x9e\xd2\xec\xa4+t\xb6$$d\xf6\x02p\x15\xe4MsK\xa5mk.N\x95\xb8\x91\xac\xd8x\x9a\x06\xda\x81\xb1\xeb\x83\x9fD\xee\x08\xa20\x06\x9d\t\xecT\xa7\x7f\xd4[D\x85\x98W\xcb\xce\xa5\x89\xd0\xb7%\xe7Z\xcf\xdf\x19\xa5U\xa9KZ\x9cZ\x94\xa5\xab\x8a\x94\xa3\x92|OZ\xbc\xe50\xc4\xb8\xe5\x89L5!\x95\x8e(u\x01hP\xf0<\rs\x1d{\xb1M1|\x8e\xeb\xf66Qc\xb8\xe0\x94\x16s\xec\xeb=\x8bGA\xde\x9cc\xb0\xd3;w\x16\xd2\xe7\x92X\xb93\xe66\xef\xa0>\xea\t\xad\xf2n\xd7eK4W\xa6\xeb\x02]\xae\xe7&\xdb=\x92\xcc\xa8\xae\xa9\xa7\x9b?*\x92pEy\xabwk\x83\x86F\xc9Y\x18_\x97\x14\x94\xa7*\xe5\x9a+\x13XLTh\xac6\xda\xb0\xe2\xd7\xbd\xe4\x07\xfe\xd1YB\xf0h\xcb\x80m\xd5@uXK\x87y\xb2~\xae\xa3\xcf\xf6\xaa;\xd1f\xc3m\xb9\xeak\x95\xd6sM\xbe\xf5\xb1\xa6\xccT,d%kR\x87\xac\xc7h\t\xc0\xec\'5\'$\x94\xa8)$\x82\x0eA\x1d+\xaal\x83iW\x1d1|ntU\xb7\xed[\x9e\xa9\xe6]\xff\x00.Sy\xce\xe9\xc7#\x91\x90G#\xc4u\x14\xbe\xebO-M\x1c\x91Bp\xe24\xfaw\x1a)\xa9\xde\xd6H\x1c\xed\x95\x11\xe9W|\xba\xc1\xb3\xda\xac\xf1\x1cq\x98w\x15:\xa9KA \xbb\xb9\xbb\x86\xc9\xec\xf7\x89#\xae\x05ND\x020@#\xb2\xa9\t\x1bR\xd9\x96\xb9\xb1~\x95\xab\xa2\xc9\x80\x14B\x8a\x1emK\r\xaf\xeaC\xad\xe4\x83\xdf\x81\xde)*V\x87\xd9\x1b\xae\x17!\xedL0\xc9\xe2\x10\xeb!j\x1exO\xe2\x90X\xea~\xee\xa6\x14\xf5\x10\xb9\xae\x04\xea\x1aH=\xc0=\x15\xba\xa6|g\xf3\xb1\xc0\x8e\xbfT\xa1\xa1v\x81\xa9\xb4\x9c\xe6\x17\x02\xe3!\xe8IX\xf5\xb0^Y[N\'<@\x07\xe1=\x858\xab-*\xdf@P\x05;\xc0\x1c+\x98\xc8\xebS\x85\x8d;\x11\xd2\x12\xdb\xb9.\xf3p\xd4\xf3XP[)\x11\x89m*\x1c\x8e\xee\x12\x92s\xf5\x12+7i[j\xbc\xeaX\xafZ\xec\xd1\xd5g\xb7:\n]W\xac\xde\x90\xf2O0T8$\x1e\xa1<OmS\xba\xdb\x9fx\xa8a\xa6\x88\xb0\x0f\x13\x9c9s\xdbs\x8e\x8aZy\x853\x0f;\xb3\xfa\x01\xaaR\xda\xd5\xd2%\xe7i7\xeb\x8c\x05\xa5q\x9d\x96R\xda\xd3\xc9a)\x08\xde\x1d\xc4\xa4\x9aUQ\tIR\x88\x00\x0c\x92y\n\x14BRI!)\x03\x89<\x00\x14\xa5\xa9o\x82BU\x0e\x1a\xbf\xa5\xc9\xc7\x07\xcf\xdc;\xbf5\xbbA\x08\x86&\xc4\xdd\x9a\x00\xf9h\x95\xbd\xc5\xce.>k6\xff\x00?\xf5\x0b\x8a\xddI>\xa9>\xe3~\x03\xaf\x9f:+>\x8a\x95yE\x03\x85\x14P\x85\xb5m\xd4Sb\x80\xdb\xd8\x92\xd8\xfa\xcf\xbc<\xff\x00\x9ac\xb6_#\xce\xe0\x86\xdeB\xba\x83\x82?4QB\x16\x8a\xd6\x12\x9d\xe3\x9cV-\xc7R1\x19e\xb6\xe3\xba\xe3\x83\xea!#\xf7\xa2\x8a\x10\x96\xee\x97\x89\xb7\x0c\xa5\xd77\x1a\xff\x00M\x1c\x13\xe7\xdbY\xf4QB\x11E\x14P\x85\xff\xd9 \xb4f#\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x16\xb3IDATx\x9c\xe5\\y\x94\\U\x99\xff}\xdf\xbd\xaf\xf6\xee$\ri\xb2@\x90\x84!MC\x96N%*\x18\xd2(\xa2a\x91\xd1\xd1RG\xc1\xed\x1cP\xcf\xc1\x99qE\x9dq\x99\x19=\xe3\x1cet\x14\xc7#\xe3\x00\xee\xa3\r\x8a\xcaf\x04\xa5\x95\x01\x87\xd0i\x12\xa0\x13\x12\x02\xd93YH\xd2\xddU\xddU\xf5\xee\xbd\xdf\xfcq\xdf\xab^R\xbd\xa6q\xfe\x98\xef\x9c:\xd5\xa7\xfa\xbd\xfb\xee\xfd\xddo\xff\xbe\xfb\x083OT(\x14\xb8\xa3\xa3C\x00\xb8\xf8\xc7\x8b/\xbe\xb8\xa1Z\xad.s\xce\xb5\x01X\x0e`)\x80\x85\x00\x9a\x00\xe4\x00\x04\xd1\xa5!\x80\xa2\x88\x1c\'\xa2}D\xb4\x1d\xc0SD\xd4\xc5\xccO?\xfe\xf8\xe3}\xc3\x9e\xc5\x85B\x81:::\x1c\x00\x99\xd1E\xcc\xe4X\x11 6\xfe!\x9f\xcf/\x02\xf0:\x11y=\x805\x00\xceff\x10\x11D\x04"~-\xf1wm \xa2\xdaw|\xads\x0eD\xb4GD\x1e\'\xa2_\x03\xd8\xd0\xd5\xd5\xb5\'\xbe\xa7P(\xa8\x99\x04hF\x80\x89&e\x01\xa0\xbd\xbd]\x17\x8b\xc5\xabD\xe4\xbdD\xf4Z\xa5T6^X\x04\x86\x05\x00\xf2\xab\x8f\x9f?z\x1e\xf1\xe2D"\xd4\x88H\x11\x11b`\xad\xb5\x03\x00\x1e\x04p;\x80{\xbb\xba\xba\xc2\xd1s9\x15:U`8\xfav\xad\xad\xad\x89t:\xfd.\x00\x1fb\xe6\xe5\x00`\xad\x1d\x0e\x04\xcf\xc0\xf3DD\\4\x9eRJ!z\xceS\x00\xbe\xd1\xd7\xd7\xf7\xbd\xe7\x9e{\xae2|^\xd3}\x10O|I}*\x14\n*z\xb0\xcb\xe7\xf3oI\xa5RO0\xf3\xbf\x13\xd1rc\x8c3\xc6X\x00\x12\xed\xb4\xc2\xccp\'\r\x1bO\x8c1\xd6\x18\xe3\x98y\x99R\xea\xd6\xc6\xc6\xc6\x8d\xabW\xaf~s<\xafh\x8e\xd3{\xd0t\xee\x89uI>\x9f_\x02\xe0+\xcc\xfcF\x11\x81\xb5\xd6F"2m\xc0#\xf52bbCr5\xe6mNDD)\xa5"1\xfb\x05\x11}\xb4\xab\xabk\xe7tu\xcfT\x81aD\xec\x99\xcf\xe7\xdf\r\xe0\xab\xcc<\xc7\x183-@\x88\x86>"\x80\xb5\x80u\x80s\x02\x11\xff\x1b\x11\xc0\x0c(&(\xe5\xff\x16\x01\\}!q""Zk\xe5\x9c;!"\x1f\xde\xb4i\xd3\x1d\xa3\xe7>\xa9\xb9Ma\x1d\n\x80mmmM\xa4R\xa9\xaf+\xa5\xde\xef\x9c\x83s\xceF\xac=ib\xf6\x0f\x0e\r0X\x11X\x0b\x04\x1a\xc8f\x08\r\x19F6\r$\x93\x04&\xc0X`\xa0,\xe8+\n\xfa\x8a\x0e\x95*\xa05\x90I\x11\x14{ G\x93\x88XfV\xcc\x0ck\xed\xad\xe5r\xf9C===\xd5x\r\x93\x99\xe3\xa4\x80\x895\xfd\xca\x95+\xe72\xf3O\xb5\xd6\x97\x86ah\xa6\xaa;8\xe2\xa7\x81AAh\x80\xb9M\x8c\x0b\xcf\xd5X\xd9\x12`\xe99\x1a\x0b\x9b\x19\xb3\x1a\x18\xc9\x00P\xca\x03\xe3\x1c`\xac\xa0\xaf$8p\xd8\xe1\x99\xe7B\xfcqK\x88\xee\xad!\x8a\x03\x82\x86,A\xab:r\xe2\x99\xce\x06Zk\xe7l\xe7\xa2&[\xe8x\xe0\xc9#\x93\xb5Z\x13.*\x1e\xa8\xad\xad\xedlf\xbe\x9f\x99\xcf7\xc6\x84D\x14Lt\xefpR\xca\x03b,\xb0\xb2%\xc05\xafNbm[\x02\x0b\xcfPP\x01\x00\x0bTB\x01\x04H\xa6\xc8\xcf,Z\xed\xe0\x80\x80\x19H\x04\x04\xd2\x80\xa9\x02\xcf\xbe`\xd0\xb1\xa1\x8c_=\\Fo\xbf\x033\x8d\xd4A\xd1\xfd\x02\t\xb5\xd2\x81\xb1\xae\'\xa9\xe9\x8a\x9e\x9e\xae=\x93\x01g\\`F\x81\xf2\x103/1\xc6\x18"\xd2\x93\x05\x84\xd9\xefz_I\xb0\xfc<\x8d\xeb\xdf\x92\xc1\xa5k\x12H\xa5\x08\x95\x8a\xa0Z\xf5\xebw\x0e\xc8\xa6\t\xd5P\xf0\xf0\xc6*\xb6l\x0fQ\xa9\x02\xcb\xcf\xd3\xb8\xe2\x92$D\x00c\xa2I3\x90N\x12t\x02\xd8\xf4T\x88\r\x8fU\xc0\xd1JN\xe6\x1c\x82V\xce\x0cT\x94\xbe\xa7\xb3\xbc\xb3X\x94\xd7L\x06\x9c\xf1\x80a\x00n\xcd\x9a5\xa79\xe7\x1ea\xe6\x96\xa9\x82\xa2\x18(W\x05D\x84\x1b\xde\x92\xc1{\xdf\x94F&M(\x96\x04\xceE\xba\x86\xbc\x9eh\xc8\x10\x9e~\xce\xe0\xef\xbf\xd5\x8f-\xdb\r\x10)\xde\xd0\x08\xae\xbc$\x85/}\xa4\xa1&ZD\x80\x8b\x94s6EP\x89z\x88\xc4\xc0\x00H\x00\xc7\x8f:s\xcd\x8d\xbd\xbaXr[\x83\x80/\xd9\xb8q\xe3\x8b\x18G!\x8f\xa54\xa9P(p:\x9d\xd6\xd6\xda\xfb\x94R\xf9)\x83\xa2\x80\xe2\xa0\xa0\xb9I\xe1k\x9fl\xc4_\xacO\xa3Z\x11\x94\xcb\x1e\x90\xe1\xa0\xe42\x84-\xcf\x86\xb8\xe1\xf3}\xd8w\xc8bv\x8e\x90J\xfaO.C\xe8\xda\x1a"\xd0\x84uk\x12(W\x00\x8e,\x19\x13P5@\xa5\x0cT*\xf5?\xe5\n\xe0B\xe0\xe8q\xe1;7\x0c\x18!u\x86\x88\xb9h\xc1\x82\x85?X\xbbv-zzz\xea\xce\xbf\xaeymooW\x1d\x1d\x1d\xd69\xf7\xcd \x08.\x89t\xca\x948\xa58 Xr\x96\xc6\xed_\x9c\x85W\xae\x08\xd0{\xc2A"\xc0b\x12\x01\x12\x01p\xf4\xb8\xc3\'n\xeeGq\xd0\xa11K062\xdd\xd6[\xa59\r\x8c{;\xcb8z\xcc!\xd0#\xfd\x19&?\xe6x\x1f\xad\xfc\x9c\x88H\x9b\xd0\x84Z\x07\x97\x88\xc8-\x1d\x1d\x1d\xb6\xbd\xbd\xbd.s\x9c\x04L\xa1PP\x9d\x9d\x9d\xa6\xad\xad\xed:\xad\xf5\xf5a\x18NI\xd12{\x13|f\xb3\xc2\xb7>\xd3\x88\xb3\xceP\xe8\xed\x17hu\xb2\xdc:\x01RI\xc2-?*\xe1\xf9\xfd\x16\xb9\x8c\x07e8\x89\xf8\xc5\x1d\xeb\xf3V)\xa1i\\O-\x06-\xe6\xca\xe1\x1f\x00 \xa2\xc0\x980TJ\xdd\xd0\xd6\xd6v]gg\xa7\xa9\xe7!\x8f\x9e+\x03\x90\xb6\xb6\xb6ED\xb4\x85\x88r"Bu\xae\xabK\xb1!\x11\x01\xbe\xf3\xf7\xb3\xb0\xea\x82\xa0\x06\xcahr\x0eH\xa7\tO\xef\x08\xf1\xeeO\xf7\x9e\xc4\t#\xc6%\xa0\x1a\x02\xb7\xfd\xe3,\xac:?@iPj\x0b\xadG\x7f\xfb\xf5~\xec\xdao\x91L\x0c9\x89\xa1\x01\xf6\x1c\xb4\xf13\x84\x88DD\x8a\xd6\xda\x15\x9b7o\xde\x1dM\xbf\xa6oF\x0c_(\x14\xe2\xb5}S)\xd5\xe8\x9c\x93\xc9\x82\x02\x00\xac\xbc\xf5y\xdf\x9b\xd2X\xb5<@o_}Pb\xd2\n\xf8\xd1\xbde\x0cV\xc6_\xa8\x88\xbf6\x95 \x8c7#\xeb\xbc\x93\xc8\x04l\xda\x1ab\xeb\xf3\x06\xcf\xec4xz\x87\xc1\xf6]f8\xf0\xe4\x9c\x13\xa5T#3\x7f\x13\x80Dk\x1fZK\xfcGl\xbe\xf2\xf9\xfc\x1b\xb5\xd6WE\xcav\xd2\x1e-\x91Wt\x8b\x17*\xbc\xe3\xaa4\x06\x8b2B\x9f\x8c^h*I\xd8\xbe\xcb\xe0w\x8fW\x90\xcb\x10\xec\x18\x86\x93"K\x94I\x13f5\x10\xac\x93\xb1wJ\xfc\x8a\x16\x9f\xa5\x91N\x122)B&\xfaN\'G\xdeED\xca\x18c\xb4\xd6W\xe6\xf3\xf97vtt\xd8\xe1"\x15\x03C\x1d\x1d\x1d\xd2\xda\xda\x9ap\xce}ID$J\x13L\x9a\x98\x81\xc1\xb2\xe0\xcauI451B3\x14\x10\x8e&\xe7\x80 \t<\xf0H\x05\'&\xe0*\x1f:\x08\xe6\xcea452\xcc8\xe3\x02\x00\x04H%\xbc\xfe\x1a\xfd9il"\x16\x11q\xce}\xa9\xb5\xb55\x11e\x1d\t\x88\x80\x894\xb3K&\x93\xd7\x06A\xb0\xd4Z\xeb0\xc5\x80\xd09\x1f\xbf\xac]\x95\x80\r\xc7\x9f\xbcR@\xa9\xe8\x1d\xb9d\x02\x90qB\xbbX?\x9c\xbbH!\x93\xa5\xba\xb1\xd1\xc8\x1b\xfc\xf5\x93\x8c\xa5\xd9Z\xeb\x82 X\x9aL&\xdf\t\xc0\xc5V\x8a\x01\xa0\xb3\xb3\xd3\xe6\xf3\xf9\x00\xc0\xc7\x9dsB4\xee\x9e\xd4\x9f|\x084\x9f\xc68{\x81B5\x94\xb1\xb9%\x12\xa3gw\x19\xec\xdck\x91JR\xdd\xdd\x1c\x1a\xdc\x8b^\xbe5\xf0cN\xb4`\x01\x8e\xf5\xbaIkF"\xa2h\xcd\x1fkoo\xd7\x9d\x9d\x9d\x16\x00\xb8\xbd\xbd]\x03\x10\xe7\xdcz\xadu\xcbt\xb8\x85\x08\x08\xadg\xf7\x86H_\x8c\x05\x8c8@i`\xf36\x83\x81\t\xac\x0b\xe0\xc3\x80\xa6Y\x8c\x97_\x98@X\xc5\xb8\xd7\x13\x036\x04v\x1f\xb0\xd0<n\xfef8\xb1\xb5\xd6)\xa5Z\xfb\xfb\xfb\xd7\x03\x90\xf6\xf6v\xcd\xcd\xcd\xcd\xf1\xed7 \xb2\xb6\x93\x1an\x14\x89\xf8XG\xa9\t\xb6*\xda\xf5\x9e\xe7\x8d_\xe48OS\xecS\x0e\xabZ5\xce>S\xa1\\\x19\x9b\x13E|\xea\xe2\xc8q\x87\xed\xbb\r\x92\t\x9a,0@\xece\x88\xbc\x1f\x00\x9a\x9b\x9b\x85;::\xec\x8a\x15+\x16\x12\xd1eQ\x02n\xda\xe9@c\'\xde%f\xa0R\x11\xec;d}\xba`\x12\x93\xbf\xe6\xd2\x94OP\x8ds\x8ds@*E\xf8\xe3\x96*\x0e\x1eqH\x04\x93\xe6\x18\x10\x91r\xce\x11\x80\xcbV\xacX\xb1\xb0\xa3\xa3\xc3r\xf4\x8f+\xb4\xd6i\x111\x98N\xba3\xf23^\xecu(W\xa4\x16\xe9\xd6\xb9\x0c\x8a\xbc\xf5\xea\xedwP\xe3,\x96\xc9s\xcb\x05K4.\xc9\'00 P\xe3\x88\x91\x07\x1c\xf8\xe9\x03e\xa8z\xf9\x99\xf1\x89\x9cs&\x08\x824\x11\xad\x07"]\xc2\xccW\x8c\xae\xedL\x85\x9c\xf8\\\xc9\xfeC\x16\xfb\x0eY\x04\x891\x14j\xe4\x85V\rP\t\x01\x1a\x0bAx}Q\t\x81\xbf\xbc2\x8dlvl?\x07\xf0z(\xd7H\xb8s\xc3 \x9ex&D.Mc\xa5>\xc7%\x11\x11f\xbe\x02\x00\xb8\xb5\xb55\'"\xaf\x88\nZ\xd3Nb+\x05\xf4\x15\x05\x0f\xfd\xb1\x82 \t\xb8q\x16\x12G\xc6c\x8e\xc5@\xb1$\xc8\xb7j\\\xd5\x9eD\xa94\xb6\xb3h\x0c0\xab\x91\xf0T\x8f\xc1\xd7\xbe_B63\x81\x95\x1bsN\xc4\xce9\x12\x91W\xb4\xb6\xb6\xe68\x91H,\'\xa2\x05\x11\xc7L\x1b\x18\x17\xb9\xe3\xff\xf9@\x19{\xf7Yd\xd2\'\xfb\x1c\xb54C\x9a0+W\xdf\x8be\xf6\xba*\x08\x08\x9fx_\x0e\x89`\xec\xdd\x8fAya\x9f\xc5G\xbe\xdc\x87rE&\xad\xb7\xea\x10\x8b\x08\x88ha2\x99\\\xc6D\x94WJQ\\\x18\x9b.\x89\x00\t\r\xbcx\xc2\xe1\xb3\xb7\x14a\x9d \x9989Z\xb6\x0eHg\x08m\xe7\x07(\r\x02A\x10W\x01\xbc\x9e\xaaV\x05\xa5A\xc1g?\x90\xc3\xaa\xd6\x00\xa5\x81\x91&=\xae&\x00\xc0\xac9\x8c\xee\xad!\xae\xff\\/\x0e\x1c\xb6H\'\xa7\'BCc\x8bU\xde\xac\xe6\xd5\x82\x05\x0bn`\xe6U\x91\x933m\x8e\x89\'\x9dJ\x12\x9e\xdbc\xb1\xedy\x83u\xf9\x04\xe6\xccbT*CQ.E\xd7\x9d\xbbH\xe3\xd1\xee*v\x1d\xb0\xb0\x0e(W\x81R\xd9\'\xb6\xfe\xe1\xc6\x06\xfc\xf9e)\xf4G\xf1V\\Jq\x91I\xce\xe6\x08\xc6\x00\xdf\xbb{\x00\x9f\xf9F\x11}E\x87Lj\x12^\xf1$\x96\xc0\xcc\xec\x9c;@\xabV\xad\xead\xe6u\xce\xb9);vc\x91b\x1fe/>S\xe1c\xef\xc9\xe15\xafL\xc0Zo\x8d\x88\xbc\x08$\x93\xc0\x91c\x0ew\xfd\xa6\x8c\x17\xf6[$\x03\xe0\xfc%\x01^\xff\xaa\x04\xe6\xcfU\xe8\xeb\x17\xc4\xdb\x14h\x9f\xe3\x05\x03\x87\x8e8<\xbc\xb1\x8a\x9f<0\x88\xa7w\x18\xe42\xbe\xdet*\x9c2\x8c\\\x04\xcc\xef\xa9\xad\xadm\'3/\x8e\x8a\xe73\xd6\xfd\xa0\xd8\xe7P\xaa\xa1`\xf9\xd2\x00\x7f}]\x16\xab\xce\xd7\xa8\x86@C\x96\x86\xec\xa9\xf6\xa9G\x02@\n\xa8\x94\x05\xd6\xf9\x14\x03kx\x17\xff\x84\xc3\xe6g\r~\xfb\xdf\x15<\xd2]\xc5\xfeC\xdeO\xc9\xa4\xa8\x96\xfb\x9d!\x92(D\xd8\xa9\x89h\xce\x8c\r\x1b\x11G\xeb\xae\x84\x82\\\x9ap\xce\x99\nM\x8d\x04\x02A\xb1\xe0\xde\xce\n*U\xc1\xd2s4\xe6\xcfedS\xbe\xdd\xc3V\x05\xc6\x00\xfd%\xc1\xc1\xa3\x06;v\x1bl\xdaj\xb0y[\x88\xbd\x87,\x8c\xf1`\xccn\xf0^\xed\x0c\x88N]"\xa2&\r \x1bwZ\xcc\xc4\xa0J\x01\xe5\x8a\xa0\x1a\x02\x97_\x94\xc4\x07\xdf\x96A\xeb\xd2\x00aY \x10|\xe1\xdbE\xfc\xf8\xbeA$\x13\x84\\\x9a0o.\xe3\xb4\xd9\x8c\x84&TB_q<\xd6\xe7\xd0\xdb/5\xd1K&\x08\xd94\xf9\x14\xdbK\x08\x08\x00\x8a\xb0\xc8j\x0cu2\x9d2)\x06N\xf4\x0b\xceY\xa0\xf07\xef\xcab\xfd\xda$\xac\x05\x8e\x1fs\x98\xd5@\xd8\xf0h\x15\x1d\xbf.\xa3\xb9\x89k;\xbe\xfb\x80\xc5\xf3{-b9f\x06\xb4&\x04\x1aH6\xf8\xbdrc\xd7\xaa_*\n&\x9d\xf9\x9f\x88\x98\xbc\xc2\xbd\xa6=\x89O]\x9f\xc3iM\xec\x15(<`\x1c\x00\xdd[C\x7fm\xa4\x7f\x00\xcf\r#\x02C\x19\xca\x1b\xdb\x19m\x1e\x9b\x1a1|\xcf\xdb\xa9\r\xc2@\xff\x80\xe0\xda7\xa4\xf1\x95\x9b\x1a\x91\xcd\x10\xfa\xfa|lS\xab\x1fU\x81u\xf9\x04\x92\t\xa0\xb7\xdf\xfb&JE\x9d\x0e\xces\x84s\x98ie:]\n\xd5\xfc\xf9\xf3?BDi\x00\xd3\xb2JL\xbe\\\xd2\xb2X\xe3\xe6\x8f5\xa2\x1azs<\xdc\x85\x8f\xe3\xa3\xc5gi,_\x1a`\xd7~\x8b\x83G\x1c\x8a\x03\x1e\x0c\xa5|a\x9eG\x96\xac\xff/(N\xd2\xf5i\x119v*\x96\x89\x18\xa8T\xbd\xa2Me\x08\xbd\'\x04\xba\x8e\x802\x01\xa5\x01\xc1\xda\xb6\x04\xd6\\\x18\xa0\xeb\x99\x10\xff\xd5\x1d\xa2{[\x88\x17\xf6\x19\x1c\xef\x93Z\x01.\x99\xa0\x11\x8e\xdd\x9f\x9a\x83D\xe4\x98&\xa2\xfdD\xb4d\xda~\x8cxqY\xd8\xcc\x10\x07\x8c\xe7;sT\xa1d\x06.^\x99\xc0\xabV\'P\x1e\x14\xec?\xec\xf0\xcc\x0e\x83\xae\x9e*\x9e\xdan\xb0\xeb\x80\xc5\xf1H\x14\xd3IB\x10\x8c\xdb,4\x93$\xe4i\xbf\x16\x91\x1dD\xb4.\xaa\x0cLo4\xf1)\x82\xc9P\x1c\xf7\x14\x07<\x87\xb0\x02\x16\xcdSXr\x96\xc25\x97\xf9H\xfa\x85\xfd\x16\x9bzB<\xb6\xb9\x8a\xcd\xcf\x1a\x1c=\xeej\xcdBL/\x9d\xb9\x8e1\x10\x91\xedj\xfe\xfc\xf9g3\xf3\x15\xd3\x8d\x95\x98<(\xb94\xe1u\x97$Q\x1e\x1c?/\x1bS\xdcBF\xf0\xd1t\xb9\xeaE\x92\t\x98w\xbaB\xdb\x05\x01\xae\xbc$\x85\xcb/Jb\xf1Y\n\x03\x83\x82}\xffc1X\xf1^1\xd1K\xa2\x8b\xe2X\xe9v5o\xde<\r\xe0}\xd3\r %JR\xed\xd8m\xd1\xf22\x8d\x96\x96\x00\x83\x03~\xca\x93e\xc08?\x13\xe7h\xc2\xa8\x83!4\xc0\xecFB[k\x80\xab\xd7%\x91\xbf0@q\x00\xd8\xb1\xdb\xc0:\xff\xdc\x99\xd4?q\x9d\t\xc0\x17TSS\xd3q\xa5\xd4\xbb\x99\xb9\x11\xbev;ey\x8a\x9b\x0b\x1f~\xa2\x82\x85\xa7),k\xd1H&|\xd6m:\x13\xafq\x13\xf9\x14C\xb9\xec\xcd\xf8\xe235\xae\\\x97D\xeb\x92\x00O\xed08\xf4\xa2C:5c\xe08\xf2\x05\xed\xfd\x95J\xe5\xb3\xea\xc8\x91#\xd5\x05\x0b\x16\xbcJ)\xd5\xe2\x9cs\xd3\xe1\x1c"oM\xc2\x10\xf8\xd5\xef*\xd8\xb2\xcdg\xe9O\x9b\xcd\x08t\x04\x10F\x16\xd6\xa6\xc4M\x11H\x95\xaa\x17\xdb\x96\xc5\xbe\xcbj\xc7.\x8b\x1d\xbb|\x1e\xe6T\xc1\x89s1"\xf2\xe0\x96-[~\xc0\x00\xe0\x9c\xbb\x7f\xaaE\xb6x\xd2Jy\x96\x7f\xf1\x84\xa0\x1a\n\xce\x9c\xa7\xd0_\x12<\xfad\x88\x83G\x1c\xb4\x02\x1as\x84\xc6\x06Bc#\xd5\x9a\t\x9d\xf3Jt*\x0b\x8a\x13Z\xbd\xfd\x82\x86\x0c\xe3\xeb\x9fn\xc4\x9aeA\xcd\xd2\x9d*E\x91\xf5\xfd\x00\xa0\x01@D\xee7\xc6\x0c2sz\xb2f;n#\x1b,\x03g/Px\xed\x95\t\\\xbc2\x81\xa5/\xd3\x98\xdb\xc4~\xa2\x0c\x0c\x94\x04w\xff\xb6\x8c\xc7\x9e\x0c1\xb7\x89\x91\xbf \xc0\x05K4\x9a\x9b\x18\x88J)q\x1f^\xdc)5\x11\xe9(P\xcdf\x08\x7f\xf7\xfe\x1c\xae\xfd\xe4\tX;\x14\xd5O\x83\x84\x99u\x18\x86\x83"\xf2\x00\x00\xe8\xa8\xcba\x7f[[\xdbCJ\xa9\xab\xa2f\xe6qc\xa88\xf1\xbdh\xbe\xc2\xb5oHc\xfd\xab\x92h\x9e\xcb\x10\xeb\x17Z,\t\x1ar\x84\x8d\x9bC\xdc|G\t\xdd[\xc3Z\xdf\\\xf03`\xfe\\\x85\x95-\x1akWygoa\xb3\xaa\xe5b*\xe1P09\xd1\x1c\x8a\x03\x82\xa5\x8b5.\xbf(\x89;7\x941\xbbazY\xbcH\x8c\x94s\xee\xa1\xcd\x9b7\xef/\x14\nJ\x1f>|8\xde\xa3[\x01\\\x8d\t\xb8%f\xe5\xb5\xab\x12\xf8\xa7\x0f7\xa0y.c\xb0$\xe8\xeb\x15 \xda\xf1\x86,\xe1\xb6\x9f\r\xe0_\x7fP\x82\xb1\xde\xb2\xc4\x01\x87\x08p\xf4\x84\xc3=\x9d\x15\xdc\xd3YAs\x13cE\x8b\xc6\xa5\xab\x93x\xe5\x8a\x00g\xceS\xb0\xc6\xa79\xc7\xab#\x01CJ\xff\xa2\x15\t\xdc\xf5\x9b\xf2\xd4\x11\x196\x14\xbc$}\x1b\x00\x0e\x1f>\\c\\\xca\xe7\xf3\xda9\xb7E)\xb54j\x18:iZq\xca\xf2\xb2W&\xf1\xd5\x9b\x1a!\xe2YZ\xf1P\x1fK.K\xf8\xeawK\xb8\xe5\xc7%45z\x91\xaaW-\x88Ms\xd5\xf81\x9c\x00g41.^\x99\xc0;\xafNc\xf9R\x8dbi\xec\x92,0\xd4\x02\xbbik\x88\xf7}\xa6wJ\xd5\xc7\xe1\xc3039\xe7\xb6\x11\xd1\x8a\xae\xae.\x03@jm \xd1y\x9f/33\xc5g\x84F/\xa6\x12\x02\x0b\x9b\x15>\xff\xc1\x1c \x82J5\xea\xad\x8b[Rs\x84_\xfe\xae\x8c\x7f\xfb\xc9\x00N\x9f\xe3\xbd\xb7\xfa-\xed\xfew\xeb\xbc\xbeh\xcc\x12f\xe7\x08\xc5\x01\xc1\xcf\x1f*\xe3\xbaO\x9e\xc0\x7f\xdc5\x80Lz\xe2\x1a\x91\x00\xb5(~:\x96)*\xb2\x91\x88|\xb9\xab\xab+<\xa9\r\x04\x00\xf7\xf7\xf7\xff0\x0c\xc3mJ\xa9\x93\xfa_9*\xb0\xbfm}\ns\xe72\x06\xcb\x18\xc1\xeaZ\xf9\x94\xe4w\xee\x1aD*9\xf9\xe0o8HJ\x01s\x1a\tZ\x03_\xbc\xb5\x84;7\x94\xd10AO\x0cG\\\\\r\xc7.\r\x8f\x03\x8aSJq\x18\x86\xdb*\x95\xca\x0f\x01p\xad\r$\xbe\xa6P(Pt\x08\xea\xa6\xc8\xd1\x19\xb1,g}\xac\xf2\xf2e\x01l\xe8c\x9c\xda\xff\x9c\x8f\x88w\xec6\xd8s\xd0\xfa^\xb9i)A\x1f\x1e0\xfb\xde\xdf\xdb~>0n\xc7\x95\x88O\xa0o\xdfe\x10\x86\xe3\x07\xb0c=2rSn\xea\xe9\xe9\xa9\x0e\xebA\x1c\xd2#q\x0fZww\xf7/\x8d1\xf7h\xad\xd5\xd0\xe9\xb4\xa8\xf1/M\x98\xdd\xc8\xb0\xb6~\x05\xb18 u\xff7Ur\xce\x17\xef\x0e\xbd\xe8\xb0\xe7\xa0w\x16\xeb\x01M\x04\x84\x15\xe0\xf7]\xd5q\xbb>\xeb\x91\x88X\xad\xb52\xc6\xdc\xd3\xdd\xdd\xfd\xcb\xd1-\xf4#0\x1e\xd6\x83v\xa3\xb5\xb6\x8f\x99=\x82\x12\xbb\xe7\x12\xf5\xc0\x8dZ:\x01\xd6x\xe5\x99\x1c\xab\xa0?U\x8a\xf6n\xac\xb1\x8c\xf5:\xed\x0f\x9b\xaa\xe8\xea\t\x91\x9dZ!_\x98\x99\xac\xb5}\x00nD\xd4\x838\xfc\x82\xd1\xcc\xe7\n\x85\x02www\xef\x16\x91\x1b\x99\x99E\xc4\x08\xbc\xfc\xf7\x97|\x84\xab\xf5\xc8\t3ygo\xc9"\x8d\xb6\x96\x00\xfd\x03rJ\xd9\xe4\xb8&5\xb7\x89q\xf6|\x8djUF\x88\x89u\xbe\xe2y\xbc\xd7\xe1\xe6;J\x13\x9a\xf5\xd1\x14\x9dgb\x11\xb9\xb1\xbb\xbb{w\xa1P8Y\xa7\x8e\xbe)j#\xd7\xdd\xdd\xdd\xdf\xb7\xd6\xde\x1a\x04A "a,N\xf7?R\x01\xa9\x93\x1b\n%Jb\x7f\xf4=Y\x9c6\x8b\xd1W\xf2\x99\xbc\xa9\x04\x1aD^\x89\x1b\xeb\xc5\xf2\xfa7g0g\x16!\xb4C\xce\x95\xb1Q\xbf\xaf\x13\xdc\xf4/\xfd\xd8\xb9\xd7 \x9d\x9a<\x97\x8aH\x18\x04\x81\xb6\xd6\xde\xda\xdd\xdd\xfd\xfd\xf6\xf6v]\xef\x14J]\xb5\xb6{\xf7n)\x14\n\xea\xc4\x89\x13\xf7;\xe7\xda\xb5\xd6\x8b\x8dq&\x95$\xde\xf6\x82\xc5\xf9/\xd3h9Oc``(\xa7\x127(\xceoVx\xf9\xb2\x04\xba\xb7\x86\xd8{\xd0\x82\x19\x08\x14\x81\xd5Pj!>\xee\xc74\xec\xc0\x05|\xcc\xd5W\x14d\xd3\x84O]\x9f\xc3[\xd7\xa7kE\xfd8Q>\xab\x91p\xf4\xb8\xc3\x87\xff\xb9\x1f\x8fl\xaa\xfa\xde\xdfI\xb6#\x88\x88\xd1Z\x07\xd6\xda\xdf\x13\xd1\xdb\xd7\xae]K\xf7\xddw_]\x01\x1co?\x87\x1f\xcb\xf9\x033\x9fo\xad1\xd6\x92N\xa7\x087\x7f\xbc\x01\x17\xafI\xa2\xd4\xe7|\x9c\xc2#\x95t\x7f\xc9\xe1G\xf7\x95q\xcf\xc3e\xec9hk\xae~\x0c\x8a\x9f\xe8\x90H&\x03\x1f*\xac[\x9d\xc0;\xaeLc\xc9"\x85\xfe\xa2\xd42\xf4\xd94\x81\x19\xd8\xf0h\x05_\xbe\xad\x84\xbd\x87,\x1asS\x06E;\xe7\xb62O|,g\\F\x8f5\xf5\xea\xd5\xab\xcf\x12\x91\xdf\x12\xf1\xb9\xe2\x8c\t-i&\xe0\xfdo\xcd\xe0\x9dW\xa7\xd1\x90#\x94\xcbR\xab\x15\xc5\x8d\x82\x99\x0c\xe1D\xaf\xe0\x99\xe7|\xfb\xfa\x9e\x83\x16\xbdE\xefs(&\xa4S\xc0\x9cF\xc6\x82f\x85?[\xa4p^\x14\x80\x96\xcb\x82rU\x90J\x10R)\xafT\x9f\xdc\x16\xe2\xf6\xbb\x07\xf1\xe0c\x15\x04\xda\x8b\xd3d\xe3\xa2a\xa0\xec$\xa2W?\xf1\xc4\x13{O\xe5 \xd7\x08p\xa2\xd7\x11\xdc\xcf\xcc\xad\xe2L\xe8\x84\x82\xfe\x92\xa0\xe5\x1c\x85\xb7_\x91\xc6k^\x91\xc4\xbc\xb9^&LT\xcc\x0f\x8dW\xa4\xa9$\xd5\x1az\x86\xa7\x1a\xe24\x02\xa2\xdaR\xdcK\x13\x04\x00\x048t\xcca\xe3\xd3!\xee\xed,\xe3\xd1\'C\x94\xab\x82\xc6,M\xa9r "\xa1\xd6:p\xce\xf5\x00\xb8\xa2\xabk\x06\x8e\xfe\x8d\x06g\xf8aQcB\xa3\x98\xd4`E\xa8R\x05\x1643\xd6\\\x18\xe0\x15\xcb\x12hY\xac1\xfftFC\x96\x11\x04\xa3\x1e2\xaa\xea\xe8\xa2F\xa0r\xd5\xd7\xad\x0f\x1c\xb6\xd8\xfa\x82A\xf7\xd6\x10\x9b\x9f58p\xc8k\xde\\f\xca\x89p\x11\x11\x1b\x04\x816\xc6<\xec\x9c{\xeb\x93O\xce\xe0a\xd1a\xa4\x00\xd8|>\x1f\x88\xc8\xd7\x95R\x1fp\xce\x01\xe2,3\xa9j\xe8\x0bo"~\x11\xa7\xcfa\x9cq\x1ac\xee\x1c\xc6\xec\x06F.C#\xeaE\xa1\x91\xda\xb1\xe1c\xbd\x0eG\x8f;\x1c9\xeep\xbc\xcfa0:\xc5\x96J\x12\x92\x01jg&\xa7\x80\xc8\xf0\xe3\xc5\xdf.\x97\xcb\x7f\xf5\x92\x1c/\x1eF5eU\xef@\xbabo\xfe\xad\xf3\x16\xc6X\xa9\xe5}\xeb\xb2>\r+\xe4+@+\x1f\'\xc5\x8d\xd1\xd3(\xd7\x0e?\x90~\\D>2\xdd\x03\xe9S\x8d.\x1c\x00*\x14\n\xaa\xab\xab\xeb\xbb\x00\xd6\x88\xc8/\xb4\xd6\x8a\x99\xd9X\xb1\xd6\xf9\x87\'\x02oIf\xe5\x08\xb3\x1b\tsf\xd5\xf94\xfa^\x97\x86\xac?6\xa3\xf5P\x8f\xdd\x14\xd3\x9e.v\xda"P\xee\x06\xb0f\xd3\xa6MwDGm\x08S|\x01\xc6\xb4\xc3\x9a\xe1\xb2\xbaz\xf5\xea7\x8b\xc8g\x99yy\xf4\x8e\x07\x07\x1f\xa0\xf1\xa9<c\x02\x8a\xdf\x0cBJ)\x8e\xde\xe9\xf0\x94\x88|\xbe\xbb\xbb\xfbg\xa3\xe78U:\xd5I\xc7\x1c\x17\xbf&\xe5:\x007\x12\xd1\xcah\xa2\x7f\x92\xd7\xa48\xe7\xb6\x88\xc8-3\xf9\x9a\x94\x19\xd9\xcdQ;\xa3\xf2\xf9\xfc\xd5\x00\xde\x03\xe0rf\xce\x02\x98\xd1\x17\xebD\xe3\x95D\xe4A"\xba#\x97\xcb\xdd\xd3\xd9\xd9i\xea\xcce\xda4\x93l>\xd6\xab\x98.\x17\x91\xf5\xf8\xff\xf8*\xa6\xd1cF\xd1*\x86\x83T\xe7\xe5]\xe7\x018\x13\xfe\xe5]Y\x00\x89\xe8\xd2*\x80\x12\x80c\x00\xf6\x11\xd1\x0e\x00[\x88h\xd3\xe8\x97w}\xees\x9f\xe3\x9e\x9e\x9e\x97\xe4\xe5]\xff\x0b`b.\xed/uM\\\x00\x00\x00\x00IEND\xaeB`\x82'

    # detect IP; use Port as manually set in header
    WiFiServerIP = getMyIP()

    # create the web server
    try:
        # 'ThreadingHTTPServer': New in version Py 3.7. Not compatible with 3.6
        # non-threading may have been cause for crashing on double requests!
        # WiFiServer = http.server.HTTPServer((WiFiServerIP, WiFiServerPort), MyServer)
        g.WiFiServer = http.server.ThreadingHTTPServer((WiFiServerIP, WiFiServerPort), MyServer)
        g.WiFiServer.timeout = 1
        wifismsg = (True, f"Ok, listening at: http://{WiFiServerIP}:{WiFiServerPort}")
    except OSError as e:
        exceptPrint(e, "")
        msg0 = "WiFiServer could not be started, because "
        if e.errno == 98:   wifismsg = (False, msg0 + "Port number {} is already in use".format(WiFiServerPort))
        else:               wifismsg = (False, msg0 + "of OS.Error: {}".format(e.errno))
    except Exception as e:
        wifismsg = (False, "Unexpected Failure - WiFiServer could not be started")
        exceptPrint(e, wifismsg)

    ### init the Geiger counter
    msg = initGMC()
    if msg > "":
        edprint(defname, f"InitGMC failed with message: {msg}")
        wifismsg = (False, "Failure to init GMC counter")
    else:
        ### init threading
        g.WiFiServerThreadStop        = False
        g.WiFiServerThread            = threading.Thread(target = WiFiServerThreadTarget)
        g.WiFiServerThread.daemon     = True   # must come before daemon start: makes threads stop on exit!
        g.WiFiServerThread.start()

    return wifismsg


def WiFiServerThreadTarget():
    """Thread constantly triggers web readings"""

    defname = gd(sys._getframe().f_code.co_name)

    while not g.WiFiServerThreadStop:
        g.WiFiServer.handle_request()
        time.sleep(0.01)


def terminateWiFiServer():
    """stop and close Web server"""

    defname = gd(sys._getframe().f_code.co_name)

    g.WiFiServerThreadStop = True
    g.WiFiServer.server_close()

    return "Terminate WiFiServer: Done"


class MyHandler(http.server.BaseHTTPRequestHandler):

    defname = gd(sys._getframe().f_code.co_name)

    def log_message(self, format, *args):
        """replacing the log_message function"""

        # output:  ... LogMsg: GET /?ID=GeigerLog&M=10&S=11&M1=12&S1=13&M2=14&S2=15&M3=16&S3=17&T=18&P=19&H=20&X=21 HTTP/1.1, 302, -
        strarg = ", ".join(args)    # count(args) = 3 (except on errors)

        if g.color == TYELLOW:    dprint("WiFiServer LogMsg: ", strarg, g.dogetmsg)


class MyServer(MyHandler):
    """This is the Web Server"""

    def do_GET(self):
        """'do_GET' overwrites class function"""

        defname    = f"{DisplayName} do_GET: "
        g.dogetmsg = ""
        g.color    = TDEFAULT

        dprint(defname, f"self.path: '{self.path}'")

        # if thread stopped this is the last dummy call to close the server
        if g.WiFiServerThreadStop:
            self.send_response(200)
            self.end_headers()
            dprint("WiFiServerThreadStop is True") # never reached?
            return

        ##########################################################################################

        # root
        if self.path == "/":
            ### call fresh data or take from cache
            if (time.time() - g.LastCall) > 1.1:
                lastrec = getDataGMC()
            else:
                lastrec = g.LastRec
                dprint(" "*40, "using cached data")

            sdata   = lastrec.replace(" ", "")   # remove all blanks to compress data list
            ldata   = sdata.split(",")

            if len(ldata) < 4:  ldata = [ldata[0], ldata[1], "---", "---"]
            # rdprint(defname, f"ldata: {ldata}")

            answer = """<!DOCTYPE html>
                        <head>
                            <title>%s</title>
                            <meta http-equiv="refresh" content="10" />
                            <style>
                                html{text-align:center; font-family:Helvetica; font-size:30px;}
                                h1 {margin:0px;}
                                table, tr, th, td {
                                    border: 1px solid black;
                                    border-collapse: collapse;
                                    font-size: 50px;
                                    font-weight:900;
                                    color: white;
                                }
                                td {width:250px;}
                                button {
                                    font-size: 50px;
                                    font-weight:900;
                                    margin:50px;
                                    padding:30px;
                                    }
                            </style>
                            <link rel="icon" type="image/png" href="/favicon.ico" sizes="16x16">
                        </head>
                        <body>
                            <h1>
                                <img src="/favicon.ico" width="80" height="80" style="vertical-align: bottom;">
                                GeigerLog Data Server
                            </h1>
                            <h1 DeviceName>%s</h1>
                            <p>
                                Connected Device: <b>%s</b><br>
                                Connected Port: <b>%s</b>
                            </p>
                            <p><b>Supported Requests:</b>
                            <br>/data &nbsp /reset &nbsp /id</p>

                            <p>DateTime: %s</p>

                            <table  style="margin: 0px auto; ">
                                <tr style="background-color:blue;">
                                    <td >CPM1st:</td>
                                    <td>%s</td>
                                <tr style="background-color:magenta;">
                                    <td>CPS1st:</td>
                                    <td>%s</td>
                                </tr>
                            </table>

                            <table  style="margin: 0px auto; ">
                                <tr style="background-color:cyan;">
                                    <td >CPM2nd:</td>
                                    <td>%s</td>
                                <tr style="background-color:#9b59b6;">
                                    <td>CPS2nd:</td>
                                    <td>%s</td>
                                </tr>
                            </table>

                            <button name="update" type="button" value="toggle" onClick="autoRefresh()">
                                Update
                            </button>

                        </body>
                        <script>
                            let intervl = 1000
                            function toggleMe(){
                                intervl =100;
                                //window.location = window.location.href;
                                window.location.href = "http://10.0.0.20:7777"
                            }

                            function setUpdate(){
                                setInterval('autoRefresh()', intervl);
                            }
                            function autoRefresh() {
                                window.location = window.location.href;
                            }
                            // setInterval('autoRefresh()', intervl);
                        </script>
                        """  % (DisplayName, DisplayName, g.GMCcounterversion, g.GMCport, stime(), str(ldata[0]), str(ldata[1]), str(ldata[2]), str(ldata[3]) )

            answer      = answer.replace("   ", "")                 # saving some bytes
            bdata       = bytes(answer, "UTF-8")

            myheader    = "Content-type", "text/html; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200

        # data
        elif   self.path.startswith("/data"):
            lastrec     = getDataGMC()                               # CSV values from a real GMC Geiger counter
            bdata       = bytes(lastrec.replace(" ", ""), "UTF-8")   # remove all blanks to compress bytes

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200

        # ID
        elif   self.path.startswith("/id"):
            answer      = g.GMCcounterversion
            bdata       = bytes(answer, "UTF-8")

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200


        # favicon
        elif self.path == '/favicon.ico':
            answer      = g.iconGeigerLogWeb                        # this is a bytes item
            bdata       = answer

            myheader    = ('Content-Type', 'image/png')
            mybytes     = bdata
            myresponse  = 200


        # reset
        elif self.path == "/reset":
            answer      = resetDevices()                            # fake operation
            bdata       = bytes(answer, "UTF-8")

            myheader    = "Content-type", "text/plain; charset=utf-8"
            mybytes     = bdata
            myresponse  = 200


        # page not found 404 error
        else:
            ### "self.headers['User-Agent']" when calling from:
            ###    Python:      BaseHTTP/0.6 Python/3.9.4
            ###    GMC counter: None
            ###    Firefox:     Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0
            ###    Chromium:    Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.72 Safari/537.36
            ###
            # dprint("self.headers['User-Agent']: ", self.headers["User-Agent"])

            g.color = TYELLOW
            if self.headers["User-Agent"] is None or "Python" in self.headers["User-Agent"]:
                answer   = "404 Page not found"
                myheader = 'Content-Type', "text/plain" # PLAIN

            else:
                answer   = "<!DOCTYPE html><style>html{text-align:center;}</style><h1>404 Page not found</h1>"
                myheader = 'Content-Type', "text/html"  # HTML

            g.dogetmsg   = f"{g.color} | {defname}{answer} {TDEFAULT}"

            mybytes    = bytes(answer, "UTF-8")
            myresponse = 404

        self.send_response(myresponse)
        self.send_header(*myheader)
        self.end_headers()

        ### Writing bytes to net
        try:
            self.wfile.write(mybytes)
        except Exception as e:
            exceptPrint(e, defname + "Writing bytes to net")


def resetDevices():
    """resets devices"""

    defname = gd(sys._getframe().f_code.co_name)

    msg = "A Reset was faked"
    dprint(msg)
    return msg


def writeLogfile(msg):
    """Make new file, or empty old one, then write msg to file"""

    defname = gd(sys._getframe().f_code.co_name)

    if Logfile == "":
        # no logfile if filename is empty
        dprint("{:33s} : {}".format("Init Logfile", "Logfile will NOT be written"))

    else:
        # filename is defined --> make logfile
        try:
            with open(Logfile, "wt") as log:
                log.write(msg)
            dprint("{:33s} : {}".format("Init Logfile",  "Ok, Logfile is: '{}'".format(Logfile)))

        except Exception as e:
            exceptPrint(e, "")
            msg = f"Logfile '{Logfile}': Could NOT be written!"
            dprint(msg)


def appendLogfile(msg):
    """append msg to the end of file"""

    defname = gd(sys._getframe().f_code.co_name)

    if Logfile > "":  # no writing if filename is empty
        try:
            with open(Logfile, 'a') as log: log.write(msg)
        except:
            pass


### get GMC data
def getDataGMC():
    """
    input:  vname - varname to get value for (only for CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd - all others return NAN)
    return: value-list as CSV bytes
    """

    GMCstart   = time.time()
    defname    = gd(sys._getframe().f_code.co_name)
    lastrec    = ""
    varlist    = g.GMCvariables.replace(" ", "").split(",")           # remove white space, split into list

    # rdprint(defname, f"varlist: {varlist}")                         # getDataGMC: varlist: ['CPM1st', 'CPS1st']
    for vname in varlist:
        # rdprint(defname, f"vname: {vname}")
        if   vname == "CPM"   : wcommand = b'<GETCPM>>'
        elif vname == "CPS"   : wcommand = b'<GETCPS>>'
        elif vname == "CPM1st": wcommand = b'<GETCPML>>'
        elif vname == "CPS1st": wcommand = b'<GETCPSL>>'
        elif vname == "CPM2nd": wcommand = b'<GETCPMH>>'
        elif vname == "CPS2nd": wcommand = b'<GETCPSH>>'
        else:                   continue

        try:
            bwrt = g.GMCser.write(wcommand)                           # bytes-written (type int)
            brec = g.GMCser.read(g.GMCbytes)                          # rec received  (type bytes)
        except Exception as e:
            exceptPrint(e, defname)
            msg  = f"# EXCEPTION: {defname} '{str(e)}'"
            appendLogfile(msg)
            value = g.NAN

            # close and open the serial port
            iydprint(defname, f"CLOSE -OPEN SERIAL PORT =======================================================================")
            try:    g.GMCser.close()
            except: pass
            try:
                g.GMCser  = serial.Serial(g.GMCport, g.GMCbaudrate, timeout=g.GMCtimeout)
            except Exception as e:
                exceptPrint(e, defname + "FAILURE connecting to GMC counter.")
            iydprint(defname, f"CLOSE -OPEN SERIAL PORT =======================================================================")

        else:
            if len(brec) == g.GMCbytes:
                # success, got expected number of bytes
                value    = getValueFromBytes(vname, brec, g.GMCbytes)

            else:
                # Fail, bytes missing or too many
                msg = "# ERROR in byte count, got {} bytes, expected {}!".format(len(brec), g.GMCbytes)
                dprint(msg)
                appendLogfile(msg)
                value = g.NAN

        lastrec += f"{value:5.5g}, "

    g.LastRec  = lastrec[0:-2]          # remove last ", "
    g.LastCall = time.time()

    dur        = 1e3 * (time.time() - GMCstart)
    if dur > g.GMCmaxdur: g.GMCmaxdur = dur                             # maxdur seen as; 383.5 ms
    dprint(defname.strip(), f" '{g.GMCcounterversion}' {' ' * 10 } {varlist} : {g.LastRec:20s}  dur: {dur:6.2f} ms  maxdur: {g.GMCmaxdur:0.1f}")

    return lastrec


def getValueFromBytes(vname, brec, GMCbytes):
    """Convert 2 or 4-byte counter CPx reading to value"""

    # 4 bytes: value = ((brec[0] << 8 | brec[1]) << 8 | brec[2]) << 8 | brec[3]
    # 2 btyes: value =  (brec[0] << 8 | brec[1])
    # "mask out high bits" applies only to CPS* calls on 300 series counters

    value = brec[0] << 8 | brec[1]                                                          # 2-bytes value
    if   GMCbytes == 4:                     value = (value << 8 | brec[2]) << 8 | brec[3]   # 4-bytes value
    elif GMCbytes == 2 and "CPS" in vname : value = value & 0x3fff                          # mask out high bits

    return value


def initGMC():
    """Initialize GMC counter"""

    ####################################################################################################
    def findGMCports():
        """make list of all USB-to-Serial port matching GMC chip"""

        # defname  = gd(sys._getframe().f_code.co_name)

        dprint(defname, "Listing USB-to-Serial Ports on this system:")
        GMCports = serial.tools.list_ports.comports()
        if len(GMCports) == 0:
            msg = "No USB-to-Serial Ports found on this system"
            dprint(defname, f"    {msg} - Cannot run without one. Exiting.")
            return f"Failure - {msg}"

        # check for a port with chip CH340
        for port in GMCports:
            if "/dev/ttyS" in str(port): continue      # ignore any /dev/ttySxy ports
            if  port.vid == 0x1a86 and port.pid == 0x7523:
                g.GMCPortsList.append({"port" : port.device})
                dprint(defname, f"    Found port with GMC matching chip: {port.device}  {port.description}")
            else:
                dprint(defname, f"    Found port NOT  matching GMC chip: {port.device}  {port.description}")

        if len(g.GMCPortsList) == 0:
            msg = "No USB-to-Serial Ports for GMC counters found on this system"
            dprint(defname, f"    {msg} - Cannot run without one. Exiting.")
            return f"Failure - {msg}"

        return ""


    def findModel(port):
        """find the baudrate for any found GMC counter and get model"""

        defname  = gd(sys._getframe().f_code.co_name)
        baudrate = None
        model    = None

        testbaudrate = (115200, 57600)
        for tbr in testbaudrate:
            try:
                ### get version
                testser = serial.Serial(port, tbr, timeout=g.GMCtimeout)
                bwrt = testser.write(b'<GETVER>>')
                trec = testser.read(14) # may leave bytes in the pipeline, if GETVER has
                                        # more than 14 bytes as may happen in newer counters
                while True:             # collect any left bytes
                    cnt = testser.in_waiting
                    if cnt == 0: break
                    trec += testser.read(cnt)
                    time.sleep(0.1)
                testser.close()

                ### get model
                # iydprint(defname, f"Len trec: {len(trec)}")
                if len(trec) > 0:
                    model = trec.decode("utf-8")
                    # iydprint(defname, f"    Found model: '{model}'")
                    if trec.startswith(b"GMC"):
                        baudrate = tbr
                        break       # for loop

            except Exception as e:
                exceptPrint(e, defname + "ERROR: Serial communication error on finding baudrate")

        return baudrate, model


    def findGMCmatchID(portitem):
        """find a GMC_ID (Model, Serial number) match"""

        # iydprint(defname, f"looking for match with GMC_ID: {g.GMC_ID}")

        port     = portitem["port"]
        baudrate = portitem["baudrate"]
        model    = portitem["model"]

        try:
            if g.GMC_ID[0] == "None":
                # a specific Model was NOT requested. You're done
                foundit = True

            else:
                # now check for Model; if match then for SN
                if model.startswith(g.GMC_ID[0]):
                    # we found the specified Model
                    dprint(defname + f"    {model} matches configured model '{g.GMC_ID[0]}' ")

                    # now check for a SerialNumber definition if requested
                    if g.GMC_ID[1] == "None":
                        # not requested
                        foundit = True
                        dprint(defname, "    Matching Serial Number was not requested")

                    else:
                        # SN was requested
                        serno = getGMC_SerialNumber(port, baudrate).replace(" ", "")
                        # iydprint(defname, f"serno: {serno}")
                        if serno.startswith(g.GMC_ID[1]):
                            # does begin with the specified SerialNo
                            foundit = True
                            g.GMCSerialNumber = serno
                            dprint(defname + f"    {model} matches configured SerialNumber '{g.GMC_ID[1]}' ")
                        else:
                            # not the specified SerialNo
                            foundit = False
                            dprint(defname + f"    {model} does NOT match configured Serial Number '{g.GMC_ID[1]}' ")

                else:
                    # not the specified Model
                    dprint(defname + f"    {model} does NOT match configured model '{g.GMC_ID[0]}' ")
                    foundit = False

        except Exception as e:
            exceptPrint(e, defname + "ERROR: Serial communication error on finding baudrate")
            baudrate = None

        return (foundit, port, baudrate, model)

    ####################################################################################################


    defname  = gd(sys._getframe().f_code.co_name)
    dprint()
    dprint(defname)

    defname = "   " + defname       # indent dprints

    if g.GMCtimeout      == "auto":  g.GMCtimeout   = 1
    if g.GMCtimeoutR     == "auto":  g.GMCtimeoutR  = 1
    if g.GMCtimeoutW     == "auto":  g.GMCtimeoutW  = 1
    # if g.GMCvariables    == "auto" :                      # is set at the end of initGMC

#ggg

    ### ports?
    msg = findGMCports()
    if msg > "":    return msg
    # iydprint(defname, f"g.GMCPortsList: {g.GMCPortsList}")

    ### baudrate, model
    iydprint(defname, f"Searching GMC counters:")
    for portitem in g.GMCPortsList:
        baudrate, model = findModel(portitem["port"])
        portitem.update({"baudrate" : baudrate})
        portitem.update({"model"    : model})
        iydprint(defname, f"    Found: @port: {portitem["port"]}  @baudrate: {baudrate}   model: {model}")
    # iydprint(defname, f"g.GMCPortsList: {g.GMCPortsList}")

    ### GMC_ID
    foundit = False
    iydprint(defname, f"Searching for ID matches with GMC_ID: {g.GMC_ID}")
    for portitem in g.GMCPortsList:
        foundit, port, baudrate, model = findGMCmatchID(portitem)
        if foundit:
            g.GMCport           = port
            g.GMCbaudrate       = baudrate
            g.GMCcounterversion = model
            break

    if not foundit:
        dprint("Could not find requested counter. Is it connected? Will exit.")
        return "Failure"

    ### get Serial number
    g.GMCSerialNumber = getGMC_SerialNumber(g.GMCport, g.GMCbaudrate).replace(" ", "")
    dprint(defname, f"GMC Serial Number: {g.GMCSerialNumber}")

    ### open the serial port with selected settings
    try:
        g.GMCser  = serial.Serial(g.GMCport, g.GMCbaudrate, timeout=g.GMCtimeout)
    except Exception as e:
        exceptPrint(e, defname + "FAILURE connecting to GMC counter. Cannot continue.")
        return "Failure"


    rdprint(defname, f"g.GMCcounterversion: {g.GMCcounterversion}")

    ### set GMCbytes
    g.GMCbytes  = 4
    if   "GMC-3"         in g.GMCcounterversion:   g.GMCbytes       = 2    # all 3XX
    elif "GMC-500Re 1."  in g.GMCcounterversion:   g.GMCbytes       = 2    # perhaps Mike is only user

    ### set number of tubes, see: https://www.gqelectronicsllc.com/support/GMC_Selection_Guide.htm
    g.GMCtubeCount = 1
    if   "GMC-500+"      in g.GMCcounterversion:   g.GMCtubeCount   = 2    # only '500+'

    if g.GMCtubeCount == 2:     g.GMCvariables = "CPM1st, CPS1st, CPM2nd, CPS2nd"
    else:                       g.GMCvariables = "CPM1st, CPS1st"

    dprint(defname, f"Ok, Port: {g.GMCport}  Baudrate: {g.GMCbaudrate}  Timeout: {g.GMCtimeout}  Variables: {g.GMCvariables}")

    return ""


def getGMC_SerialNumber(usbport, baudrate):
    """Get the counter's serial number"""

    # send <GETSERIAL>> and read 7 bytes
    # each nibble of 4 bit is a single hex digit of a 14 character serial number
    # e.g.: F488007E051234
    #
    # return: the serial number as a 14 character ASCII string plus DSID string

    defname = gd(sys._getframe().f_code.co_name)
    # dprint(defname)

    ### get GMC ExtraByte()
    try:
        with serial.Serial(usbport, baudrate=baudrate, timeout=g.GMCtimeoutR, write_timeout=g.GMCtimeoutW) as ABRser:
            sbwrt  = ABRser.write(b'<GETSERIAL>>')
            sbrec  = ABRser.read(7)                       # get the GMC device serial number
            sbrec += getGMC_WaitBytes(ABRser)
    except Exception as e:
        errmessage1 = defname + "FAILURE: Reading Serial Number from device; returning None"
        exceptPrint(e, errmessage1)
        return None

    ###################################################################################
    # DSID - 2nd part of serial number "sometimes needed when upgrading firmware"
    try:
        with serial.Serial(usbport, baudrate=baudrate, timeout=g.GMCtimeoutR, write_timeout=g.GMCtimeoutW) as ABRser:
            dbwrt  = ABRser.write(b'<DSID>>')
            dbrec  = ABRser.read(1)                  # if DSID is not supported, then the response is 8 * '\x00'
            dbrec += getGMC_WaitBytes(ABRser)
    except Exception as e:
        exceptPrint(e, defname + "FAILURE: Reading DSID Serial Number from device")
    ###################################################################################

    snCombo = " ".join(f"{b:02X}" for b in sbrec) + " - " + " ".join(f"{b:02X}" for b in dbrec)
    # dprint(defname, "Found: " + snCombo)

    return snCombo


def getGMC_WaitBytes(serialHandle):
    """getting and returning waiting bytes"""

    brec = b""
    while True:
        time.sleep(0.01)
        bytesWaiting = serialHandle.in_waiting
        if bytesWaiting == 0: break
        brec += serialHandle.read(bytesWaiting)

    return brec


def main():

    defname = gd(sys._getframe().f_code.co_name)

    ### clear the terminal
    ### docs: os.name:  "The following names have currently been registered: 'posix', 'nt', 'java' (nothing else!)."
    os.system('cls' if os.name == 'nt' else 'clear')


    ### verify Python version is >= v3.7 (needed for HTTP server)
    svi = sys.version_info
    if svi < (3, 7):
        print("This software requires Python Version 3.7 or later.")
        print("Your Python version is Version {}.{}.{} .".format(svi[0], svi[1], svi[2]))
        print("Cannot continue, will exit.")
        return

    ### print system docu
    print("=" * 150)
    dprint("{:33s} : {}".format("Version of {}".format(__script__), __version__))
    dprint("{:33s} : {}".format("Version of Python", sys.version.split(" ")[0]))
    dprint("{:33s} : {}".format("Version of Operating System", platform.platform()))
    dprint("{:33s} : {}, {}".format("Machine, Architecture", platform.machine(), platform.architecture()[0]))

    ### init logfile
    msg  = "# Log file created with: '{}', Version: {}\n".format(__script__, __version__)
    msg += "# Python Version:   {}\n".format(sys.version.replace('\n', ""))
    msg += "# Operating System: {}\n".format(platform.platform())
    msg += "# Machine, Arch:    {}, {}\n".format(platform.machine(), platform.architecture()[0])
    msg += "# Index,                DateTime,      CPM,      CPS,   CPM1st,   CPS1st,   CPM2nd,   CPS2nd,   CPM3rd,   CPS3rd,     Temp,    Press,    Humid,     Xtra,   Duration[ms]\n"
    writeLogfile(msg)
    print()


    ### init the WiFi Server
    WSsuccess, WSresponse = initWiFiServer()
    if WSsuccess:
        dprint()
        dprint("{:33s} : {}".format("Init WiFi Server",        WSresponse))
        dprint()
    else:
        dprint("{:33s} : {}".format("Init WiFi Server FAILED", WSresponse))
        return



#######################################################################################################################

if __name__ == '__main__':
    main()
    # Loop until CTRL-C
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            print()
            dprint(terminateWiFiServer())
            break

    dprint("Exiting {}".format(__script__))
    print()


#######################################################################################################################
### code for heartbeat use - not active here ##########################################################################

# import serial

# class GlobalVars():
#     # ...
#     GMC_usbport   = "/dev/ttyUSB1"
#     GMC_baudrate  = 115200
#     GMC_timeoutR  = 1
#     GMC_timeoutW  = 1
#     GMCbytes      = 200


# def init ...
#     # ### turn Heartbeat --> ON --- use only for TESTING heartbeat !
#     turnGMC_HeartbeatON()
#     turnGMC_HeartbeatOFF()
#     # ### end


# def turnGMC_HeartbeatON():
#     # from:  https://www.gqelectronicsllc.com/download/GQ-RFC1801.txt
#     # 3. Turn on the GQ GMC heartbeat
#     # Note:     This command enable the GQ GMC unit to send count per second data to host every second AUTOMATICALLY.
#     # Command:  <HEARTBEAT1>>
#     # Return:   A 32 bit unsigned integer is returned every second automatically. Each data package consist of 4 bytes data from GQ GMC unit. The first byte is MSB byte data and last byte is LSB byte data.
#     #     e.g.: 00 00 00 1C     the returned 1 second count is 28.
#     # Firmware supported:  GMC-500, GMC-500+, GMC-600, GMC-600+
#     #
#     # NOTE: Bei dem GMC-800 können 4 bytes gelesen werden. Scheinen CPS zu sein. Das letzte scheint das LSB zu sein
#     #       Daten können ausgelesen werden, OHNE vorher einen CPS Befehl senden zu müssen
#     # ???       What CPS does one get? That one for the first tube? How to get one for the second tube?

#     defname = gd(sys._getframe().f_code.co_name)
#     dprint(defname)

#     wcommand = b'<HEARTBEAT1>>'

#     errmessage      = "none"
#     try:
#         for i in range(1):
#             with  serial.Serial(g.GMC_usbport, g.GMC_baudrate, timeout=g.GMC_timeoutR, write_timeout=g.GMC_timeoutW) as g.GMCser:
#                 bwrt = g.GMCser.write(wcommand)                           # bytes-written (type int)
#                 brec = g.GMCser.read(g.GMCbytes)                          # rec received  (type bytes)
#                 # iydprint(defname, f"brec: {brec}")
#                 for b in brec:
#                     print(f"b: {b}", end="  ")
#                 print()


#     except Exception as e:
#         exceptPrint(e, defname + "'{}'".format(errmessage))

#     GMCread()


# def GMCread():

#     defname = gd(sys._getframe().f_code.co_name)
#     dprint(defname)

#     wcommand    = b'<GETCPS>>'
#     errmessage  = "none"
#     try:
#         for i in range(10):
#             with  serial.Serial(g.GMC_usbport, g.GMC_baudrate, timeout=g.GMC_timeoutR, write_timeout=g.GMC_timeoutW) as g.GMCser:
#                 # bwrt = g.GMCser.write(wcommand)       # bytes-written (type int)  --- not needed when Heartbeat=On!
#                 brec = g.GMCser.read(g.GMCbytes)        # rec received  (type bytes)
#                                                         # ohne write und ohne Heartbeat kommt nix!
#                 for b in brec:
#                     print(f"b: {b}", end="  ")
#                 print()
#             time.sleep(0.0001)  # es kommt nur alle 1 sec

#     except Exception as e:
#         exceptPrint(e, defname + "'{}'".format(errmessage))


# def turnGMC_HeartbeatOFF():
#     # from:  https://www.gqelectronicsllc.com/download/GQ-RFC1801.txt
#     # 4. Turn off the GQ GMC heartbeat
#     # Command:  <HEARTBEAT0>>
#     # Return:   None (Stops the heartbit from the unit.)
#     # Firmware supported:  GMC-500, GMC-500+, GMC-600, GMC-600+

#     defname = gd(sys._getframe().f_code.co_name)
#     dprint(defname)

#     wcommand = b'<HEARTBEAT0>>'

#     errmessage      = "none"
#     try:
#         for i in range(1):
#             with  serial.Serial(g.GMC_usbport, g.GMC_baudrate, timeout=g.GMC_timeoutR, write_timeout=g.GMC_timeoutW) as g.GMCser:
#                 bwrt = g.GMCser.write(wcommand)                           # bytes-written (type int)
#                 brec = g.GMCser.read(g.GMCbytes)                          # rec received  (type bytes)
#                 # iydprint(defname, f"brec: {brec}")
#                 for b in brec:
#                     print(f"b: {b}", end="  ")
#                 print()

#     except Exception as e:
#         exceptPrint(e, defname + "'{}'".format(errmessage))

#     GMCread()

#######################################################################################################################
