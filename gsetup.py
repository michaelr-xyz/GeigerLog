#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
GeigerLog - A combination of data logger, data presenter, and data analyzer
            to handle Geiger counters as well as environmental sensors for
            Temperature, Pressure, Humidity, CO2, and else

Start as 'geigerlog -h' for help on available options and commands.
Use document 'GeigerLog-Manual-v<version_number>.pdf' for further details.

This file serves as front-end to verify that Python is installed in proper
version before real GeigerLog is started.
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

########################################################################################################
# RASPI
#
# Raspi 5 does NOT boot when creating an SD image with 32bit-Debian Bullseye. Message:
# --> set os_check=0 in config.txt  --> keine Meldung mehr, aber Raspi 5 bootet gar nicht erst???
# telegram install
# had to remove apt-installed python-telegram-bot and then make pip-install in venv!!!
#
# pyqt5 install - always fails when done in venv on Raspi
# but an apt-installed version can be used when pip command gets --system-site-packages=True  option set


########################################################################################################
# VIRTUAL ENVIRONMENT (venv):
# 2 Options for creating a Virtual Environment for GeigerLog
#
# Option 1 : (NOT recommended) creating a venv and activating it
#
# ~$ python -m venv /home/ullix/geigerlog/geigerlog/venvGL                         # creating the venv venvGL from any directory by giving full path
# Activating the venv:
#   <venv> must be replaced by the path to the directory containing the virtual environment):
#   POSIX:                    source <venv>/bin/activate
#   Windows: cmd.exe:         C:\> <venv>\Scripts\activate.bat
#   Windows: PowerShell:      PS C:\> <venv>\Scripts\Activate.ps1
# De-Activating the venv:
#   all systems:              deactivate
#
# Breaking System:
# see:  https://stackoverflow.com/questions/75608323/how-do-i-solve-error-externally-managed-environment-every-time-i-use-pip-3
# However if you really want to install packages that way, then there are a couple of solutions:
#    use pip's argument --break-system-packages,
#
# alternatively allow system-site-packages by flag in venv call:     python -m venv --system-site-packages venvGL
#
# No '--user' available in venv!
#   -->  b"ERROR: Can not perform a '--user' install. User site-packages are not visible in this virtualenv.\n"
#
# Example for a Linux system:
#   cd /home/ullix/geigerlog/geigerlog                          # change into the GeigerLog working directory
#   python -m venv venvGL                                       # create the venv 'venvGL' - NOT  using flag: --system-site-packages
#   python -m venv --system-site-packages venvGL                # create the venv 'venvGL' - WITH using flag: --system-site-packages
#   source venvGL/bin/activate                                  # activate
#   (venvGL) ullix@urkam:~/geigerlog/geigerlog$                 # --> this is the result
#   (venvGL) ullix@urkam:~/geigerlog/geigerlog$ ./geigerlog     # starting GeigerLog (all Py modules have been installed for a successful start)
#   (venvGL) ullix@urkam:~/geigerlog/geigerlog$ deactivate      # optional - deactivate the venv
#   ullix@urkam:~/geigerlog/geigerlog$                          # --> result; back to normal
#
#
# Option 2 : (RECOMMENDED) using the python scripts
#
# ullix@urkam:~/geigerlog/geigerlog$ ./GeigerLog.sh setup       # starting GeigerLog setup
#   should end with:
#       GeigerLog Setup was successful.
#       From now on simply start GeigerLog with command:  ./GeigerLog.sh
#
# ullix@urkam:~/geigerlog/geigerlog$ ./GeigerLog.sh -dvw devel connect load     # starting GeigerLog with options


########################################################################################################

