#! /usr/bin/env python
# -*- coding: UTF-8 -*-

"""
I2C module INA228 - for Voltage, Current, Power, Die-Temperature
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


class SensorINA228:
    """Code for the INA228 sensors from Texas Instruments"""

    addr            = 0x40              # addr options: 0x40 ... 0x4F (16 addresses)
    id              = 0x2281            # sensor id:    0x228 << 4 + 0x1  (Device identification bits + Device revision identification)
    name            = "INA228"          # Texas Instruments, https://www.ti.com/lit/ds/symlink/ina228.pdf
    handle          = g.I2CDongle       # default for use by 'I2C' device; RaspiI2C defines its own
    inaDetails      = False             # flag for extended printout; set manually

    ### specific for breakout board "KEXIAO High Precisions 5832 INA228":
    Imax            = 10.0                              # max Ampere allowed
    RShunt          = 0.015                             # 15 mOhm
    Cur_lsb         = Imax / 2**19                      # LSB from max current 10 A and shunt of 15 mOhm and 20 bit ADC
    SHUNT_CAL       = int(13107.2E6 * Cur_lsb * RShunt) # SHUNT_CAL = 13107.2 x 10E6 x CURRENT_LSB x RSHUNT = 3750
    VoltLSB         = 195.3125E-6                       # 195.3125 μV/LSB for the range 0...85 Volt
    ShuntVoltLSB    = 312.5E-9                          # Resolution: 312.5   nV/LSB when ADCRANGE = 0
                                                        #              78.125 nV/LSB when ADCRANGE = 1
                                                        #
                                                        # Check: @ ±163.84 mV full scale: 163.84 mV/ 312.5   nV => 524288;  *2 = 1048576 = 2^20
                                                        # Check: @ ± 40.96 mV full scale:  40.96 mV/  78.125 nV => 524288;  *2 = 1048576 = 2^20


    def __init__(self, addr, I2Chandle=None):
        """Init SensorINA228 class"""

        self.addr    = addr
        if I2Chandle is not None: self.handle = I2Chandle
        else:                     self.handle = g.I2CDongle


    def SensorInit(self):
        """check presence, check ID, Reset, check scaling, configure ADC, calibrate Shunt"""

        defname = gd(sys._getframe().f_code.co_name)
        # dprint(defname)
        setIndent(1)

    ### find an I2C device at addr
        if self.handle.DongleIsSensorPresent(self.addr):
            # device found
            gdprint(defname, f"Found an I2C device at address 0x{self.addr:02X} --> {g.I2CSensorDict[self.addr]}")
        else:
            # no device found
            msg = f"Did not find any I2C device at address 0x{self.addr:02X}"
            rdprint(defname, msg)
            setIndent(0)
            return  False, msg


    ### check ID
        checkID = self.getID()
        if self.id  == checkID :
            gdprint(defname, f"Sensor {self.name:8s} at address 0x{self.addr:02X} has expected ID: 0x{self.id:04X}")
        else:
            setIndent(0)
            return (False, f"Failure - Did find sensor, but ID: '{checkID}' is not as expected: 0x{self.id:02X}")


    ### System reset
        icdprint(defname, f"System Reset")
        rconfig = self.SensorReset()


    ### check scaling
        rconfig = self.setConfig()
        ScaleBit4 = (rconfig & 0x10) > 0
        ScaleTxt  = "±40.96mV  78.125 nV/LSB" if ScaleBit4 else "±163.84mV   312.5 nV/LSB"
        icdprint(defname, f"Current setting:  Shunt full-scale differential: {ScaleTxt}")

        if ScaleBit4:
            msg  = f"ATTENTION: Scaling is set to 'ADCRANGE = 1', while code expects 'ADCRANGE = 0'!"
            msg += f"<br>This will not work. Sensor {self.name} cannot be used!"
            edprint(defname, msg)
            return (False, msg)


    ### set ADC configuration
        ADCconfig = self.setADCconfig(ADCcfg16Bit=0xFB68 | 0x7)     # set averaging:  7h: --> 1024 times
        ADCavg7h  = ADCconfig & 0x7 > 0
        if ADCavg7h: icdprint(defname, f"Current setting: averages: 1024  (Bit 2-0: 0x7)")
        else:        irdprint(defname, f"Current setting: averages: unknown  (Bit 2-0: 0b{ADCconfig & 0x7:03b})")


    ### set Shunt Calibration
        shuntVolt = self.setShuntCalibration(self.SHUNT_CAL)
        icdprint(defname, f"Shunt Calibration: SHUNT_CAL: {self.SHUNT_CAL} (0x{self.SHUNT_CAL:04X})")

    ### print variables
        icdprint(defname, f"Variables: {', '.join('{}'.format(x) for x in g.Sensors["INA228"][5])}")

        setIndent(0)
        return (True,  "")


    def getID(self):
        """get sensor ID - expect 0x2281:   (0x228 << 4 + 0x1)  (Device identification bits + Device revision identification)"""
        ### ID answ: [34, 129] --> 34 * 256 + 129 = 8833  (=0x2281)

        defname  = gd(sys._getframe().f_code.co_name)

        try:
            tmsg      = "checkID"
            register  = 0x3F
            readbytes = 2
            data      = []
            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            checkid   = ValFromBytes(answ, readbytes)
            icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {checkid}")
        except Exception as e:
            exceptPrint(e, tmsg)
            checkid = 0xFFFF

        return checkid


    def setConfig(self, cfg16Bit=None):
        """read / set config"""

        defname  = gd(sys._getframe().f_code.co_name)

        try:
            tmsg      = "Set Config"
            register  = 0x00
            readbytes = 2

            if cfg16Bit is None:
                data = []
            else:
                ### MUST be a 16bit value in a list of 2-Hex bytes
                ### like: [0x0E, 0xA6] for 3750 (0x0EA6) instead of default 4096 (0x1000)
                data =  [cfg16Bit >> 8,  cfg16Bit & 0xFF]

            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            rconfig   = ValFromBytes(answ, readbytes)
            icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   data: {data}  ValBytes: {rconfig}")
        except Exception as e:
            exceptPrint(e, tmsg)
            rconfig = 0xFFFF

        return rconfig


    def setADCconfig(self, ADCcfg16Bit=None):
        """read / set ADC config"""

        ### 7.6.1.2 ADC Configuration (ADC_CONFIG) Register (Address = 1h) [reset = FB68h]  (16 bit)
        ### Selects ADC sample averaging count. The averaging setting applies to all active inputs.
        ### When >0h, the output registers are updated after the averaging has completed.
        ###     0h = 1
        ###     1h = 4
        ###     2h = 16
        ###     3h = 64
        ###     4h = 128
        ###     5h = 256
        ###     6h = 512
        ###     7h = 102

        defname  = gd(sys._getframe().f_code.co_name)

        try:
            tmsg      = "Read / Set ADC Config"
            register  = 0x01
            readbytes = 2

            if ADCcfg16Bit is None:
                data = []
            else:
                ### MUST be a 16bit value in a list of 2-Hex bytes
                ### like: [0x0E, 0xA6] for 3750 (0x0EA6) instead of default 4096 (0x1000)
                data =  [ADCcfg16Bit >> 8,  ADCcfg16Bit & 0xFF]

            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            ADCcfg    = ValFromBytes(answ, readbytes)
            icdprint(defname, f"answ: {answ} {getAnswHex(answ)}   ValBytes: {ADCcfg:6.0f}  Twos: {" ---  "}   ADCcfg: {ADCcfg:0.0f} {ADCcfg:016b}  ")
        except Exception as e:
            exceptPrint(e, tmsg)
            ADCcfg = 0xFFFF

        return ADCcfg


    def setShuntCalibration(self, cal16Bit=None):
        """set Shunt Calibration"""

        ### 7.6.1.3 Shunt Calibration (SHUNT_CAL) Register (Address = 2h) [reset = 1000h]
        ### SHUNT_CAL   = 13107.2 x 10E6 x CURRENT_LSB x Rshunt
        ### CURRENT_LSB = (Maximum Expected Current) / 2^19  => 10 / 524288 = 19.073486 µA/LSB
        ### Rshunt      = 0.015 Ohm
        ### MaxCur      = 10 A
        ### SHUNT_CAL   = 13107.2 x 10E6 x (10A / 2^19) * 0.015 = 3750 = 0x0EA6

        defname   = gd(sys._getframe().f_code.co_name)

        try:
            tmsg      = "Set SHUNT CAL"
            register  = 0x02
            readbytes = 2

            if cal16Bit is None:
                data = []
            else:
                ### MUST be a 16bit value in a list of 2-Hex bytes
                ### like: [0x0E, 0xA6] for 3750 (0x0EA6) instead of default 4096 (0x1000)
                data =  [cal16Bit >> 8,  cal16Bit & 0xFF]

            answ       = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            SHUNT_CAL0 = ValFromBytes(answ, readbytes)
            SHUNT_CAL2 = TwosComplement(SHUNT_CAL0, 16)
            SHUNT_CAL  = SHUNT_CAL2
            icdprint(defname, f"answ: {answ} {getAnswHex(answ)}   ValBytes: {SHUNT_CAL0:6.0f}  Twos: {SHUNT_CAL2:6.0f}   SHUNT_CAL: {SHUNT_CAL:0.0f}")
        except Exception as e:
            exceptPrint(e, tmsg)
            SHUNT_CAL = 0xFFFF

        return SHUNT_CAL


#sgv
    def SensorgetValues(self):
        """ get one measurement of Temp, Press, Humid"""
        ### duration: 8.5 ... 8.8 ms  same for each; Volt, Amp, Pow
        ### overall:  34 ... 40 ms for combined Volt, Amp, Pow, and Temp

        startSgV = time.time()

        defname  = gd(sys._getframe().f_code.co_name)
        defname += f"{self.name:10s}: "

        startV = time.time()
        try:
            ### 7.6.1.6 Bus Voltage Measurement (VBUS) Register (Address = 5h) [reset = 0h
            ### assumes 20 bit
            tmsg      = "getVoltage"
            register  = 0x05
            readbytes = 3
            data      = []
            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            inaVolt0  = ValFromBytes(answ, readbytes)
            inaVolt1  = inaVolt0 >> 4
            inaVolt2  = TwosComplement(inaVolt1, 20)
            inaVolt   = inaVolt2 * self.VoltLSB #195.3125E-6           # 195.3125 μV/LSB
            if self.inaDetails:  icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {inaVolt0:6.0f}  Twos: {inaVolt2:6.0f}   inaVolt: {inaVolt:0.6f}")
        except Exception as e:
            exceptPrint(e, tmsg)
            inaVolt   = g.NAN
        durV = 1e3*(time.time() - startV)

        startC = time.time()
        try:
            ### assumes 20 bit
            tmsg      = "getCurrent"
            register  = 0x07
            readbytes = 3
            data      = []
            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            inaCurr0  = ValFromBytes(answ, readbytes)
            inaCurr1  = inaCurr0 >> 4
            inaCurr2  = TwosComplement(inaCurr1, 20)
            inaCurr   = inaCurr2 * self.Cur_lsb
            if self.inaDetails:  icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {inaCurr0:6.0f}  Twos: {inaCurr2:6.0f}   inaCurr: {inaCurr:0.6f}")
        except Exception as e:
            exceptPrint(e, tmsg)
            inaCurr   = g.NAN
        durC = 1e3*(time.time() - startC)


        ### looks like Pow is exactly V * C
        ### LONG CALL TIMES: durV: 8.7  durC: 8.5  durP: 8.5  durT: 8.3
        ### Values: V:9.159 , C:0.040 , P:0.369 , Pcalc:0.369 , T:22.242   dur:34.2 ms
        ###                             ^^^^^^^^^^^^^^^^^^^^^ is same!
        startP = time.time()
        # try:
        #     ### always positive; assumes 24 bit
        #     ### Power [W] = 3.2 x CURRENT_LSB x POWER
        #     ### CURRENT_LSB = (Maximum Expected Current) / 2^19  => 10 / 524288 = 19.073486 µA/LSB
        #     tmsg      = "getPower"
        #     register  = 0x08
        #     readbytes = 3
        #     data      = []
        #     answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
        #     inaPow0   = ValFromBytes(answ, readbytes)
        #     inaPowr   = 3.2 * self.Cur_lsb * inaPow0    ### Power [W] = 3.2 x CURRENT_LSB x POWER
        #     if self.inaDetails:  icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {inaPow0:6.0f}  Twos: {' ---  '}   inaPowr:  {inaPowr:0.6f}")
        # except Exception as e:
        #     exceptPrint(e, tmsg)
        #     inaPowr   = g.NAN
        inaPowr = inaVolt * inaCurr
        durP    = 1e3*(time.time() - startP)


        ### Read inaTemp
        inaTemp, durT = self.getDieTemp()

        # ### read Shunt Voltage
        # self.getShuntVoltage()

        duration = 1E3 * (time.time() - startSgV)
        if self.inaDetails:  gdprint(defname, f"V:{inaVolt:<6.3f}, C:{inaCurr:<6.3f}, P:{inaPowr:<6.3f}, T:{inaTemp:<6.3f}   dur:{duration:<0.1f} ms")

        ### post message when either call takes too long
        tlimit = 20 # ms
        if durV > tlimit or durC > tlimit or durP > tlimit or durT > tlimit :
            irdprint(defname, f"LONG CALL TIMES [ms]:  durV: {durV:0.1f}  durC: {durC:0.1f}  durP: {durP:0.1f}  durT: {durT:0.1f}")
            QueueSound("doublebip")

        return (inaVolt, inaCurr, inaPowr, inaTemp)


    def getDieTemp(self):
        """get the internal die temperature in °C"""
        ### duration: 8.3 ... 8.5 ms

        ### 7.6.1.7 Temperature Measurement (DIETEMP) Register (Address = 6h) [reset = 0h]
        ### Internal die temperature measurement. Two's complement value. Conversion factor: 7.8125 m°C/LSB

        defname  = gd(sys._getframe().f_code.co_name)
        defname += f"{self.name:10s}: "

        startT = time.time()
        try:
            tmsg      = "Read DIETEMP"
            register  = 0x06
            readbytes = 2
            data      = []
            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            inaTemp0  = ValFromBytes(answ, readbytes)
            inaTemp1  = TwosComplement(inaTemp0, bits=16)
            inaTemp   = inaTemp1 * 7.8125e-3
            if self.inaDetails: icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {inaTemp0:6.0f}  Twos: {inaTemp1:6.0f}   inaTemp: {inaTemp:0.1f}")
        except Exception as e:
            exceptPrint(e, tmsg)
            inaTemp = g.NAN
        durT = 1e3*(time.time() - startT)

        return inaTemp, durT


    def getShuntVoltage(self):
        """read the voltage across the shunt (here: 15 mOhms; Volt range: ±163.84 mV)"""

        ### Table 7-9. VSHUNT Register Field Descriptions
        ### Bit 23-4 Field: VSHUNT  Differential voltage measured across the shunt output. Two's complement value.
        ###     Conversion factor:
        ###        312.5 nV/LSB when ADCRANGE = 0
        ###         78.125 nV/LSB when ADCRANGE = 1
        ### Bit 3-0 Reserved. Always reads 0

        defname  = gd(sys._getframe().f_code.co_name)
        defname += f"{self.name:10s}: "

        try:
            tmsg      = "Read VSHUNT"
            register  = 0x04
            readbytes = 3
            data      = []
            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            VSHUNT0   = ValFromBytes(answ, readbytes)
            VSHUNT1   = VSHUNT0 >> 4
            VSHUNT2   = TwosComplement(VSHUNT1, 20)
            VSHUNT    = VSHUNT2 * self.ShuntVoltLSB      # 312.5E-9 Volt / LSB
            icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {VSHUNT0:6.0f}  Twos: {VSHUNT2:6.0f}   VSHUNT: {VSHUNT:0.6f} Volt  @R=15mOhm --> I= {VSHUNT / 15.0E-3:0.6f} A")
        except Exception as e:
            exceptPrint(e, tmsg)
            VSHUNT = g.NAN

        return VSHUNT


    ### is NOT being used
    def getConvStatus(self):
        """get Conversion Status of INA228 by reading register 'DiagAlert' and isolating field 'CNVRF' """
        ### return CNVRFstat: presently ALWAYS True, i.e. conversion is always complete
        ### is that the consequence of auto-conversion?

        ### 7.6.1.12 Diagnostic Flags and Alert (DIAG_ALRT) Register (Address = Bh) [reset = 0001h]
        ###
        ### CNVR seems to configure action on the alert pin:
        ### Field: CNVR  - Setting this bit (= Bit 14) high configures the Alert pin to be asserted when the Conversion
        ###     Ready Flag (bit 1) is asserted, indicating that a conversion cycle has completed.
        ###     0h = Disable conversion ready flag on ALERT pin
        ###     1h = Enables conversion ready flag on ALERT pin
        ###
        ### Field: CNVRF - This bit (= Bit 1) is set to 1 if the conversion is completed.
        ###     0h = Normal
        ###     1h = Conversion is complete
        ###     When ALATCH =1 this bit is cleared by reading this register or starting a new triggered conversion.

        defname = gd(sys._getframe().f_code.co_name)

        try:
            tmsg      = "get DiagAlert"
            register  = 0x0B
            readbytes = 2
            data      = []
            answ      = self.handle.DongleWriteRead (self.addr, register, readbytes, data, addrScheme=1, msg=tmsg)
            DiagAlert = ValFromBytes(answ, readbytes)
            CNVRFstat = (DiagAlert & 0x01) > 0
            icdprint(defname, f"answ: {str(answ):15s} {str(getAnswHex(answ)):9s}   ValBytes: {DiagAlert}   CNVRFstat: {CNVRFstat}")
        except Exception as e:
            exceptPrint(e, tmsg)
            CNVRFstat = 0xFFFF

        return CNVRFstat


    def SensorReset(self):
        """System Reset of the INA228 sensor"""
        # duration: 8.8 ms

        ### 7.6.1.1 Configuration (CONFIG) Register (Address = 0h) [reset = 0h]
        ### Bit 15, Field: RST - Reset Bit. Setting this bit to '1' generates a system reset that is the
        ### same as power-on reset. Resets all registers to default values.
        ###     0h = Normal Operation
        ###     1h = System Reset sets registers to default values
        ###     This bit self-clears.

        defname = gd(sys._getframe().f_code.co_name)

        data    = 0x8000                    # Bit 15 is set
        rconfig = self.setConfig(data)

        return rconfig


    def SensorGetInfo(self):

        info  = "{}\n"                             .format("Voltage, Current, Power")
        info += "- Address:         0x{:02X}\n"    .format(self.addr)
        info += "- ID:              0x{:02X}\n"    .format(self.id)
        info += "- Variables:       {}\n"          .format(", ".join("{}".format(x) for x in g.Sensors["INA228"][5]))

        return info.split("\n")

