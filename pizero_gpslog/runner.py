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

import sys
import os
import logging
import signal
import threading

from pizero_gpslog.gpsdata import GpsData
from pizero_gpslog.gpsreader import GpsReader
from pizero_gpslog.filewriter import FileWriter
from pizero_gpslog.ledthread import LedController

if os.environ.get('USE_SYSTEMD_DAEMON', '') != 'false':
    USE_SYSTEMD = True
    from systemd.daemon import notify, Notification
else:
    USE_SYSTEMD = False

if 'LED_PIN_RED' in os.environ and 'LED_PIN_GREEN' in os.environ:
    from gpiozero import LED
else:
    from pizero_gpslog.fakeled import FakeLed as LED

logger = logging.getLogger(__name__)


class InterruptHandler(object):

    def __init__(self, stopper, worker_list):
        self.stopper = stopper
        self.workers = worker_list

    def __call__(self, signum, frame):
        self.stopper.set()
        for worker in self.workers:
            worker.join()
        if USE_SYSTEMD:
            notify(Notification.STOPPING)
        raise SystemExit(0)


class GpsLogger(object):

    def __init__(self):
        self._stopper = False

    def run(self):
        data = GpsData()
        datalock = threading.Lock()
        stopper = threading.Event()

        # create threads
        logger.debug('Initializing thread classes')
        reader = GpsReader(stopper, data, datalock)
        writer = FileWriter(stopper, data, datalock)
        led_1_pin = int(os.environ.get('LED_PIN_RED', '-1'))
        led_2_pin = int(os.environ.get('LED_PIN_GREEN', '-2'))
        logger.debug(
            'LEDs using class %s; pins %s and %s',
            LED.__name__, led_1_pin, led_2_pin
        )
        leds = LedController(stopper, data, datalock, LED, led_1_pin, led_2_pin)

        # setup signal handler
        logger.debug('Setting up signal handler')
        ih = InterruptHandler(stopper, [reader, writer, leds])
        signal.signal(signal.SIGINT, ih)

        # start threads
        logger.debug('Starting threads')
        reader.start()
        writer.start()
        leds.start()

        if USE_SYSTEMD:
            notify(Notification.READY)

        # wait for work to complete, or interrupt
        reader.join()
        # finish all threads
        ih(None, None)


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