# VSCODE:
# "files to exclude: " *.proglog, *.stdlog, *data/*, *misc, COPYING, backup*, *.notes, *__venv*
#
# Wiggly red lines under all imports
# see vscode Settings: python.languageserver
#       Default     (-->Pylance if available, fallback is Jedi)
#       Jedi        (nach Neustart: KEINE wiggly lines under imports, aber auch KEINE wrong functions detected! Scheint abgeschaltet)
#       Pylance     (wiggly lines under imports; wrong functions are detected)
#       None        (nirgends wiggly lines, auch nicht bei falschen Funktionen!)
#
# Wiggle lines come both in regular Python call and in VENV call
# when both "code ." is called in Py3.8 venv, dann keine Wiggle lines
# jetzt geht es wieder, egal ob venv oder nicht ???? languageserver ist auf Default (=Pylance)


########################################################################################################
# compile python  ######################################################################################
########################################################################################################
# compiling Python 3.12.5
# How to install Python 3.12.5 on Debian 11 bullseye
# see:  https://aruljohn.com/blog/install-python-debian/
#
# compiling Python 3.11:
# Build Instructions
# ------------------
# On Unix, Linux, BSD, macOS, and Cygwin::
#     ./configure
#     make
#     make test
#     sudo make altinstall
#
# DON'T EVER DO THIS:  #     sudo make install
#     as this will install Python as `python3`, overwriting system Python, destroying system!!!
#
# Installing multiple versions
# ----------------------------
# On Unix and Mac systems if you intend to install multiple versions of Python
# using the same installation prefix (``--prefix`` argument to the configure
# script) you must take care that your primary python executable is not
# overwritten by the installation of a different version.  All files and
# directories installed using ``make altinstall`` contain the major and minor
# version and can thus live side-by-side.  ``make install`` also creates
# ``${prefix}/bin/python3`` which refers to ``${prefix}/bin/python3.X``.  If you
# intend to install multiple versions using the same prefix you must decide which
# version (if any) is your "primary" version.  Install that version using ``make
# install``.  Install all other versions using ``make altinstall``.

# For example, if you want to install Python 2.7, 3.6, and 3.11 with 3.11 being the
# primary version, you would execute ``make install`` in your 3.11 build directory
# and ``make altinstall`` in the others.

# install Python from source
# CAREFUL: see 'altinstall' option!!!
#
# https://docs.rstudio.com/resources/install-python-source/
# ./configure \
#     --prefix=/opt/python/${PYTHON_VERSION} \
#     --enable-shared \
#     --enable-optimizations \
#     --enable-ipv6 \
#     LDFLAGS=-Wl,-rpath=/opt/python/${PYTHON_VERSION}/lib,--disable-new-dtags
#
# make
# sudo make altinstall
#
# remember:
# "The altinstall target will make sure the default Python on your machine is not touched,
#  or to avoid overwriting the system Python."
#
# To add to path: make File: /etc/profile.d/python.sh with content:
#   export PATH=$PATH:/opt/python/3.13.1/bin/
#


# *********************
# ***** WARNINGS: *****
# *********************
#   Linux install:  python3-venv must have been installed
#   pip             with error message: "There was an error checking the latest version of pip" do: rm -r ~/.cache/pip/selfcheck/
#                   see: https://stackoverflow.com/questions/72439001/there-was-an-error-checking-the-latest-version-of-pip
#   numpy           Do NOT use numpy 1.25.0 or 1.25.1 as there is a bug!!!   Use older 1.24.4, or later 1.26.1 and 1.26.2
#                   latest version 2.1.0  REQUIRES Python >= 3.10
#   scipy           latest version 1.14.1 REQUIRES Python >= 3.10
#   matplotlib      3.5.0 konnte NICHT installiert werden - auch nicht manuell - aber 3.6.0 konnte ???
#   matplotlib      Version: 3.9.1   was YANKED  https://pypi.org/project/matplotlib/#history
#   libportaudio2   musste manuell installiert werden
#   smbus           dead project? - last update: 8. März 2019 to version '1.1.post2'
#   smbus2          alive project - last update 25. Aug. 2023 to version: 0.4.3
#
#   seen on Raspi 4:
#      pyserial== (from versions: 2.3, 2.4, 2.5, 2.6, 2.7, 3.0, 3.0.1, 3.1, 3.1.1, 3.2, 3.2.1, 3.3, 3.4, 3.5b0, 3.5)
#      pyserial     version: 3.5b0    # ?3.5b0 is < 3.5 ???
#
#   seen on Raspi 5:
#      RPi.GPIO     version: 0.7.1a4
#      smbus2       version: 0.4.2
#
#   new needed for Raspi 5:
#      rpi-lgpio    version: 0.4



