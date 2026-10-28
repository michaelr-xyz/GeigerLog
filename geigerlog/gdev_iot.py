#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
gdev_iot.py     IOT Device support using a MQTT connection
                including support of Tasmota devices
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

# which programs are using a certain port?
#       sudo netstat -anp | grep 1883


# Installing MQTT on Ubuntu:
# see: https://www.digitalocean.com/community/tutorials/how-to-install-and-secure-the-mosquitto-mqtt-messaging-broker-on-ubuntu-16-04
# site includes steps to set up secure server!

# To install the software on a Linux system:
#     sudo apt-get install mosquitto mosquitto-clients
#     without anything else, the mosquitto server will ONLY respond to 'localhost'!!!

# Testing MQTT, assuming mosqitto running on mysite.com:
# Subscribe in terminal #1:
#     mosquitto_sub -v -h mysite.com -p <port> -t geigerlog/#
#     example: mosquitto_sub -v -h test.mosquitto.org -t "geigerlog/#"
#     example: mosquitto_sub -v -h 10.0.0.51 -t "geigerlog/temp/#"
#     example: mosquitto_sub -v -h localhost -p 1885 -t "geigerlog/temp/#"


# Publish in terminal #2:
#     mosquitto_pub -h mysite.com -t geigerlog/temp -m "hello world"
#     example: mosquitto_pub -h test.mosquitto.org -t geigerlog/temp  -m "hello world"
#     example: mosquitto_pub -h 10.0.0.51          -t geigerlog/temp  -m "hello world"
#     example: mosquitto_pub -h localhost -p 1885  -t geigerlog/temp  -m "hello world"

# You should see in terminal #1:
#     geigerlog/temp hello world

#     or with GLDataServer running on Raspi with current setting:
#         geigerlog/data 456,2.933,25,3.425121,,,,,21.9,1017.697,41.201,607.5

# Running mosquitto locally
#   mosquitto -c mostest.conf
#   content of /home/ullix/.mosquitto/mostest.conf:
#       listener 1883                                               # using (standard) port 1883
#       #allow_anonymous true                                       # this allows password free access
#       allow_anonymous false                                       # this reqires user & password
#       password_file /etc/mosquitto/mospw.txt                      # the pw file can be anywhere
#
#   content of password file: mospw.txt:
#       rw:$7$101$IAmdz8+idAePnwJ5$X1MZn9zxz8oqZ04pXW/sQpFhTxi85O4jkaE0u99cc8ZUWQN1BRED0qtwkpWixcXapuBM284OVWOeE+9TgoQZcQ==
#
#   generating a password file:
#       create pw file with 1st user rw: mosquitto_passwd -c ~/.mosquitto/mospw.txt rw
#       create more user:                mosquitto_passwd -b ...

# To use test.mosquitto.org with user and password:
# mosquitto_sub -h test.mosquitto.org -t "geigerlog/#" -u rw -P readwrite -p 1884 -v

# Important consideration paho-mqtt
# see:  https://github.com/eclipse/paho.mqtt.python/issues/514

# Tasmota Device Manager:
# https://github.com/jziolkowski/tdm
# GUI application to discover and monitor devices flashed with https://github.com/arendst/Sonoff-Tasmota

# install:    pip install tdmgr       (broader: https://github.com/jziolkowski/tdm/wiki/Prerequisites-installation-and-running)
# CAUTION:    Successfully uninstalled PyQt5-5.15.9, Successfully installed PyQt5-5.14.2 tdmgr-0.2.11
#             Installing tdmgr.py is Downgrading PyQt5 !!!
# start:      tdmgr.py

# Calibration Procedure:
#     Verify the Power reading in the web UI (optionally with the power meter as well) for the
#     expected wattage. Adjust the power offset if needed (in Watts):
#     PowerSet 60.0
#     If you're using something other than a 60W bulb, enter your load's power rating

#     Verify the Voltage reading. Adjust the voltage offset if needed (in Volts):
#     VoltageSet <voltage>
#     Replace <voltage> with your standard voltage or with reading on your multi-meter if you have
#     one. Your voltage will vary depending on the electrical standards and your electrical grid.

# Configuring Tasmota Plug:
#     - in tablet select WLAN tasmota-xyz....
#     - in browser enter 192.168.4.1 and select own network
#     - in tablet WLAN config select own network
#     - in browser enter ip of new plug and configure


#
# TASMOTA Templates
#
# Plug:  Nous A8T 10A Power Monitoring Plug (A8T)
# https://templates.blakadder.com/nous_A8T.html
# Configuration for ESP32
# Eingabe unter: Configuration --> Other parameters
# check: Activate!
# Save
# {"NAME":"NOUS A8T","GPIO":[1,1,320,1,32,1,1,1,1,224,2624,1,1,1,1,1,0,1,1,1,0,1,2656,2720,0,0,0,0,1,1,1,1,1,0,0,1],"FLAG":0,"BASE":1}
# "calibrating" the Voltage: on Console enter: 'VoltageSet 233'  to set Voltage to 233 Volt
# setting resolution:                          'Voltres 3'       to set voltage to 3 decimal places
# setting resolution:                          'Wattres 3'       to set Power   to 3 decimal places


