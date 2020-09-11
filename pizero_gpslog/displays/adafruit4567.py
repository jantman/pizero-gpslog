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
from typing import Optional, ClassVar, Tuple
from board import SCL, SDA, D4
import busio
import digitalio
import adafruit_ssd1305
from pizero_gpslog.displays.base import BaseDisplay
from pizero_gpslog.utils import FixType
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

logger = logging.getLogger(__name__)


class Adafruit4567(BaseDisplay):

    #: width of the display in characters
    width_chars: ClassVar[int] = 20

    #: height of the display in lines
    height_lines: ClassVar[int] = 4

    #: the minimum number of seconds between refreshes of the display
    min_refresh_seconds: ClassVar[int] = 0.1

    def __init__(self):
        super().__init__()
        self._oled_reset = digitalio.DigitalInOut(D4)
        self._i2c = busio.I2C(SCL, SDA)
        # Create the SSD1305 OLED class.
        # The first two parameters are the pixel width and pixel height.
        # Change these to the right size for your display!
        self._disp = adafruit_ssd1305.SSD1305_I2C(
            128, 32, self._i2c, reset=self._oled_reset
        )
        self.clear()
        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self._width = self._disp.width
        self._height = self._disp.height
        self._image = Image.new("1", (self._width, self._height))
        # Get drawing object to draw on image.
        self._draw = ImageDraw.Draw(self._image)
        # Draw a black filled box to clear the image.
        self._draw.rectangle(
            (0, 0, self._width, self._height), outline=0, fill=0
        )
        self._top = -2
        self._font = BaseDisplay.font(8)
        #self._font = ImageFont.load_default()

    def update_display(
        self, fix_type: FixType, lat: float, lon: float, extradata: str,
        fix_precision: Tuple[float, float], dt: datetime, should_clear: bool
    ):
        if should_clear:
            self.clear()
        dts = dt.strftime('%H:%M:%S Z')
        lines = ['', '', '', '']
        if fix_type == FixType.NO_GPS:
            lines = [
                dts,
                'No GPS yet',
                '',
                extradata
            ]
        elif fix_type == FixType.NO_FIX:
            lines = [
                dts,
                'No Fix yet',
                '',
                extradata
            ]
        elif fix_type == FixType.FIX_2D:
            lines = [
                dts + ' | 2D fix',
                f'Lat: {lat:.15}',
                f'Lon: {lon:.15}',
                extradata
            ]
        elif fix_type == FixType.FIX_3D:
            lines = [
                dts + ' | 3D fix',
                f'Lat: {lat:.15}',
                f'Lon: {lon:.15}',
                extradata
            ]
        self._write_lines(lines)

    def _write_lines(self, lines):
        logging.info('Begin update display')
        self._draw.rectangle(
            (0, 0, self._width, self._height), outline=0, fill=0
        )
        for idx, content in enumerate(lines):
            coords = (0, self._top + (idx * 8))
            self._draw.text(
                coords, content, font=self._font, fill=255
            )
        # Display image.
        self._disp.image(self._image)
        self._disp.show()
        logging.info('End update display')

    def clear(self):
        self._disp.fill(0)
        self._disp.show()

    def __del__(self):
        self.clear()