__author__              = "ullix"
__copyright__           = "Copyright 2016 - 2025"
__credits__             = [""]
__license__             = "GPL3"

import os, sys, subprocess, platform, pathlib
import gglobs as g                                  # import all global vars
from   geigerlog     import getPlatform

# colors
TDEFAULT                = '\033[0m'                 # default, i.e greyish
TRED                    = '\033[91m'                # red
BRED                    = '\033[91;1m'              # bold red
BGREEN                  = '\033[92m'                # light green
BGREEN                  = '\033[92;1m'              # bold green
TYELLOW                 = '\033[93m'                # yellow
TCYAN                   = '\033[96m'                # cyan
BCYAN                   = '\033[96;1m'              # bold cyan


class globalvars():
    """Variables to use globally"""

    GLinstalls_Base = {
        # name                     version       comment                                         # purpose

        "pip"                   : [[25,  1,  1], "required, Base"],                              # module handling
        "setuptools"            : [[80,  9,  0], "required, Base"],                              # module handling
        "wheel"                 : [[ 0, 45,  1], "required, Base"],                              # module handling
        "PyQt6"                 : [[ 6,  9,  0], "required, Base"],                              #
        "pillow"                : [[11,  2,  1], "required, Base"],                              # needed for matplotlib (still needed 2024-08-05)
        "numpy"                 : [[ 2,  2,  6], "required, Base"],                              # math and stats
        "scipy"                 : [[ 1, 15,  3], "required, Base"],                              # math and stats; latest is 1.14.0
        "matplotlib"            : [[ 3, 10,  3], "required, Base"],                              # plotting   # MUST NOT use Version: 3.9.1 - see WARNINGS above!
        "cffi"                  : [[ 1, 17,  1], "required, Base"],                              # required by soundfile AND sounddevice
        # see claim for solution: https://stackoverflow.com/questions/69245722/error-259-on-python-playsound-unable-to-sound : use 1.2.2
        # "playsound"           : [[ 1,  3,  0], "required, Base"],  1.3.0 fails on win11        # Sound playing; using the old, original playsound:https://pypi.org/project/playsound/
        "playsound"             : [[ 1,  2,  2], "required, Base"],                              # Sound playing; using the old, original playsound:https://pypi.org/project/playsound/
        "sounddevice"           : [[ 0,  5,  2], "required, Base"],                              # Sound making / playing, AudioCounter Series
        # "playsound3"          : [[ 3,  2,  3], "required, Base"],                              # Sound playing, bips and burps; fork of playsound; # https://pypi.org/project/playsound3/
        # "play_sounds"         : [[ 0,  6,  0], "required, Base"],                              # playing sound

        "pyserial"              : [[ 3,  5,   ], "required, Base"],                              # Serial Port for GMC, GammaScout, I2C, Ambiomon, Pulse
                                                                                                 # platformio 6.1.11 requires pyserial==3.5.* !!!
        "paho-mqtt"             : [[ 2,  1,  0], "required, Base"],                              # mqtt for IOT Series, RadMon Series
        "psutil"                : [[ 7,  0,  0], "required, Base"],                              # system details (CPU, Memory, ...)
        "ntplib"                : [[ 0,  4,  0], "required, Base"],                              # Network Time Protocol Check
        "py-cpuinfo"            : [[ 9,  0,  0], "required, Base"],                              # CPU info
        "bmm150"                : [[ 0,  2,  2], "required, Base"],                              # Handling I2C BMM150 Geomagnetic device

        "lxml"                  : [[ 5,  4,  0], "required, Base"],                              # handling XML files
        "fpdf"                  : [[ 1,  7,  2], "required, Base"],                              # generating pdf files

        "LabJackPython"         : [[ 2,  1,  0], "optional, required for LabJack Series"],       # required for LabJack device
        "pip-check"             : [[ 3,  1    ], "optional, recommended tool for Pip"],          # convenient tool
        "simplepyble"           : [[ 0, 10,  3], "required, Base"],                              # Bluetooth support
        "fritzconnection"       : [[ 1, 15,  0], "optional, required for FritzBox"],             # Fritzbox support

      # "pyqtgraph"             : [[ 0, 13,  7], "required, Base"],                              # Graphic pyqt support
      # "python-telegram-bot"   : [[13, 15,   ], "optional, required for Telegram Messenger"],   # required for using Telegram; MUST (!!!) stay at version 13.15
      # "urllib3"               : [[ 2,  1,  0], "optional, required for Telegram Messenger"],   # required for using Telegram; not used elsewhere!
    }

    GLinstalls_Raspi = {
        "PyQt6"                 : [[ 6,  4,  2], "required, Base"],                              # GUI - only on Raspi!
        "RPi.GPIO"              : [[ 0,  7,  1], "optional, required for RaspiPulse Series - install ONLY on Raspberry Pi Versions 1,2,3,4"   ], # reading Raspi pins
        "smbus2"                : [[ 0,  4,  3], "optional, required for RaspiI2C Series   - install ONLY on Raspberry Pi"   ], # improved alternative to smbus
    }

    GLinstalls_Raspi5 = {
        "PyQt6"                 : [[ 6,  4,  2], "required, Base"],                              # GUI - only on Raspi!
        "rpi-lgpio"             : [[ 0,  4,   ], "optional, required for RaspiPulse Series - install ONLY on Raspberry Pi Version 5"   ], # reading Raspi pins
        "smbus2"                : [[ 0,  4,  3], "optional, required for RaspiI2C Series   - install ONLY on Raspberry Pi"   ], # improved alternative to smbus
    }

    GLinstalls              = GLinstalls_Base
    pipdict                 = {}

