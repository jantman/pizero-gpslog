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
from typing import Optional, Tuple
from enum import Enum
from datetime import datetime, timezone
from pizero_gpslog.displays.base import BaseDisplay
from pizero_gpslog.utils import ThreadSafeValue, FixType

logger = logging.getLogger(__name__)


class DisplayWriterThread(Thread):

    def __init__(
        self, driver_cls: BaseDisplay.__class__, fix_type: ThreadSafeValue,
        lat: ThreadSafeValue, lon: ThreadSafeValue,
        extradata: ThreadSafeValue, fix_precision: ThreadSafeValue,
        should_clear: ThreadSafeValue, refresh_sec: int = 0
    ):
        super().__init__(name='DisplayWriter', daemon=True)
        self._fix_type: ThreadSafeValue = fix_type
        self._lat: ThreadSafeValue = lat
        self._lon: ThreadSafeValue = lon
        self._extradata: ThreadSafeValue = extradata
        self._fix_precision: ThreadSafeValue = fix_precision
        self._should_clear: ThreadSafeValue = should_clear
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
        driver.update_display(
            fix_type=self._fix_type.get(),
            fix_precision=self._fix_precision.get(),
            lat=self._lat.get(), lon=self._lon.get(),
            extradata=self._extradata.get(),
            dt=datetime.now(timezone.utc),
            should_clear=self._should_clear.get()
        )
        self._should_clear.set(False)


class DisplayManager:

    def __init__(self, modname: str, clsname: str):
        self._fix_type: ThreadSafeValue = ThreadSafeValue(FixType.NO_GPS)
        self._fix_precision: ThreadSafeValue = ThreadSafeValue((0.0, 0.0))
        self._lat: ThreadSafeValue = ThreadSafeValue()
        self._lon: ThreadSafeValue = ThreadSafeValue()
        self._extradata: ThreadSafeValue = ThreadSafeValue()
        self._should_clear: ThreadSafeValue = ThreadSafeValue(False)
        self._writer_thread: Optional[DisplayWriterThread] = None
        logger.debug('Import %s:%s', modname, clsname)
        mod = import_module(modname)
        self._driver_cls: BaseDisplay.__class__ = getattr(mod, clsname)
        self.clear()

    def start(self):
        refresh_sec = int(os.environ.get('DISPLAY_REFRESH_SEC', '0'))
        self._writer_thread = DisplayWriterThread(
            self._driver_cls, self._fix_type, self._lat, self._lon,
            self._extradata, self._fix_precision, self._should_clear,
            refresh_sec=refresh_sec
        )
        self._writer_thread.start()

    def set_fix_type(self, gps_status: FixType):
        self._fix_type.set(gps_status)

    def set_fix_precision(self, precision: Tuple[float, float]):
        self._fix_precision.set(precision)

    def set_lat(self, lat: float):
        self._lat.set(lat)

    def set_lon(self, lon: float):
        self._lon.set(lon)

    def set_extradata(self, s: str):
        self._extradata.set(s)

    def clear(self):
        self._should_clear.set(True)
