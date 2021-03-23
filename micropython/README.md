This is a pair of micropython modules for the SparkFun Qwiic Alphanumeric Display Module.
By Matthew Noury, March 7, 2021

* SparkFunAlphaDisplay.py - Single Display functionality
* SparkFunMultiDisplay.py - Multiple display chaining functionality (requires SparkFunAlphaDisplay)

It is loosely based on the C++ library written by
Priyanka Makin @ SparkFun Electronics, Feb 25, 2020,
https://github.com/sparkfun/SparkFun_Alphanumeric_Display_Arduino_Library,
as updated May 2, 2020 by Gaston Williams to add the defineChar function.

This module was developed on the SparkFun Thing Plus XBee.
Pickup a board here: https://www.sparkfun.com/products/15454

On resource constrained devices you may need to load the SparkFunAlphaDisplay module first.
To reduce memory consumption further, you can use mpy-cross to pre-compile the module:
```
    mpy-cross -mno-unicode -msmall-int-bits=31 SparkFunAlphaDisplay.py
    mpy-cross -mno-unicode -msmall-int-bits=31 SparkFunMultiDisplay.py
```
This will generate .mpy versions of the module which will be considerably smaller in size.
The above -m options should work for the SparkFun Thing Plus (XBee 3).  You may meed to
adjust these for compatibility with other architectures.

Development environment specifics:

* IDE: `Digi XTCU`
* Hardware Platform: `XBee3 Zigbee with EFR32MG, Function Set Digi Xbee3 Zigbee 3.0, Firmware 100B`
* MicroPython `v1.12-1548-gfc68e2a on 2020-09-01`
* Alphanumeric Display Breakout Version: `1.0.0`


This code is beerware; if you see me (or any other contributor) at the
local, and you've found our code helpful, please buy us a round!

Distributed as-is; no warranty is given.

----------------------------------------------------------------------------------------------------

# SparkFunAlphaDisplay.py

Basic Instructions:
```python
import SparkFunAlphaDisplay
from machine import I2C
i2c = I2C(1)
i2c.scan()
display = SparkFunAlphaDisplay.AlphaDisplay(i2c, address)
display.begin()
display.printString('Demo')
```

----------------------------------------------------------------------------------------------------
**`AlphaDisplay` Class - Definition**
**Constructor** | **Description**
--------------------------- | -----------------------------------------------------------------------
`AlphaDisplay(i2cInstance, address = DEFAULT_ADDRESS)` | i2cInstance = An instance of the machine module's I2C class (machine.I2C)<br>address = The I2C address of the display to control.<br>(Default address is 0x70 in hexidecimal, or 112 in decimal).

----------------------------------------------------------------------------------------------------
**`AlphaDisplay` Class - Basic Functions**
**Function** | **Description**
--------------------------- | -----------------------------------------------------------------------
`begin()` | Verifies the display is connected and initializes/clears it (includes calling the `initialize()` function).  Returns True on success. Calling this function is the simplest way to get ready for other print functions.
`setBrightness(duty)` | Sets the display brightness. Valid values are 0-15. Returns True on success.
`setBlinkRate(rate)` | Sets the display blink rate. Valid values for `rate` are 0 (no blink), .5, 1, or 2 Hz. Returns True on success.
`clear(doUpdate = True)` | Zero's the display RAM, and if doUpdate is True also clears/updates the display. Returns True on success.
`printString(stringToWrite)` | Writes `stringToWrite` to the display (with wrap-around at the end of the display). Updates the display. Turns on ':' and '.' if included in the string, will skip digits to ensure proper positioning (mostly). Returns True on success.
`printNum(numberToWrite)` | Write a number to the display (must be a number fitting the pattern '####', `###.#`, `##.#`, or `#.#`). Returns True on success.
`printTime(majorVal, minorVal)` | Write a time to the display (must fit pattern `MM:mm`, `MM` = `majorVal`, `mm` = `minorVal`). Returns True on success.
`shiftRight(shiftAmount = 1, insertText = ' ')` | Shifts the contents of the display `shiftAmount` digits to the right. Inserts `insertText`on the left. Defaults to shifting one digit and inserts a space on the left. Returns the character(s) shifted out.
`shiftLeft(shiftAmount = 1, insertText = ' ')` | Shifts the contents of the display `shiftAmount` digits to the left. Inserts `insertText`on the right. Defaults to shifting one digit and inserts a space on the right. Returns the character(s) shifted out.

