#! /usr/bin/env python
# -*- coding: UTF-8 -*-

### DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY DUMMY
### placeholder for real code

"""
I2C module LTR390 Light-Sensor for Visible Light and UV
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

# Document:     # LTR390    has 2 values, 1 VIS value + 1 UV value
# Example:

class SensorLTR390:
    """Code for the LTR390 sensors"""

    name        = "LTR390"
    addr        = 0x53              # I2C address of the module is 0x53. (No other addr)
    id          = 0xB2              # 0xB2 = 178
    handle      = g.I2CDongle       # default for use by 'I2C' device; RaspiI2C defines its own


    def __init__(self, addr, I2Chandle=None):
        """Init SensorLTR390 class"""

        defname   = gd(sys._getframe().f_code.co_name)

        self.addr = addr
        if I2Chandle is not None: self.handle = I2Chandle

        self.handle  = g.I2CDongle


        # get sensor id (should be 0xB2)
        id = self.getIdLTR390()
        if id == self.id:  msg = "Sensor {} at address {:#04x} has proper ID: {:#04x}"
        else:              msg = "Sensor {} at address {:#04x} has wrong ID: '{}'"
        gdprint(msg.format(self.name, self.addr, id))

        ### is there any value to read the registers?
        ### read the MAIN_CTRL register
        main = self.getMainRegLTR390()
        rdprint("read Main Ctrl: {:#04x}".format(main))

        ### read the STATUS register; thereby clearing it
        status = self.getStatusRegLTR390()
        rdprint("read Status1:   {:#04x}".format(status))

        self.resetLTR390() # presently has only deque reset

        self.getValLTR390()                                     # dump first value
        g.I2CstoreLTR390.append(self.getValLTR390())            # fill first value



    def getIdLTR390(self):
        """read ID of LTR390; should be 0xB2 (=178)"""
        # runtime on Raspi: < 1 ms (0.56 ms)

        start   = time.time()
        defname = "getIdLTR390: "

        try:
            rbytes   = 1
            # raw      = getI2CBytes(self.name, self.addr, self.reg_partid, rbytes)
            raw      = self.handle.ELVreadBytes(rbytes, msg="")
            irdprint(defname, f"raw: {raw}")
            idresp   = raw[0]
        except Exception as e:
            exceptPrint(e, defname)
            idresp   = g.NAN
            raw      = b"Fail"

        dur = 1000 * (time.time() - start)
        dprint(defname + " Resp:{}  raw:{:10s}  dur:{:0.2f} ms".format(idresp, str(raw), dur))

        return idresp


############################################################################################################################
### From down here only copy from BH1750!! see Raspi code for real code !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!



    def SensorInit(self):
        """check ID, check PID, Reset, enable measurement"""

        defname = "SensorInit: " + self.name + ": "
        # dprint(defname)
        setIndent(1)

        # check for presence of an I2C device at I2C address
        if not self.handle.DongleIsSensorPresent(self.addr):
            # no device found
            setIndent(0)
            return  (False, "Did not find any I2C device at address 0x{:02X}".format(self.addr))
        else:
            # device found
            gdprint(defname, "Found an I2C device at address 0x{:02X}".format(self.addr))

        # reset
        gdprint(defname, self.SensorReset())

        dmsg     = "Sensor {:8s} at address 0x{:02X}  ".format(self.name, self.addr)
        setIndent(0)

        return (True,  dmsg)


    def LTR390enableMeasurements(self):
        """setting Power to On"""
        # not needed, see datasheet: "'Power On' Command is possible to omit."

        return

        # tmsg      = "set PowerOn"
        # register  = 0x01
        # readbytes = 0
        # data      = []
        # answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)


    def SensorgetValues(self):
        """get data in One time L-resolution mode"""
        # duration: ISS: 1 ... 2.5 ms

        start    = time.time()
        defname  = "SensorgetValues: {:10s}: ".format(self.name)

        # cdprint(defname)
        # setIndent(1)

        # One time L-resolution mode
        # tmsg      = "get LowMode - scale:/1.2"      # must divide result by 1.2; see: 'Measurement Accuracy' (manual page 2/17)
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

        duration = 1000 * (time.time() - start)
        # gdprint(defname, "Vis:{:<0.3f}".format(*response) + ", dur:{:0.1f} ms".format(duration))

        # setIndent(0)

        return response


    def SensorGetInfo(self):

        info  = "{:25s}\n"                        .format("Ambient Light (Visible)")
        info += "- Address:         0x{:02X}\n"   .format(self.addr)
        info += "- Variables:       {}\n"         .format(", ".join("{}".format(x) for x in g.Sensors["LTR390"][5]))

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

        return defname + "Data register => 0; dur:{:0.1f} ms".format(duration)