### end of class globalvars()

# instantiate globalvars for this script only
gv = globalvars

# holding venv versions
VenvPythonExc = sys.executable   # gesetup must have been started in venv!


######################################################################################################


def removeModules(myremoves):
    """###CAREFUL! -- this may remove all modules except pip and setuptools ###################################"""

    defname = "removeModules: "

    dprint("\nRemoving Python Modules - but keeping pip and setuptools")

    for pname in gv.GLinstalls:
        dprint("module: {:20s} :".format(pname), end="")
        if pname == "pip" or pname == "setuptools":
            dprint("don't kill yourself! - keeping:", pname)
            continue
        elif pname in myremoves:
            dprint("uninstall: ", pname)
            pip_output = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', pname], capture_output=True)
            # rprint(defname, "pip_output: ", pip_output)
            for a in pip_output.stdout.decode('UTF-8', errors='replace').strip().split("\n"):
                dprint(a.strip(), end="\n")
                rprint(pip_output.stderr.decode('UTF-8', errors='replace').strip())
        else:
            dprint("keeping:   ", pname)

    return False


def executePipCommand(pname, latest=False):
    """Execute any command on shell"""

    defname = "executePipCommand: "

    if latest: pipcmd = [VenvPythonExc, '-m', 'pip', 'install', '-U', pname]   # '-U' for update
    else:      pipcmd = [VenvPythonExc, '-m', 'pip', 'install',       pname]   # forcing predefined version (as part of pname, like: '==1.2.3')
    dprint("   ", defname, "Installing with Command:", " ".join(c for c in pipcmd))

    pip_output = subprocess.run(pipcmd, capture_output=True)
    for pipout in pip_output.stdout.decode('UTF-8', errors='replace').split("\n"):
        if pipout > "":  dprint("    pipout: " + pipout)

    for piperr in pip_output.stderr.decode('UTF-8', errors='replace').split("\n"):
        if piperr > "": rprint("    piperr: " + piperr)

    if pip_output.returncode == 0:
        gprint("   ", defname, "    Sussessful\n")
        return True
    else:
        rprint("   ", defname, f"    FAILURE executing command: {' '.join(c for c in pipcmd)}\n")
        return False