----------------------------------------------------------------------------------------------------
**`AlphaDisplay` Class - Additional Functions**
**Function** | **Description**
--------------------------- | -----------------------------------------------------------------------
`getAddress()` | Returns the configured display's I2C address
`isConnected()` | Returns True if the configured display is available on the I2C bus
`initialize()` | Enables the display system clock, turns on the display, clears the display, sets brightness to maximum, and sets to no blink. Returns True on success.
`displayOn()` | Turns on the display. Returns True on success.
`displayOff()` | Turns off the display. Returns True on success.
`decimalOn()` | Turns on the decimal point. Returns True on success.
`decimalOff()` | Turns off the decimal point. Returns True on success.
`colonOn()` | Turns on the colon. Returns True on success.
`colonOff()` | Turns off the colon. Returns True on success.
`updateDisplay()` | Updates the display. Writes the stored displayRAM copy to the device. Returns True on success.
`clearDigit(digit)` | Turns off a single digit (0 - 3) on the display. This only done in the display RAM, call updateDisplay() for it to show on the display. It always succeeds and does not return a value.
`defineChar(displayChar, segmentsToTurnOn)` | Redefines the segment pattern (`segmentsToTurnOn` as 0bNMLKJIHGFEDCBA) for the indicated character (`displayChar`). `displayChar` can be any ASCII character ('!' through '~'). Always succeeds and returns True.
`setDigit(displayChar, digit, overwrite = True)` | Sets `digit` to character `displayChar` on the display. Clears any previous segment pattern on the digit if `overwrite` is True. Call updateDisplay() to see the change. Does not return a value.
`writeBuffer(buffer, overwrite = True)` | Writes the characters in `buffer` to the display (with wraparound). Updates the display. Turns on the decimal and colon appropriately for the buffer, skipping digits as necessary to ensure proper spacing. Clears any underlaying characters if `overwrite` is True. Returns True on success.

----------------------------------------------------------------------------------------------------
**`AlphaDisplay` Class - Advanced Functions**
**Function** | **Description**
--------------------------- | -----------------------------------------------------------------------
`writeRAM(ramAddress, buff)` | Write to display RAM.  `ramAddress` = 0-15, `buff` = data to write (multiple bytes ok). Returns True on success.
`writeRAW(dataToWrite)` | Send raw binary data in `dataToWrite` to the display No pre-processing of the data. On you to make sure it's a valid command. Returns True if the data is successfully sent (ACKs received).
`readRAM`(ramAddress = 0, numberOfBytes = 16) | Returns the requested display RAM values. Defaults to the entire display 16-byte display RAM.
`setDisplayOnOff(turnOnDisplay)` | Turns on the display when called with True, or off when called with False. Returns True on success.
`setDecimalOnOff(turnOnDecimal)` | Turns the decimal point on when called with True, or off when called with False. Returns True on success.
`setColonOnOff(turnOnColon)` | Turns the colon on when called with True, or off when called with False. Returns True on success.
`enableSystemClock()` | Wakes up the display from sleep by enabling the system clock. Returns True on success. After power-on, you must call this function before the display will light up - note that `begin()` and `initialize()` will do this for you.
`disableSystemClock()` | Puts the display to sleep by disabling the system clock. Returns True on success. The display is unable to illuminate while asleep. Possibly useful to reduce power consumption.
`illuminateSegment(segment, digit)` | Illuminates `segment` ('A' - 'N') on `digit` (0 - 3). This only done in the display RAM, call updateDisplay() for it to show on the display. It always succeeds and does not return a value.
`illuminateChar(segmentsToTurnOn, digit, overwrite = True)` | Given a binary set of segments (0bNMLKJIHGFEDCBA) and a digit (0 - 3), stores this data into the display RAM. If `overwrite` is True, the digit is cleared before setting the segments on (False will overwrite the new character on top of the old character without turning any of the old segments off.)
`getSegmentsToTurnOn(charPos)` | Returns the binary set of segments for the requested character index (0 - SFE_ALPHANUM_UNKNOWN_CHAR). Returns the default segment pattern for the character unless it has been explicitly redfined with `defineChar()`.
`writeByte(byte, overwrite = True)` | Writes character `byte` to the display at the current display position, and increments the position (wraps around at the end of the display). Updates the display. If `overwrite` is True, any previous segments on the digit are cleared before setting the new character. Returns True on success.
`_resetPos()` | Sets the current digit position to digit 0, and turns off the colon and decimal. Updates the display. Does not return a value.

