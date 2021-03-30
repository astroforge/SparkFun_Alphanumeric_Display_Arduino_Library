# ******************************************************************************
# SparkFunMultiDisplay.py
# Multiple SparkFun Alphanumeric Display Driver Python Module
# 
# This is a micropython module for the SparkFun Qwiic Alphanumeric Display Module.
# By Matthew Noury, March 7, 2021
#
# It is loosely based on a C++ library written by
# Priyanka Makin @ SparkFun Electronics, Feb 25, 2020
# https://github.com/sparkfun/SparkFun_Alphanumeric_Display_Arduino_Library
# As updated May 2, 2020 by Gaston Williams to add defineChar function
# 
# Pickup a board here: https://sparkle.sparkfun.com/sparkle/storefront_products/16391
#
# On resource constrained devices you may need to load the SparkFunAlphaDisplay module first.
# To reduce memory consumption more, you can use mpy-cross to pre-compile the module.
#
# This file implements all functions of the HT16K33 class. Functions here range
# from printing to one or more Alphanumeric Displays, changing the display settings, and writing/
# reading the RAM of the HT16K33.
#
# The Holtek HT16K33 seems to be susceptible to address changes intra-sketch. The ADR pins
# are muxed with the ROW and COM drivers so as semgents are turned on/off that affect
# the ADR1/ADR0 pins the address has been seen to change. The best way around this is
# to do a isConnected check before updateRAM() is sent to the driver IC.
#
# Development environment specifics:
#     IDE: Digi XTCU
#     Hardware Platform: XBee3 Zigbee with EFR32MG, Function Set Digi Xbee3 Zigbee 3.0, Firmware 100B
#     MicroPython v1.12-1548-gfc68e2a on 2020-09-01
#     Alphanumeric Display Breakout Version: 1.0.0
#
# This code is beerware; if you see me (or any other SparkFun employee) at the
# local, and you've found our code helpful, please buy us a round!
#
# Distributed as-is; no warranty is given.
# ******************************************************************************
#
#  Basic Instructions:
#  import SparkFunAlphaDisplay
#  import SparkFunMultiDisplay
#  from machine import I2C
#  i2c = I2C(1)
#  i2c.scan()
#  # Below addresses must be a comma separated list of addresses, can be 1 address, but brackets required
#  display = SparkFunMultiDisplay.MultiDisplay(i2c, [address1 ... , addressN])
#  display.begin()
#  display.printString('This is a test')
#  display.scrollPrint('This text will be scrolled across all displays.')
#

try:
    import SparkFunAlphaDisplay
except:
    print('Unable to import SparkFunAlphaDisplay. Try importing it before importing this module.')

# If we have sleep_ms() available, use it, otherwise we can use sleep()
try:
    from time import sleep_ms
except ImportError:
    from time import sleep
    def sleep_ms(time): sleep(time/1000)

DEFAULT_ADDRESSES = [0x70]      # Default I2C address list, 0x70 = 112
DEFAULT_SCROLLDELAY = (1000)       # Number of ms delay between scroll frames