def installModulesToLatest(selection="All"):
    """update all modules in selection to the latest version"""

    defname = "installModulesToLatest: "

    if selection == "All": modules = gv.GLinstalls.keys()
    else:                  modules = selection

    for pname in modules:
        dprint("Module: {:20s}".format(pname))

        ### handle Telegram:
        # module = pname
        # if pname == "python-telegram-bot":
        #     dprint(TRED + "    Version MUST stay frozen at 13.15!" + TDEFAULT)
        #     module = pname + "==13.15"

        cprint("    Installing LATEST")
        success = executePipCommand(pname, latest=True)

    return success


def installModulesToDefault(ListOnly=False):
    """
    Checks for complete installation and installs modules where needed
    return: True on success
            False on failure
    """

    defname = "installModulesToDefault: "

    needInstall = {}

    # check which modules need update
    getPipList("venv")    # to fill gv.pipdict

    # for pd in gv.pipdict:
    #     yprint(pd, gv.pipdict[pd])

    for pname in gv.GLinstalls:
        print(f"        Module:     {pname:20s}", end= " ")
        # cprint(defname, f"        GLinstalls: {gv.GLinstalls[pname]}")
        minversion = ".".join(str(x) for x in gv.GLinstalls[pname][0])
        # cprint(defname, f"        minversion: {minversion}")
        # yprint(defname, f"        gv.pipdict: {gv.pipdict[pname]}")

        if pname in gv.pipdict:                                     # does the key == modul exist?
            pipv   = gv.pipdict[pname]
            # yprint(defname, f"pipv: {pipv}")
            lnpipv = []                                             # holder for list of numbers
            for i, tt in enumerate(pipv.split(".")):                # convert to list of numbers if possible
                try:    lnpipv.append(int(tt))
                except: lnpipv.append(tt.strip())                   # does seem to contain alphanumerics

            # yprint(f"  pipv: {pipv:6s}  lnpipv: {lnpipv}", end="   ")
            dprint("Installed Version: {:15s}  Min Version: {:15s}".format(pipv, minversion), end=" ")

            if gv.GLinstalls[pname][0] > lnpipv:
                dprint("{:10s}".format(": Needs version {:10s}".format(minversion)), end="")
                needInstall.update({pname : True})
            else:
                dprint("{:10s}".format(": Ok"), end="")

        else: # pname NOT found in gv.pipdict
            # rprint(defname, f"pname '{pname}' NOT found")
            print("Installed Version: {:15s}  Min Version: {:15s} {:10s}".format("None", minversion, ": MISSING"), end=" ")
            needInstall.update({pname : True})

        # # add msg to printout - only for python-telegram-bot
        # if pname == "python-telegram-bot":
        #     # dprint(pipv, "  ", minversion, end="  -  ")
        #     if pipv != minversion:
        #         needInstall.update({pname : True})
        #         dprint("{:10s}".format(": Needs version {:10s}".format(minversion)), end="")
        #     dprint("NOTE: Module '" + pname + "' MUST stay frozen at version 13.15", end="")

        dprint()

    if ListOnly: return


    #
    # This does the install if anything needs installation
    #
    if len(needInstall) == 0:
        # nothing needs to be installed
        dprint("Installation is complete; no errors.\n")
        success = True

    else:
        # needs one or more installs
        cprint()
        cprint(defname, "Some modules need installation or update:")

        failures = 0
        for pname in needInstall:
            dprint("Module: {:20s}".format(pname), end="   ")
            pnameversion = ".".join(str(x) for x in gv.GLinstalls[pname][0])
            dprint("    Forcing Version: ", pnameversion)
            failures += not (executePipCommand(f"{pname}=={pnameversion}", latest=False))

        if failures == 0:
            dprint("Installation is complete; no errors.\n")
            success = True
        else:
            rprint("Installation or update had errors!")
            success = False

    return success