# Plug:  Eightree 16A Plug (ET28)
# https://templates.blakadder.com/eightree_16A.html
# Configuration for ESP32-C3:
# {"NAME":"EIGHTREE","GPIO":[0,0,0,2720,2624,32,224,2656,0,0,0,0,0,0,0,0,0,0,0,0,320,7648],"FLAG":0,"BASE":1}
#
#
# Configuring SmartMeter Reader bitShake-Air
# SmartReader PIN:
#     WICHTIG:  nach Eingabe der PIN muss man durch das ganze Menü wandern, umd am Ende
#     einzugeben: PIN=OFF  !!! Erst dann wird die PIN nicht erneut abgefragt
#     Ebenfalls: info=ON
#
#
# see: https://tasmota.github.io/docs/Smart-Meter-Interface/#descriptor-syntax
# +<M>,<rxGPIO>,<type>,  <flag>,      <parameter>,<jsonPrefix>{,<txGPIO>,<txPeriod>,<cmdTelegram>}
# + 1,  pin,     o(OBIS), [0,1,16,32],9600baud,    eBZ,          pin(opt)

# WattWaechter Script  - see difference in line: +1,3,...
# >D
# >B
# =>sensor53 r
# >M 1
# +1,3,o,16,9600,eBZ,4
# 1,1-0:1.8.0*255(@1,Verbrauch,kWh,E_in,8
# 1,1-0:2.8.0*255(@1,Einspeisung,kWh,E_out,3
# 1,1-0:32.7.0*255(@1,Spannung L1,V,32_7_0,6
# 1,1-0:52.7.0*255(@1,Spannung L2,V,52_7_0,3
# 1,1-0:72.7.0*255(@1,Spannung L3,V,72_7_0,0
# 1,1-0:16.7.0*255(@1,akt. Leistung,W,Power,3
# 1,1-0:36.7.0*255(@1,Leistung L1,W,36_7_0,2
# 1,1-0:56.7.0*255(@1,Leistung L2,W,56_7_0,2
# 1,1-0:76.7.0*255(@1,Leistung L3,W,76_7_0,2
# 1,1-0:96.1.0*255(@#),Identifikation,,96_1_0,0
# #

# bitShake Script - see difference in line: +1,5,...
# >D
# >B
# =>sensor53 r
# >M 1
# +1,5,o,16,9600,eBZ,4
# 1,1-0:1.8.0*255(@1,Verbrauch,kWh,E_in,3
# 1,1-0:2.8.0*255(@1,Einspeisung,kWh,E_out,3
# 1,1-0:32.7.0*255(@1,Spannung L1,V,32_7_0,6
# 1,1-0:52.7.0*255(@1,Spannung L2,V,52_7_0,3
# 1,1-0:72.7.0*255(@1,Spannung L3,V,72_7_0,0
# 1,1-0:16.7.0*255(@1,Leistung,W,Power,3
# 1,1-0:36.7.0*255(@1,Leistung L1,W,36_7_0,3
# 1,1-0:56.7.0*255(@1,Leistung L2 OG,W,56_7_0,3
# 1,1-0:76.7.0*255(@1,Leistung L3,W,76_7_0,3
# 1,1-0:96.1.0*255(@#),Identifikation,,96_1_0,0
# #

# Dimex script  - see difference in line: +1,3,...
# >D
# >B
# =>sensor53 r
# >M 1
# +1,3,o,1,9600,eBZ,4
# 1,1-0:1.8.0*255(@1,Verbrauch,kWh,E_in,3
# 1,1-0:2.8.0*255(@1,Einspeisung,kWh,E_out,3
# 1,1-0:16.7.0*255(@1,akt. Leistung,W,Power,3
# 1,1-0:36.7.0*255(@1,Leistung L1,W,36_7_0,3
# 1,1-0:56.7.0*255(@1,Leistung L2,W,56_7_0,3
# 1,1-0:76.7.0*255(@1,Leistung L3,W,76_7_0,3
# 1,1-0:32.7.0*255(@1,Spannung L1,V,32_7_0,3
# 1,1-0:52.7.0*255(@1,Spannung L2,V,52_7_0,3
# 1,1-0:72.7.0*255(@1,Spannung L3,V,72_7_0,3
# 1,1-0:96.1.0*255(@#),Identifikation,,96_1_0,0
# #

# all Smart Meter Readers (bitShake, WattWächter, Diamex)
# eBZ Verbrauch	21328,910 kWh               # CPM1st
# eBZ Einspeisung	0,000 kWh               # CPS1st
#
# eBZ Spannung L1	0,000 V                 # CPM2nd
# eBZ Spannung L2	0,000 V                 # CPS2nd
# eBZ Spannung L3	0,000 V                 # CPM3rd
#
# eBZ akt. Leistung	304,240 W               # Temp
# eBZ Leistung L1	47,200 W                # Press
# eBZ Leistung L2	254,020 W               # Humid
# eBZ Leistung L3	3,180 W                 # Xtra
#
# eBZ Identifikation "1EBZ0100900290"       # g.IOTClientTasmotaSMRID
#

# see: https://community.simon42.com/t/ebz-dd3-esplesekopf-und-fehlende-daten/9765/4
# ; Statuswort, 4 Byte Information über den Betriebszustand, HEX string
# ; tasmota can decode one string per device only!
# ;1,1-0:96.5.0*255(@#),Status1,,96_5_0,0
# ;1,1-0:96.8.0*255(@#),Status2,,96_8_0,0