class MultiDisplay:
    """
    This class controls multiple LCD display modules over I2C.
    The SparkFunAlphaDisplay module is required.
    Import it first if you get a memory error loading this module.
    """
    # Constructor; I2C Port and list of LED Stick address should be included
    def __init__(self, i2cInstance, addresses = DEFAULT_ADDRESSES):
        assert all((0x08 < x < 0x77) for x in addresses), "Invalid I2C Address, Out of Range: 0x08 < address < 0x77"
        self._i2c = i2cInstance
        self._displayAddresses = addresses
        self.displayIndex = 0
        self.digitPosition = 0
        self.scrollDelay = DEFAULT_SCROLLDELAY      # Tracks delay between scrollPrint() frames

        self._displays = [SparkFunAlphaDisplay.AlphaDisplay(self._i2c, addr) for addr in addresses]

    # ------------------ Display Configuration Functions ------------------------

    def getAddresses(self):
        return self._displayAddresses

    # Check that all displays are responding
    def isConnected(self):
        return all([display.isConnected() for display in self._displays])

    def updateDisplay(self):
        return all([display.updateDisplay() for display in self._displays])
            
    def clear(self, doUpdate = True):
        self.displayIndex = 0
        self.digitPosition = 0
        return all([display.clear(doUpdate) for display in self._displays])

    # Duty valid between 1 and 15
    def setBrightness(self, duty):
        return all([display.setBrightness(duty) for display in self._displays])

    # Set blink rate in Hz, Valid values are 0 (no blink), .5, 1, or 2 Hz
    def setBlinkRate(self, rate):
        return all([display.setBlinkRate(rate) for display in self._displays])

    # Set or clear the display on/off bit of a given display number (True = on)
    def setDisplayOnOff(self, turnOnDisplay):
        return all([display.setDisplayOnOff(turnOnDisplay) for display in self._displays])

    def displayOn(self):    return self.setDisplayOnOff(True)      
    def displayOff(self):   return self.setDisplayOnOff(False)

    def setDecimalOnOff(self, turnOnDecimal):
        return all([display.setDecimalOnOff(turnOnDecimal) for display in self._displays])

    def decimalOn(self):    return self.setDecimalOnOff(True)
    def decimalOff(self):   return self.setDecimalOnOff(False)

    def setColonOnOff(self, turnOnColon):
        return all([display.setColonOnOff(turnOnColon) for display in self._displays])

    def colonOn(self):  return self.setColonOnOff(True)
    def colonOff(self): return self.setColonOnOff(False)

    # --------------------------- Device Status----------------------------------
    
    def enableSystemClock(self):
        return all([display.enableSystemClock() for display in self._displays])

    def disableSystemClock(self):
        return all([display.disableSystemClock() for display in self._displays])
        
    def initialize(self):
        return all([display.initialize() for display in self._displays])

    def begin(self):
        return all([display.begin() for display in self._displays])


    # Define a new segment pattern for a particular character
    # displayChar is the character to redefine ('A')
    # segmentsToTurn on is a 14-bit value, one bit per segment (0bNMLKJIHGFEDCBA)
    def defineChar(self, displayChar, segmentsToTurnOn):
        return all([display.defineChar(displayChar, segmentsToTurnOn) for display in self._displays])

    # Write a byte to the display
    def writeByte(self, b, overwrite = True):
        result = self._displays[self.displayIndex].writeByte(b, overwrite)
        self.digitPosition = self._displays[self.displayIndex].digitPosition
        if self.digitPosition == 0: self.displayIndex = (self.displayIndex + 1) % len(self._displays)
        return result and self.updateDisplay()
    
    # Write a character buffer to the display
    def writeBuffer(self, buffer, overwrite = True):
        bufferPosition = 0
        result = True
        while bufferPosition < len(buffer):
            if (((self.digitPosition >= 2) and (buffer[bufferPosition] == ':'))
                or ((self.digitPosition >= 3) and (buffer[bufferPosition] == '.'))):
                self.digitPosition = 0
                self.displayIndex += 1
                if (self.displayIndex >= len(self._displays)):
                    self.displayIndex = 0
                    break
            result = result and self._displays[self.displayIndex].writeByte(buffer[bufferPosition], overwrite)
            bufferPosition += 1
            self.digitPosition = self._displays[self.displayIndex].digitPosition
            if self.digitPosition == 0: self.displayIndex += 1
            if (self.displayIndex >= len(self._displays)):
                self.displayIndex = 0
                break

        return result and self.updateDisplay()

    # Write a string to the display
    def printString(self, stringToWrite):
        return self.clear() and self.writeBuffer(stringToWrite)

    # Shift the display content to the right shiftAmount digits
    def shiftRight(self, shiftAmount = 1):
        carryOver = ' ' * shiftAmount
        for display in self._displays:
            carryOver = display.shiftRight(shiftAmount, carryOver)
        return carryOver

    # Shift the display content to the left shiftAmount digits
    def shiftLeft(self, shiftAmount = 1):
        carryOver = ' ' * shiftAmount
        reversedDisplays = self._displays.copy()
        reversedDisplays.reverse()
        for display in reversedDisplays:
            carryOver = display.shiftLeft(shiftAmount, carryOver)
        return carryOver

    def rotateRight(self):
        carryOver = self._displays[-1]._displayContent[-1:]
        for display in self._displays:
            carryOver = display.shiftRight(1, carryOver)

    def rotateLeft(self):
        carryOver = self._displays[0]._displayContent[0]
        reversedDisplays = self._displays.copy()
        reversedDisplays.reverse()
        for display in reversedDisplays:
            carryOver = display.shiftLeft(1, carryOver)

    # Returns the calculated display length for a string, starting at a given digit position
    def calcLength(self, text, startDigit = 0):
        length = 0
        position = startDigit
        for char in text:
            if char == ':': length += (2 - position) % 4
            elif char == '.': length += (3 - position) % 4
            else: length += 1
            position = (startDigit + length) % 4
        return length
 
    # Trims the given string to fit on the displays without wraparound
    def trimToFit(self, text, startDigit = 0):
        length = 0
        position = startDigit
        trimmedString = ""
        textIndex = 0
        while (length < len(self._displays) * 4) and (textIndex < len(text)):
            char = text[textIndex]
            if char == ':': length += (2 - position) % 4
            elif char == '.': length += (3 - position) % 4
            else: length += 1
            position = (startDigit + length) % 4
            trimmedString += char
            textIndex += 1
        return trimmedString

    # Prints a string to all the displays, performing a shift animation to display
    # any text that doesn't fit.  Returns after the animation has completed (it may
    # take several seconds to complete).
    def scrollPrint(self, stringToPrint):
        maxlength = max(self.calcLength(stringToPrint), len(stringToPrint))
        extralen = maxlength - (len(self._displays) * 4)
        for startIndex in range(extralen + 1):
            sleep_ms(self.scrollDelay)
            self.printString(self.trimToFit(stringToPrint[startIndex:]))
        sleep_ms(self.scrollDelay)

    # Sets the scroll delay for scrollPrint() in ms
    def setScrollDelay(self, delay):
        self.scrollDelay = delay


    
