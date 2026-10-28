#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gsup_config.py - GeigerLog support file to evaluate the configuration

include in programs with:
    import gsup_config
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


def readGeigerLogConfig(filename):
    """reading the configuration file, return if not available.
    Not-available or illegal options are being ignored with only a debug message"""

    ######  local functions  ###########################################################
    def getConfigEntry(section, parameter, ptype, fallback="auto"):
        """utility for reading GeigerLog Config"""

        defname = gd(sys._getframe().f_code.co_name)

        # ### Testing
        # fallback = "fallback"
        # ###

        errmsg = ""

        try:
            if config.has_option(section, parameter):
                # option DOES exist
                # optval = config.get(section, parameter, raw=False, vars=None, fallback=fallback) # optval is type:str
                optval = config.get(section, parameter, raw=False, vars=None) # optval is type:str
                # if section == "WiFiServerDevice": iydprint(defname, f"optval: {optval}")

                ### a comment beginning with "#" may be in a 1 line or multi-line configuration
                newov = ""
                if "#" in optval:
                    for ov in optval.split("\n"):
                        if ov.find("#") != -1: optval = ov[0: ov.find("#")]  # remove comments
                        else:                  optval = ov                   # no comment "#" found
                        newov += optval + "\n"
                    optval = newov

                # ### testing
                # if optval == "fallback":
                #     # never observed so far!
                #     mdprint(defname, f"section: {section:18s}  parameter: {parameter:22s}  ptype: {ptype:6s}  optval: {optval}  optval_type: {type(optval)}")
                # ###

            else:
                # option does NOT exist
                #   IS  an error when in  "geigerlog.cfg"
                #   NOT an error when in  "custom.cfg"
                optval = "MISSING"
                if filename == "geigerlog.cfg":
                    errmsg = f"Cannot find section:  [{section}]  with parameter: {parameter}"
                    rdprint(defname, errmsg)
                    g.configAlerts += errmsg + "\n"

        except Exception as e:
            errmsg += f"Section: {section}, Parameter: {parameter}\n\nProblem: {e}"
            g.configAlerts += errmsg + "\n\n"
            edprint("WARNING: " + errmsg)
            return "WARNING"

        if   ptype == "str":    optval = optval.strip().replace(" ", "")
        if   ptype == "rawstr": optval = optval.strip()
        elif ptype == "upper":  optval = optval.strip().replace(" ", "").upper()

        return optval


    def cfg_dprint(text):
        dprint("cfg: " + text)
        g.configMsg += text + "\n"


    ####### END local function ###########################################################

    defname = gd(sys._getframe().f_code.co_name)

    dprint()
    dprint(defname, f"Reading '{filename}'")
    setIndent(1)

    infostrHeader = "{:35s} {}"
    infostr       = "    {:35s}: {}"

    if filename == "custom.cfg":    ConfigFile = g.configCustomFile     # filename == "custom.cfg"
    else:                           ConfigFile = g.configFile           # filename == "geigerlog.cfg"


    g.configMsg += f"\nConfiguration from file <b>'{filename}':</b>\n\n"

    while True:

    # does the geigerlog.cfg file exist and can it be read?
        if filename == "geigerlog.cfg":
            if not os.path.isfile(ConfigFile) or not os.access(ConfigFile, os.R_OK) :
                msg = f"Configuration file <b>'geigerlog.cfg'</b> in folder <b>'{g.configDirectory}'</b> does not exist or is not readable."
                edprint(msg)
                msg += "<br><br>Please check and correct. <br><br>Cannot continue, will exit."
                g.startupProblems = msg
                break
        else:
            # filename == "custom.cfg":
            if not os.path.isfile(ConfigFile) or not os.access(ConfigFile, os.R_OK) :
                msg = f"Custom Configuration file 'custom.cfg' in folder '{g.configDirectory}' does not exist or is not readable. Creating it now."
                dprint(msg)
                makeCustomCfgTemplate()


    # is the geigerlog.cfg file error free?
        try:
            config = configparser.ConfigParser()
            with open(ConfigFile) as f:
               config.read_file(f)
        except Exception as e:
            exceptPrint(e, defname)
            emsg = (str(sys.exc_info()[1])).replace(":", ":\n")
            msg  = "Configuration file <b>'geigerlog.cfg'</b> cannot be interpreted."
            msg += "\n\nNote that duplicate entries are not allowed!"
            msg += "\n\nERROR Message:\n" + emsg
            msg += "\n\nPlease check and correct. Cannot continue, will exit."
            g.startupProblems = msg.replace("\n", "<br>")
            break

    # the config file exists and can be read:
        cfg_dprint(infostrHeader.format("Startup values", ""))

    # Logging
        t = getConfigEntry("Logging", "LogCycle", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "AUTO":                         g.LogCycle = 1
            else:
                try:    g.LogCycle = max(0.1, float(t))
                except: g.LogCycle = 1
            cfg_dprint(infostr.format("Logcycle (sec)",  g.LogCycle))


    # DataDirectory
        t = getConfigEntry("DataDirectory", "DataDir", "str")
        if t not in ("WARNING", "MISSING"):
            errmsg = "WARNING: "
            try:
                if t.upper() == "AUTO":
                    pass                        # no change to default = 'data'
                else:
                    if os.path.isabs(t): testpath = t                           # is it absolute path? yes
                    else:                testpath = g.dataDir + "/" + t   # it is relative path? yes
                    #cdprint("path:", testpath)

                    # Make sure the data directory exists; create it if needed
                    # ignore if it cannot be made or is not writable
                    if os.access(testpath, os.F_OK):
                        # dir exists, ok
                        if not os.access(testpath , os.W_OK):
                            # dir exists, but is not writable
                            errmsg += "Configured data directory '{}' exists, but is not writable".format(testpath)
                            raise NameError
                        else:
                            # dir exists and is writable
                            g.dataDir = testpath
                    else:
                        # dir does not exist; make it
                        try:
                            os.mkdir(testpath)
                            g.dataDir = testpath
                        except:
                            # dir cannot be made
                            errmsg += "Could not make configured data directory '{}'".format(testpath)
                            raise NameError

            except Exception as e:
                cfg_dprint(errmsg, "; Exception:", e)

            cfg_dprint(infostr.format("Data directory", g.dataDir))



    ### from the config file - removed
    # # USEVENVSUBDIR
    # # When you create Virtual Environments (venv) you get the ability to run an unlimited
    # # number of GeigerLog instances from the same code base.
    # #
    # # This would create problems when those many instances all use the same resources of
    # # GeigerLog. Therefore you have the option of creating subdirectories, each with the
    # # name of the venv, which give each instance of GeigerLog separate resources.
    # #
    # # If you run only a single instance of GeigerLog, I suggest to NOT have
    # # subdirectories and have this setting at 'no'!
    # #
    # # Options:      no | yes
    # # Default     = no
    # UseVenvSubDir = no

    # # USEVENVSUBDIR
    #     t = getConfigEntry("DataDirectory", "UseVenvSubDir", "upper")
    #     if t not in ("WARNING", "MISSING"):
    #         if   t == "AUTO":                     g.useVenvDirectory = False
    #         elif t == "YES":                      g.useVenvDirectory = True
    #         else:                                 g.useVenvDirectory = False
    #     cfg_dprint(infostr.format("UseVenvSubDir", g.useVenvDirectory))


    # [TimeZone]
    # # UTC Correction
    # # The time difference between time at your location and UTC time is recognized
    # # by GeigerLog automatically.
    # #
    # # However, browsers like Firefox and Chrome have the unfortunate property of converting
    # # all Javascript time formats as if they were UTC times. Other browsers may respond
    # # differently, so if the automatic correction fails, you can enter the desired
    # # correction here.
    # #
    # # The value entered here is ADDED to the times found by the browsers. E.g., Germany
    # # has a (negative) 1 h offset to UTC in wintertime, and 2h in summertime.
    # # So, in summertime correct with  -2 * 3600 (= minus 7200) sec.
    # #
    # # NOTE: For some odd political reasons the maximum plus time zone is indeed 14h and
    # # not 12h! (https://en.wikipedia.org/wiki/Time_zone)
    # #
    # # Option auto (recommended) defaults to the automatic calculation.
    # #
    # # Options:        auto | <any number from -43200 (=-12*3600) to +50400 (=+14*3600)>
    # # Default       = auto
    # TimeZoneUTCcorr = auto

    # TimeZone Offset to UTC
        t = getConfigEntry("TimeZone", "TimeZoneOffset", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "AUTO":                                 g.TimeZoneOffset = "auto"
            else:
                try:
                    tzuc = int(float(t))
                    if -12 * 3600 <= tzuc <= +14 * 3600:    g.TimeZoneOffset = tzuc
                    else:                                   g.TimeZoneOffset = "auto"
                except Exception as e:
                    exceptPrint(e, "TimeZoneOffset has non-numeric value: '{}'".format(t))
                    g.TimeZoneOffset = "auto"

            cfg_dprint(infostr.format("TimeZone Offset",        g.TimeZoneOffset))


    # # Manual
    #     t = getConfigEntry("Manual", "ManualName", "str")
    #     if t not in ("WARNING", "MISSING"):
    #         if t.upper() == "AUTO" or t == "":
    #             g.manual_filename = "auto"
    #             dprint(infostr.format("Filename GeigerLog Manual",      g.manual_filename))
    #         else:
    #             pathisabs = os.path.isabs(t)
    #             if pathisabs: manual_file = t
    #             else:         manual_file = os.path.join(getPathToProgDir(), t)
    #             if os.path.isfile(manual_file):     # does the file exist?
    #                 # it exists
    #                 g.manual_filename = t
    #                 dprint(infostr.format("Filename GeigerLog Manual",  g.manual_filename))
    #             else:
    #                 # it does not exist
    #                 g.manual_filename = "auto"
    #                 dprint("WARNING: Filename GeigerLog Manual '{}' does not exist".format(t))


    # Monitor Server
        cfg_dprint(infostrHeader.format("Monitor Server", ""))

        # MonServer Autostart
        t = getConfigEntry("MonServer", "MonServerAutostart", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if     t == "NO":                                g.MonServerAutostart = False
            else:                                            g.MonServerAutostart = True
            cfg_dprint(infostr.format("MonServer Autostart", g.MonServerAutostart))

        # MonServer SSL
        t = getConfigEntry("MonServer", "MonServerSSL", "upper")
        if t not in ("WARNING", "MISSING"):
            if     t == "YES":                               g.MonServerSSL = True
            else:                                            g.MonServerSSL = False
            cfg_dprint(infostr.format("MonServer SSL",       g.MonServerSSL))

        # MonServer Port
        t = getConfigEntry("MonServer", "MonServerPort", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "AUTO":                                  g.MonServerPorts = "auto"
            else:
                default = False
                mspraw = t.split(",")
                # edprint("mspraw: ", mspraw)
                MSPorts = []
                for pn in mspraw:
                    pn = pn.strip()
                    if pn == "":    continue
                    try:
                        tport = int(float(pn))
                        # edprint("tport: ", tport)
                        if 1024 <= tport <= 65535:
                            MSPorts.append(tport)
                        else:
                            default = True
                            break
                    except Exception as e:
                        exceptPrint(e, "MonServerPort has non-numeric value")
                        default = True
                        break

                if default: g.MonServerPorts = "auto"
                else:       g.MonServerPorts = MSPorts

            cfg_dprint(infostr.format("MonServer Port",         g.MonServerPorts))

        # MonServerThresholds (low, high)
        t = getConfigEntry("MonServer", "MonServerThresholds", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "AUTO":                                         g.MonServerThresholds = "auto"
            else:
                ts = t.split(",")
                if len(ts) == 2:
                    try:
                        lo = float(ts[0])
                        hi = float(ts[1])
                        if lo > 0 and hi > lo:                      g.MonServerThresholds = (lo, hi)
                        else:                                       g.MonServerThresholds = "auto"
                    except:
                        g.MonServerThresholds = "auto"
                else:
                    g.MonServerThresholds = "auto"

            cfg_dprint(infostr.format("MonServer Thresholds",   g.MonServerThresholds))


        # MonServerPlotConfig       (Default:  10, 0, 1, auto, auto, auto)
        t = getConfigEntry("MonServer", "MonServerPlotConfig", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "AUTO":                                         g.MonServerPlotConfig = "auto"
            else:
                ts = t.replace(" ", "").split(",")
                if len(ts) == 6:
                    try:
                        plotlen = clamp(    float(ts[0]),  0.1, 1500)
                        plottop = clamp(int(float(ts[1])),   0, 11)
                        plotbot = clamp(int(float(ts[2])),   0, 11)

                        try:    plotMin = float(ts[3])
                        except: plotMin = "auto"
                        try:    plotMax = float(ts[4])
                        except: plotMax = "auto"

                        plotrefresh = ts[5]
                        if plotrefresh == "AUTO":
                            plotrefresh = "auto"
                        else:
                            try:    plotrefresh = float(plotrefresh)
                            except: plotrefresh = "auto"

                        g.MonServerPlotConfig = (plotlen, plottop, plotbot, plotMin, plotMax, plotrefresh)
                    except:
                        exceptPrint(e, "config MonServerPlotConfig")
                        g.MonServerPlotConfig = "auto"
                else:
                    g.MonServerPlotConfig = "auto"

            cfg_dprint(infostr.format("MonServer PlotConfig",   g.MonServerPlotConfig))


        # MonServerDataConfig       (Default:  1, 3, 10)
        t = getConfigEntry("MonServer", "MonServerDataConfig", "upper")
        if t not in ("WARNING", "MISSING"):
            # edprint("config: t: ", t)
            if t == "AUTO":                                         g.MonServerDataConfig = "auto"
            else:
                ts = t.split(",")
                # edprint("config: ts: ", ts)
                if len(ts) == 3:
                    try:
                        dataA = clamp(float(ts[0]), 1, 1000)
                        dataB = clamp(float(ts[1]), 2, 1000)
                        dataC = clamp(float(ts[2]), 3, 1000)
                        g.MonServerDataConfig = (dataA, dataB, dataC)
                    except:
                        exceptPrint(e, "config MonServerDataConfig")
                        g.MonServerDataConfig = "auto"
                else:
                    g.MonServerDataConfig = "auto"

            cfg_dprint(infostr.format("MonServer DataConfig",   g.MonServerDataConfig))

#inactive ####################
    # #from geigerlog.cfg
    #     # MonServer REFRESH
    #     # This sets the refresh timings for the web pages Monitor, Data, Graph. The
    #     # numbers give the seconds after which the site will be refreshed. Numbers
    #     # must be separated by comma.
    #     #
    #     # Option auto defaults to 1, 10, 3
    #     #
    #     # Options:         auto | < <Monitor Refresh> , <Data Refresh> , <Graph Refresh> >
    #     # Default        = auto
    #     # MonServerRefresh = auto
    #     MonServerRefresh = 1, 10, 1

    # # from here
    #     # # MonServer Refresh
    #     # t = getConfigEntry("MonServer", "MonServerRefresh", "upper")
    #     # if t not in ("WARNING", "MISSING"):
    #     #     if t == "AUTO":                                 g.MonServerRefresh = "auto"
    #     #     else:
    #     #         ts = t.split(",")
    #     #         try:
    #     #             g.MonServerRefresh[0] = int(ts[0])
    #     #             g.MonServerRefresh[1] = int(ts[1])
    #     #             g.MonServerRefresh[2] = int(ts[2])
    #     #         except Exception as e:
    #     #             exceptPrint(e, "MonServer Refresh defined improperly")
    #     #             g.MonServerRefresh  = "auto"
    #     #     dprint(infostr.format("MonServer Refresh",     g.MonServerRefresh))
# end inactive ####################



    # Window
        cfg_dprint(infostrHeader.format("Window", ""))

    # # Window HiDPIactivation
    #     t = getConfigEntry("Window", "HiDPIactivation", "upper")
    #     if t not in ("WARNING", "MISSING"):
    #         if    t == 'AUTO':         g.hidpiActivation = "auto"
    #         elif  t == 'YES':          g.hidpiActivation = "yes"
    #         elif  t == 'NO':           g.hidpiActivation = "no"
    #         else:                      g.hidpiActivation = "auto"
    #         cfg_dprint(infostr.format("Window HiDPIactivation", g.hidpiActivation))

    # # Window HiDPIscaleMPL
    #     t = getConfigEntry("Window", "HiDPIscaleMPL", "upper")
    #     if t not in ("WARNING", "MISSING"):
    #         if    t == 'AUTO':         g.hidpiScaleMPL = "auto"
    #         try:                       g.hidpiScaleMPL = int(float(t))
    #         except:                    g.hidpiScaleMPL = "auto"
    #         cfg_dprint(infostr.format("Window HiDPIscaleMPL", g.hidpiScaleMPL))

    # Window dimensions
        sw = getConfigEntry("Window", "windowWidth",  "str")
        sh = getConfigEntry("Window", "windowHeight", "str")
        # rdprint("Window dimension: ", sw, "  ", sh)
        if sw not in ("WARNING", "MISSING") and sh not in ("WARNING", "MISSING"):
            try:        g.window_width  = clamp(int(sw), 1024, 4 * 1024)
            except:     g.window_width  = 1366
            try:        g.window_height = clamp(int(sh),  768, 4 *  768)
            except:     g.window_height = 720
            cfg_dprint(infostr.format("Window Dimensions (pixel)", f"{g.window_width} x {g.window_height}"))

    # Window Size
        t = getConfigEntry("Window", "windowSize", "upper")
        if t not in ("WARNING", "MISSING"):
            if    t == 'MAXIMIZED':    g.window_size = 'maximized'
            else:                      g.window_size = 'auto'
            cfg_dprint(infostr.format("Window Size ", g.window_size))

    # Window Style
        t = getConfigEntry("Window", "windowStyle", "str")
        if t not in ("WARNING", "MISSING"):
            available_style = QStyleFactory.keys()
            if t in available_style:    g.windowStyle = t
            else:                       g.windowStyle = "auto"
            cfg_dprint(infostr.format("Window Style ", g.windowStyle))

    # WINDOW PAD COLORS cannot be used due to a bug in PyQt5
    # # from the geigerlog.cfg file:
    # # WINDOW PAD COLORS:
    # # Sets the background color of NotePad and LogPad. Default is a
    # # very light green for NotePad, and very light blue for LogPad.
    # # Colors can be given as names (red, green, lightblue,...) - not
    # # all names will work - or #<red><green><blue> with red, green, blue
    # # in HEX notation.
    # # Example: #FFFFFF is pure white, #FF0000 is pure red, #00FF00 is pure green,
    # # #CCCCFF is a blueish grey, and #000000 is pure black.
    # #
    # # Option auto defaults to: '#FaFFFa, #FaFaFF'
    # #
    # # Options:       auto | <color name, color name>
    # # Default      = auto
    # windowPadColor = auto
    # # windowPadColor = #FaFFFa, #e0e0FF
    #
    # # Window Pad Color
    #     t = getConfigEntry("Window", "windowPadColor", "str")
    #     if t not in ("WARNING", "MISSING"):
    #         if t.upper() == "AUTO":     g.windowPadColor = ("#FaFFFa", "#FaFaFF")
    #         else:
    #             ts = t.split(",")
    #             Np = ts[0].strip()
    #             Lp = ts[1].strip()
    #             g.windowPadColor      = (Np, Lp)
    #         dprint(infostr.format("Window Pad BG-Color ", g.windowPadColor))


    # Graphic
        cfg_dprint(infostrHeader.format("Graphic", ""))

        # Graphic MovingAverage
        t = getConfigEntry("Graphic", "MovingAverage", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "AUTO":                                             g.mav_initial = 60
            else:
                try:                                                    g.mav_initial = max(1, int(float(t)))
                except:                                                 g.mav_initial = 60
            g.mav =                                                     g.mav_initial
            cfg_dprint(infostr.format("Moving Average Initial (sec)",   g.mav_initial))

        # Graphic Plotstyle markersymbol
        t = getConfigEntry("Graphic", "markersymbol", "str")
        if t not in ("WARNING", "MISSING"):
            t = t[0]
            if t in "osp*h+xDCEM" :                                     g.markersymbol = t          # C=Chrismas, E=Easter, M=Musical notes
            else:                                                       g.markersymbol = 'o'
            cfg_dprint(infostr.format("markersymbol",                   g.markersymbol))

        # Graphic Plotstyle markersize
        t = getConfigEntry("Graphic", "markersize", "str")
        if t not in ("WARNING", "MISSING"):
            try:                                                        g.markersize = float(t)
            except:                                                     g.markersize = 15
            cfg_dprint(infostr.format("markersize",                     g.markersize))

        # Graphic Plotstyle linewidth
        t = getConfigEntry("Graphic", "linewidth", "str")
        if t not in ("WARNING", "MISSING"):
            try:                                                        g.linewidth = float(t)
            except:                                                     g.linewidth = 1.0
            cfg_dprint(infostr.format("linewidth",                      g.linewidth))

        # Graphic Plotstyle linecolor
        #              CPM,  CPS,     CPM1st,      CPS1st, CPM2nd, CPS2nd,  CPM3rd, CPS3rd, Temperature, Pressure, Humidity, Xtra
        # linecolor  = blue, magenta, deepskyblue, violet, cyan,   #9b59b6, brown,  orange, red,         black,    green,    #00ff00
        t = getConfigEntry("Graphic", "linecolor", "str")
        if t not in ("WARNING", "MISSING"):
            linecolorlist = t.split(",")
            if len(linecolorlist) == 12:
                g.linecolor = t
                for i, vname in enumerate(g.VarsCopy):
                    g.VarsCopy[vname][3] = linecolorlist[i]
            else:
                g.linecolor = "auto"
            cfg_dprint(infostr.format("linecolor",                      g.linecolor))


    # Network
        cfg_dprint(infostrHeader.format("Network", ""))

        # WiFi SSID
        t = getConfigEntry("Network", "WiFiSSID", "str")
        if t not in ("WARNING", "MISSING"):
            g.WiFiSSID = t
            cfg_dprint(infostr.format("WiFiSSID",                        g.WiFiSSID))

        # WiFi Password
        t = getConfigEntry("Network", "WiFiPassword", "str")
        if t not in ("WARNING", "MISSING"):
            g.WiFiPassword = t
            cfg_dprint(infostr.format("WiFiPassword",                    g.WiFiPassword))


    # Radiation World Maps
        section = "Worldmaps"
        cfg_dprint(infostrHeader.format(section, ""))

        t = getConfigEntry(section, "gmcmapWebsite", "str")
        if t not in ("WARNING", "MISSING"):
            g.gmcmapWebsite = t
            cfg_dprint(infostr.format("Website",        g.gmcmapWebsite))

        t = getConfigEntry(section, "gmcmapURL", "str")
        if t not in ("WARNING", "MISSING"):
            g.gmcmapURL = t
            cfg_dprint(infostr.format("URL",            g.gmcmapURL))

        t = getConfigEntry(section, "gmcmapUserID", "str")
        if t not in ("WARNING", "MISSING"):
            g.gmcmapUserID = t
            cfg_dprint(infostr.format("UserID",         g.gmcmapUserID))

        t = getConfigEntry(section, "gmcmapCounterID", "str")
        if t not in ("WARNING", "MISSING"):
            g.gmcmapCounterID = t
            cfg_dprint(infostr.format("CounterID",      g.gmcmapCounterID))


    #
    # Custom Names
    #
        section = "Comment"
        cfg_dprint(infostrHeader.format(section, ""))

        for vname in g.VarsCopy:
            Custom_vname = section + vname
            t = getConfigEntry(section, Custom_vname, "rawstr")
            # rdprint(defname, "t: ", t)
            if t not in ("WARNING", "MISSING"):
                g.VarsCopy[vname][6] = t[0:15]                                  # maximum 15 character comment
                cfg_dprint(infostr.format(Custom_vname, g.VarsCopy[vname][6]))


    #
    # ValueFormula - it DOES modify the variable value!
    #
        cfg_dprint(infostrHeader.format("ValueFormula", ""))
        for vname in g.VarsCopy:
            t = getConfigEntry("ValueFormula", vname, "upper")
            if t not in ("WARNING", "MISSING"):
                g.ValueScale[vname] = t
                cfg_dprint(infostr.format(vname, g.ValueScale[vname]))


    #
    # GraphFormula - it does NOT modify the variable value, only the plot value
    #
        cfg_dprint(infostrHeader.format("GraphFormula", ""))
        for vname in g.VarsCopy:
            t = getConfigEntry("GraphFormula", vname, "upper")
            if t not in ("WARNING", "MISSING"):
                g.GraphScale[vname] = t
                cfg_dprint(infostr.format(vname, g.GraphScale[vname]))


    ###
    ### TubeSensitivities
    ###
        cfg_dprint(infostrHeader.format("TubeSensitivities", ""))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivityDef", "str")
        # rdprint(defname, "t Def: ", t)
        if t not in ("WARNING", "MISSING"):
            if    t.upper() == 'AUTO':              g.TubeSensitivity[0] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[0] = tf
                    else:                           g.TubeSensitivity[0] = "auto"
                except:                             g.TubeSensitivity[0] = "auto"
            cfg_dprint(infostr.format("TubeSensitivityDef", g.TubeSensitivity[0]))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivity1st", "str")
        # rdprint(defname, "t 1st: ", t)
        if t not in ("WARNING", "MISSING"):
            if    t.upper() == 'AUTO':              g.TubeSensitivity[1] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[1] = tf
                    else:                           g.TubeSensitivity[1] = "auto"
                except:                             g.TubeSensitivity[1] = "auto"
            cfg_dprint(infostr.format("TubeSensitivity1st", g.TubeSensitivity[1]))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivity2nd", "str")
        # rdprint(defname, "t 2nd: ", t)
        if t not in ("WARNING", "MISSING"):
            if    t.upper() == 'AUTO':              g.TubeSensitivity[2] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[2] = tf
                    else:                           g.TubeSensitivity[2] = "auto"
                except:                             g.TubeSensitivity[2] = "auto"
            cfg_dprint(infostr.format("TubeSensitivity2nd", g.TubeSensitivity[2]))

        t = getConfigEntry("TubeSensitivities", "TubeSensitivity3rd", "str")
        # rdprint(defname, "t 3rd: ", t)
        if t not in ("WARNING", "MISSING"):
            if    t.upper() == 'AUTO':              g.TubeSensitivity[3] = "auto"
            else:
                try:
                    tf = float(t)
                    if tf > 0:                      g.TubeSensitivity[3] = tf
                    else:                           g.TubeSensitivity[3] = "auto"
                except:                             g.TubeSensitivity[3] = "auto"
            cfg_dprint(infostr.format("TubeSensitivity3rd", g.TubeSensitivity[3]))


    # Alarm
        section = "Alarm"
        cfg_dprint(infostrHeader.format("Alarm", ""))

        # Alarm Activation
        t = getConfigEntry(section, "AlarmActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":                                  g.AlarmActivation = True
            else:                                           g.AlarmActivation = False
            cfg_dprint(infostr.format("AlarmActivation",     g.AlarmActivation))

            # show remainder of alarm only if activated
            if g.AlarmActivation:
                # Alarm AlarmSound
                t = getConfigEntry(section, "AlarmSound", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t in ("YES", "NO"):                      g.AlarmSound = True if t == "YES" else False
                    else:                                       g.AlarmSound = False
                    cfg_dprint(infostr.format("AlarmSound",      g.AlarmSound))

                # Alarm IdleCycles
                t = getConfigEntry(section, "AlarmIdleCycles", "str")
                if t not in ("WARNING", "MISSING"):
                    try:    g.AlarmIdleCycles = max(0, int(t))
                    except: g.AlarmIdleCycles = 30
                    cfg_dprint(infostr.format("AlarmIdleCycles",        g.AlarmIdleCycles))

                # Alarm AlarmLimits
                for vname in g.AlarmLimits:
                    avname = section + vname
                    cealarm = getConfigEntry(section, avname, "upper").strip()
                    # ydprint(defname, "cealarm: ", cealarm)
                    if cealarm == "NONE" or cealarm == "":
                        g.AlarmLimits[vname] = None
                    else:
                        cealarm = cealarm.split(",")
                        if len(cealarm) < 3:
                            msg  = "Section: {},  Parameter: {}<br>".format(section, avname)
                            msg += "Problem: Configuration: '{}' has not enough values<br>".format(avname)
                            msg += "Alarm will be inactivated!"
                            g.AlarmLimits[vname] = None

                        else:
                            try:
                                AlarmN     = clamp(int(cealarm[0]), 1, 60)
                                AlarmLower = None if cealarm[1].strip() == "NONE" else float(cealarm[1])
                                AlarmUpper = None if cealarm[2].strip() == "NONE" else float(cealarm[2])
                            except Exception as e:
                                exceptPrint(e, defname + "AlarmConfig vname: '{}".format(vname))
                                AlarmN, AlarmLower, AlarmUpper = (g.NAN, g.NAN, g.NAN)
                                msg  = "Section: {},  Parameter: {}<br>".format(section, avname)
                                msg += "Problem: Configuration: '{}' values must be numeric<br>".format(avname)
                                msg += "Alarm will be inactivated!"
                                g.AlarmLimits[vname] = None

                            g.AlarmLimits[vname] = [AlarmN, AlarmLower, AlarmUpper]

                    cfg_dprint(infostr.format(avname, g.AlarmLimits[vname]))


    # EMAIL
        cfgnames  = ["Protocol", "Host", "Port", "From", "To", "Password" ]
        section   = "Email"

        cfg_dprint(infostrHeader.format(section, ""))

        # Email Activation
        t = getConfigEntry(section, "emailActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.emailActivation = True
                g.emailUsage      = True            # for convenience; also set for usage

            cfg_dprint(infostr.format("emailActivation", g.emailActivation))

            if g.emailActivation:       # show remainder of email only if activated
                parameter = "emailReadFromFile"
                t = getConfigEntry(section, parameter, "str", fallback="")
                # rdprint(defname, "emailReadFromFile: ", t)
                if t != "WARNING" and t > "":
                    try:
                        g.emailReadFromFile = t
                        with open(t) as f:
                            while True:
                                t1 = f.readline().strip()
                                if t1 > "" and not t1.startswith("#"): break

                    except Exception as e:
                        exceptPrint(e, "emailReadFromFile failed with exception")
                        msg = "Section: {},  Parameter: {}<br>".format(section, parameter)
                        msg += "Problem: File not found or not readable:<br>File: &nbsp;&nbsp; {}<br><br>".format(t)
                        msg += "Email will be inactivated!"
                        g.emailActivation = False  # inactivate due to errors in config

                    else:
                        cfg_dprint(infostr.format("Read email cfg from file", g.emailReadFromFile))
                        cfgvals     = t1.strip().replace(" ", "").split(',')
                        # rdprint(defname, "cfgvals: ", cfgvals)
                        for i, emailprop in enumerate(cfgnames):
                            if i != 2:  g.email[emailprop] = cfgvals[i]                        # all strings
                            else:       g.email[emailprop] = int(cfgvals[i])                   # except Port is integer

                            if i < 5: cfg_dprint(infostr.format(emailprop, cfgvals[i]))         # show all props except password
                            else:     cfg_dprint(infostr.format(emailprop, "*********"))        # show Password only as hidden

                else:
                    try:
                        # emailProtocol (SMTP or SMTP_SSL)
                        g.email["Protocol"] = getConfigEntry(section, "emailProtocol",  "str", fallback="SMTP_SSL")
                        cfg_dprint(infostr.format("emailProtocol", g.email["Protocol"]))

                        # emailHost     (like: smtp.johndoe.com)
                        g.email["Host"]     = getConfigEntry(section, "emailHost",      "str", fallback="smtp.johndoe.com")
                        cfg_dprint(infostr.format("emailHost", g.email["Host"]))

                        # emailPort     (like: 465 (preferred) or 587 (old))
                        t = getConfigEntry(section, "emailPort",                        "str", fallback="465")
                        try:    g.email["Port"] = int(t)
                        except: g.email["Port"] = 465
                        cfg_dprint(infostr.format("emailPort", g.email["Port"]))

                        # emailFrom     (Sender)
                        g.email["From"]     = getConfigEntry(section, "emailFrom",      "str", fallback="john@johndoe.com")
                        cfg_dprint(infostr.format("emailFrom", g.email["From"]))

                        # emailTo       (Recipient)
                        g.email["To"]       = getConfigEntry(section, "emailTo",        "str", fallback="info@johndoe.com")
                        cfg_dprint(infostr.format("emailTo", g.email["To"]))

                        # emailPassword (like: topsecret)
                        g.email["Password"] = getConfigEntry(section, "emailPassword",  "str", fallback="topsecret")
                        cfg_dprint(infostr.format("emailPassword", "*********"))                         # Password is: g.email["Password"]))
                    except Exception as e:
                        exceptPrint(e, "bummer")


                # verify proper email settings; emailcfgOk > 0 means error
                emailcfgOk = 0
                if g.email["Protocol"] not in ("SMTP", "SMTP_SSL"): emailcfgOk += 1
                if g.email["Host"]     == ""                      : emailcfgOk += 2
                if g.email["Port"]     not in (465, 587)          : emailcfgOk += 4
                if g.email["From"]     == ""                      : emailcfgOk += 8
                if g.email["To"]       == ""                      : emailcfgOk += 16
                if g.email["Password"] == ""                      : emailcfgOk += 32

                # emailcfgOk = 255 # for testing
                if emailcfgOk > 0:
                    # inactivate email since an error in config was found
                    g.emailActivation = False

                    # output for both terminal and HTML
                    msg = "Problem: Email configuration has improper settings.\n"
                    msg += "Section: {}, see all Parameters marked with arrow\n".format(section)
                    msg += "Email will be inactivated!\n"
                    msg += "\nCurrent configuration:\n"

                    # output for terminal
                    cfgmsg = ""
                    for i, emailprop in enumerate(cfgnames):
                        cfgmsg += "    {:10s} : {:20s}  {}\n".format(emailprop, str(g.email[emailprop]), "<---- " if (emailcfgOk & (2**i)) else "")
                    edprint(msg + cfgmsg)

                    # output for HTML
                    cfgmsg = "<table>"
                    for i, emailprop in enumerate(cfgnames):
                        cfgmsg += "<tr><td>"
                        cfgmsg += "&nbsp;" * 5 + "{:10s}</td><td> : {:20s}</td><td>{}".format(emailprop, str(g.email[emailprop]), "&lt;---- " if (emailcfgOk & (2**i)) else "")
                        cfgmsg += "</td></tr>"
                    cfgmsg += "</table>"


###
### DEVICES
###

        cfg_dprint(infostrHeader.format("Activated Devices", ""))

        # re-definition for increased indentation
        infostrHeader       = "    {:31s} {}"
        infostr             = "        {:31s}: {}"
        ActivatedDevices    = 0

    # GMC_Device
        t = getConfigEntry("GMC_Device", "GMC_Activation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["GMC"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["GMC"][g.ACTIV]: # show only if activated
                cfg_dprint(infostrHeader.format("GMC Device", ""))

                # GMC_Device Firmware Bugs
                # location bug: "GMC-500+Re 1.18, GMC-500+Re 1.21"
                t = getConfigEntry("GMC_Device", "GMC_locationBug", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                  g.GMC_locationBug = "auto"
                    else:                                    g.GMC_locationBug = t
                    cfg_dprint(infostr.format("Location Bug",g.GMC_locationBug))

                # GMC_Device Firmware Bugs
                # FET bug: GMC_FastEstTime
                t = getConfigEntry("GMC_Device", "GMC_FastEstTime", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == "AUTO":                       g.GMC_FastEstTime = "auto"
                    elif t == "DYNAMIC":                    g.GMC_FastEstTime = 3
                    else:
                        try:    tFET = int(float(t))
                        except: tFET = 0
                        if   tFET in (3,5,10,15,20,30,60):  g.GMC_FastEstTime = tFET
                        else:                               g.GMC_FastEstTime = "auto"
                    cfg_dprint(infostr.format("FET",        g.GMC_FastEstTime))


                # GMC_Device RTC_OFFSET
                t = getConfigEntry("GMC_Device", "GMC_RTC_Offset", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == "AUTO":                       g.GMC_RTC_Offset = "auto"
                    else:
                        try:    rtcos = clamp(int(float(t)), -59, 59)
                        except: rtcos = 0
                        g.GMC_RTC_Offset = rtcos
                    cfg_dprint(infostr.format("RTC_OFFSET",     g.GMC_RTC_Offset))


                # GMC_Device CLOCK_CORRECTION
                t = getConfigEntry("GMC_Device", "GMC_ClockCorrection", "upper")
                # rdprint(defname, "GMC_ClockCorrection: ", g.GMC_ClockCorrection)
                if t not in ("WARNING", "MISSING"):
                    if   t == "AUTO":                               g.GMC_ClockCorrection = "auto"
                    else:
                        try:    rtcos = clamp(int(float(t)), 0, 59)
                        except: rtcos = "auto"
                        if 1:                                       g.GMC_ClockCorrection = rtcos
                    cfg_dprint(infostr.format("CLOCK_CORRECTION",   g.GMC_ClockCorrection))


                # GMC_Device memory
                t = getConfigEntry("GMC_Device", "GMC_memory", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t ==  '2MB':                       g.GMC_memory = 2**21   # 2 097 152
                    elif t ==  '1MB':                       g.GMC_memory = 2**20   # 1 048 576
                    elif t == '64KB':                       g.GMC_memory = 2**16   #    65 536
                    else:                                   g.GMC_memory = 'auto'
                    cfg_dprint(infostr.format("Memory",     g.GMC_memory))

                # GMC_Device GMC_SPIRpage
                t = getConfigEntry("GMC_Device", "GMC_SPIRpage", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == '2K':                         g.GMC_SPIRpage = 2048     # @ 2k speed: 6057 B/sec
                    elif t == '4K':                         g.GMC_SPIRpage = 4096     # @ 4k speed: 7140 B/sec
                    elif t == '8K':                         g.GMC_SPIRpage = 4096 * 2 # @ 8k speed: 7908 B/sec
                    elif t == '16K':                        g.GMC_SPIRpage = 4096 * 4 # @16k speed: 8287 B/sec
                    else:                                   g.GMC_SPIRpage = "auto"
                    cfg_dprint(infostr.format("SPIRpage",   g.GMC_SPIRpage))

                # GMC_Device GMC_SPIRbugfix
                t = getConfigEntry("GMC_Device", "GMC_SPIRbugfix", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == 'YES':                        g.GMC_SPIRbugfix = True
                    elif t == 'NO':                         g.GMC_SPIRbugfix = False
                    else:                                   g.GMC_SPIRbugfix = 'auto'
                    cfg_dprint(infostr.format("SPIRbugfix", g.GMC_SPIRbugfix))

                # GMC_Device GMC_configsize
                t = getConfigEntry("GMC_Device", "GMC_configsize", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == '256':                         g.GMC_configsize = 256
                    elif t == '512':                         g.GMC_configsize = 512
                    else:                                    g.GMC_configsize = 'auto'
                    cfg_dprint(infostr.format("Configsize",  g.GMC_configsize))

                # GMC_Device GMC_voltagebytes
                t = getConfigEntry("GMC_Device", "GMC_voltagebytes", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == '1':                           g.GMC_voltagebytes = 1
                    elif t == '5':                           g.GMC_voltagebytes = 5
                    elif t == '0'   :                        g.GMC_voltagebytes = 0
                    else:                                    g.GMC_voltagebytes = 'auto'
                    cfg_dprint(infostr.format("Voltagebytes",g.GMC_voltagebytes))

                # GMC_Device GMC_endianness
                t = getConfigEntry("GMC_Device", "GMC_endianness", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == 'LITTLE':                     g.GMC_endianness = 'little'
                    elif t == 'BIG':                        g.GMC_endianness = 'big'
                    else:                                   g.GMC_endianness = 'auto'
                    cfg_dprint(infostr.format("Endianness", g.GMC_endianness))


                # GMC_Device GMC_CfgHiIndex
                t = getConfigEntry("GMC_Device", "GMC_CfgHiIndex", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == "AUTO":                       g.GMC_CfgHiIndex = "auto"
                    elif t in  range(0, 8):                 g.GMC_CfgHiIndex = int(t)
                    else:                                   g.GMC_CfgHiIndex = "auto"
                    cfg_dprint(infostr.format("cfgHiIndex", g.GMC_CfgHiIndex))


                # GMC_Device GMC_WiFiPeriod
                t = getConfigEntry("GMC_Device", "GMC_WiFiPeriod", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "AUTO":                         g.GMC_WiFiPeriod = "auto"
                    else:
                        try:
                            ift = int(float(t))
                            if ift > 0 and ift < 256:       g.GMC_WiFiPeriod = ift
                            else:                           g.GMC_WiFiPeriod = "auto"
                        except:                             g.GMC_WiFiPeriod = "auto"
                    cfg_dprint(infostr.format("WiFiPeriod", g.GMC_WiFiPeriod))


                # GMC_Device GMC_WiFiSwitch
                t = getConfigEntry("GMC_Device", "GMC_WiFiSwitch", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "AUTO":                         g.GMC_WiFiSwitch = "auto"
                    else:
                        if t == "ON":                       g.GMC_WiFiSwitch = 1
                        else:                               g.GMC_WiFiSwitch = 0
                    cfg_dprint(infostr.format("WiFiSwitch", g.GMC_WiFiSwitch))


                # GMC_Device GMC_Bytes
                t = getConfigEntry("GMC_Device", "GMC_Bytes", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "AUTO":                         g.GMC_Bytes = "auto"
                    else:
                        try:
                            nt = int(t)
                            if nt in (2, 4):                g.GMC_Bytes = nt
                            else:                           g.GMC_Bytes = "auto"
                        except Exception as e:
                            exceptPrint(e, "GMC_Device GMC_Bytes")
                            g.GMC_Bytes = "auto"

                    cfg_dprint(infostr.format("Bytes",      g.GMC_Bytes))


                # GMC_Device variables
                t = getConfigEntry("GMC_Device", "GMC_Variables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.GMC_Variables = "auto"
                    else:                                   g.GMC_Variables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("Variables",  g.GMC_Variables))


                # GMC USB port
                t = getConfigEntry("GMC_Device", "GMC_usbport", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":               g.GMC_usbport = "auto"
                    else:                                   g.GMC_usbport = t
                    cfg_dprint(infostr.format("USB Port",   g.GMC_usbport))


                # GMC Device ID (Model, Serial No)
                t = getConfigEntry("GMC_Device", "GMC_ID", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":               g.GMC_ID = "auto"
                    else:
                        ts = t.split(",")
                        if len(ts) != 2:                    g.GMC_ID = "auto"
                        else:
                            ts[0] = ts[0].strip()
                            ts[1] = ts[1].strip()
                            if   ts[0].upper() == "NONE": ts[0] = None
                            if   ts[1].upper() == "NONE": ts[1] = None
                            elif ts[1].upper() == "":     ts[1] = None
                            g.GMC_ID = ts
                    cfg_dprint(infostr.format("Device IDs",  g.GMC_ID))



    # AudioCounter
        t = getConfigEntry("AudioCounter", "AudioActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["Audio"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["Audio"][g.ACTIV]: # show only if activated
                cfg_dprint(infostrHeader.format("AudioCounter Device", ""))

                # AudioCounter DEVICE
                t = getConfigEntry("AudioCounter", "AudioDevice", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":                   g.AudioDevice = "auto"
                    elif not ("," in t):                        g.AudioDevice = "auto" # must have 2 items separated by comma
                    else:
                        t = t.split(",", 1)
                        t[0] = t[0].strip()
                        t[1] = t[1].strip()
                        if t[0].isdecimal():   t[0] = int(t[0])
                        if t[1].isdecimal():   t[1] = int(t[1])
                        g.AudioDevice = tuple(t)
                    cfg_dprint(infostr.format("AudioDevice",        g.AudioDevice))

                # AudioCounter LATENCY
                t = getConfigEntry("AudioCounter", "AudioLatency", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":                   g.AudioLatency = "auto"
                    elif not ("," in t):                        g.AudioLatency = "auto" # must have 2 items separated by comma
                    else:
                        t = t.split(",", 1)
                        try:    t[0] = float(t[0])
                        except: t[0] = 1.0
                        try:    t[1] = float(t[1])
                        except: t[1] = 1.0
                        g.AudioLatency = tuple(t)
                    cfg_dprint(infostr.format("AudioLatency",       g.AudioLatency))

                # AudioCounter PULSE Dir
                t = getConfigEntry("AudioCounter", "AudioPulseDir", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == "AUTO":                               g.AudioPulseDir = "auto"
                    elif t == "NEGATIVE":                           g.AudioPulseDir = False
                    elif t == "POSITIVE":                           g.AudioPulseDir = True
                    else:                                           pass # unchanged from default False
                    cfg_dprint(infostr.format("AudioPulseDir",       g.AudioPulseDir))

                # AudioCounter PULSE Max
                t = getConfigEntry("AudioCounter", "AudioPulseMax", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "AUTO":                     g.AudioPulseMax = "auto"
                    else:
                        try:                            g.AudioPulseMax = int(float(t))
                        except:                         g.AudioPulseMax = "auto"
                        if g.AudioPulseMax <= 0:   g.AudioPulseMax = "auto"
                    cfg_dprint(infostr.format("AudioPulseMax", g.AudioPulseMax))

                # AudioCounter LIMIT
                t = getConfigEntry("AudioCounter", "AudioThreshold", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "AUTO":             g.AudioThreshold = "auto"
                    else:
                        try:                    g.AudioThreshold = int(float(t))
                        except:                 g.AudioThreshold = 60
                        if g.AudioThreshold < 0 or g.AudioThreshold > 100:
                                                g.AudioThreshold = 60
                    cfg_dprint(infostr.format("AudioThreshold", g.AudioThreshold))

                # AudioCounter Variables
                t = getConfigEntry("AudioCounter", "AudioVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.AudioVariables = "auto"
                    else:                                   g.AudioVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("AudioVariables", g.AudioVariables))


    # SerialPulse Device (e.g. Audio-To-Serial Device)
        t = getConfigEntry("SerialPulseDevice", "SerialPulseActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["SerialPulse"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["SerialPulse"][g.ACTIV]:       # show next lines only if Pulse device is activated
                cfg_dprint(infostrHeader.format("SerialPulse Device", ""))

            # AudioToSerial USB Port
                t = getConfigEntry("SerialPulseDevice", "SerialPulseUsbport", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.SerialPulseUsbport = "auto"
                    else:                                   g.SerialPulseUsbport = t
                    cfg_dprint(infostr.format("Serial Port",    g.SerialPulseUsbport))

            # AudioToSerial variables
                t = getConfigEntry("SerialPulseDevice", "SerialPulseVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.SerialPulseVariables = "auto"
                    else:                                   g.Pulse                = correctVariableCaps(t)
                    cfg_dprint(infostr.format("Variables",      g.SerialPulseVariables))


    # IOT Device
        # IOT Activation
        t = getConfigEntry("IOTDevice", "IOTActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["IOT"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["IOT"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("IOT Device", ""))

                # IOT Server IP
                t = getConfigEntry("IOTDevice", "IOTBrokerIP", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                     g.IOTBrokerIP = "auto"
                    else:                                       g.IOTBrokerIP = t
                    cfg_dprint(infostr.format("IOTBrokerIP",    g.IOTBrokerIP ))

                # IOT Server Port
                t = getConfigEntry("IOTDevice", "IOTBrokerPort", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                     g.IOTBrokerPort = "auto"
                    else:
                        try:                                    g.IOTBrokerPort = abs(int(t))
                        except:                                 g.IOTBrokerPort = "auto"
                    cfg_dprint(infostr.format("IOTBrokerPort",  g.IOTBrokerPort))

                # IOT IOTUsername
                t = getConfigEntry("IOTDevice", "IOTUsername", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                     g.IOTUsername = "auto"
                    else:                                       g.IOTUsername = t
                    cfg_dprint(infostr.format("IOTUsername",    g.IOTUsername))

                # IOT IOTPassword
                t = getConfigEntry("IOTDevice", "IOTPassword", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                     g.IOTPassword = "auto"
                    else:                                       g.IOTPassword = t
                    cfg_dprint(infostr.format("IOTPassword",    g.IOTPassword))

                # IOT timeout
                t = getConfigEntry("IOTDevice", "IOTTimeout", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == 'AUTO':                             g.IOTTimeout = "auto"
                    else:
                        try:
                            if float(t) > 0:                    g.IOTTimeout = float(t)
                            else:                               g.IOTTimeout = "auto"  # if zero or negative value given
                        except:                                 g.IOTTimeout = "auto"
                    cfg_dprint(infostr.format("IOTTimeout",     g.IOTTimeout))

                # IOT Broker Folder  (= 'geigerlog/')
                t = getConfigEntry("IOTDevice", "IOTBrokerFolder", "str")
                if t not in ("WARNING", "MISSING"):
                    if t == "" or t.upper() == "AUTO":          g.IOTBrokerFolder = "auto"
                    else:
                        g.IOTBrokerFolder = t
                        if g.IOTBrokerFolder[-1] != "/":        g.IOTBrokerFolder += "/"
                    cfg_dprint(infostr.format("IOTBrokerFolder",g.IOTBrokerFolder))

            ###########################

                # IOT Client configs:  (IOTClients)
                t = getConfigEntry("IOTDevice", "IOTClients", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                             g.IOTClients = "auto"
                    else:                                               g.IOTClients = t
                    cfg_dprint(infostr.format("IOTClients",             "\n" + g.IOTClients))


                # # IOT Client configs: IOTClientDataGLvars
                # t = getConfigEntry("IOTDevice", "IOTClientDataGLvars", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientDataGLvars = "auto"
                #     else:                                               g.IOTClientDataGLvars = t
                #     cfg_dprint(infostr.format("IOTClientDataGLvars",    g.IOTClientDataGLvars))


                # # IOT Client configs: IOTClientTasmotaPL1
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaPL1", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaPL1 = "auto"
                #     else:                                               g.IOTClientTasmotaPL1 = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaPL1",    g.IOTClientTasmotaPL1))


                # # IOT Client configs: IOTClientTasmotaPL2
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaPL2", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaPL2 = "auto"
                #     else:                                               g.IOTClientTasmotaPL2 = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaPL2",    g.IOTClientTasmotaPL2))


                # # IOT Client configs: IOTClientTasmotaPL3
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaPL3", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaPL3 = "auto"
                #     else:                                               g.IOTClientTasmotaPL3 = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaPL3",    g.IOTClientTasmotaPL3))


                # # IOT Client configs: IOTClientTasmotaPL4
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaPL4", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaPL4 = "auto"
                #     else:                                               g.IOTClientTasmotaPL4 = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaPL4",    g.IOTClientTasmotaPL4))



                # # IOT Client configs: IOTClientTasmotaA8T1
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaA8T1", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaA8T1 = "auto"
                #     else:                                               g.IOTClientTasmotaA8T1 = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaA8T1",   g.IOTClientTasmotaA8T1))

                # # IOT Client configs: IOTClientTasmotaA8T2
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaA8T2", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaA8T2 = "auto"
                #     else:                                               g.IOTClientTasmotaA8T2 = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaA8T2",   g.IOTClientTasmotaA8T2))


                # # IOT Client configs: IOTClientTasmotaSMR
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaSMR", "str")
                # if t not in ("WARNING", "MISSING"):
                #     if t.upper() == "AUTO":                             g.IOTClientTasmotaSMR = "auto"
                #     else:                                               g.IOTClientTasmotaSMR = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaSMR",    g.IOTClientTasmotaSMR))


                # # IOT Client configs: IOTClientTasmotaBSH
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaBSH", "str")
                    #     if t.upper() == "AUTO":                         g.IOTClientTasmotaBSH = "auto"
                #     else:                                           g.IOTClientTasmotaBSH = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaBSH", g.IOTClientTasmotaBSH))


                # # IOT Client configs: IOTClientTasmotaWWR
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaWWR", "str")
                    #     if t.upper() == "AUTO":                         g.IOTClientTasmotaWWR = "auto"
                #     else:                                           g.IOTClientTasmotaWWR = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaWWR", g.IOTClientTasmotaWWR))


                # # IOT Client configs: IOTClientTasmotaDMX
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaDMX", "str")
                    #     if t.upper() == "AUTO":                         g.IOTClientTasmotaDMX = "auto"
                #     else:                                           g.IOTClientTasmotaDMX = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaDMX", g.IOTClientTasmotaDMX))


                # # IOT Client configs: IOTClientTasmotaCTM
                # t = getConfigEntry("IOTDevice", "IOTClientTasmotaCTM", "str")
                    #     if t.upper() == "AUTO":                         g.IOTClientTasmotaCTM = "auto"
                #     else:                                           g.IOTClientTasmotaCTM = t
                #     cfg_dprint(infostr.format("IOTClientTasmotaCTM", g.IOTClientTasmotaCTM))



    # RadMonPlus
        # RadMon Activation
        t = getConfigEntry("RadMonPlusDevice", "RMActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["RadMon"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["RadMon"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("RadMonPlus Device", ""))

                # RadMon Server IP
                t = getConfigEntry("RadMonPlusDevice", "RMServerIP", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                 g.RMServerIP = "auto"
                    else:                                   g.RMServerIP = t
                    cfg_dprint(infostr.format("RMServerIP",     g.RMServerIP ))

                # RadMon Server Port
                t = getConfigEntry("RadMonPlusDevice", "RMServerPort", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                 g.RMServerPort = "auto"
                    else:
                        try:    g.RMServerPort = abs(int(t))
                        except: g.RMServerPort = "auto"
                    cfg_dprint(infostr.format("RMServerPort",   g.RMServerPort))

                # Radmon timeout
                t = getConfigEntry("RadMonPlusDevice", "RMTimeout", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == 'AUTO':                         g.RMTimeout = "auto"
                    else:
                        try:
                            if float(t) > 0:                g.RMTimeout = float(t)
                            else:                           g.RMTimeout = "auto"  # if zero or negative value given
                        except:                             g.RMTimeout = "auto"
                    cfg_dprint(infostr.format("RMTimeout",      g.RMTimeout))

                # RadMon Server Folder
                t = getConfigEntry("RadMonPlusDevice", "RMServerFolder", "str")
                if t not in ("WARNING", "MISSING"):
                    # blank in folder name not allowed
                    if " " in t or t.upper() == "AUTO":     g.RMServerFolder = "auto"
                    else:
                        g.RMServerFolder = t
                        if g.RMServerFolder[-1] != "/":g.RMServerFolder += "/"
                    cfg_dprint(infostr.format("RMServerFolder", g.RMServerFolder ))

                # Radmon variables
                t = getConfigEntry("RadMonPlusDevice", "RMVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.RMVariables = "auto"
                    else:
                        g.RMVariables = correctVariableCaps(t)
                        if g.RMVariables.count("CPM") > 1 or g.RMVariables.count("CPS") > 0:
                            edprint("WARNING: Improper configuration of variables: ", g.RMVariables)
                            edprint("WARNING: Only a single CPM* is allowed, and no CPS*")
                            g.RMVariables = "auto"
                            edprint("WARNING: RadMon variables are reset to: ", g.RMVariables)
                    cfg_dprint(infostr.format("RMVariables",    g.RMVariables))


    # AmbioMon
        t = getConfigEntry("AmbioMonDevice", "AmbioActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["AmbioMon"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["AmbioMon"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("AmbioMon Device", ""))

                # AmbioMon Server IP
                t = getConfigEntry("AmbioMonDevice", "AmbioServerIP", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == 'AUTO':                 g.AmbioServerIP = "auto"
                    else:                                   g.AmbioServerIP = t
                    cfg_dprint(infostr.format("AmbioServerIP",  g.AmbioServerIP ))

                # AmbioMon Server Port
                t = getConfigEntry("AmbioMonDevice", "AmbioServerPort", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "AUTO":                             g.AmbioServerPort = "auto"
                    else:
                        wp = int(float(t))
                        if 0 <= wp  <= 65535:                   g.AmbioServerPort = wp
                        else:                                   g.AmbioServerPort = "auto"
                    cfg_dprint(infostr.format("AmbioServerPort",    g.AmbioServerPort ))

                # AmbioMon timeout
                t = getConfigEntry("AmbioMonDevice", "AmbioTimeout", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == 'AUTO':                         g.AmbioTimeout = "auto"
                    else:
                        try:
                            if float(t) > 0:                g.AmbioTimeout = float(t)
                            else:                           g.AmbioTimeout = "auto"  # if zero or negative value given
                        except:                             g.AmbioTimeout = "auto"
                    cfg_dprint(infostr.format("AmbioTimeout",   g.AmbioTimeout))

                # AmbioMon DataType
                t = getConfigEntry("AmbioMonDevice", "AmbioDataType", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":               g.AmbioDataType = "auto"
                    elif t.upper() == "AVG":                g.AmbioDataType = "AVG"
                    else:                                   g.AmbioDataType = "LAST"
                    cfg_dprint(infostr.format("AmbioDataType",  g.AmbioDataType))

                # AmbioMon variables
                t = getConfigEntry("AmbioMonDevice", "AmbioVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.AmbioVariables = "auto"
                    else:                                   g.AmbioVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("AmbioVariables", g.AmbioVariables))



    # Gamma-Scout counter
        # Gamma-Scout Activation
        t = getConfigEntry("GammaScoutDevice", "GSActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["GammaScout"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["GammaScout"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("GammaScout Device", ""))

                # Gamma-Scout variables
                t = getConfigEntry("GammaScoutDevice", "GSVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                 g.GSVariables = "auto"
                    else:                                   g.GSVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("Variables",      g.GSVariables))

                # Gamma-Scout USB Port
                t = getConfigEntry("GammaScoutDevice", "GSusbport", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":               g.GSusbport = "auto"
                    else:                                   g.GSusbport = t
                    cfg_dprint(infostr.format("Serial Port",    g.GSusbport))



    # LabJack U3 (type U3B, perhaps with probe EI1050)
        # LabJack Activation
        t = getConfigEntry("LabJackDevice", "LJActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["LabJack"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["LabJack"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("LabJack Device", ""))

                # LabJack  EI1050 Activation
                t = getConfigEntry("LabJackDevice", "LJEI1050Activation", "upper", fallback="NO")
                if t not in ("WARNING", "MISSING"):
                    if t == "YES":                              g.LJEI1050Activation = True
                    cfg_dprint(infostr.format("LJEI1050Activation", g.LJEI1050Activation))

                # LabJack variables
                t = getConfigEntry("LabJackDevice", "LJVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                     g.LJVariables = "auto"
                    else:                                       g.LJVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("LJVariables",        g.LJVariables))


    # MiniMon
        t = getConfigEntry("MiniMon", "MiniMonActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["MiniMon"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["MiniMon"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("MiniMon Device", ""))

                # MiniMon Device
                t = getConfigEntry("MiniMon", "MiniMonOS_Device", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                     g.MiniMonOS_Device = "auto"
                    else:                                       g.MiniMonOS_Device = t
                    cfg_dprint(infostr.format("MiniMonOS_Device",   g.MiniMonOS_Device))

                # MiniMon Variables
                t = getConfigEntry("MiniMon", "MiniMonVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                     g.MiniMonVariables = "auto"
                    else:                                       g.MiniMonVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("MiniMonVariables",   g.MiniMonVariables))

                # MiniMon Interval
                t = getConfigEntry("MiniMon", "MiniMonInterval", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                     g.MiniMonInterval = "auto"
                    else:
                        try:
                            g.MiniMonInterval = float(t)
                            if g.MiniMonInterval < 0:      g.MiniMonInterval = "auto"
                        except:                                 g.MiniMonInterval = "auto"
                    cfg_dprint(infostr.format("MiniMonInterval",    g.MiniMonInterval))


    # Manu
        t = getConfigEntry("Manu", "ManuActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["Manu"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["Manu"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("Manu Device", ""))

                # Manu Variables
                t = getConfigEntry("Manu", "ManuVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO" :                    g.ManuVariables = "auto"
                    else:                                       g.ManuVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("ManuVariables",      g.ManuVariables))



    # WiFiServer
        section = "WiFiServerDevice"
        WiFiServerErrmsg  = "\n<b>Problems in Configuration File</b>\n"
        t = getConfigEntry(section, "WiFiServerActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["WiFiServer"][g.ACTIV] = True
                ActivatedDevices += 1

                cfg_dprint(infostrHeader.format("WiFiServer Device", ""))

                # WiFiServer
                option = "WiFiServer"
                if config.has_option(section, option):                      # check if option WiFiServer exists
                    t = getConfigEntry(section, option, "str")
                    if t not in ("WARNING", "MISSING"):
                        wsl = t.split("\n")                                 # NEW: Serverlist can have any number of lines!
                        # iydprint(defname, f"wsl: {wsl}")
                else:
                    cfg_dprint(infostr.format("WiFiServer", "Option does not exist"))
                    if g.configAlerts == "": g.configAlerts += WiFiServerErrmsg
                    errmsg = f"Section: {section}, Option: {option}\nProblem: WiFiServer is activated, but has no configuration\n\n"
                    g.configAlerts += errmsg

                WiFiServerCount = len(wsl)
                if WiFiServerCount == 0:
                    cfg_dprint(infostr.format("WiFiServer", "No WiFi Servers were defined"))
                    if g.configAlerts == "": g.configAlerts += WiFiServerErrmsg
                    errmsg = f"Section: {section}, Option: {option}\nProblem: WiFiServer is activated, but no WiFi Servers were defined\n\n"
                    g.configAlerts += errmsg

                for ServNo in range(WiFiServerCount):
                    # iydprint(defname, f"ServNo: {ServNo}")
                    # iydprint(defname, f"wsl[ServNo]: {wsl[ServNo]}")

                    wsl[ServNo] = wsl[ServNo].strip()                                 # remove whitespace
                    if wsl[ServNo].endswith(","): wsl[ServNo] = wsl[ServNo][0:-1]     # remove any ',' at the end
                    wsList = wsl[ServNo].replace(" ", "").split(",", 5)               # must have 6 entries after 5 splits
                    if len(wsList) != 6:
                        if g.configAlerts == "": g.configAlerts += WiFiServerErrmsg
                        errmsg  = f"Section: {section}, Option: {option}\n"
                        errmsg += f"Problem: Improper WiFiServer configuration: {wsList} \n"
                        errmsg += f"Needed are: 6 comma separated sections! \n\n"
                        g.configAlerts += errmsg
                        break
                    wsDict = {}
                    da = True if "y" in  wsList[0].lower() else False       # is WiFiServer activated?
                    wsDict.update({"DevActiv"   : da}       )               # from config
                    wsDict.update({"DevCat"     : wsList[1]})               # from config
                    wsDict.update({"DevType"    : wsList[2]})               # from config
                    wsDict.update({"DevIP"      : wsList[3]})               # from config
                    wsDict.update({"DevPort"    : int(wsList[4])})          # from config
                    wsDict.update({"DevVars"    : wsList[5]})               # from config

                    wsDict.update({"DevUrl"     : "Undefined"})             # from init
                    wsDict.update({"DevConnect" : False})                   # from init
                    wsDict.update({"DevID"      : "Undefined"})             # from init
                    wsDict.update({"DevName"    : "Undefined"})             # from init
                    wsDict.update({"CPSlist"    : deque([], 60)})           # from data calls

                    # iydprint(defname, f"ServNo: {ServNo}   wsList: {wsList}")
                    # iydprint(defname, f"ServNo: {ServNo}   wsDict: {wsDict}")

                    if wsDict["DevActiv"]: # check next stuff only if current WiFiServer is activated

                        # Port check
                        if 0 <= int(wsDict["DevPort"]) <= 65535:
                            pass
                            # print("valid Port")
                        else:
                            rdprint("INVALID Port")
                            if g.configAlerts == "": g.configAlerts += WiFiServerErrmsg
                            option = "WiFiServer#" + str(i)
                            errmsg = f"Section: {section}, Option: {option}\nProblem: has invalid Port: {wsDict["Port"]}\n\n"
                            g.configAlerts += errmsg

                        # checking vars
                        VarsAsList = []
                        for i, cVars in enumerate(wsDict["DevVars"].split(",")):
                            cname = cVars.strip()
                            # icdprint(defname, f"cname: {cname}")
                            if  cname in g.VarsCopy:
                                # Variable name is ok
                                pass
                            elif cname == "None":
                                pass
                            else:
                                # Variable name is NOT ok
                                rdprint(f"Unknown Variable '{cname}' in checking vars")
                                if g.configAlerts == "":   g.configAlerts += WiFiServerErrmsg
                                option = "WiFiServer#" + str(i)
                                errmsg = "Section: {}, Option: {}\nProblem: has wrong value:".format(section, option)
                                g.configAlerts += errmsg + "  ILLEGAL Variable {} ".format(cname)
                                cname = "None"

                            VarsAsList.append(cname)

                            wsDict["DevVarsList"] = VarsAsList
                            # cdprint(defname, f"wsDict[Vars]: {wsDict['Vars']}")

                        g.WiFiServerList.append(wsDict)

                # printout
                for i, ws in enumerate(g.WiFiServerList):
                    cfg_dprint(infostr.format(f"WiFiServer #{i}", ws))



    # WiFiClient
        t = getConfigEntry("WiFiClientDevice", "WiFiClientActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["WiFiClient"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["WiFiClient"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("WiFiClient Device", ""))

                # WiFiClient Server Port
                t = getConfigEntry("WiFiClientDevice", "WiFiClientPort", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == 'AUTO':                                     g.WiFiClientPort = "auto"
                    else:
                        try:
                            if float(t) > 0:                            g.WiFiClientPort = int(float(t))
                            else:                                       g.WiFiClientPort = "auto"  # if zero or negative value given
                        except:                                         g.WiFiClientPort = "auto"
                    cfg_dprint(infostr.format("WiFiClientPort",          g.WiFiClientPort ))


                # WiFiClient Type
                t = getConfigEntry("WiFiClientDevice", "WiFiClientType", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == "GENERIC":                                  g.WiFiClientType = "GENERIC"
                    else:                                               g.WiFiClientType = "GMC"
                    cfg_dprint(infostr.format("WiFiClientType",          g.WiFiClientType))


                # GENERIC  - WiFiClient variables for WiFiClientType = "GENERIC"
                if g.WiFiClientType == "GENERIC":
                    t = getConfigEntry("WiFiClientDevice", "WiFiClientVariablesGENERIC", "str")
                    if t not in ("WARNING", "MISSING"):
                        if t.upper() == "AUTO":                         g.WiFiClientVariables = "auto"
                        else:                                           g.WiFiClientVariables = correctVariableCaps(t)
                        cfg_dprint(infostr.format("WiFiClientVariables", g.WiFiClientVariables))


                # GMC  - WiFiClient variables for WiFiClientType = "GMC"
                else:
                    t = getConfigEntry("WiFiClientDevice", "WiFiClientVariablesGMC", "str")
                    if t not in ("WARNING", "MISSING"):
                        if t.upper() == "AUTO":                         g.WiFiClientMapping = "auto"
                        else:                                           g.WiFiClientMapping = t
                        cfg_dprint(infostr.format("WiFiClientMapping",   g.WiFiClientMapping))



    # RaspiPulse
        # RaspiPulse Activation
        t = getConfigEntry("RaspiPulseDevice", "RaspiPulseActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["RaspiPulse"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["RaspiPulse"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("RaspiPulse Device", ""))

                # RaspiPulse Server Pin
                t = getConfigEntry("RaspiPulseDevice", "RaspiPulsePin", "upper")
                if t not in ("WARNING", "MISSING"):
                    if t == 'AUTO':                                     g.RaspiPulsePin = "auto"
                    else:
                        try:
                            if float(t) > 0:                            g.RaspiPulsePin = int(float(t))
                            else:                                       g.RaspiPulsePin = "auto"  # if zero or negative value given
                        except:                                         g.RaspiPulsePin = "auto"
                    cfg_dprint(infostr.format("RaspiPulsePin",           g.RaspiPulsePin))

                # RaspiPulse Edge
                t = getConfigEntry("RaspiPulseDevice", "RaspiPulseEdge", "upper")
                if t not in ("WARNING", "MISSING"):
                    if   t == "AUTO":                                   g.RaspiPulseEdge = "auto"
                    elif t in ("RISING", "FALLING"):                    g.RaspiPulseEdge = t
                    else:                                               g.RaspiPulseEdge = "auto"
                    cfg_dprint(infostr.format("RaspiPulseEdge",          g.RaspiPulseEdge))

                # RaspiPulse variables
                t = getConfigEntry("RaspiPulseDevice", "RaspiPulseVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                             g.RaspiPulseVariables = "auto"
                    else:                                               g.RaspiPulseVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("RaspiPulseVariables",     g.RaspiPulseVariables))



    # I2CDevice
        # I2C variables:  included in sensors settings
        t = getConfigEntry("I2CDevice", "I2CActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["I2C"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["I2C"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("I2CSensor Device", ""))

                # I2C Dongle - ISS, ELV, IOW  (Dongle FTD is no longer supported!)
                t = getConfigEntry("I2CDevice", "I2CDongle", "upper")
                if t not in ("WARNING", "MISSING"):
                    t = t.strip()
                    try:
                        if t in ["ISS", "ELV", "IOW"]:                  g.I2CDongleName = t     # no FTD support!
                        else:                                           g.I2CDongleName = "ISS"
                    except:
                        g.I2CDongleName = "ISS"
                    cfg_dprint(infostr.format("Dongle",                 g.I2CDongleName))


                # I2C usbport
                t = getConfigEntry("I2CDevice", "I2Cusbport", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                             g.I2Cusbport = "auto"
                    else:                                               g.I2Cusbport = t
                    cfg_dprint(infostr.format("Serial Port",            g.I2Cusbport))


                # I2C Sensors Options (3 sep by comma):  < yes | no > , <Sensor Addr in hex>, <variables>
                # like: I2CSensorBME280  = y, 0x76, Temp, Press, Humid
                # here 'y' and 'n' can be used for 'yes' and 'no'

                # I2C Sensors - LM75, addr 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4E | 0x4F
                # like: I2CSensorLM75      = yn, 0x48, CPS3rd
                t = getConfigEntry("I2CDevice", "I2CSensorLM75", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["LM75"][0] = True
                        else:                                           g.I2CSensor["LM75"][0] = False
                        g.I2CSensor["LM75"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["LM75"][0] = False
                        g.I2CSensor["LM75"][1] = 0x48
                    g.I2CSensor["LM75"][2] = t[2:]
                    cfg_dprint(infostr.format("SensorLM75",             g.I2CSensor["LM75"]))


                # I2C Sensors - BME280, addr 0x76 | 0x77
                # I2CSensorBME280 : [True, 118, [' Temp', ' Press', ' Humid']]
                t = getConfigEntry("I2CDevice", "I2CSensorBME280", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["BME280"][0] = True
                        else:                                           g.I2CSensor["BME280"][0] = False
                        g.I2CSensor["BME280"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["BME280"][0] = False
                        g.I2CSensor["BME280"][1] = 0x76
                    g.I2CSensor["BME280"][2] = t[2:]
                    cfg_dprint(infostr.format("SensorBME280",           g.I2CSensor["BME280"]))


                # I2C Sensors - SCD41, addr 0x62
                t = getConfigEntry("I2CDevice", "I2CSensorSCD41", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["SCD41"][0] = True
                        else:                                           g.I2CSensor["SCD41"][0] = False
                        g.I2CSensor["SCD41"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["SCD41"][0] = False
                        g.I2CSensor["SCD41"][1] = 0x29
                    g.I2CSensor["SCD41"][2] = t[2:]
                    cfg_dprint(infostr.format("SensorSCD41",            g.I2CSensor["SCD41"]))

                # I2C Sensors - SCD30, addr 0x61
                t = getConfigEntry("I2CDevice", "I2CSensorSCD30", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["SCD30"][0] = True
                        else:                                           g.I2CSensor["SCD30"][0] = False
                        g.I2CSensor["SCD30"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["SCD30"][0] = False
                        g.I2CSensor["SCD30"][1] = 0x61
                    g.I2CSensor["SCD30"][2] = t[2:]
                    cfg_dprint(infostr.format("SensorSCD30",            g.I2CSensor["SCD30"]))

                # I2C Sensors - TSL2591, addr 0x29
                t = getConfigEntry("I2CDevice", "I2CSensorTSL2591", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["TSL2591"][0] = True
                        else:                                           g.I2CSensor["TSL2591"][0] = False
                        g.I2CSensor["TSL2591"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["TSL2591"][0] = False
                        g.I2CSensor["TSL2591"][1] = 0x29
                    g.I2CSensor["TSL2591"][2] = t[2:]
                    cfg_dprint(infostr.format("SensorTSL2591",          g.I2CSensor["TSL2591"]))


                # I2C Sensors - BH1750, addr 0x23 oder 0x5C
                t = getConfigEntry("I2CDevice", "I2CSensorBH1750", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["BH1750"][0] = True
                        else:                                           g.I2CSensor["BH1750"][0] = False
                        g.I2CSensor["BH1750"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["BH1750"][0] = False
                        g.I2CSensor["BH1750"][1] = 0x23
                    g.I2CSensor["BH1750"][2] = t[2:]
                    cfg_dprint(infostr.format("SensorBH1750",           g.I2CSensor["BH1750"]))


                # I2C Sensors - GDK101, addr 0x18
                t = getConfigEntry("I2CDevice", "I2CSensorGDK101", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["GDK101"][0] = True
                        else:                                           g.I2CSensor["GDK101"][0] = False
                        g.I2CSensor["GDK101"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["GDK101"][0] = False
                        g.I2CSensor["GDK101"][1] = 0x18
                    g.I2CSensor["GDK101"][2] = t[2:]                    # the variables
                    cfg_dprint(infostr.format("SensorGDK101",           g.I2CSensor["GDK101"]))


                # I2C Sensors - LTR390, addr 0x53
                t = getConfigEntry("I2CDevice", "I2CSensorLTR390", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["LTR390"][0] = True
                        else:                                           g.I2CSensor["LTR390"][0] = False
                        g.I2CSensor["LTR390"][1] = int(t[1], 16)
                    except:
                        g.I2CSensor["LTR390"][0] = False
                        g.I2CSensor["LTR390"][1] = 0x18
                    g.I2CSensor["LTR390"][2] = t[2:]                    # the variables
                    cfg_dprint(infostr.format("SensorLTR390",           g.I2CSensor["LTR390"]))


                # I2C Sensors - INA228, addr 0x40
                t = getConfigEntry("I2CDevice", "I2CSensorINA228", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():                 g.I2CSensor["INA228"][0] = True     # activate
                        else:                                           g.I2CSensor["INA228"][0] = False
                        g.I2CSensor["INA228"][1] = int(t[1], 16)                                            # address
                    except:
                        g.I2CSensor["INA228"][0] = False
                        g.I2CSensor["INA228"][1] = 0x40
                    g.I2CSensor["INA228"][2] = t[2:]                    # the variables
                    cfg_dprint(infostr.format("SensorINA228",           g.I2CSensor["INA228"]))



    # RaspiI2C
        # RaspiI2C Activation
        t = getConfigEntry("RaspiI2CDevice", "RaspiI2CActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["RaspiI2C"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["RaspiI2C"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("RaspiI2C Device", ""))


                # in config find:
                #    I2C Sensors Options (4 sep by comma):  < yes | no > , <Sensor Addr in hex>, <avg cycles>, <variables sep. by comma>
                #    like: I2CSensorBME280  = yn, 0x76, 3, Temp, Press, Humid
                #    TIP: the presence of "y" in the first column makes it a "yes"; its absence a "no"

                # RaspiI2C Sensors - LM75, addr 0x48 | 0x49 | 0x4A | 0x4B | 0x4C | 0x4E | 0x4F
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorLM75", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["LM75"][1] = True
                        else:                                   g.RaspiI2CSensor["LM75"][1] = False
                        g.RaspiI2CSensor["LM75"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["LM75"][1] = False
                        g.RaspiI2CSensor["LM75"][0] = 0x48
                    try:
                        g.RaspiI2CSensor["LM75"][7] = int(float(t[2]))
                    except:
                        pass

                    g.RaspiI2CSensor["LM75"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorLM75",         g.RaspiI2CSensor["LM75"]))


                # RaspiI2C Sensors - BME280, addr 0x76 | 0x77
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorBME280", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["BME280"][1] = True
                        else:                                   g.RaspiI2CSensor["BME280"][1] = False
                        g.RaspiI2CSensor["BME280"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["BME280"][1] = False
                        g.RaspiI2CSensor["BME280"][0] = 0x76
                    try:
                        g.RaspiI2CSensor["BME280"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["BME280"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorBME280",       g.RaspiI2CSensor["BME280"]))


                # RaspiI2C Sensors - BH1750, addr 0x23 oder 0x5C
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorBH1750", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["BH1750"][1] = True
                        else:                                   g.RaspiI2CSensor["BH1750"][1] = False
                        g.RaspiI2CSensor["BH1750"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["BH1750"][1] = False
                        g.RaspiI2CSensor["BH1750"][0] = 0x23
                    try:
                        g.RaspiI2CSensor["BH1750"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["BH1750"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorBH1750",       g.RaspiI2CSensor["BH1750"]))


                # RaspiI2C Sensors - TSL2591, addr 0x29
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorTSL2591", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["TSL2591"][1] = True
                        else:                                   g.RaspiI2CSensor["TSL2591"][1] = False
                        g.RaspiI2CSensor["TSL2591"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["TSL2591"][1] = False
                        g.RaspiI2CSensor["TSL2591"][0] = 0x29
                    try:
                        g.RaspiI2CSensor["TSL2591"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["TSL2591"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorTSL2591",      g.RaspiI2CSensor["TSL2591"]))


                # RaspiI2C Sensors - BMM150, addr 0x10
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorBMM150", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["BMM150"][1] = True
                        else:                                   g.RaspiI2CSensor["BMM150"][1] = False
                        g.RaspiI2CSensor["BMM150"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["BMM150"][1] = False
                        g.RaspiI2CSensor["BMM150"][0] = 0x29
                    try:
                        g.RaspiI2CSensor["BMM150"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["BMM150"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorBMM150",      g.RaspiI2CSensor["BMM150"]))


                # RaspiI2C Sensors - SCD30, addr 0x61
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorSCD30", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["SCD30"][1] = True
                        else:                                   g.RaspiI2CSensor["SCD30"][1] = False
                        g.RaspiI2CSensor["SCD30"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["SCD30"][1] = False
                        g.RaspiI2CSensor["SCD30"][0] = 0x29
                    try:
                        g.RaspiI2CSensor["SCD30"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["SCD30"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorSCD30",      g.RaspiI2CSensor["SCD30"]))


                # RaspiI2C Sensors - SCD41, addr 0x62
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorSCD41", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["SCD41"][1] = True
                        else:                                   g.RaspiI2CSensor["SCD41"][1] = False
                        g.RaspiI2CSensor["SCD41"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["SCD41"][1] = False
                        g.RaspiI2CSensor["SCD41"][0] = 0x29
                    try:
                        g.RaspiI2CSensor["SCD41"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["SCD41"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorSCD41",      g.RaspiI2CSensor["SCD41"]))


                # RaspiI2C Sensors - GDK101, addr 0x18
                t = getConfigEntry("RaspiI2CDevice", "RaspiI2CSensorGDK101", "str")
                if t not in ("WARNING", "MISSING"):
                    t = t.split(",")
                    try:
                        if "Y" in t[0].strip().upper():         g.RaspiI2CSensor["GDK101"][1] = True
                        else:                                   g.RaspiI2CSensor["GDK101"][1] = False
                        g.RaspiI2CSensor["GDK101"][0] = int(t[1], 16)
                    except:
                        g.RaspiI2CSensor["GDK101"][1] = False
                        g.RaspiI2CSensor["GDK101"][0] = 0x29
                    try:
                        g.RaspiI2CSensor["GDK101"][7] = int(float(t[2]))
                    except:
                        pass
                    g.RaspiI2CSensor["GDK101"][5] = t[3:]
                    cfg_dprint(infostr.format("SensorGDK101",      g.RaspiI2CSensor["GDK101"]))


    # RadPro
        # RadPro Activation
        t = getConfigEntry("RadProDevice", "RadProActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["RadPro"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["RadPro"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("RadPro Device", ""))

                # RadProPort
                t = getConfigEntry("RadProDevice", "RadProPort", "str")
                if t not in ("WARNING, "):
                    if t.upper() in ("AUTO", "MISSING"):                g.RadProPort = "auto"
                    else:                                               g.RadProPort = t
                    cfg_dprint(infostr.format("RadProPort",              g.RadProPort))


                # RadProClockCorrection
                t = getConfigEntry("RadProDevice", "RadProClockCorrection", "upper")
                if t not in ("WARNING, "):
                    if t in ("AUTO", "MISSING"):                        g.RadProClockCorrection = "auto"
                    else:
                        try:
                            intt = int(t)
                            if 0 <= intt < 60:                          g.RadProClockCorrection = int(t)
                            else:                                       g.RadProClockCorrection = "auto"
                        except Exception as e:
                            exceptPrint(e, "RadProClockCorrection t:'{t}'")
                            g.RadProClockCorrection = "auto"
                    cfg_dprint(infostr.format("RadProClockCorrection",   g.RadProClockCorrection))


                # RadProDevice Anode Voltage
                t = getConfigEntry("RadProDevice", "RadProVoltageDefault", "upper")
                if t not in ("WARNING",):
                    if t in ("AUTO", "MISSING"):                        g.RadProVoltageDefault = "auto"
                    else:
                        try:
                            ft = float(t)
                            if ft < 200 or ft > 800:                    g.RadProVoltageDefault = "auto"
                            else:                                       g.RadProVoltageDefault = ft
                        except Exception as e:
                            exceptPrint(e, "RadProVoltageDefault setting: '{t}'")
                            g.RadProVoltageDefault                                             = "auto"
                    cfg_dprint(infostr.format("RadProVoltageDefault",    g.RadProVoltageDefault))


                # RadProDevice Anode Voltage Configuration
                t = getConfigEntry("RadProDevice", "RadProVoltageGeneration", "upper")
                if t not in ("WARNING",):
                    if t in ("AUTO", "MISSING"):                        g.RadProVoltageGeneration = "auto"
                    else:                                               g.RadProVoltageGeneration = t
                    cfg_dprint(infostr.format("RadProVoltageGeneration", g.RadProVoltageGeneration))


                # RadProDevice Anode Voltage Control
                t = getConfigEntry("RadProDevice", "RadProHVControl", "upper")
                if t not in ("WARNING",):
                    if t in ("AUTO", "MISSING"):                        g.RadProHVControl = "auto"
                    else:
                        ts = t.split(",")
                        if len(ts) == 3:
                            try:       active   = True if "Y" in ts[0] else False
                            except:    active   = None

                            try:       dtime    = clamp(float(ts[1]), 1, 1000)
                            except:    dtime    = None

                            try:       strength = clamp(float(ts[2]), 0.1, 1.0)
                            except:    strength = None

                            if   active is None or dtime is None or strength is None:   g.RadProHVControl = "auto"
                            else:                                                       g.RadProHVControl = [active, dtime, strength]
                        else:                                                           g.RadProHVControl = "auto"
                    cfg_dprint(infostr.format("RadProHVControl",                         g.RadProHVControl))


                # RadProVariables
                t = getConfigEntry("RadProDevice", "RadProVariables", "str")
                if t not in ("WARNING, "):
                    if t in ("AUTO", "MISSING"):                        g.RadProVariables = "auto"
                    else:                                               g.RadProVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("RadProVariables",        g.RadProVariables))


    # GEMF devices
        # GEMF Activation
        t = getConfigEntry("GEMF_Device", "GEMF_Activation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["GEMF"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["GEMF"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("GEMF Device", ""))


                # GEMF_usbport
                t = getConfigEntry("GEMF_Device", "GEMF_usbport", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                     g.GEMF_usbport = "auto"
                    else:                                       g.GEMF_usbport = t
                    cfg_dprint(infostr.format("GEMF_usbport",    g.GEMF_usbport))


                # GEMF Device ID (Model, Serial No)
                t = getConfigEntry("GEMF_Device", "GEMF_ID", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":                   g.GEMF_ID = "auto"
                    else:
                        ts = t.split(",")
                        if len(ts) != 2:                        g.GEMF_ID = "auto"
                        else:
                            ts[0] = ts[0].strip()
                            ts[1] = ts[1].strip()
                            if ts[0].upper() == "NONE": ts[0] = None
                            if ts[1].upper() == "NONE": ts[1] = None
                            g.GEMF_ID = ts
                    cfg_dprint(infostr.format("GEMF Device IDs", g.GEMF_ID))


                # GEMF_ClockCorrection
                t = getConfigEntry("GEMF_Device", "GEMF_ClockCorrection", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                             g.GEMF_ClockCorrection = "auto"
                    else:
                        try:
                            if 0 <= int(t) < 60:                        g.GEMF_ClockCorrection = int(t)
                            else:                                       g.GEMF_ClockCorrection = "auto"
                        except Exception as e:
                            exceptPrint(e, "GEMF_ClockCorrection t:'{t}'")
                            g.GEMF_ClockCorrection = "auto"
                    cfg_dprint(infostr.format("GEMF_ClockCorrection",   g.GEMF_ClockCorrection))


                # GEMF Command
                t = getConfigEntry("GEMF_Device", "GEMF_CustomCmd", "str")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":                           g.GEMF_CustomCmd = "auto"
                    elif t.upper() == "NONE":                           g.GEMF_CustomCmd = "auto"
                    else:
                        try:
                            if t.startswith("<") and t.endswith(">>"):  g.GEMF_CustomCmd = t
                            else:                                       g.GEMF_CustomCmd = "auto"
                        except Exception as e:
                            exceptPrint(e, "GEMF_CustomCmd t:'{t}'")
                            g.GEMF_CustomCmd = "auto"
                    cfg_dprint(infostr.format("GEMF_CustomCmd",         g.GEMF_CustomCmd))


                # GEMF_Variables
                t = getConfigEntry("GEMF_Device", "GEMF_Variables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                             g.GEMF_Variables = "auto"
                    else:                                               g.GEMF_Variables = t
                    cfg_dprint(infostr.format("GEMF_Variables",         g.GEMF_Variables))


    #DMM
        ##############################################################################
        ### test Mac Address
        def isMacAddress(x):
            # if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", x.lower()): return True  # für 12 Hex zahlen
            if re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){2}$", x.lower()): return True    # für 6 Hex Zahlen
            else:                                                                        return False
        ##############################################################################

        # DMM Activation
        t = getConfigEntry("DMM", "DMMActivation", "upper")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["DMM"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["DMM"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("DMM Device", ""))

                # DMM Device
                t = getConfigEntry("DMM", "DMMDevice", "str")
                # mdprint(defname, f"t: '{t}'  isMacAddress: {isMacAddress(t)}")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO" :                          g.DMMDevice = "auto"
                    elif t.upper() == "" :                              g.DMMDevice = "auto"        # empty becomes BDM
                    elif isMacAddress(t):                               g.DMMDevice = "BDM|" + t    # it is only a MAC string; needs label
                    else:                                               g.DMMDevice = t
                    cfg_dprint(infostr.format("DMMDevice",              g.DMMDevice))


                # DMM Variables
                t = getConfigEntry("DMM", "DMMVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO" :                            g.DMMVariables = "auto"
                    else:                                               g.DMMVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("DMMVariables",           g.DMMVariables))




    # Formula Device
        # Formula Device Activation
        t = getConfigEntry("Formula", "FormulaActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.Devices["Formula"][g.ACTIV] = True
                ActivatedDevices += 1

            if g.Devices["Formula"][g.ACTIV]: # show the other stuff only if activated
                cfg_dprint(infostrHeader.format("Formula Device", ""))

                # Formula Device Variables
                t = getConfigEntry("Formula", "FormulaVariables", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                     g.FormulaVariables = "auto"
                    else:                                       g.FormulaVariables = correctVariableCaps(t)
                    cfg_dprint(infostr.format("FormulaVariables",   g.FormulaVariables))



        ActivatedDevices2 = 0
        for dev in g.Devices:
            # irdprint(defname, f"dev: {dev}")
            if g.Devices[dev][g.ACTIV]: ActivatedDevices2 += 1

        # irdprint(defname, f"ActivatedDevices:  {ActivatedDevices}")
        # irdprint(defname, f"ActivatedDevices2: {ActivatedDevices2}")

        if ActivatedDevices2 == 0:
            cfg_dprint(infostrHeader.format("None found", ""))



    # FritzBox devices
        # FritzBox Activation
        t = getConfigEntry("FritzBox", "FritzBoxActivation", "upper", fallback="NO")
        if t not in ("WARNING", "MISSING"):
            if t == "YES":
                g.FritzBoxActivation = True
                ActivatedDevices += 1
                cfg_dprint(infostrHeader.format("FritzBox", ""))

                # FritzBox IP
                t = getConfigEntry("FritzBox", "FritzBoxIP", "str")
                if t not in ("WARNING", "MISSING"):
                    if t.upper() == "AUTO":                         g.FritzBoxIP = "auto"
                    else:                                           g.FritzBoxIP = t
                    cfg_dprint(infostr.format("FritzBoxIP",         g.FritzBoxIP))


                # FritzBox Password
                t = getConfigEntry("FritzBox", "FritzBoxPassword", "rawstr")
                if t not in ("WARNING", "MISSING"):
                    if   t.upper() == "AUTO":                       g.FritzBoxPassword = "auto"
                    else:                                           g.FritzBoxPassword = t
                    cfg_dprint(infostr.format("FritzBoxPassword",   "*" * 10))


        infostrHeader = "{:35s} {}"            # back to original settings
        infostr       = "    {:35s}: {}"

    # End Devices *************************************************************************************


    #### removed from code !!!!!!!!!!
    # # Telegram
    #     section   = "Telegram"
    #     dprint(infostrHeader.format(section, ""))

    #     # Telegram Activation
    #     t = getConfigEntry(section, "TelegramActivation", "upper")
    #     if t not in ("WARNING", "MISSING"):
    #         if t == "YES":                          g.TelegramActivation = True
    #         ActivatedDevices += 1
    #     # rdprint(defname, "1   g.TelegramActivation: ", g.TelegramActivation)

    #     if not g.TelegramActivation:
    #         dprint(infostr.format(section, "is NOT activated"))
    #         # rdprint(defname, "2   g.TelegramActivation: ", g.TelegramActivation)

    #     else:
    #         # Telegram Token
    #         t = getConfigEntry(section, "TelegramToken", "str")
    #         if t not in ("WARNING", "MISSING"):
    #             g.TelegramToken = t.strip()
    #         dprint(infostr.format("TelegramToken",          g.TelegramToken))


    #         # Telegram UpdateCycle
    #         t = getConfigEntry(section, "TelegramUpdateCycle", "upper")
    #         if t not in ("WARNING", "MISSING"):
    #             if t == "AUTO":                             g.TelegramUpdateCycle = 3600
    #             else:
    #                 try:    g.TelegramUpdateCycle = float(t)
    #                 except: g.TelegramUpdateCycle = 3600
    #         dprint(infostr.format("TelegramUpdateCycle",    g.TelegramUpdateCycle))


    #         # Telegram ChatID
    #         t = getConfigEntry(section, "TelegramChatID", "str")
    #         if t not in ("WARNING", "MISSING"):
    #             g.TelegramChatID = t.strip
    #         dprint(infostr.format("TelegramChatID",    g.TelegramChatID))


    ### New feature Spectro *************************************************************************************
    # Spectro
        section = "Spectro"
        SpectroErrmsg  = "\n<b>Problems in Configuration File for Spectro</b>\n"
        t = getConfigEntry(section, "CalibLines", "rawstr")
        if t not in ("WARNING", "MISSING"):
            raw_spectroCalibLines = t.split("\n")
            # irdprint(defname, f"raw_spectroCalibLines: {raw_spectroCalibLines}")
            cleanCalibLines = []
            for line in raw_spectroCalibLines:
                # irdprint(defname, f"line: {line}")
                sline = line.strip()
                if sline > "":
                    sls = sline.split(",", 2)
                    # irdprint(defname, f"sls: {sls}")
                    cleanCalibLines.append(f"{sls[0].strip()},{sls[1].strip()},{sls[2].strip()}")

            g.spectroCalibLines = cleanCalibLines.copy()
            # cfg_dprint(infostr.format("CalibLines", g.spectroCalibLines))

        if config.has_option(section, "CalibLinesCustom"):
            t = getConfigEntry(section, "CalibLinesCustom", "rawstr")
            if t not in ("WARNING", "MISSING"):
                custom_spectroCalibLines = t.split("\n")
                # irdprint(defname, f"custom_spectroCalibLines: {custom_spectroCalibLines}")
                cleanCalibLines = []
                for line in custom_spectroCalibLines:
                    # irdprint(defname, f"line: {line}")
                    sline = line.strip()
                    if sline > "":
                        sls = sline.split(",", 2)
                        # irdprint(defname, f"sls: {sls}")
                        cleanCalibLines.append(f"{sls[0].strip()},{sls[1].strip()},{sls[2].strip()}")

                # cfg_dprint(infostr.format("CustomCalibLines", cleanCalibLines))
                g.spectroCalibLines += cleanCalibLines.copy()                       # combine full and custom


    # End New feature Spectro *************************************************************************************


        if g.configAlerts > "":
            errmsg  = f"\n\n<b>Problems in GeigerLog Configuration File: '{filename}'</b>\n"
            errmsg += f"-" * 100
            # if filename == "geigerlog.cfg": g.configAlertsDef  = errmsg + "\n\n" + g.configAlerts
            # else:                           g.configAlertsCust = errmsg + "\n\n" + g.configAlerts
            if filename == "geigerlog.cfg": g.configAlertsDef  = errmsg + "\n" + g.configAlerts
            else:                           g.configAlertsCust = errmsg + "\n" + g.configAlerts

        g.configAlerts = ""

        dprint(defname, f"Reading '{filename}' complete")

        break # still in while loop, don't forget to break!

    setIndent(0)

# End Configuration file evaluation #############################################################################
#################################################################################################################


def readPrivateConfig():
    """reads the private.cfg file if present, and adds the definitions to the config.
    If not present, the geigerlog.cfg settings remain in use unmodified"""
    # g.TelegramToken was e.g. 2008102243:AAHGv...kG9Pg1rfVY. It is no longr in use
    # g.TelegramToken    = data[4].strip()
    # g.TelegramChatID   = data[5].strip()
    #
    # the private file uses this format:
    # g.WiFiSSID, g.WiFiPassword, g.gmcmapUserID, g.gmcmapCounterID, g.FritzBoxIP, g.FritzBoxPassword
    # like:
    #       mySSID, myPW, 012345, 01234567890, 1.2.3.4, myFBPW

    defname  = "readPrivateConfig: "
    dprint(defname)
    setIndent(1)

    filepath = os.path.join(g.progDir, "../private.cfg")
    if not os.access(filepath, os.R_OK) :
        dprint("{:25s}: {}".format(defname, "Private file is not readable"))
    else:
        dprint("{:25s}: {}".format(defname, "Private file is readable"))
        try:
            with open(filepath) as f:
                pfilecfg = f.readlines()
        except Exception as e:
            exceptPrint(e, defname + "FAILURE reading Private file")
        else:
            try:
                foundData = False
                for i, line in enumerate(pfilecfg):
                    a = line.strip()
                    if   a.startswith("#"): continue
                    elif a == "":           continue
                    else:
                        # gdprint("{:25s}: {}".format(defname, "line: {}:  {}".format(i, a[:-1])))
                        data = a.split(",")
                        if len(data) >= 6:
                            g.WiFiSSID         = data[0].strip()
                            g.WiFiPassword     = data[1].strip()
                            g.gmcmapUserID     = data[2].strip()
                            g.gmcmapCounterID  = data[3].strip()
                            g.FritzBoxIP       = data[4].strip()
                            g.FritzBoxPassword = data[5].strip()
                            foundData = True
                        else:
                            dprint("{:25s}: {}".format(defname, "Not enough data in Private file; you need to have at least 6 entries"))

                if not foundData:
                    dprint("{:25s}: {}".format(defname, "Invalid Private file"))

            except Exception as e:
                exceptPrint(e, defname + "FAILURE interpreting Private file")

    setIndent(0)



