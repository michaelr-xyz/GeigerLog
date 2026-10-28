#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
I2C module BH1750 Ambient-Light-Sensor for Visible Light
    The breakout board carrying the BH1750 sensor is mostly called GY-30!
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

# Document:     https://datasheetspdf.com/datasheet/BH1750FVI.html
#               Ambient Light Sensor IC Series, Digital 16bit Serial Output Type, Ambient Light Sensor IC, BH1750FVI
# Example:      https://wolles-elektronikkiste.de/en/bh1750fvi-gy-30-302-ambient-light-sensor

class SensorBH1750:
    """Code for the BH1750 sensors"""

    name        = "BH1750"
    addr        = 0x23              # "The standard I2C address of the module is 0x23. You can change
                                    #  it to 0x5C by connecting the address pin (ADDR or ADD) to HIGH."
    # id                            # sensor does not have id
    handle      = g.I2CDongle       # default for use by 'I2C' device; RaspiI2C defines its own


    def __init__(self, addr, I2Chandle=None):
        """Init SensorBH1750 class"""

        defname = gd(sys._getframe().f_code.co_name)

        self.addr = addr
        if I2Chandle is not None: self.handle = I2Chandle
        else:                     self.handle = g.I2CDongle


    def SensorInit(self):
        """check ID, check PID, Reset, enable measurement"""

        defname = gd(sys._getframe().f_code.co_name)
        # dprint(defname)
        setIndent(1)

        # check for presence of an I2C device at I2C address
        if not self.handle.DongleIsSensorPresent(self.addr):
            # no device found
            setIndent(0)
            return  (False,  f"Did not find any I2C device at address 0x{self.addr:02X}")
        else:
            # device found
            gdprint(defname, f"Found an I2C device at address 0x{self.addr:02X} --> {g.I2CSensorDict[self.addr]}")

        # reset
        cdprint(defname, self.SensorReset())

        # dmsg = "Sensor {:8s} at address 0x{:02X}  ".format(self.name, self.addr)
        dmsg = ""
        setIndent(0)

        return (True,  dmsg)


    def BH1750enableMeasurements(self):
        """setting Power to On"""
        # not needed, see datasheet: "'Power On' Command is possible to omit."

        tmsg      = "set PowerOn"
        register  = 0x01
        readbytes = 0
        data      = []
        answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)


    def SensorgetValues(self):
        """get data in One time L-resolution mode"""
        # duration: ISS: 1 ... 2.5 ms

        # start    = time.time()
        defname  = f"SensorgetValues: {self.name:10s}: "

        # One time L-resolution mode
        tmsg      = "getData LowMode (/1.2)"      # must divide result by 1.2; see: 'Measurement Accuracy' (manual page 2/17)
        register  = 0x23
        readbytes = 2
        data      = []
        answ      = self.handle.DongleWriteRead  (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)

        if len(answ) == readbytes:
            vis = (answ[0] << 8 | answ[1]) / 1.2   # scale /1.2!
            response = (vis, )

        else:
            # Error: answ too short or too long
            edprint(defname + "incorrect data, answ: ", answ)
            response = (g.NAN, )

        # duration = 1000 * (time.time() - start)
        # gdprint(defname, "Vis:{:<0.3f}".format(*response) + ", dur:{:0.1f} ms".format(duration))

        return response


    def SensorGetInfo(self):

        info  = "{:25s}\n"                        .format("Ambient Light (Visible)")
        info += "- Address:         0x{:02X}\n"   .format(self.addr)
        info += "- Variables:       {}\n"         .format(", ".join("{}".format(x) for x in g.Sensors["BH1750"][5]))

        return info.split("\n")


    def SensorReset(self):
        """Reset the data register"""

        # Reset command is for only reset Illuminance data register. ( reset value is '0' )
        # It is not necessary even power supply sequence.It is used for removing previous
        # measurement result. This command is not working in power down mode, so
        # that please set the power on mode before input this command.
        #
        # duration: ELV:    ??? ms
        #           ISS:    1.0 ms
        #           Raspi5: 0.8 ms

        start     = time.time()
        defname   = "SensorReset: "

        tmsg      = "Reset"
        register  = 0x07     # reset
        readbytes = 0
        data      = []
        answ      = self.handle.DongleWriteRead(self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)

        duration  = 1000 * (time.time() - start)

        return defname + f"Data register => 0; dur:{duration:0.1f} ms"