----------------------------------------------------------------------------------------------------
**`AlphaDisplay` Class - Variables**
**Variable** | **Description**
--------------------------- | -----------------------------------------------------------------------
`_i2c` | Internal reference to the display's I2C instance.
`_displayAddress` | The display's I2C address.
`digitPosition` | Current digit position on the display (0 - 3). This is the digit the next character will be printed to.
`didWraparound` | Is True immediately following the printing of a digit that causes a display wrap-around (at the end of the display).
`displayOnOff` | Tracks the value of the display's On/Off bit.
`decimalOnOff` | Tracks the value of the display's Decimal on/off bit.
`colonOnOff` | Tracks the value of the display's colon on/off bit.
`blinkRate` | Tracks the value of the display's blink rate. One of `ALPHA_BLINK_RATE_NOBLINK`, `ALPHA_BLINK_RATE_2HZ`, `ALPHA_BLINK_RATE_1HZ`, `ALPHA_BLINK_RATE_0_5HZ`
`_charDefList` | List of character definitions, is a list of `{'position':x, 'segments':y}` dictionaries
`_displayRAM` | Local copy of the display RAM, a bytearray that is 16 bytes in size.
`_displayContent` | Local copy of what is on the display. Read-only.

----------------------------------------------------------------------------------------------------
**`SparkFunAlphaDisplay` Module - Constants (These are not class members.)**
**Constant** | **Description**
--------------------------- | -----------------------------------------------------------------------
`SFE_ALPHANUM_UNKNOWN_CHAR` | Character index for undefined character / DEL / RUBOUT
`_alphanumeric_segs` | Tuple of character segment definitions
`DEFAULT_ADDRESS` | Default I2C address to use when not specified
`ALPHA_BLINK_RATE_NOBLINK` | Internal blink rate value for No Blink. Used for class variable `blinkRate`.
`ALPHA_BLINK_RATE_2HZ` | Internal blink rate value for 2 Hz. Used for class variable `blinkRate`.
`ALPHA_BLINK_RATE_1HZ` | Internal blink rate value for 1 Hz. Used for class variable `blinkRate`.
`ALPHA_BLINK_RATE_0_5HZ` | Internal blink rate value for 0.5 Hz. Used for class variable `blinkRate`.
`ALPHA_DISPLAY_ON` | Internal value for display On. Used for class variable `displayOnOff`.
`ALPHA_DISPLAY_OFF` | Internal value for display Off. Used for class variable `displayOnOff`.
`ALPHA_DECIMAL_ON` | Internal value for display Decimal on. Used for class variable `decimalOnOff`.
`ALPHA_DECIMAL_OFF` | Internal value for display Decimal off. Used for class variable `decimalOnOff`.
`ALPHA_COLON_ON` | Internal value for display Colon on. Used for class variable `colonOnOff`.
`ALPHA_COLON_OFF` | Internal value for display Colon off. Used for class variable `colonOnOff`.

----------------------------------------------------------------------------------------------------

# SparkFunMultiDisplay.py