# Stattdessen wurde noch folgende Werte übertragen:
# 0.0-0:96_8_0__255 Wartungseintrag (Total)
# 0.1-0:0_0_0__255 Meter Owner Number
# 0.1-0:96_1_0__255 Serialnumber
# 0.1-0:96_5_0__255 Letzter Mittelwert 1 Wartungseintrag (Total)

# Script:
# Default: but with higher resolution in output)
# NOTE: for Wattwächter you need:  # +1,3,o,16,9600,eBZ,4
#       bitShake needs:            # +1,5,o,16,9600,eBZ,4
# -----------------------------------------------
# >D
# >B
# option???: TelePeriod 30
# =>sensor53 r
# >M 1
# +1,3,o,16,9600,eBZ,4
# 1,1-0:1.8.0*255(@1,Verbrauch,kWh,E_in,8
# 1,1-0:2.8.0*255(@1,Einspeisung,kWh,E_out,8
# 1,1-0:16.7.0*255(@1,akt. Leistung,W,Power,2
# 1,1-0:36.7.0*255(@1,Leistung L1,W,36_7_0,2
# 1,1-0:56.7.0*255(@1,Leistung L2,W,56_7_0,2
# 1,1-0:76.7.0*255(@1,Leistung L3,W,76_7_0,2
# ; Spannungen werden nicht angezeigt über den optischen Lesekopf
# 1,1-0:32.7.0*255(@1,Spannung L1,V,32_7_0,3
# 1,1-0:52.7.0*255(@1,Spannung L2,V,52_7_0,3
# 1,1-0:72.7.0*255(@1,Spannung L3,V,72_7_0,3
# 1,1-0:96.1.0*255(@#),Identifikation,,96_1_0,0
# #
# -----------------------------------------------------------------------------------------------
#
# Um Verbrauch anzuzeigen:
# see: https://www.smartcircuits.de/faq/  -> Tages- und Monatsverbrauch in der Übersicht anzeigen
# -----------------------------------------------------------------------------------------------
# >D
# p:nullUhr=0
# p:heute=0
# p:gestern=0
# p:vorgestern=0
# p:month1=0
# p:month2=0
# p:month3=0
# hr=0
# dy=0

# >B
# ->sensor53 r

# >S
# hr=hours
# dy=days

# if nullUhr==0
#   then
#     nullUhr=sml[2]
# endif

# if chg[hr]>0
#   and hr==0
#     then
#       nullUhr=sml[2]
#       vorgestern=gestern
#       gestern=heute
#       month1=month1+heute

#       if chg[dy]>0
#         and dy==1
#           then
#             month3=month2
#             month2=month1
#             month1=0
#       endif

#       ;p-Variablen im Flash speichern
#       svars
# endif

# heute=sml[2]-nullUhr

# >M 1
# +1,3,o,0,9600,eBZ
# 1,1-0:96.1.0*255(@#),Identifikation,,96_1_0,0
# 1,1-0:1.8.0*255(@1,Verbrauch,kWh,E_in,8
# 1,1-0:2.8.0*255(@1,Einspeisung,kWh,E_out,8
# 1,1-0:16.7.0*255(@1,Leistung Gesamt,W,Power,2
# 1,1-0:36.7.0*255(@1,Leistung L1,W,36_7_0,2
# 1,1-0:56.7.0*255(@1,Leistung L2,W,56_7_0,2
# 1,1-0:76.7.0*255(@1,Leistung L3,W,76_7_0,2
# #

# >W
# Verbrauch
# ----------------------------
# Heute: {m} %3heute% kWh
# Gestern: {m} %3gestern% kWh
# Vorgestern: {m} %3vorgestern% kWh
# ----------------------------
# Dieser Monat: {m} %3month1% kWh
# Letzter Monat: {m} %3month2% kWh
# Vorletzter Monat: {m} %3month3% kWh


# ; cannot show Spannungen
# ;1,1-0:32.7.0*255(@1,Spannung L1,V,32_7_0,3
# ;1,1-0:52.7.0*255(@1,Spannung L2,V,52_7_0,3
# ;1,1-0:72.7.0*255(@1,Spannung L3,V,72_7_0,3

# ;1,1-0:0.0.0*255(@#),Zähler ID,,meter_number,0
# -----------------------------------------------------------------------------------------------
#
# Default MQTT Einstellungen:
#   Host:       broker.hivemq.com
#   Port:       1883
#   user:       <empty>
#   pw:         <empty>
#   Topic:      TasmotaSMR
#   Full Topic: geigerlog/%prefix%/%topic%/
#
# Logging-Einstellungen:
#   Telemetrieperiode (300):  10              This is the Minimum accepted; aka the fastest setting
#   Telemetrieperiode (300):   0              This switches off the telemetrie


__author__          = "ullix"
__copyright__       = "Copyright 2016 - 2025"
__credits__         = [""]
__license__         = "GPL3"

from gsup_utils   import *


