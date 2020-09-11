# *****************************************************************************
# * | File        :	  epd2in13bc.py
# * | Author      :   Waveshare team
# * | Function    :   Electronic paper driver
# * | Info        :
# *----------------
# * | This version:   V4.0
# * | Date        :   2019-06-20
# # | Info        :   python demo
# -----------------------------------------------------------------------------
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documnetation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to  whom the Software is
# furished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"""
Modified from:
https://github.com/waveshare/e-Paper/blob/
717cbb8d9215e58f9f3cdde45ee329f516504afe/RaspberryPi%26JetsonNano/python/
lib/waveshare_epd/epd2in13bc.py

Display driver class for Waveshare e-Paper Display HAT 2.13 inch (B)

https://www.waveshare.com/wiki/2.13inch_e-Paper_HAT_(B)
https://www.amazon.com/gp/product/B075FR81WL/

The latest version of this package is available at:
<http://github.com/jantman/pizero-gpslog>

##################################################################################
Copyright 2018-2020 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of pizero-gpslog, also known as pizero-gpslog.

    pizero-gpslog is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pizero-gpslog is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with pizero-gpslog.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
##################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/pizero-gpslog> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
##################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
##################################################################################
"""

import time
import logging
import spidev
import RPi.GPIO
from typing import Optional, ClassVar, Tuple
from pizero_gpslog.displays.base import BaseDisplay
from pizero_gpslog.utils import FixType
from datetime import datetime
from PIL import Image, ImageDraw


logger = logging.getLogger(__name__)


class EPD2in13bc(BaseDisplay):

    #: width of the display in characters
    width_chars: ClassVar[int] = 21

    #: height of the display in lines
    height_lines: ClassVar[int] = 5

    #: the minimum number of seconds between refreshes of the display
    min_refresh_seconds: ClassVar[int] = 15

    def __init__(
        self, bus: int = 0, device: int = 0, rst_pin: int = 17,
        dc_pin: int = 25, cs_pin: int = 8, busy_pin: int = 24,
        epd_width: int = 104, epd_height: int = 212
    ):
        super().__init__()
        logger.debug(
            'EPD.__init__(bus=%d, device=%d, rst_pin=%d, dc_pin=%d,'
            'cs_pin=%d, busy_pin=%d, epd_width=%d, epd_height=%d)',
            bus, device, rst_pin, dc_pin, cs_pin, busy_pin, epd_width,
            epd_height
        )
        self._GPIO = RPi.GPIO
        self._SPI = spidev.SpiDev(bus, device)
        self._reset_pin: int = rst_pin
        self._dc_pin: int = dc_pin
        self._busy_pin: int = busy_pin
        self._cs_pin: int = cs_pin
        self._width: int = epd_width
        self._height: int = epd_height
        self._GPIO.setmode(self._GPIO.BCM)
        self._GPIO.setwarnings(False)
        self._GPIO.setup(self._reset_pin, self._GPIO.OUT)
        self._GPIO.setup(self._dc_pin, self._GPIO.OUT)
        self._GPIO.setup(self._cs_pin, self._GPIO.OUT)
        self._GPIO.setup(self._busy_pin, self._GPIO.IN)
        self._SPI.max_speed_hz = 4000000
        self._SPI.mode = 0b00
        self._initialize()
        self._wrote_black: bool = True
        self._wrote_red: bool = True
        self.clear()
        self._wrote_black: bool = False
        self._wrote_red: bool = False
        time.sleep(1)  # present in upstream example
        logger.debug('EPD initialize complete')

    def _digital_write(self, pin, value):
        self._GPIO.output(pin, value)

    def _digital_read(self, pin):
        return self._GPIO.input(pin)

    def _delay_ms(self, delaytime):
        time.sleep(delaytime / 1000.0)

    def _spi_writebyte(self, data):
        self._SPI.writebytes(data)

    def _hardware_reset(self):
        logger.debug('Reset EPD')
        self._digital_write(self._reset_pin, 1)
        self._delay_ms(200)
        self._digital_write(self._reset_pin, 0)
        self._delay_ms(10)
        self._digital_write(self._reset_pin, 1)
        self._delay_ms(200)

    def _send_command(self, command):
        self._digital_write(self._dc_pin, 0)
        self._digital_write(self._cs_pin, 0)
        self._spi_writebyte([command])
        self._digital_write(self._cs_pin, 1)

    def _send_data(self, data):
        self._digital_write(self._dc_pin, 1)
        self._digital_write(self._cs_pin, 0)
        self._spi_writebyte([data])
        self._digital_write(self._cs_pin, 1)

    @property
    def _is_busy(self):
        return self._digital_read(self._busy_pin) == 0

    def _wait_for_not_busy(self):
        logger.debug("Waiting until display is not busy (100ms check interval)")
        while self._is_busy:
            self._delay_ms(100)
        logger.debug("display is no longer busy")

    def _initialize(self):
        logger.debug('Initialize EPD')
        self._hardware_reset()
        self._send_command(0x06)  # BOOSTER_SOFT_START
        self._send_data(0x17)
        self._send_data(0x17)
        self._send_data(0x17)
        self._send_command(0x04)  # POWER_ON
        self._wait_for_not_busy()
        self._send_command(0x00)  # PANEL_SETTING
        self._send_data(0x8F)
        self._send_command(0x50)  # VCOM_AND_DATA_INTERVAL_SETTING
        self._send_data(0xF0)
        self._send_command(0x61)  # RESOLUTION_SETTING
        self._send_data(self._width & 0xff)
        self._send_data(self._height >> 8)
        self._send_data(self._height & 0xff)
        logger.debug('EPD Initialized')

    def _getbuffer(self, image):
        buf = [0xFF] * (int(self._width/8) * self._height)
        image_monocolor = image.convert('1')
        imwidth, imheight = image_monocolor.size
        pixels = image_monocolor.load()
        if imwidth == self._width and imheight == self._height:
            logger.debug("Vertical")
            for y in range(imheight):
                for x in range(imwidth):
                    # Set the bits for the column of pixels at the current position.
                    if pixels[x, y] == 0:
                        buf[int((x + y * self._width) / 8)] &= ~(0x80 >> (x % 8))
        elif imwidth == self._height and imheight == self._width:
            logger.debug("Horizontal")
            for y in range(imheight):
                for x in range(imwidth):
                    newx = y
                    newy = self._height - x - 1
                    if pixels[x, y] == 0:
                        buf[int((newx + newy*self._width) / 8)] &= ~(0x80 >> (y % 8))
        return buf

    def _display(
        self, black: Optional[Image.Image] = None,
        red: Optional[Image.Image] = None
    ):
        if black is not None:
            logger.debug('Displaying black image')
            buf = self._getbuffer(black)
            self._send_command(0x10)
            for i in range(0, int(self._width * self._height / 8)):
                self._send_data(buf[i])
            self._send_command(0x92)
            self._wrote_black = True
        if red is not None:
            logger.debug('Displaying red image')
            buf = self._getbuffer(red)
            self._send_command(0x13)
            for i in range(0, int(self._width * self._height / 8)):
                self._send_data(buf[i])
            self._send_command(0x92)
            self._wrote_red = True
        logger.debug('Refresh')
        self._send_command(0x12)  # REFRESH
        self._wait_for_not_busy()
        logger.debug('Done refreshing')

    def update_display(
        self, fix_type: FixType, lat: float, lon: float, extradata: str,
        fix_precision: Tuple[float, float], dt: datetime, should_clear: bool
    ):
        if should_clear:
            self.clear()
        lines = [dt.strftime('%H:%M:%S UTC')]
        if fix_type == FixType.NO_GPS:
            lines.extend(['No GPS yet', '', ''])
        elif fix_type == FixType.NO_FIX:
            lines.extend(['No Fix yet', '', ''])
        else:
            ft = '??'
            if fix_type == FixType.FIX_2D:
                ft = '2D'
            elif fix_type == FixType.FIX_3D:
                ft = '3D'
            lines.append(f'{ft} {fix_precision[0]:.8},{fix_precision[1]:.8}')
            lines.append(f'Lat: {lat:.15}')
            lines.append(f'Lon: {lon:.15}')
        lines.append(extradata)
        self._write_lines(lines)

    def _write_lines(self, lines):
        """
        Write ``lines`` to the display.
        """
        logging.info('Begin update display')
        font = self.font(16)
        HBlackimage = Image.new('1', (self._height, self._width), 255)
        drawblack = ImageDraw.Draw(HBlackimage)
        for idx, content in enumerate(lines):
            drawblack.text(
                (0, 20 * idx), content, font=font, fill=0
            )
        self._display(black=HBlackimage)
        logging.info('End update display')

    def clear(self):
        if self._wrote_black:
            logger.debug('Clearing black')
            self._send_command(0x10)
            for i in range(0, int(self._width * self._height / 8)):
                self._send_data(0xFF)
            self._send_command(0x92)
            self._wrote_black = False
        if self._wrote_red:
            logger.debug('Clearing red')
            self._send_command(0x13)
            for i in range(0, int(self._width * self._height / 8)):
                self._send_data(0xFF)
            self._send_command(0x92)
            self._wrote_red = False
        logger.debug('Done clearning')
        logger.debug('Refresh')
        self._send_command(0x12)  # REFRESH
        self._wait_for_not_busy()
        logger.debug('Done refreshing')

    def _put_to_sleep(self):
        self._send_command(0x02)  # POWER_OFF
        self._wait_for_not_busy()
        self._send_command(0x07)  # DEEP_SLEEP
        self._send_data(0xA5)  # check code

    def _destroy(self):
        logger.debug("spi end")
        self._SPI.close()
        logger.debug("close 5V, Module enters 0 power consumption ...")
        self._GPIO.output(self._reset_pin, 0)
        self._GPIO.output(self._dc_pin, 0)
        self._GPIO.cleanup()
        logger.debug('EPD cleaned up')

    def __del__(self):
        self._put_to_sleep()
        self._destroy()
