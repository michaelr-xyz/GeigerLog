#! /usr/bin/env python3
# -*- coding: UTF-8 -*-

# DataServer:
#     DataServer supports 3 kind of systems:
#         - GMC Geiger counters
#         - I2C Sensors
#         - Pulse counters
#
#     It requires Python 3.7 or later.
#
#     DataServer can be run on ANY computer (Windows, Linux, Mac, Raspi) as long as it
#     is configured to ONLY use the GMC counters. Those need to be connected by USB.
#
#     If you want to use the "I2C Sensor" or "Pulse Counter" feature, then it MUST be
#     run on a Raspberry Pi computer. Otherwise DataServer exits with a message.
#
#     DataServer is a Python based webserver serving data to GeigerLog as a device of type:
#         - 'GeigerLog WiFiServer Device' - when in the local (WiFi-)LAN
#         - 'GeigerLog IOT Device'        - using MQTT from a place anywhere in the world
#
#     DataServer can act as either one type or both at the same time.
#
#     The Raspi manages any devices connected to it; it starts them, collects their data,
#     prepares the data, and sends them by the desired means.
#
#     Supported Hardware Devices for the Raspi, which can all be run simultaeously, are:
#
#         GMC counter, any model          by USB connection
#
#         I2C Sensors                     by GPIO connection
#             Supported I2C Sensors:
#             - LM75B     temperature
#             - BME280    temperature, barometric pressure, humidity
#             - BH1750    visible light intensity in Lux
#             - VEML6075  UV-A and UV-B intensity
#             - LTR390    visible light and UV
#             - GDK101    Geiger count rate
#
#         Pulse counters                  by GPIO connection
#             e.g. CAJOE counter
#
#     To use the devices and sensors they need to be configured for usage in
#     the CUSTOMIZE section in file 'rconfig.py'.
#
# Start with:     path/to/dataserver
# Stop  with:     CTRL-C

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


# Test for Python being at least minimal version; exit otherwise
import sys
svi        = sys.version_info       # current Python version
minVersion = (3, 7)                 # at least this version is required


if svi < minVersion :
    msg = """
        The DataServer program requires Python in version {}.{} or later!
        Your Python version is only: {}.{}.{}.

        You can download a new version of Python from:
        https://www.python.org/downloads/
        """.format(*minVersion, *svi)

    print(msg)
    sys.exit(1)


import rmain
rmain.main()
