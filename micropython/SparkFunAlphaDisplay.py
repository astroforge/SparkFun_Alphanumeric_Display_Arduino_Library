# ******************************************************************************
# SparkFunAlphaDisplay.py
# SparkFun Alphanumeric Display Driver Python Module
#
# Please see full credits in SparkFunMultiDisplay.py.  Kept short here to
# keep the module smaller for constrained devices.
#
# Last updated 3/7/2021 by Matthew Noury
#
# Built and tested on Digi XBee 3
# 
#  Basic Instructions:
#  import SparkFunAlphaDisplay
#  from machine import I2C
#  i2c = I2C(1)
#  i2c.scan()
#  display = SparkFunAlphaDisplay.AlphaDisplay(i2c, address)
#  display.begin()
#  display.printString('Demo')

# If we have sleep_ms() available, use it, otherwise we can use sleep()
try:
    from time import sleep_ms
except ImportError:
    from time import sleep
    def sleep_ms(time): sleep(time/1000)

DEFAULT_ADDRESS = (0x70)      # Default I2C address, 0x70 = 112

# Alpha Blink Rate Values
ALPHA_BLINK_RATE_NOBLINK = (0b00)
ALPHA_BLINK_RATE_2HZ = (0b01)
ALPHA_BLINK_RATE_1HZ = (0b10)
ALPHA_BLINK_RATE_0_5HZ = (0b11)

# Alpha Display State Values
ALPHA_DISPLAY_ON = (0b1)
ALPHA_DISPLAY_OFF = (0b0)

# Alpha Decimal State Values
ALPHA_DECIMAL_ON = (0b1)
ALPHA_DECIMAL_OFF = (0b0)

# Alpha Colon State Values
ALPHA_COLON_ON = (0b1)
ALPHA_COLON_OFF = (0b0)

# Alpha Commands
ALPHA_CMD_SYSTEM_SETUP = (0b00100000)
ALPHA_CMD_DISPLAY_SETUP = (0b10000000)
ALPHA_CMD_DIMMING_SETUP = (0b11100000)

# --------------------------- Character Map ----------------------------------
SFE_ALPHANUM_UNKNOWN_CHAR = (95)