def initIOT():
    """Initialize the client and set all Callbacks"""

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    g.Devices["IOT"][g.DNAME] = "IOT Device"
    errmsg                    = ""                                                  # to be returned; no error if empty
    g.iot_data                = {}                                                  # holds the new data
    for vname in g.VarsCopy:  g.iot_data[vname] = g.NAN                             # fill new data with NANs

    # set auto configuration; default is WITHOUT authorization
    if g.IOTBrokerIP         == "auto": g.IOTBrokerIP      = g.GeigerLogIP
    if g.IOTBrokerPort       == "auto": g.IOTBrokerPort    = 1883
    if g.IOTBrokerFolder     == "auto": g.IOTBrokerFolder  = "geigerlog/"
    if g.IOTTimeout          == "auto": g.IOTTimeout       = 10
    if g.IOTUsername         == "auto": g.IOTUsername      = ""                     # no username -> without authorization
    if g.IOTPassword         == "auto": g.IOTPassword      = ""                     # no password -> without authorization

    autoclients  = ""
    autoclients += "yes,  Tplug1,   PVData,     CPM, CPS, CPM1st\n"
    autoclients += "no,   Tplug2,   Heater,     None, None, CPS2nd\n"
    autoclients += "no,   Tplug3,   FishTank,   CPM2nd, CPS2nd\n"
    autoclients += "no,   Tsmr1,    HomePower,  CPM3rd, CPS3rd, Temp, Press, Humid, Xtra\n"
    autoclients += "no,   GLdev,    GLdevice,   CPM, CPS, CPM1st, CPS1st, CPM2nd, CPS2nd, CPM3rd, CPS3rd, Temp, Press, Humid, Xtra"

    if g.IOTClients          == "auto": g.IOTClients       = autoclients

    # irdprint(defname, f"autoclients: {autoclients}")
    # irdprint(defname, f"g.IOTClients: {bytes(g.IOTClients, "utf-8")}")

    # reconfigure Client config
    # limit to max=4 splits to get no more than 5 items. Thus, all variables are then within one single value (to
    # avoid further splitting by the commas between var names)
    #
    # 0      1         2               3           4
    # y,     Tplug1,   PVData,         10,         CPM, CPS, CPM1st
    g.IOTClientConfig = {}
    totalvars         = ""
    for ccs in g.IOTClients.split("\n"):
        ccssplits = ccs.split(",", 3)
        for i in range(len(ccssplits)): ccssplits[i] = ccssplits[i].replace(" ", "")
        gdprint(defname, f"IOTclients: {ccssplits}")
        iotdev = ccssplits[1]
        g.IOTClientConfig[iotdev]    = ccssplits
        g.IOTClientConfig[iotdev][0] = True if "y" in g.IOTClientConfig[iotdev][0] else False        # active
        if g.IOTClientConfig[iotdev][0] : totalvars += g.IOTClientConfig[iotdev][3] + ", "

    # irdprint(defname, f"g.IOTClientConfig: {g.IOTClientConfig}")

    g.IOTVariables = setLoggableVariables("IOT", totalvars)

    #
    # set mqtt client as g.iot_client
    #
    # CAUTION: protocol can be either MQTTv31 or MQTTv311; MQTTv31 is deprecated - do NOT use!
    client_id = f'python-mqtt-{np.random.randint(0, 10)}'
    g.iot_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=client_id, clean_session=True, userdata="Keine ", protocol=mqtt.MQTTv311)

    # set callbacks
    g.iot_client.on_connect       = on_connect
    g.iot_client.on_subscribe     = on_subscribe
    g.iot_client.on_message       = on_message
    g.iot_client.on_publish       = on_publish
    g.iot_client.on_disconnect    = on_disconnect
    g.iot_client.on_log           = on_log                      # set client logging

    # connect
    try:
        # if a username is set, then configure for login with username + pw
        if g.IOTUsername > "":
            dprint(defname, f"using authorized access: username: '{g.IOTUsername}', Password: {g.IOTPassword}")
            g.iot_client.username_pw_set(username=g.IOTUsername, password=g.IOTPassword)
        else:
            dprint(defname, f"using NON-authorized access: username: '{g.IOTUsername}', Password: '{g.IOTPassword}'")

        dprint(defname, f"connecting to: IOTBrokerIP: '{g.IOTBrokerIP}', IOTBrokerPort: {g.IOTBrokerPort}")
        g.iot_client.connect(g.IOTBrokerIP, port=g.IOTBrokerPort, keepalive=180)       # 180 sec (default=60sec)
        g.iot_client.user_data_set("<empty>")                                          # set userdata to my "empty"

    except Exception as e:
        srcinfo = defname + "ERROR: Connection to IOT server failed"
        exceptPrint(e, srcinfo)
        g.iot_client     = None
        errmsg += f"\nERROR: Connection failed using: server IP='{g.IOTBrokerIP}', port={g.IOTBrokerPort}"
        errmsg += f"\nERROR: '{sys.exc_info()[1]}'"
        errmsg += f"\n{g.Devices["IOT"][g.DNAME]} not connected. Is server offline? Verify server IP, server port, username, and password"

        setIndent(0)
        return errmsg

    # start the loop
    g.iot_client.loop_start()                                       # threaded loop; must be stopped on exit!
    dprint(defname + "IOT client loop was started")

    # wait for confirmation of connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.IOTTimeout):
        if g.IOTconnectionState:
            timeout = False
            g.IOTconnectDuration = "{:0.3f} ms".format((time.time() - starttime) * 1000)
            dprint(defname + "Connected after: {}".format(g.IOTconnectDuration))
            break
        time.sleep(0.01)

    ### needed?
    if timeout:
        # no callback received; i.e. no connection
        dprint(defname, f"IOT connection timed out ({g.IOTTimeout} sec)")
        errmsg += "Timeout ERROR: Connection to IOT server failed; IOT inactivated"
        g.IOTconnectDuration = f"Failure, timeout after {g.IOTTimeout} sec"                         # for use in info
        g.Devices["IOT"][g.CONN] = False
    else:
        g.Devices["IOT"][g.CONN] = g.IOTconnectionState

        g.IOTThreadRun         = True
        g.IOTThread            = threading.Thread(target = IOTThreadTarget)
        g.IOTThread.daemon     = True                                                               # must come before start: makes threads stop on exit!
        g.IOTThread.start()

    setIndent(0)
    return errmsg


