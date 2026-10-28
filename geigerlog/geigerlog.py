#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
GeigerLog - A combination of data logger, data presenter, and data analyzer
            to handle Geiger counters as well as environmental sensors for
            Temperature, Pressure, Humidity, CO2, and else

Use document 'GeigerLog-Manual-v<version number>.pdf' for details. The manual is
found in the 'gmanual' folder of GeigerLog's working directory, and online at
https://sourceforge.net/projects/geigerlog/
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
#
# Python version support:
# Python 3.5
#   Python 3.5 reached end of life on September 13th, 2020.
#   pip 21.0 will drop support for Python 3.5 in January 2021.
#   Python 3.5 does NOT support ordered dicts, resulting in major problems!
# Python 3.6
#   Python 3.6 reached end of life on 23 Dec 2021
#   Python 3.6 has no threading HTTP server
# Python 3.7  reached end of life on 27 Jun 2023
#   cannot install PyQt5 anymore

# Python 3.8  will reach end of life on 14 Oct 2024
# Python 3.9  will reach end of life on 05 Oct 2025
# Python 3.10 will reach end of life on 04 Oct 2026
# Python 3.11 will reach end of life on    Oct 2027
# Python 3.12 will reach end of life on    Oct 2028
# Python 3.13 will reach end of life on    Oct 2029
#
# currently supported (Nov 2024):  sarch for:  "GeigerLog supported python versions" in file 'geigerlog.py'

__author__              = "ullix"
__copyright__           = "Copyright 2016 - 2025"
__credits__             = [""]
__license__             = "GPL3"

import os, sys, subprocess, shutil, platform
import traceback
import gglobs as g                                  # import all global vars

# colors
TDEFAULT                = '\033[0m'                 # default, i.e greyish
TRED                    = '\033[91m'                # red
BRED                    = '\033[91;1m'              # bold red
BGREEN                  = '\033[92m'                # light green
BGREEN                  = '\033[92;1m'              # bold green
TYELLOW                 = '\033[93m'                # yellow
BYELLOW                 = '\033[93;1m'              # bold yellow
TCYAN                   = '\033[96m'                # cyan
BCYAN                   = '\033[96;1m'              # bold cyan

defvenv                 = f"__venv{g.__version__}"  # put GeigerLog version into name of Virtual Environment

######################################################################################################

def helpInfo():

    return """
    HELP - Command Line Options and Commands in SETUP mode

    Usage:  on Linux, Mac, Raspi:  ./GeigerLog.sh setup [Options] [Commands]
            on Windows:            GeigerLog.bat  setup [Options] [Commands]

    Options:
        -h, --help          Show this help and exit.

    Commands:
        showlatest          Show all GeigerLog modules in latest and default version
        python3.12          Example to use specific Python version for venv (allowed 3.10, 3.11, 3.12, 3.13)
        piplist             Print a list of all pip installed modules, both from venv and from system
"""


def getPlatform():
    """get computer type"""
    # Python Doc: Returns the system/OS name, such as 'Linux', 'Darwin', 'Java', 'Windows'.
    #             An empty string is returned if the value cannot be determined.

    myplatform  = platform.system().upper()

    if "LINUX" in myplatform:
        g.isRaspi = False
        if is_raspberrypi():                                    # checking for Raspi
                                    g.isRaspi = True
                                    computer  = g.RaspiModel    # like: on Raspi 5: 'Raspberry Pi 5 Model B Rev 1.0'
        else:                       computer  = "Linux"
    elif "WINDOWS" in myplatform:   computer  = "Windows"
    elif "DARWIN"  in myplatform:   computer  = "Mac"
    else:                           computer  = "Unknown"

    return computer


def is_raspberrypi():
    """check if it is a Raspberry Pi computer"""

    defname = "is_raspberrypi: "

    g.RaspiVersion = 0
    g.RaspiModel   = "Not a Raspi"

    try:
        with open('/sys/firmware/devicetree/base/model', 'r') as m:
            g.RaspiModel = m.read().strip().replace("\x00", "")         # apparently a C string; must remove \x00 ending
        # dprint("Raspi Model: ", g.RaspiModel)

        mread = g.RaspiModel.lower()
        if   'raspberry pi 5' in mread:   g.RaspiVersion = 5            # Raspi 5: 'Raspberry Pi 5 Model B Rev 1.0'
        elif 'raspberry pi 4' in mread:   g.RaspiVersion = 4
        elif 'raspberry pi 3' in mread:   g.RaspiVersion = 3            # Raspi 3: 'Raspberry Pi 3 Model B Plus Rev 1.3'
        elif 'raspberry pi 2' in mread:   g.RaspiVersion = 2
        elif 'raspberry pi 1' in mread:   g.RaspiVersion = 1
        else: return False

    except Exception as e:
        # not a Raspi
        return False

    # dprint("    This is a Raspberry Pi computer, model:", g.RaspiModel)

    return True