Basic Instructions:
```python
import SparkFunAlphaDisplay
import SparkFunMultiDisplay
from machine import I2C
i2c = I2C(1)
i2c.scan()
display = SparkFunMultiDisplay.MultiDisplay(i2c, [address1, address2, ..., addressN])
display.begin()
display.printString('Demo')
```

----------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------
**`MultiDisplay` Class - Definition**
**Constructor** | **Description**
--------------------------- | -----------------------------------------------------------------------
`MultiDisplay(i2cInstance, addresses = DEFAULT_ADDRESSES)` | i2cInstance = An instance of the machine module's I2C class (machine.I2C)<br>addresses = A comma separated [] list of I2C address of displays to control.<br>(Default address list is one display, [112]).

----------------------------------------------------------------------------------------------------
**`MultiDisplay` Class - Basic Functions**
**Function** | **Description**
--------------------------- | -----------------------------------------------------------------------
`begin()` | Verifies the display is connected and initializes/clears it (includes calling the `initialize()` function).  Returns True on success. Calling this function is the simplest way to get ready for other print functions.
`setBrightness(duty)` | Sets the display brightness on all displays. Valid values are 0-15. Returns True on success.
`setBlinkRate(rate)` | Sets the display blink rate on all displays. Valid values for `rate` are 0 (no blink), .5, 1, or 2 Hz. Returns True on success.
`clear(doUpdate = True)` | Zero's the cursor position, zeros the display RAM for all displays, and if doUpdate is True also clears/updates all displays. Returns True on success.
`printString(stringToWrite)` | Clears all displays and writes `stringToWrite` to sequence of displays (with wrap-around at the end of the displays). Updates the displays. Turns on ':' and '.' on the appropriate display if included in the string, will skip digits to ensure proper positioning (mostly). Returns True on success.
`shiftRight(shiftAmount = 1)` | Shifts the contents of all displays `shiftAmount` digits to the right. Inserts spaces on the left. Defaults to shifting one digit. Returns the character(s) shifted out.
`shiftLeft(shiftAmount = 1)` | Shifts the contents of all displays `shiftAmount` digits to the left. Inserts spaces on the right. Defaults to shifting one digit. Returns the character(s) shifted out.
`rotateRight(shiftAmount = 1)` | Rotates the contents of all displays 1 digit to the right.  Does not return a value.
`rotateLeft(shiftAmount = 1)` | Rotates the contents of all displays 1 digit to the left.  Does not return a value.
`scrollPrint(stringToPrint)` | Produces an animation that scrolls the given text on the available displays, until the entire string has been shown. Does not return until after the animation completes (this may take a long time, depending on the string length).
`setScrollDelay(delay)` | Sets the scrolling speed of scrollPrint. This is the delay time per frame in milliseconds.

----------------------------------------------------------------------------------------------------
**`MultiDisplay` Class - Additional Functions**
**Function** | **Description**
--------------------------- | -----------------------------------------------------------------------
`initialize()` | Enables all display system clocks, turns on all displays, clears all displays, sets brightness to maximum, and sets to no blink. Returns True on success.
`getAddresses()` | Returns the list of configured display addresses.
`isConnected()` | Returns True if all configured displays are present on the I2C bus.
`updateDisplay()` | Updates all displays to match the stored displayRAM copies to the devices. Returns True on success.
`displayOn()` | Turns on all displays. Returns True on success.
`displayOff()` | Turns off all displays. Returns True on success.
`decimalOn()` | Turns on the decimal point on all displays. Returns True on success.
`decimalOff()` | Turns off the decimal point on all displays. Returns True on success.
`colonOn()` | Turns on the colon on all displays. Returns True on success.
`colonOff()` | Turns off the colon on all displays. Returns True on success.
`defineChar(displayChar, segmentsToTurnOn)` | Redefines the segment pattern (`segmentsToTurnOn` as 0bNMLKJIHGFEDCBA) for the indicated character (`displayChar`). `displayChar` can be any ASCII character ('!' through '~'). Always succeeds and returns True.
`writeBuffer(buffer, overwrite = True)` | Writes the characters in `buffer` to the display (with wraparound). Updates the display. Turns on the decimal and colon appropriately for the buffer, skipping digits as necessary to ensure proper spacing. Clears any underlaying characters if `overwrite` is True. Returns True on success.
`calcLength(text, startDigit = 0)` | Returns the number of digit positions required to completely display `text`.  If `startDigit` (0 - 3) is specified, this starting position is taken into account for the calculation.  The insertion of spaces to correctly position ':' and '.' affects this calculation, and strings that contain these characters may generate different lengths depending on the start digit.
`trimToFit(text, startDigit = 0)` | Returns `text` truncated to fit on all displays (without wraparound). If `startDigit` (0 - 3) is specified, this starting position is taken into account for the calculation.  The insertion of spaces to correctly position ':' and '.' affects this calculation, and strings that contain these characters may produce different results depending on the start digit.