# This is the lookup table of segments for various characters
_alphanumeric_segs = (
    # nmlkjihgfedcba
    # 1111----------
    # 32109876543210
    0b00000000000000, # ' ' (space)
    0b00001000001000, # '!'  - added to map
    0b00001000000010, # '"' - added to map
    0b1001101001110,  # '#'
    0b1001101101101,  # '$'
    0b10010000100100, # '%'
    0b110011011001,   # '&'
    0b1000000000,     # '''
    0b111001,         # '('
    0b1111,           # ')'
    0b11111010000000, # '*'
    0b1001101000000,  # '+'
    0b10000000000000, # ','
    0b101000000,      # '-'
    0b00000000000000, # '.' - uses blank
    0b10010000000000, # '/'
    0b111111,         # '0'
    0b10000000110,    # '1'
    0b101011011,      # '2'
    0b101001111,      # '3'
    0b101100110,      # '4'
    0b101101101,      # '5'
    0b101111101,      # '6'
    0b1010000000001,  # '7'
    0b101111111,      # '8'
    0b101100111,      # '9'
    0b00000000000000, # ':' - uses blank
    0b10001000000000, # ';'
    0b110000000000,   # '<'
    0b101001000,      # '='
    0b01000010000000, # '>'
    0b01000100000011, # '?'
    0b00001100111011, # '@'
    0b101110111,      # 'A'
    0b1001100001111,  # 'B'
    0b111001,         # 'C'
    0b1001000001111,  # 'D'
    0b101111001,      # 'E'
    0b101110001,      # 'F'
    0b100111101,      # 'G'
    0b101110110,      # 'H'
    0b1001000001001,  # 'I'
    0b11110,          # 'J'
    0b110001110000,   # 'K'
    0b111000,         # 'L'
    0b10010110110,    # 'M'
    0b100010110110,   # 'N'
    0b111111,         # 'O'
    0b101110011,      # 'P'
    0b100000111111,   # 'Q'
    0b100101110011,   # 'R'
    0b110001101,      # 'S'
    0b1001000000001,  # 'T'
    0b111110,         # 'U'
    0b10010000110000, # 'V'
    0b10100000110110, # 'W'
    0b10110010000000, # 'X'
    0b1010010000000,  # 'Y'
    0b10010000001001, # 'Z'
    0b111001,         # '['
    0b100010000000,   # '\'
    0b1111,           # ']'
    0b10100000000000, # '^'
    0b1000,           # '_'
    0b10000000,       # '`'
    0b101011111,      # 'a'
    0b100001111000,   # 'b'
    0b101011000,      # 'c'
    0b10000100001110, # 'd'
    0b1111001,        # 'e'
    0b1110001,        # 'f'
    0b110001111,      # 'g'
    0b101110100,      # 'h'
    0b1000000000000,  # 'i'
    0b1110,           # 'j'
    0b1111000000000,  # 'k'
    0b1001000000000,  # 'l'
    0b1000101010100,  # 'm'
    0b100001010000,   # 'n'
    0b101011100,      # 'o'
    0b10001110001,    # 'p'
    0b100101100011,   # 'q'
    0b1010000,        # 'r'
    0b110001101,      # 's'
    0b1111000,        # 't'
    0b11100,          # 'u'
    0b10000000010000, # 'v'
    0b10100000010100, # 'w'
    0b10110010000000, # 'x'
    0b1100001110,     # 'y'
    0b10010000001001, # 'z'
    0b10000011001001, # '{'
    0b1001000000000,  # '|'
    0b110100001001,   # '}'
    0b00000101010010, # '~'
    0b11111111111111  # Unknown character (DEL or RUBOUT)
)


