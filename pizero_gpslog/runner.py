"""
The latest version of this package is available at:
<http://github.com/jantman/pizero-gpslog>

##################################################################################
Copyright 2018 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

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
from datetime import datetime
import atexit

from pizero_gpslog.gpsd import GpsClient, GpsResponse

if 'LED_PIN_RED' in os.environ and 'LED_PIN_GREEN' in os.environ:
    from gpiozero import LED
else:
    from pizero_gpslog.fakeled import FakeLed as LED

logger = logging.getLogger(__name__)


class GpsLogger(object):

    def __init__(self):
        led_1_pin = int(os.environ.get('LED_PIN_RED', '-1'))
        logger.info('Initializing LED1 (Red) on pin %d', led_1_pin)
        self.LED1 = LED(led_1_pin)
        led_2_pin = int(os.environ.get('LED_PIN_GREEN', '-2'))
        logger.info('Initializing LED2 (Green) on pin %d', led_2_pin)
        self.LED2 = LED(led_2_pin)
        self.LED2.on()
        logger.info('Connecting to gpsd')
        self.gps = GpsClient()
        self.interval_sec = int(os.environ.get('GPS_INTERVAL_SEC', '5'))
        logger.info('Sleeping %s seconds between writes', self.interval_sec)
        self.flush_file = os.environ.get('FLUSH_FILE', '') != 'false'
        self.outdir = os.path.abspath(os.environ.get('OUT_DIR', os.getcwd()))
        logger.debug('Writing logs in: %s', self.outdir)

    def run(self):
        outfile = os.path.join(
            self.outdir, '%s.out' % datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        )
        logger.info('Writing output to: %s', outfile)
        with open(outfile, 'w') as fh:
            self.LED2.off()
            while True:
                time.sleep(self.interval_sec)
                logger.debug('Reading current position from gpsd')
                packet = self.gps.current_fix
                if packet.mode == 0:
                    logger.warning(
                        'No data returned by gpsd (no active GPS) - %s',
                        packet
                    )
                    self.LED1.on()
                    continue
                if self.LED1.is_lit:
                    self.LED1.off()
                if packet.mode == 1:
                    logger.warning('No GPS fix yet - %s', packet)
                    self.LED1.blink(on_time=0.1, off_time=0.1, n=3)
                    continue
                if packet.mode == 2:
                    # 2D Fix
                    logger.info(packet)
                    self.LED1.blink(on_time=0.5, off_time=0.5, n=2)
                elif packet.mode == 3:
                    # 3D Fix
                    logger.info(packet)
                    self.LED1.blink(on_time=0.5, off_time=0.5, n=1)
                fh.write('%s\n' % json.dumps(packet.raw_packet))
                if self.flush_file:
                    fh.flush()
                self.LED2.blink(on_time=0.25, off_time=0.25, n=1)


def set_log_info(logger):
    """
    set logger level to INFO via :py:func:`~.set_log_level_format`.
    """
    set_log_level_format(logger, logging.INFO,
                         '%(asctime)s %(levelname)s:%(name)s:%(message)s')


def set_log_debug(logger):
    """
    set logger level to DEBUG, and debug-level output format,
    via :py:func:`~.set_log_level_format`.
    """
    set_log_level_format(
        logger,
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(logger, level, format):
    """
    Set logger level and format.

    :param logger: the logger object to set on
    :type logger: logging.Logger
    :param level: logging level; see the :py:mod:`logging` constants.
    :type level: int
    :param format: logging formatter format string
    :type format: str
    """
    formatter = logging.Formatter(fmt=format)
    logger.handlers[0].setFormatter(formatter)
    logger.setLevel(level)


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