def terminateIOT():
    """opposit of init ;-)"""

    if g.iot_client is None: return

    defname = gd(sys._getframe().f_code.co_name)
    dprint(defname)
    setIndent(1)

    # stop MQTT thread
    dprint(defname + "stopping MQTT client loop")
    g.iot_client.loop_stop()

    # print("111111111111nanu????")

    # disconnect MQTT client
    dprint(defname, "disconnecting MQTT client")
    g.iot_client.disconnect()    # output printed in callback

    # print("22222222222nanu????")

    # shut down IOT thread
    dprint(defname, "stopping IOT thread")
    g.IOTThreadRun        = False
    g.IOTThread.join()                 # "This blocks the calling thread until the thread
                                       #  whose join() method is called is terminated."

    dprint(defname + "setting MQTT client to: None")
    g.iot_client = None

    # wait for confirmation of dis-connection
    starttime = time.time()
    timeout   = True
    while time.time() < (starttime  + g.IOTTimeout):
        if not g.IOTconnectionState:
            timeout = False
            break
        time.sleep(0.05)

    # verify that IOT thread has ended, but wait not longer than 5 sec (takes 0.006...0.016 ms)
    start = time.time()
    while g.IOTThread.is_alive() and (time.time() - start) < 5:
        pass
    msgalive = "Yes" if g.IOTThread.is_alive() else "No"
    waiting  = 1000 * (time.time() - start)
    dprint(defname, f"IOT thread-status: alive: {msgalive}, waiting took:{waiting:0.1f} ms")

    if timeout:
        dprint(defname, "IOT dis-connection timed out ({} sec)".format(g.IOTTimeout))
        QueuefPrint("ERROR: Dis-Connection from IOT server failed; IOT inactivated")
        retval = "timeout"
    else:
        retval = ""

    g.Devices["IOT"][g.CONN] = g.IOTconnectionState

    dprint(defname, "Terminated")
    setIndent(0)

    return retval


def getInfoIOT(extended=False):
    """Info on the IOT Device"""

    defname = gd(sys._getframe().f_code.co_name)

    IOTInfo =  f"Configured Connection:        MQTT on '{g.IOTBrokerIP}':{g.IOTBrokerPort}  topic: '{g.IOTBrokerFolder}'\n"

    if not g.Devices["IOT"][g.CONN]: return IOTInfo + "<red>Device is not connected</red>"

    IOTInfo += f"Connected Device:             {g.Devices["IOT"][g.DNAME]}\n"
    IOTInfo += f"Configured Variables overall: {g.IOTVariables}\n"
    IOTInfo += f"Client Devices:               Name        Topic       Cmnd      Vars\n"
    for i, clc in enumerate(g.IOTClientConfig):
        # irdprint(defname, "clc: ", clc)
        name  = g.IOTClientConfig[clc][2]
        topic = g.IOTClientConfig[clc][1]
        vars  = g.IOTClientConfig[clc][3]
        if g.IOTClientConfig[clc][0]:  IOTInfo += f"   Client Device #{i} {clc:6s}:   {name:10s}  {topic:10s}  {vars}\n"
        else:                          IOTInfo += f"   Client Device #{i} {clc:6s}:   {'Not activated'}\n"

    IOTInfo     += getTubeSensitivities(g.IOTVariables)

    if extended == True:
        IOTInfo += "\n"
        IOTInfo += "MQTT Timeout:                 {} sec\n".format(g.IOTTimeout)
        IOTInfo += "MQTT Username:                {}\n".format(g.IOTUsername if (g.IOTUsername > "") else "&lt;empty>")
        IOTInfo += "MQTT Password:                {}\n".format(g.IOTPassword if (g.IOTPassword > "") else "&lt;empty>")
        IOTInfo += "Duration of connecting:       {}\n".format(g.IOTconnectDuration)

    return IOTInfo