class AlphaDisplay:
    """
    This class controls one LCD display module over I2C.
    """
    # Constructor; I2C Port and LED Stick address should be included
    def __init__(self, i2cInstance, address = DEFAULT_ADDRESS):
        assert (0x08 < address < 0x77), "Invalid I2C Address, Out of Range: 0x08 < address < 0x77"
        self._i2c = i2cInstance
        self._displayAddress = address
        self._displayRAM = bytearray(b'\x00' * 16) # RAM = 16 bytes
        self._displayContent = ' ' * 4
        self.digitPosition = 0
        self.didWraparound = False
        self.displayOnOff = 0    # Tracks display on/off bit of display setup register
        self.decimalOnOff = 0    # Tracks decimal on/off bit of display setup register
        self.colonOnOff = 0      # Tracks colon on/off bit of display setup register
        self.blinkRate = ALPHA_BLINK_RATE_NOBLINK   # Tracks blink rate bits in display setup register
        self._charDefList = []   # List of character definitions, should be a list of {'position':x, 'segments':y} dictionaries

    # ------------------ Display Configuration Functions ------------------------

    def getAddress(self):
        return self._displayAddress

    # Check that displays is responding
    # The Holtek IC sometimes fails to respond. This attempts multiple times before giving up.
    def isConnected(self):
        triesBeforeGiveup = 20
        for _x in range(triesBeforeGiveup):
            connectedDevices = self._i2c.scan()
            if connectedDevices.count(self._displayAddress) > 0:
                return True
            sleep_ms(1)
        return False
        
    # Write the contents of the buffer out to the Holtek IC
    def writeRAM(self, ramAddress, buff):
        data = bytearray([ramAddress]) + bytearray(buff)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received

    # Write raw data to the Holtek IC.
    def writeRaw(self, dataToWrite):
        data = bytearray(dataToWrite)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received

    # Read the display RAM.  Will return the full 16 bytes if ramAddress and
    # numberOfBytes are omitted.  Valid ramAddresses are 0 - 16.
    def readRAM(self, ramAddress = 0, numberOfBytes = 16):
        assert ramAddress + numberOfBytes <= 16, "readRAM: Error, ramAddress + numberOfBytes > 16"
        self._i2c.writeto(self._displayAddress, bytearray([ramAddress]))
        return self._i2c.readfrom(self._displayAddress, numberOfBytes)


    def updateDisplay(self):
        return self.writeRAM(0x00, self._displayRAM)
            
    def clear(self, doUpdate = True):
        self._displayRAM = bytearray(b'\x00' * 16)  # RAM = 16 bytes
        self.digitPosition = 0
        self.didWraparound = False
        if doUpdate: return self.updateDisplay()
        return True

    # Duty valid between 1 and 15
    def setBrightness(self, duty):
        assert duty <= 0b1111, "Invalid Brightness Value, Out of Range: Required duty <= 15, received " + str(duty)
        command = [ALPHA_CMD_DIMMING_SETUP | duty]
        data = bytearray(command)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received

    # Set blink rate in Hz, Valid values are 0 (no blink), .5, 1, or 2 Hz
    def setBlinkRate(self, rate):
        self.blinkRate = {0:ALPHA_BLINK_RATE_NOBLINK,0.5:ALPHA_BLINK_RATE_0_5HZ, 1:ALPHA_BLINK_RATE_1HZ, 2:ALPHA_BLINK_RATE_2HZ}[rate]
        command = [ALPHA_CMD_DISPLAY_SETUP | (self.blinkRate << 1) | self.displayOnOff]  # Enable system clock
        data = bytearray(command)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received

    # Set or clear the display on/off bit of a given display number (True = on)
    def setDisplayOnOff(self, turnOnDisplay):
        self.displayOnOff = {True:ALPHA_DISPLAY_ON, False:ALPHA_DISPLAY_OFF}[turnOnDisplay]
        command = [ALPHA_CMD_DISPLAY_SETUP | (self.blinkRate << 1) | self.displayOnOff]  # Enable system clock
        data = bytearray(command)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received  

    def displayOn(self):    return self.setDisplayOnOff(True)      
    def displayOff(self):   return self.setDisplayOnOff(False)

    def setDecimalOnOff(self, turnOnDecimal):
        self.decimalOnOff = {True:ALPHA_DECIMAL_ON, False:ALPHA_DECIMAL_OFF}[turnOnDecimal]
        RAMaddress = 0x03
        self._displayRAM[RAMaddress] |= self.decimalOnOff
        return self.updateDisplay()

    def decimalOn(self):    return self.setDecimalOnOff(True)
    def decimalOff(self):   return self.setDecimalOnOff(False)

    def setColonOnOff(self, turnOnColon):
        self.colonOnOff = {True:ALPHA_COLON_ON, False:ALPHA_COLON_OFF}[turnOnColon]
        RAMaddress = 0x01
        self._displayRAM[RAMaddress] |= self.colonOnOff
        return self.updateDisplay()

    def colonOn(self):  return self.setColonOnOff(True)
    def colonOff(self): return self.setColonOnOff(False)

    # --------------------------- Device Status----------------------------------
    
    def enableSystemClock(self):
        command = [ALPHA_CMD_SYSTEM_SETUP | 1]  # Enable system clock
        data = bytearray(command)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received

    def disableSystemClock(self):
        command = [ALPHA_CMD_SYSTEM_SETUP | 0]  # Disable system clock / standby mode
        data = bytearray(command)
        acksreceived = self._i2c.writeto(self._displayAddress, data) # Send the command
        return (acksreceived == len(data))  # Return true if all acks received
        
    def initialize(self):
        result = (self.enableSystemClock()
            and self.setBrightness(15)
            and self.setBlinkRate(0)
            and self.clear())
        if result:
            sleep_ms(10)
            return self.displayOn()
        return False

    def begin(self):
        return (self.isConnected() and self.initialize())


    # --------------------------- Light-Up Functions ----------------------------

    # Given a segment ('A'-'N' ) and a digit (0-3), set the matching bit within the RAM of the Holtek RAM set
    def illuminateSegment(self, segment, digit):
        segIndex = ord(segment) - ord('A')   # Convert the segment letter back to a number
        ramAddress = segIndex * 2   # RAM layout skips a byte between segments
        nibble = 0b00000001         # Segs A-G are in nibble 0, seg I-N in nibble 1
        if segIndex > 6:            # Corrects the address for segs I-N, sets nibble
            ramAddress = (segIndex - 7) * 2
            nibble = 0b00010000
        if segIndex == 7: ramAddress = 2     # Segments H(7) and I(8) need to be switched
        if segIndex == 8: ramAddress = 0
        data = nibble << digit
        self._displayRAM[ramAddress] |= data

    # Clears a single digit (0-3) on the display
    def clearDigit(self, digit):
        digitmask = ~(0b00010001 << digit)  # Shift and invert
        for ramAddress in range(0, 14, 2):
            self._displayRAM[ramAddress] &= digitmask
        self._displayContent = self._displayContent[:digit] + ' ' + self._displayContent[digit+1:]

    # Given a binary set of segments and a digit, store this data into the RAM array
    # If overwrite is True (default), the digit is cleared before lighting up the character
    def illuminateChar(self, segmentsToTurnOn, digit, overwrite = True):
        if overwrite: self.clearDigit(digit)
        for i in range(14):
            if ((segmentsToTurnOn >> i) & 0b1):
                self.illuminateSegment(chr(ord('A') + i), digit)
    
    # Get the character map from the definition list or default table
    # Character definition list is a list of {'position':x, 'segments':y} dictionaries
    def getSegmentsToTurnOn(self, charPos):
        try:
            charDef = next((x for x in self._charDefList if x['position'] == charPos))
        except StopIteration:
            charDef = None
        return charDef['segments'] if charDef else _alphanumeric_segs[charPos]

    # Define a new segment pattern for a particular character
    # displayChar is the character to redefine ('A')
    # segmentsToTurn on is a 14-bit value, one bit per segment (0bNMLKJIHGFEDCBA)
    # Character definition list is a list of {'position':x, 'segments':y} dictionaries
    def defineChar(self, displayChar, segmentsToTurnOn):
        # Check to see if character is within range of displayable ASCII characters
        assert ('!' <= displayChar <= '~'), "In defineChar: displayChar out of range: ('!' <= displayChar <= '~'), received " + str(displayChar)
        # Get the index of character in table and update its 14-bit segment value
        charPos = ord(displayChar) - ord('!') + 1
        # Create a new character definition, masking segment value to 14 bits only
        self._charDefList.append({'position':charPos,'segments':segmentsToTurnOn & 0x3FFF})
        return True

    # Show a character on display, expects an ASCII value int or a 1-character string
    def setDigit(self, displayChar, digit, overwrite = True):
        # if we were passed an int, convert it to a character
        if type(displayChar) == int: displayChar = chr(displayChar)

        characterIndex = None
        # space
        if (displayChar == ' '):
            characterIndex = 0
        # printable symbols
        elif (displayChar >= '!' and displayChar <= '~'):
            characterIndex = ord(displayChar) - ord('!') + 1

        # take care of special characters
        if (characterIndex == 14): self.decimalOn()  # '.'
        elif (characterIndex == 26): self.colonOn()    # ':'
        elif (characterIndex == None): characterIndex = SFE_ALPHANUM_UNKNOWN_CHAR   # unknown character
        
        segmentsToTurnOn = self.getSegmentsToTurnOn(characterIndex)
        self.illuminateChar(segmentsToTurnOn, digit, overwrite)

    # Write a byte to the display
    def writeByte(self, b, overwrite = True):
        # If user wants to print '.' or ':', advance digitPosition to after the mark
        if (b == '.'):
            self.decimalOn()
            self.digitPosition = 3
        elif (b == ':'):
            self.colonOn()
            self.digitPosition = 2
        else:
            self.setDigit(b, self.digitPosition, overwrite)
            self._displayContent = self._displayContent[:self.digitPosition] + b + self._displayContent[self.digitPosition+1:]
            self.digitPosition += 1
            self.didWraparound = (self.digitPosition > 3)
            self.digitPosition %= 4
        return self.updateDisplay()
    
    # Write a character buffer to the display
    def writeBuffer(self, buffer, overwrite = True):
        for currentChar in buffer:
            if (currentChar == '.') and (self.digitPosition < 4) and not self.didWraparound:
                self.decimalOn()
                while (self.digitPosition < 3):     # pad display with spaces to position '.' correctly
                    if overwrite : self.clearDigit(self.digitPosition)
                    self.digitPosition += 1
            elif (currentChar == ':') and (self.digitPosition < 3) and not self.didWraparound:
                self.colonOn()
                while (self.digitPosition < 2):     # pad display with spaces to position ':' correctly
                    if overwrite : self.clearDigit(self.digitPosition)
                    self.digitPosition += 1
            else: 
                if (currentChar != '.') and (currentChar !=':'):
                    self.setDigit(currentChar, self.digitPosition, overwrite)
                    self._displayContent = self._displayContent[:self.digitPosition] + currentChar + self._displayContent[self.digitPosition+1:]
                    self.digitPosition += 1
                    self.didWraparound = (self.digitPosition > 3)

            self.digitPosition %= 4

        return self.updateDisplay()

    def _resetPos(self):
        self.digitPosition = 0
        self.didWraparound = False
        self.colonOff()
        self.decimalOff()
        self.updateDisplay()

    # Write a string to the display
    def printString(self, stringToWrite):
        assert (stringToWrite != None), "In printString: Value required, stringToWrite is None"
        stringToWrite = '{:4}'.format(stringToWrite)    # pad with spaces on the right to ensure digit clearing
        return self.writeBuffer(stringToWrite)

    # Write a number to the display (must fit pattern ###.#)
    def printNum(self, numberToWrite):
        stringToWrite = '{:>5.1f}'.format(numberToWrite).rstrip('0'.rstrip('.'))
        splitString = stringToWrite.split('.', 1)
        if len(splitString[0]) > 3 : stringToWrite = splitString[0]
        self._resetPos()
        return self.writeBuffer(stringToWrite)

    # Write a time to the display (must fit pattern MM:mm, MM = majorVal, mm = minorVal)
    def printTime(self, majorVal, minorVal):
        stringToWrite = '{:>2}:{:0>2}'.format(majorVal, minorVal)    # format as time
        self._resetPos()
        return self.writeBuffer(stringToWrite)

    # Shift the display content to the right shiftAmount digits
    # returns the characters shifted out
    # If len(insertText) < shiftAmount, it is repeated for shiftAmount characters
    def shiftRight(self, shiftAmount = 1, insertText = ' '):
        if len(insertText) < shiftAmount: insertText = (insertText * shiftAmount)[:shiftAmount]
        shiftedOut = self._displayContent[-shiftAmount:]
        self.printString(insertText + self._displayContent[:-shiftAmount])
        return shiftedOut

    # Shift the display content to the left shiftAmount digits
    # returns the characters shifted out
    def shiftLeft(self, shiftAmount = 1, insertText = ' '):
        if len(insertText) < shiftAmount: insertText = (insertText * shiftAmount)[:shiftAmount]
        shiftedOut = self._displayContent[:shiftAmount]
        self.printString(self._displayContent[shiftAmount:] + insertText)
        return shiftedOut



    