def dprint(*stuff, end="\n"):
    for a in stuff: print(a, end="")
    print(TDEFAULT)


def gprint(*stuff, end="\n"):
    dprint(BGREEN, *stuff, end=end)


def rprint(*stuff, end="\n"):
    dprint(BRED, *stuff, end=end)


def yprint(*stuff, end="\n"):
    dprint(TYELLOW, *stuff, end=end)


def cprint(*stuff, end="\n"):
    dprint(BCYAN, *stuff, end=end)


def exceptPrint(e, srcinfo):
    """Print exception details (errmessage, file, line no)"""

    defname = "exceptPrint: "

    exc_type, exc_obj, exc_tb = sys.exc_info()
    # rdprint(defname, "sys.exc_info(): ", sys.exc_info(), type(sys.exc_info()), type(exc_type), type(exc_obj), type(exc_tb) )
    # rdprint(defname, "exc_type, exc_obj, exc_tb : ", exc_type, exc_obj, exc_tb,  type(exc_type), type(exc_obj), type(exc_tb) )
    # rdprint(defname, "srcinfo: ", srcinfo)
    if exc_tb is None:
        fname  = "'filename unknown'"
        lineno = "'lineno unknown'"
    else:
        fname  = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]    # which file?
        lineno = exc_tb.tb_lineno

    yprint("EXCEPTION: {} (e:'{}') in file: {} in line: {}".format(srcinfo.replace("\n", " "), e, fname, lineno))
    if g.traceback:
        yprint(traceback.format_exc()) # print only on devel & trace


def printMissingVenvMsg(defname):
    """print fixed msg"""

    rprint()
    rprint(defname, "Cannot find the required Virtual Environment!")
    rprint(defname, "GeigerLog needs to be 'setup' before you can use it")
    rprint()
    rprint(defname, f"************************************************************************")
    rprint(defname, f"Please, start GeigerLog in SETUP-Mode using this command:")
    rprint(defname, f"   - on Linux, Mac, Raspi:   ./GeigerLog.sh setup")
    rprint(defname, f"   - on Windows:             GeigerLog.bat setup")
    rprint(defname, f"************************************************************************")


def startup():
    """Verifies that GeigerLog can run and runs setup or runtime"""

    defname = "startup: "

    if "setup" in sys.argv:
        setup = True
        mode  = "in SETUP mode"
    else:
        setup = False
        mode  = "in RUNTIME mode"

    # clear the terminal
    # docs: os.name:  "The following names have currently been registered: 'posix', 'nt', 'java' (nothing else!)."
    os.system('cls' if os.name == 'nt' else 'clear')

    gprint(f"\nGeigerLog Startup -------------------- {mode} ---------------------------")

    # Cmd line
    dprint(defname, "Command Line:        ", sys.argv)

    if setup:
        if "-h" in sys.argv or "--help" in sys.argv :
            print(helpInfo())
            return

    # System Python
    # 'sys.executable' is like:
    #   Windows:        C:\Users\ullix\AppData\Local\Programs\Python\Python312\python.exe
    #   Linux, Mac:     /usr/bin/python3
    # 'sys.version_info' is like:
    #   Windows:        sys.version_info(major=3, minor=10, micro=12, releaselevel='final', serial=0)
    #   Linux, Mac:     sys.version_info(major=3, minor=10, micro=12, releaselevel='final', serial=0)
    SystemPython = "Python {}.{}.{}".format(*sys.version_info)      # like: Python 3.10.12
    dprint(defname, "System Python:       ", SystemPython)

    # check for working directory
    dirlisting = os.listdir(os.getcwd())
    # yprint(defname, "dirlisting: ", dirlisting)
    if "gsetup.py" in dirlisting and "gmain.py" in dirlisting and "ggeiger.py" in dirlisting and "gglobs.py" in dirlisting:
        # This looks like a GeigerLog working directory
        pass
    else:
        dprint(defname, "This is NOT a GeigerLog working directory! Please, change into it and restart")
        return False

    # check if venv is in working dir
    foundvenv = None
    if defvenv in dirlisting:
        # venv DOES exist
        dprint(defname, f"Virtual Environment: venv found: {defvenv}")
        foundvenv = defvenv

        # find python version used for venv
        # look into file pyvenv.cfg, and search for line starting with 'version'
        with open(os.path.join(defvenv, "pyvenv.cfg"), "rt") as venvcfg:
            for line in venvcfg:
                if line.startswith("version"):  break                               # line    like: 'version = 3.12.4'; ends with "\n"
        venvVersionLine = (line.strip().split(" ")[2]).split(".")                   # list    like: venvVersionLine:  ['3', '12', '5']
        venvPython      = "Python {}.{}".format(*venvVersionLine)                   # string  like: venvPython:       Python 3.12.5
        # venvPython      = "Python {}.{}.{}".format(*venvVersionLine)                   # string  like: venvPython:       Python 3.12.5
        # dprint(defname, f"Virtual Environment: venv uses Python {line.strip()}")
        dprint(defname,  "Virtual Environment: venv uses:  Python {}.{}.{}".format(*venvVersionLine))

    else:
        # venv does NOT exist
        # is ok only if you are doing a setup right now; otherwiase exit
        dprint(defname, f"Virtual Environment: Expected venv directory '{defvenv}' was NOT found")
        if not setup:
            printMissingVenvMsg(defname)
            return

    # on showlatest-request skip further startup and go directly to gsetup
    if "showlatest" in sys.argv:
        if foundvenv is not None:
            dprint(defname, "Completed:           Handing control to GeigerLog 'showlatest' in Virtual Environment")
            if getPlatform() == "Windows": vfolder = "Scripts"
            else:                          vfolder = "bin"
            soutput = subprocess.run([f"./{defvenv}/{vfolder}/python", "gsetup.py"] + sys.argv[1:])
            return

        else:
            printMissingVenvMsg(defname)
            return