def IOTThreadTarget():
    """Thread triggers readings about some e.g. 300ms before next cycle is due"""

    defname = gd(sys._getframe().f_code.co_name)

    # find the count of active devices
    activeCount = 0
    for clc in g.IOTClientConfig:
        if g.IOTClientConfig[clc][0]: activeCount += 1
    # irdprint(defname, f"activeCount: {activeCount}")

    # set headstart in sec
    g.IOTHeadStart = max(300, 200 + activeCount * 100)            # ms; observed single call: 50 ... 150 ms
    dprint(defname, f"IOT headstart: {g.IOTHeadStart} ms")

    # wait until logging has started
    while g.nexttime == 0:
        if not g.IOTThreadRun: return
        time.sleep(0.1)

    # actions only when logging and time is due
    while g.IOTThreadRun:
        THREAD_nexttime = g.nexttime - g.IOTHeadStart / 1e3

        if not g.logging:
            # print(f"not logging  g.nexttime: {g.nexttime}") # g.nexttime does NOT change in this loop!
            time.sleep(0.1)

        else:
            nowtime = time.time()
            if (nowtime - g.nexttime) > g.LogCycle * 2 :
                # irdprint(defname, f"Delta time > 2 x cycle")
                continue

            if nowtime >= THREAD_nexttime:
                # iydprint(defname, f"nowtime: {nowtime}    nexttime: {THREAD_nexttime}  delta: {nowtime - THREAD_nexttime:0.6f}")
                if not g.iot_client.is_connected():
                    irdprint(defname, f"NO CONNECTION")
                else:
                    ### duration: 0.5 ... 1.5 ms (... 21 ms!)
                    g.IOTtotalDuration = 0.0
                    startIOTFetch = time.time()
                    # fetch the values
                    for clc in g.IOTClientConfig:
                        if g.IOTClientConfig[clc][0]:                                     # send 'command' only if activated
                            device = g.IOTClientConfig[clc][1]
                            topic  = g.IOTBrokerFolder + device + "/cmnd/Status"
                            if   "Tplug" in device or "Tsmr" in device: payld = "10"      # cmd: 'SEND', or '8', or '10', or 'None', or ...
                            elif "GLdev" in device:                     payld = "SEND"
                            else:                                       payld = "None"
                            if payld != "None":
                                qos    = 0
                                retain = False

                                ### PUBLISH #########################################################################
                                success, publishID = g.iot_client.publish(topic, payld, qos=qos, retain=retain)
                                g.iot_pub_start = time.time()       # 50 ... 150 ms for single call
                                ### end PUBLISH #####################################################################

                                succflag = "Yes" if success == 0 else "No"
                                msg = f"PUBLISH:  topic:{topic}  payld:'{payld}'  qos:{qos}  retain:{retain}  success:{succflag}  publishID:{publishID}"

                                if success == 0: mdprint(defname, msg)
                                else:            rdprint(defname, msg)
                            else:
                                mdprint(defname, f"PUBLISH:  topic: {topic}  payld: '{payld}'  - No payload --> No need for any publishing")
                    durIOTFetch = 1e3 * (time.time() - startIOTFetch)
                    g.IOTtotalDuration += durIOTFetch
                    # irdprint(defname, f"g.IOTtotalDuration: {g.IOTtotalDuration:0.1f} ms")

                    # set time for next-cycle calls
                    THREAD_nexttime = g.nextnexttime - g.IOTHeadStart / 1e3 - 0.01
                    time.sleep(max(0, THREAD_nexttime - time.time()))

        # time.sleep(0.0005)    # idle period in while loop
        time.sleep(0.1)    # idle period in while loop


def getValuesIOT(varlist):
    """Read all IOT data from the buffer g.iot_data"""

    defname = gd(sys._getframe().f_code.co_name)

    start = time.time()

    alldata = {}
    for vname in varlist:
        alldata[vname]    = applyValueFormula(vname, g.iot_data[vname], g.ValueScale[vname])
        g.iot_data[vname] = g.NAN   # reset value to NAN

    # vprintLoggedValues(defname, varlist, alldata, (time.time() - start) * 1000)
    vprintLoggedValues(defname[0:-6] + "(async)", varlist, alldata, g.IOTtotalDuration)

    return alldata


###############################################################################
# BEGIN MQTT Callbacks
###############################################################################
#
# in all Callbacks:
#
# NOTE: if publishing is more frequent than reading, only the last published data will be read
#
# client:       is a python object
# userdata:     as defined in Client call
#               its type is as defined initially: can be Nonetype, str, int, float, ...
# msg:          the message coming from the IOT device; an instance of MQTTMessage, a
#               class with members topic, payload, qos, retain.
#                   type of msg.topic:   <class 'str'>
#                   type of msg.payload: <class 'bytes'>
#                   type of msg.qos:     <class 'int'>
#                   type of msg.retain:  <class 'int'>
# flags:        a dict that contains response flags from the broker
# rc:           indicates the connecion / disconnection state
# mid:          message ID
# granted_qos:  a list of integers that give the QoS level the broker has granted for each of the different subscription requests
#


#onm
def on_message(client, userdata, msg):
    """The callback indicating that a PUBLISH message has been received by the server"""
    ### msg.payload:                is a binary string,         like: b'{"StatusSNS":{"Time":"2025-10-19T10:19:47","ENERGY": ...
    ###                             or could be just a number,  like: b'10'
    ### json.loads(msg.payload):    is a string in json format, like: {'StatusSNS': {'Time': '2025-10-25T11:07:40',
    ###                                                                'ENERGY': {'TotalStartTime': '2025-10-16T14:16:20',
    ###                                                                'Total': 1.021, 'Yesterday': 0.008, 'Today': 0.004,
    ###                                                                'Power': 0.3, 'ApparentPower': 1.825, 'ReactivePower': 1.8,
    ###                                                                'Factor': 0.16, 'Voltage': 228.1, 'Current': 0.008}}}

    # ignore everything coming when not logging
    if not g.logging: return

    defname = gd(sys._getframe().f_code.co_name)
    # mdprint(f">IOT {defname}qos:{msg.qos}  retain:{msg.retain}  topic: {msg.topic:35s}   userdata: {userdata}   payload: {msg.payload}")

    if len(msg.payload) == 0:
        irdprint(defname, f"EMPTY msg.payload: '{msg.payload}' ööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööööö")
        return
    else:
        try:
            pljson = json.loads(msg.payload)
            # irdprint(defname, f"json.loads(msg.payload): \n{pljson}")  # output like: 10
                                                                         # output like: {'StatusSNS': {'Time': '2025-10-28T11:27:19', 'ENERGY': ...
        except Exception as e:
            msg = f"loading json msg.payload: {msg.payload}"
            exceptPrint(e, defname + msg)
            QueuefPrint(msg, color="<red>", error=True)
            return

    if pljson == "":                                # passiert das jemals?
        msg = f"pljson is empty"
        irdprint(defname, msg)
        # return
        QueuefPrint(msg, color="<red>", error=True)