----------------------------------------------------------------------------------------------------
**`MultiDisplay` Class - Advanced Functions**
**Function** | **Description**
--------------------------- | -----------------------------------------------------------------------
`setDisplayOnOff(turnOnDisplay)` | Turns on all displays when called with True, or off when called with False. Returns True on success.
`setDecimalOnOff(turnOnDecimal)` | Turns the decimal point on all displays on when called with True, or off when called with False. Returns True on success.
`setColonOnOff(turnOnColon)` | Turns the colon onon all displays  when called with True, or off when called with False. Returns True on success.
`enableSystemClock()` | Wakes up all displays from sleep by enabling the system clock. Returns True on success. After power-on, you must call this function before the display will light up - note that `begin()` and `initialize()` will do this for you.
`disableSystemClock()` | Puts all displays to sleep by disabling the system clock. Returns True on success. The display is unable to illuminate while asleep. Possibly useful to reduce power consumption.
`writeByte(byte, overwrite = True)` | Writes character `byte` to the display/digit at the current cursor position, and increments the position (wraps from one display toi the next and back to display 0 at the end of the last display). Updates the display. If `overwrite` is True, any previous segments on the digit are cleared before setting the new character. Returns True on success.

----------------------------------------------------------------------------------------------------
**`MultiDisplay` Class - Variables**
**Variable** | **Description**
--------------------------- | -----------------------------------------------------------------------
`_i2c` | Internal reference to the I2C instance the displays are connected to.
`_displayAddresses` | The list of display I2C address this class will control.
`displayIndex` | Index of the display that the current cursor position resides on.  Valid values are between 0 and (# of displays - 1). This is the display the next character will be printed to when sequential printing functions are used.  Wraps to display 0, digit 0 after printing the last character on the last display.
`digitPosition` | Current digit position (0 - 3) on the current (`displayIndex`) display. This is the digit the next character will be printed to.  After printing a character at digit position 3, `displayIndex` is automatically incremented and `digitPosition` resets to 0.
`scrollDelay` | Current delay value (in milliseconds) used for animation functions.  Defaults to the value of module constant `SparkFunMultiDisplay.DEFAULT_SCROLLDELAY`.
`_displays` | Internal list of display instances used to manipulate the displays.  Each list element is an instance of SparkFunAlphaDisplay and corresponds to one display from the list of addresses in `_displayAddresses`.  You can directly manipulate the individual displays, for example calling `myMultiDisplayInstance._displays[2].clear()` will clear only the 3rd display, and `display.disableSystemClock() for display in myMultiDisplayInstance._displays` will put all displays to sleep byy iterating through the list (this is the same as calling `myMultiDisplayInstance.enableSystemClock()` directly on the multi display class).

----------------------------------------------------------------------------------------------------
**`SparkFunMultiDisplay` Module - Constants (These are not class members.)**
**Constant** | **Description**
--------------------------- | -----------------------------------------------------------------------
`DEFAULT_ADDRESSES` | Default list of display I2C addresses to use when not specified.  Defaults to `[112]` (a single display).
`DEFAULT_SCROLLDELAY` | Default scroll delay to use for animation functions, in milliseconds.  Defaults to 1000ms (1 second).