def getPipList(typePython):
    """get and return the full 'pip list' either from "venv" or from OS-default like "python" """

    defname = "getPipList: "

    if typePython == "venv": cmd = [VenvPythonExc, '-m', 'pip', 'list']  # from venv
    else:                    cmd = ["python",      '-m', 'pip', 'list']  # from e.g. OS default

    pip_output = subprocess.check_output(cmd)
    piplist    = pip_output.decode('UTF-8', errors='replace').strip().split("\n")     # like: piplist = 'PyQt5_sip             12.15.0', 'pyserial              3.5', ...
    # yprint(defname, f"piplist: {piplist}")  # pip is 25.1

    gv.pipdict = {}
    for pl in piplist:
        snr = pl.split(" ", 1)
        pdu = {snr[0].strip(): snr[1].strip()}
        gv.pipdict.update(pdu)

    # yprint(defname, f"piplist: {piplist}")  # pip is 25.1

    return piplist


def printPipList():
    """make pip list both from OS-default and venv"""
    # piplist is like:  'setuptools            59.6.0', 'PyQt5                 5.15.6', ...

    defname = "printPipList: "

    cprint(defname)
    dprint(f"PIP Module Listing from venv: '{g.VenvName}'")
    piplist = getPipList("venv")
    counter = 0
    for pl in piplist:
        ppl = pl.split()[0].strip()
        if ppl in gv.GLinstalls.keys():
            counter += 1
            dprint(f"   {counter:2d}  {pl}")

    dprint(f"\nPIP Module Listing from OS-default")
    piplist = getPipList("default")
    counter = 0
    for pl in piplist:
        ppl = pl.split()[0].strip()
        if ppl in gv.GLinstalls.keys():
            counter += 1
            dprint(f"   {counter:2d}  {pl}")

    dprint()


def dprint(*stuff, end="\n"):
    print(*stuff, end=end)


def gprint(*stuff, end="\n"):
    print(BGREEN, end="")
    print(*stuff, end=end)
    print(TDEFAULT, end="")


def rprint(*stuff, end="\n"):
    print(BRED, end="")
    print(*stuff, end=end)
    print(TDEFAULT, end="")


def yprint(*stuff, end="\n"):
    print(TYELLOW, end="")
    print(*stuff, end=end)
    print(TDEFAULT, end="")


def cprint(*stuff, end="\n"):
    print(BCYAN, end="")
    print(*stuff, end=end)
    print(TDEFAULT, end="")