# data in GeigerLog format, like from: Simul_IOTClient.py
    if "GLdevice" in msg.topic and b"DATA" in msg.payload:                  # accepts only 'DATA' payload on 'GLdevice'!
        clcfg = g.IOTClientConfig["GLvars"]
        if clcfg[0]:                                                        # is activated?
            for vname in clcfg[3].split(","):
                try:                    g.iot_data[vname] = pljson["DATA"][vname]
                except Exception as e:  g.iot_data[vname] = g.NAN

# tasmota SMR Default Reader
    elif "geigerlog/stat/tasmotaSMR/STATUS10" in msg.topic :
        # geigerlog/stat/tasmotaSMR/STATUS10 {"StatusSNS":{"Time":"2024-10-16T08:59:44","eBZ":{"E_in":21376.092,"E_out":0.000,"Power":470.220,
        # "36_7_0":111.040,"56_7_0":325.110,"76_7_0":34.070,"32_7_0":0.000,"52_7_0":0.000,"72_7_0":0.000,"96_1_0":"}
        clcfg = g.IOTClientConfig["SMR"]
        if clcfg[0]: getSmartMeterData(pljson, clcfg[3].split(","), msg)                    # is activated?

# tasmota bitShake Reader
    elif "geigerlog/stat/tasmotaBSH/STATUS10" in msg.topic :
        clcfg = g.IOTClientConfig["BSH"]
        if clcfg[0]: getSmartMeterData(pljson, clcfg[3].split(","), msg)                    # is activated?

# tasmota Wattwaechter
    elif "geigerlog/stat/tasmotaWWR/STATUS10"  in msg.topic :
        clcfg = g.IOTClientConfig["WWR"]
        if clcfg[0]: getSmartMeterData(pljson, clcfg[3].split(","), msg)                    # is activated?

# tasmota DIAMEX Reader
    elif "geigerlog/stat/tasmotaDMX/STATUS10" in msg.topic :
        clcfg = g.IOTClientConfig["DMX"]
        if clcfg[0]: getSmartMeterData(pljson, clcfg[3].split(","), msg)                    # is activated?

# all tasmota plugs - TplugN
    elif "Tplug" in msg.topic and "/STATUS10" in msg.topic :
        # 13:05:02.774 MQT: geigerlog/Tplug7/STATUS10 = {"StatusSNS":{"Time":"2025-10-16T13:05:02",
        #   "ENERGY":{"TotalStartTime":"2025-10-10T10:44:01","Total":0.006,"Yesterday":0.000,"Today":0.003,
        #   "Power":20,"ApparentPower":40,"ReactivePower":34,"Factor":0.52,"Voltage":230,"Current":0.172}}}

        indx   = msg.topic.rfind("Tplug")
        client = msg.topic[indx : indx + 6]
        clcfg  = g.IOTClientConfig[client]

        if clcfg[0]:                                                              # is activated?
            # deltaTime = 1e3 * (time.time() - g.iot_pub_start)

            sensor = ["Voltage", "Current", "Power"]
            # irdprint(defname, f"clcfg: {clcfg}")
            for i, vname in enumerate(clcfg[3].split(",")[0 : len(sensor)]):      # '3' is the index to list of variables
                if vname == "None": continue

                try:
                    data = float(pljson["StatusSNS"]["ENERGY"][sensor[i]])
                except Exception as e:
                    exceptPrint(e, f"tasmota: topic: {msg.topic}  vname: {vname}")
                    data = g.NAN
                g.iot_data[vname] = data
                # mdprint(f">IOT {defname[0:-5]}device: {client:7s}  sensor: {sensor[i]:7s}  vname: {vname:6s}  data: {data}  msg.topic: {msg.topic}  duration: {deltaTime:0.1f} ms")
                mdprint(f">IOT {defname[0:-5]}device: {client:7s}  sensor: {sensor[i]:7s}  vname: {vname:6s}  data: {data}  msg.topic: {msg.topic}")

        # irdprint(f">IOT {defname[0:-5]} mid: {msg.mid}  info: {msg.info}  payload: {msg.payload}  state: {msg.state}")
    else:
        ### likely:  no topic hit: 'geigerlog/Tplug7/cmnd/Status'   'b'10''
        # iydprint(defname, f"no topic hit: '{msg.topic}'   '{msg.payload}'  ")
        return


    ### duration overall since publish
    maxdelta  = g.IOTHeadStart   # ms
    deltaTime = 1e3 * (time.time() - g.iot_pub_start)
    g.IOTtotalDuration += deltaTime
    if deltaTime > maxdelta:
        irdprint(f">IOT {defname[0:-5]}Delta Time Publish to message: {deltaTime:0.1f} ms")
        QueueSound("cocoo")
    # irdprint(defname, f"duration: {deltaTime:0.1f} ms     g.IOTtotalDuration: {g.IOTtotalDuration:0.1f} ms")


