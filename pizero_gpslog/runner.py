"""
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

import os
import logging
import time
import json
from typing import Optional
from _io import TextIOWrapper
from datetime import datetime

from pizero_gpslog.gpsd import (
    GpsClient, NoActiveGpsError, NoFixError, GpsResponse
)
from pizero_gpslog.version import VERSION, PROJECT_URL
from pizero_gpslog.utils import set_log_info, set_log_debug
from pizero_gpslog.displaymanager import DisplayManager

if 'LED_PIN_RED' in os.environ and 'LED_PIN_GREEN' in os.environ:
    from gpiozero import LED
else:
    from pizero_gpslog.fakeled import FakeLed as LED

logger = logging.getLogger(__name__)


class GpsLogger(object):

    def __init__(self):
        logger.warning(
            'Starting pizero-gpslog version %s <%s>', VERSION, PROJECT_URL
        )
        led_1_pin: int = int(os.environ.get('LED_PIN_RED', '-1'))
        logger.info('Initializing LED1 (Red) on pin %d', led_1_pin)
        self.LED1: LED = LED(led_1_pin)
        led_2_pin: int = int(os.environ.get('LED_PIN_GREEN', '-2'))
        logger.info('Initializing LED2 (Green) on pin %d', led_2_pin)
        self.LED2: LED = LED(led_2_pin)
        self.LED2.on()
        logger.info('Connecting to gpsd')
        self.gps: GpsClient = GpsClient()
        self.interval_sec: int = int(os.environ.get('GPS_INTERVAL_SEC', '5'))
        logger.info('Sleeping %s seconds between writes', self.interval_sec)
        self.flush_file: str = os.environ.get('FLUSH_FILE', '') != 'false'
        self.outdir: str = os.path.abspath(
            os.environ.get('OUT_DIR', os.getcwd())
        )
        logger.debug('Writing logs in: %s', self.outdir)
        self._fh: Optional[TextIOWrapper] = None
        self._display: Optional[DisplayManager] = None
        if 'DISPLAY_CLASS' in os.environ:
            modname, clsname = os.environ['DISPLAY_CLASS'].split(':')
            self._display = DisplayManager(modname, clsname)
            self._display.start()

    def run(self):
        self.LED2.off()
        while True:
            time.sleep(self.interval_sec)
            logger.debug('Reading current position from gpsd')
            try:
                packet = self.gps.current_fix
            except NoActiveGpsError:
                packet = GpsResponse()
                packet.mode = 0
            except NoFixError:
                packet = GpsResponse()
                packet.mode = 1
            self._handle_packet(packet)

    def _handle_waiting_gps(self, packet: GpsResponse):
        logger.warning(
            'No data returned by gpsd (no active GPS) - %s',
            packet
        )
        if not self.LED1.is_lit:
            self.LED1.on()
        if self._display is not None:
            self._display.clear()
            self._display.set_heading(
                datetime.utcnow().strftime('%H:%M:%S UTC')
            )
            self._display.set_status('no active GPS. waiting...')

    def _handle_no_fix(self, packet: GpsResponse):
        logger.warning('No GPS fix yet - %s', packet)
        self.LED1.blink(on_time=0.1, off_time=0.1, n=3)
        if self._display is not None:
            self._display.clear()
            self._display.set_heading(
                datetime.utcnow().strftime('%H:%M:%S UTC')
            )
            self._display.set_status('no fix yet; waiting...')

    def _ensure_file_open(self, packet: GpsResponse):
        if self._fh is not None:
            return
        logger.info(
            'Got GPS packet with fix; GPS time is %s (UTC)'
            '' % packet.get_time()
        )
        outfile = os.path.join(
            self.outdir,
            '%s.json' % packet.get_time().strftime('%Y-%m-%d_%H-%M-%S')
        )
        logger.info('Writing output to: %s', outfile)
        self._fh = open(outfile, 'w', buffering=1)

    def _handle_2d_fix(self, packet: GpsResponse):
        logger.info(packet)
        self.LED1.blink(on_time=0.5, off_time=0.25, n=2)
        if self._display is not None:
            self._display.clear()
            self._display.set_heading(
                packet.get_time().strftime('%H:%M:%S UTC')
            )
            self._display.set_status('2D Fix; %s,%s' % packet.position_precision())
            lat, lon = packet.position()
            self._display.set_lat('Lat %s' % lat)
            self._display.set_lon('Lon %s' % lon)

    def _handle_3d_fix(self, packet: GpsResponse):
        logger.info(packet)
        self.LED1.blink(on_time=0.5, off_time=0.25, n=1)
        if self._display is not None:
            self._display.clear()
            self._display.set_heading(
                packet.get_time().strftime('%H:%M:%S UTC')
            )
            self._display.set_status('3D Fix; %s,%s' % packet.position_precision())
            lat, lon = packet.position()
            self._display.set_lat('Lat %s' % lat)
            self._display.set_lon('Lon %s' % lon)

    def _handle_packet(self, packet: GpsResponse):
        if packet.mode == 0:
            return self._handle_waiting_gps(packet)
        if self.LED1.is_lit:
            self.LED1.off()
        if packet.mode == 1:
            return self._handle_no_fix(packet)
        # else we have a fix
        self._ensure_file_open(packet)
        if packet.mode == 2:
            self._handle_2d_fix(packet)
        elif packet.mode == 3:
            self._handle_3d_fix(packet)
        self._fh.write('%s\n' % json.dumps(packet.raw_packet))
        if self.flush_file:
            self._fh.flush()
        self.LED2.blink(on_time=0.25, off_time=0.25, n=1)


def main():
    global logger
    format = "[%(asctime)s %(levelname)s] %(message)s"
    logging.basicConfig(level=logging.WARNING, format=format)
    logger = logging.getLogger()

    # set logging level
    if os.environ.get('LOG_LEVEL', None) == 'DEBUG':
        set_log_debug(logger)
    elif os.environ.get('LOG_LEVEL', None) == 'INFO':
        set_log_info(logger)
    GpsLogger().run()


if __name__ == "__main__":
    main()