def setup():

    defname = "setup: "

    cprint("\nGeigerLog Setup " + "-"*70)

    # checking for computer type
    dprint(defname, f"This is a '{getPlatform()}' computer")

    if   g.RaspiVersion == 5:           gv.GLinstalls |= gv.GLinstalls_Raspi5     # only Raspi 5
    elif g.RaspiVersion in (1,2,3,4):   gv.GLinstalls |= gv.GLinstalls_Raspi      # all other Raspi
    else:                               pass                                      # is not a Raspi

    # checking for running in venv
    if sys.prefix != sys.base_prefix:
        g.isSetVenv     = True
        g.VenvName      = pathlib.Path(sys.prefix).parts[-1]
        g.VenvMessage   = f"{g.VenvName}"
    else:
        rprint(defname, "FAILURE: NOT running in a Virtual Environment! Cannot continue!")
        if getPlatform() == "Windows":   command = "GeigerLog.bat setup"
        else:                            command = "./GeigerLog.sh setup"
        rprint(f"Please, restart GeigerLog Setup with: '{command}'")
        dprint()
        return False

    dprint(defname, f"Virtual Environment:  {g.VenvMessage}")
    dprint(defname, f"Virtual Environment:  Has Python Executable: {VenvPythonExc}")

    # this Python's version
    dprint(defname,  "Virtual Environment:  Using Python version:  {}.{}.{}".format(*sys.version_info) )
    dprint(defname,  "    sys.base_prefix: ", sys.base_prefix)
    dprint(defname,  "    sys.prefix:      ", sys.prefix)
    dprint()

    # check and show latest version
    if "showlatest" in sys.argv:
        dprint(defname, "Showing Modules with Minimal, Installed, and Latest Versions:")
        dprint(f"    {'Module':20s} {'Minimal':15s} {'Installed':15s} {'Latest':15s}")
        # yprint(defname, "gv.GLinstalls: ", gv.GLinstalls)
        for pname in gv.GLinstalls:
            pip_output = subprocess.run([VenvPythonExc, '-m', 'pip', 'index', 'versions', pname], capture_output=True)
            pipLatVers = pip_output.stdout.decode('UTF-8', errors='replace').split("\n")[0].split(" ")
            latversion = pipLatVers[1].strip()[1:-1]                                          # strip '\r' on windows and exclude the '(' and ')'

            pip_output = subprocess.run([VenvPythonExc, '-m', 'pip', 'show',pname], capture_output=True)
            # yprint(defname, "pip_output: ", pip_output)
            listpip_output = pip_output.stdout.decode('UTF-8', errors='replace').split("\n")
            # yprint(defname, "listpip_output: len: ", len(listpip_output), listpip_output)
            if len(listpip_output) > 1:
                pipLatVers = listpip_output[1]
                is_version = pipLatVers.split(" ")[1].strip()
            else:
                is_version = "MISSING"

            minversion = ".".join(str(x) for x in gv.GLinstalls[pname][0])

            dprint(f"    {pname:20s} {minversion:15s} {is_version:15s}", end=" ")
            if is_version == latversion: dprint(f"{latversion}")
            else:                        rprint(f"{latversion}")

        dprint()
        return

    # remove modules
    if "remove" in sys.argv:
        myremoves  = gv.GLinstalls                                                            # alles (ausser pip und setuptools)
        myremoves  = ("psutil", "urllib3", "paho-mqtt", )                                     # limit the deletions to these modules
        removeModules(myremoves)
        return

    # pip list all modules in venv and system
    if "piplist" in sys.argv:
        printPipList()

    # update to latest modules - CAUTION - better to NOT use - may result in conflicting versions!
    if "latest" in sys.argv:
        success = installModulesToLatest()

    # doing default install
    else:
        cprint(defname, "Initial Module Status: ")
        success = installModulesToDefault()                                                 # install GeigerLog-specified module minimal versions

    # cleanup GeigerLog configs
    if success:
        try:
            progDir           = os.path.dirname(os.path.realpath(__file__))                 # /home/ullix/geigerlog/geigerlog
            configDir         = g.configDirectory                                           # "gconfig"

            # remove settings File
            settingsFile      = os.path.join(progDir, configDir, "geigerlog.settings")      # /home/ullix/geigerlog/geigerlog/gconfig/geigerlog.settings
            if os.path.exists(settingsFile):
                dprint(defname, f"Removing the settings file '{settingsFile}'")
                os.remove(settingsFile)

        except Exception as e:
            yprint(defname, f"Exception: {e}")

    cprint()
    cprint(defname, "Final Module Status:")
    installModulesToDefault(ListOnly=True)     # to get a list of the installed modules AFTER installation; no further action

    # Final statement for starting
    if success:
        if getPlatform() == "Windows":   command = "GeigerLog.bat"      # Windows
        else:                            command = "./GeigerLog.sh"     # Linux, Mac, (other?)
        dprint()
        stars = f"*" * 90
        gprint(stars)
        dprint(f"GeigerLog has been set up successfully. From now on start GeigerLog with:  {BGREEN + command + TDEFAULT}")
        dprint(f"For more options see GeigerLog Manual chapter 'Auto-Starting GeigerLog'")
        gprint(stars)
        dprint()

#####################################################################################################

if __name__ == '__main__':
    try:
        setup()
        if "piplist" in sys.argv: printPipList()

    except KeyboardInterrupt:
        print()
        rprint("Exit by CTRL-C from setup() in gsetup.py")
        print()