def on_connect(client, userdata, flags, reason_code, properties):
    """The callback for when the client receives a CONNACK response from the server"""

    defname = gd(sys._getframe().f_code.co_name)

    if reason_code == 0: g.IOTconnectionState = True
    else:                g.IOTconnectionState = False

    dprint(">IOT: on_connect: Client connected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with flags"        , flags))
    dprint(">        {:20s}: {}".format("with result"       , reason_code))

    # Subscribing within 'on_connect()' means that if we lose the connection and
    # reconnect, then subscriptions will be renewed.
    # g.iot_client.subscribe("$SYS/#") # gives huge amount of traffic when online! Careful!!!
    g.iot_client.subscribe(g.IOTBrokerFolder + "#", qos=0)

    dprint(">IOT: ", defname, "IOTconnectionState: ", g.IOTconnectionState)


def on_disconnect(client, userdata, flags, reason_code, properties):
    """When the client has sent the disconnect message it generates an on_disconnect() callback."""

    defname = gd(sys._getframe().f_code.co_name)

    g.IOTconnectionState = False # whatever the cause - it is disconnected

    dprint(">IOT: on_disconnect: Client disconnected:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with reason_code"  , reason_code))

    dprint(">IOT: ", defname, "IOTconnectionState: ", g.IOTconnectionState)


def on_subscribe(client, userdata, mid, reason_codes, properties):
    """Callback when a subscribe has occured"""

    defname = gd(sys._getframe().f_code.co_name)

    dprint(">IOT: on_subscribe: Topic subscribed:")
    dprint(">        {:20s}: {}".format("with userdata"     , userdata))
    dprint(">        {:20s}: {}".format("with message ID"   , mid))
    dprint(">        {:20s}: {}".format("with reason_codes" , reason_codes))

    dprint(">IOT: ", defname, "IOTconnectionState: ", g.IOTconnectionState)


# should this not be on_unsub...? Bug in doc?
# https://eclipse.dev/paho/files/paho.mqtt.python/html/migrations.html
def on_unsubscribe(client, userdata, mid, reason_codes, properties):
    # In NEW version, reason_codes is always a list. Empty for MQTTv3

    defname = gd(sys._getframe().f_code.co_name)

    for unsub_result in reason_codes:
        # Any reason code >= 128 is a failure.
        if reason_codes[0] >= 128:
            # error processing
            pass


def on_publish(client, userdata, mid, reason_codes, properties):
    """ Called when a message that was to be sent using the publish() call has completed transmission to the broker"""

    defname = gd(sys._getframe().f_code.co_name)

    msg = f">IOT {defname}reason_codes: {reason_codes}  userdata: {userdata}  publishID: {mid}   properties: {properties}"

    if reason_codes == "Success":   pass            #gdprint(msg)
    else:                           rdprint(msg)


def on_log(client, userdata, level, buf):

    defname = gd(sys._getframe().f_code.co_name)

    # dprint(defname, f"log:  userdata: {userdata}  level: {level}   buf: {buf}")


###############################################################################
# END MQTT Callbacks
###############################################################################



def getSmartMeterData(pljson, vars, msg):
    """extract the Smart Reader data from the Tasmota SMR responses"""

    defname = gd(sys._getframe().f_code.co_name)

    try:
        plshort = pljson["StatusSNS"]["eBZ"]
    except Exception as e:
        exceptPrint(e, defname + f"get plshort from {pljson}")
        return

    try:    g.IOTClientTasmotaSMRID = plshort["96_1_0"]
    except: pass

    for vname in vars:
        vname = vname.strip()
        try:
            # if   vname == "CPM1st":  g.iot_data[vname] = float(plshort["E_in"])       # Verbrauch in kWh
            # elif vname == "CPS1st":  g.iot_data[vname] = float(plshort["E_out"])      # Einspeisung in kWh

            if   vname == "CPM3rd":  g.iot_data[vname] = float(plshort["E_in"]) / 1e3   # Verbrauch in MWh
            elif vname == "CPS3rd":  g.iot_data[vname] = float(plshort["E_out"]) / 1e3  # Einspeisung in MWh

            # elif vname == "CPM2nd":  g.iot_data[vname] = float(plshort["32_7_0"])     # Spannung L1
            # elif vname == "CPS2nd":  g.iot_data[vname] = float(plshort["52_7_0"])     # Spannung L2
            # elif vname == "CPM3rd":  g.iot_data[vname] = float(plshort["72_7_0"])     # Spannung L3

            elif vname == "Temp":    g.iot_data[vname] = float(plshort["Power"])      # akt. Leistung
            elif vname == "Press":   g.iot_data[vname] = float(plshort["36_7_0"])     # Leistung L1
            elif vname == "Humid":   g.iot_data[vname] = float(plshort["56_7_0"])     # Leistung L2
            elif vname == "Xtra":    g.iot_data[vname] = float(plshort["76_7_0"])     # Leistung L3

            # ydprint(defname, vname, "  ", g.iot_data[vname])

        except Exception as e:
            exceptPrint(e, f"TasmotaSMR: topic: {msg.topic}  vname: {vname}")
            g.iot_data[vname] = g.NAN

