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
from importlib import import_module
import time
from threading import Thread
from typing import Optional, List
from pizero_gpslog.version import VERSION, PROJECT_URL
from pizero_gpslog.displays.base import BaseDisplay
from pizero_gpslog.utils import ThreadSafeValue

logger = logging.getLogger(__name__)


class DisplayWriterThread(Thread):

    def __init__(
        self, driver_cls: BaseDisplay.__class__, status: ThreadSafeValue,
        lat: ThreadSafeValue, lon: ThreadSafeValue,
        extradata: ThreadSafeValue, heading: ThreadSafeValue,
        refresh_sec: int = 0
    ):
        super().__init__(name='DisplayWriter', daemon=True)
        self._status: ThreadSafeValue = status
        self._lat: ThreadSafeValue = lat
        self._lon: ThreadSafeValue = lon
        self._extradata: ThreadSafeValue = extradata
        self._heading: ThreadSafeValue = heading
        self._driver_cls: BaseDisplay.__class__ = driver_cls
        self._refresh_sec = refresh_sec
        logger.info(
            'Initialize DisplayWriterThread; driver_class=%s refresh_sec=%s',
            driver_cls, refresh_sec
        )

    def run(self):
        logger.debug('Initialize display driver class')
        driver: BaseDisplay = self._driver_cls()
        if (
            self._refresh_sec != 0 and
            driver.min_refresh_seconds > self._refresh_sec
        ):
            logger.debug(
                'Set refresh_sec to %s based on driver\'s '
                'min_refresh_seconds=%s', self._refresh_sec,
                driver.min_refresh_seconds
            )
            self._refresh_sec = driver.min_refresh_seconds
        logger.info('Refresh display every %d seconds', self._refresh_sec)
        while True:
            start = time.time()
            self.iteration(driver)
            duration = time.time() - start
            if duration < self._refresh_sec:
                t = self._refresh_sec - duration
                logger.debug('Sleep %s sec before next refresh', t)
                time.sleep(t)

    def iteration(self, driver: BaseDisplay):
        driver.set_line(0, self._heading.get())
        driver.set_line(1, self._status.get())
        driver.set_line(2, self._lat.get())
        driver.set_line(3, self._lon.get())
        driver.set_line(4, self._extradata.get())
        driver.update_display()


class DisplayManager:
    """
    We expect a display to have 5 lines. From top to bottom:

    heading
    status
    lat
    lon
    extradata

    If a given display supports less than 5 lines, the presedence is:
    lat
    lon
    status
    extradata
    heading
    """

    def __init__(self, modname: str, clsname: str):
        self._status: ThreadSafeValue = ThreadSafeValue()
        self._lat: ThreadSafeValue = ThreadSafeValue()
        self._lon: ThreadSafeValue = ThreadSafeValue()
        self._extradata: ThreadSafeValue = ThreadSafeValue()
        self._heading: ThreadSafeValue = ThreadSafeValue()
        self._writer_thread: Optional[DisplayWriterThread] = None
        logger.debug('Import %s:%s', modname, clsname)
        mod = import_module(modname)
        self._driver_cls: BaseDisplay.__class__ = getattr(mod, clsname)
        # set the initial text
        self.set_filled_text(
            f'pizero-gpslog v{VERSION}\n{PROJECT_URL}\nstarting....'
        )

    def start(self):
        refresh_sec = int(os.environ.get('DISPLAY_REFRESH_SEC', '0'))
        self._writer_thread = DisplayWriterThread(
            self._driver_cls, self._status, self._lat, self._lon,
            self._extradata, self._heading, refresh_sec=refresh_sec
        )
        self._writer_thread.start()

    def set_status(self, s: str):
        self._status.set(s)

    def set_lat(self, s: str):
        self._lat.set(s)

    def set_lon(self, s: str):
        self._lon.set(s)

    def set_extradata(self, s: str):
        self._extradata.set(s)

    def set_heading(self, s: str):
        self._heading.set(s)

    def set_filled_text(self, s: str):
        chars: int = self._driver_cls.width_chars
        lines: int = self._driver_cls.height_lines
        slots: List[str] = []
        parts = s.split("\n")
        for p in parts:
            if len(p) <= chars:
                slots.append(p)
                continue
            # we have a line that needs to wrap
            chunks = [p[i:i + chars] for i in range(0, len(p), chars)]
            slots.extend(chunks)
        if len(slots) > lines:
            removed = slots[lines:]
            slots = slots[:lines]
            logger.warning('Filled text overflowed. Removed: %s', removed)
        while len(slots) < 5:
            slots.append('')
        self._heading.set(slots[0])
        self._status.set(slots[1])
        self._lat.set(slots[2])
        self._lon.set(slots[3])
        self._extradata.set(slots[4])

    def clear(self):
        self._status.set('')
        self._lat.set('')
        self._lon.set('')
        self._extradata.set('')
        self._heading.set('')