### sss
    # setup or runtime
    if setup:
        # here setup begins
        dprint()

        # GeigerLog supported python versions
        supPythons = ["python3.13", "python3.12", "python3.11", "python3.10"]                       # numpy und scipy erfordern >= 3.10
        # supPythons = ["python3.9", "python3.10", "python3.14"]                                    # testing
        dprint(defname, f"{'HELP INFO:':20s} {'Python Versions supporting GeigerLog:'}  {', '.join(p for p in supPythons)}")

        #
        # platform dependent handling
        # Finding Python versions:
        # https://www.askpython.com/python/examples/find-where-python-is-installed
        #
        # Windows
        if getPlatform() == "Windows":
            rprint(defname, f"Computer Type:       Windows")
            # only one python accessible at a time
            defpython  = "python"
            reqPython  = "python"
            venvPython = "python"
            installedPythons = {reqPython : defpython}

        # Linux or Mac
        # works ok on MacBook Pro,on macOS Sequoia 15.3
        elif getPlatform() == "Linux" or getPlatform() == "Mac":
            rprint(defname, f"Computer Type:       Linux or Mac")

            # find installed Pythons:
            dprint(defname, "Python Versions supporting GeigerLog existing on this computer:")
            installedPythons = {}
            for pyv in supPythons:                                                                     # check only for GL useable Pythons
                pyv = pyv.lower().replace(" ", "")
                whereispython = subprocess.run([f"whereis {pyv}"], capture_output=True, shell=True)
                pyr           = whereispython.stdout.decode('UTF-8', errors='replace').strip().split(" ")
                if len(pyr) > 1:
                    # rprint(f"{pyv}  :  {pyr[1]}")
                    installedPythons.update({pyv : pyr[1]})
            if len(installedPythons) == 0:  dprint(defname, "   None found")

            # Installed Pythn versions useable for GeigerLog
            InstalledPythons  = ", ".join(p for p in installedPythons)               # make one long string
            for key, val in installedPythons.items():
                dprint(defname, f"   {key:17s} called by:  {val}")

            # is a supported python version installed?
            defpython = None
            for testPy in supPythons:
                if testPy in InstalledPythons:
                    defpython = testPy              # pick the first (=most recent) Python version
                    break

            if defpython is None:
                rprint(defname, f"No Python version was found which supports GeigerLog!")
                rprint(defname, f"Supporting versions are: {',  '.join(p for p in supPythons)}")
                rprint(defname, f"See the GeigerLog manual for guidance on installing Python")
                return
            else:
                reqPython = defpython
                dprint(defname, f"Virtual Environment: A new default venv would use Python in latest version: '{defpython}'")

###custom
            # is a py version requested on the cmd line?
            custPy = None
            for pycl in sys.argv[1:]:
                if pycl.startswith("python"):
                    custPy   = pycl
                    dprint(defname, f"Virtual Environment: Custom Python requested is '{custPy}'")
                    break

            if custPy is None:
                # no, a custom python was NOT requested
                pass
            else:
                # yes, a custom python was requested
                custPySup = False
                for testPy in supPythons:
                    if custPy.lower().replace(" ", "") == testPy.lower().replace(" ", ""):
                        custPySup = True
                        break

                if custPySup:
                    reqPython = custPy
                    # dprint(defname, f"Virtual Environment: '{testPy}' will be used for venv")
                    pass
                else:
                    rprint(defname, f"Virtual Environment: Custom Python version '{custPy}' is unsufficient to support GeigerLog!")
                    rprint(defname, f"Currently supporting Python versions are:  {',  '.join(p for p in supPythons)}")
                    return

                custPyInstalled = False
                for key, val in installedPythons.items():
                    if custPy in key.lower().replace(" ", ""):
                        custPyInstalled = True
                        break

                if custPyInstalled:
                    # is requested py version a supported one?
                    pass

                else:
                    rprint(defname, f"Requested Custom version '{custPy}' is NOT installed!")
                    rprint(defname, f"Currently installed Python versions are:  {',  '.join(p for p in installedPythons)}")
                    return

        else:
            rprint(defname, f"Computer Type:       Unknown")
            # does this work for an 'unknown' OS?
            # only one python accessible at a time
            defpython  = "python"
            reqPython  = "python"
            venvPython = "python"
            installedPythons = {reqPython : defpython}

        # end Setup per Operating system

        # all OS
        # an already existing venv will first be removed, but ONLY if its python is different from current one
        if foundvenv is not None:
            # yprint(defname, f"reqPython: {reqPython}  venvPython: {venvPython}")
            if reqPython.lower().replace(" ", "") != venvPython.lower().replace(" ", ""):
                dprint(defname, f"Virtual Environment: Removing old venv '{defvenv}'")
                shutil.rmtree(defvenv, ignore_errors=True)
                foundvenv = None
            else:
                dprint(defname, f"Virtual Environment: New Virtual Environment uses same Python as old one; re-using venv")

        # establish venv; create new if needed
        # yprint(defname, f"reqPython: {reqPython}  installedPythons: {installedPythons}")
        try:
            dprint(defname, f"Virtual Environment: Configuring venv as '{defvenv}' using Python '{reqPython}'")
            for qPy in installedPythons:
                # yprint("reqPython: ", reqPython, "   qPy: ", qPy)
                if reqPython.lower().replace(" ", "") in qPy.lower().replace(" ", ""):
                    runPy = installedPythons[qPy]
                    break

            # cmd becomes like:  python -m venv --system-site-packages __venv1.5.1pre22
            if   g.RaspiVersion in (4, 5):  cmd = [runPy, "-m","venv", "--system-site-packages", defvenv]  # für Raspi 4 + 5 when with bookworm
            elif getPlatform() == "Mac":    cmd = [runPy, "-m","venv", "--system-site-packages", defvenv]  # für Mac  needed???
            else:                           cmd = [runPy, "-m","venv", "--system-site-packages", defvenv]  # use it for all ???
            # else:                           cmd = [runPy, "-m","venv", defvenv]  # use it for all ???
            dprint(defname, "Virtual Environment: Creating by cmd: ", " ".join(cc for cc in cmd))
            soutput = subprocess.run(cmd)

        except Exception as e:
            exceptPrint(e, defname + "Creating Virtual Environment. ERROR: ")
            return

        else:
            if soutput.returncode != 0:
                rprint(defname, "FAILURE Creating Virtual Environment. ERROR: Returncode:", soutput.returncode)
                rprint(defname, "Please, retry")
                return
            else:
                gprint(defname, f"Virtual Environment  '{defvenv}'  using '{reqPython}' was established successfully")
                pass

        # ### testing
        # print("TESTING EXIT")
        # sys.exit(9999)
        # ###

        # venv has been created; switch to it for setup
        dprint(defname, f"Completed:           Handing control to GeigerLog setup in Virtual Environment: '{defvenv}'")
        if getPlatform() == "Windows":  cmdp = "Scripts"
        else:                           cmdp = "bin"
        soutput = subprocess.run([f"./{defvenv}/{cmdp}/python", "gsetup.py"] + sys.argv[1:])

    else:
        # runtime begins - running GeigerLog
        dprint(defname, f"Completed:           Handing control to GeigerLog Runtime in Virtual Environment: '{defvenv}'\n")
        if getPlatform() == "Windows":  cmdp = "Scripts"
        else:                           cmdp = "bin"
        soutput = subprocess.run([f"./{defvenv}/{cmdp}/python", "gmain.py"] + sys.argv[1:])
        # cprint(defname, "soutput: ", soutput)
        cprint(f"GeigerLog has finished")

#####################################################################################################

if __name__ == '__main__':
    try:
        startup()
    except KeyboardInterrupt:
        print()
        cprint("Exit by CTRL-C from startup() in geigerlog.py")
        print()

