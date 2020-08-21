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

import logging
from pizero_gpslog.displays.base import BaseDisplay
from typing import ClassVar
import time
import os

logger = logging.getLogger(__name__)


class DummyDisplay(BaseDisplay):

    #: width of the display in characters
    width_chars: ClassVar[int] = 21

    #: height of the display in lines
    height_lines: ClassVar[int] = 5

    #: the minimum number of seconds between refreshes of the display
    min_refresh_seconds: ClassVar[int] = 15

    def __init__(self):
        super().__init__()
        self.sleep_time: int = int(os.environ.get('DUMMY_SLEEP_TIME', '2'))
        logger.debug(
            'Initialize DummyDisplay; sleep time (%d sec) set by '
            'DUMMY_SLEEP_TIME environment variable.'
        )

    def update_display(self):
        """
        Write ``self._lines`` to the display.
        """
        fmt: str = 'DUMMYDISPLAY>|%-' + '%ds|' % self.width_chars
        for l in self._lines:
            logger.warning(fmt, l)
        logger.debug('Dummy display sleeping %d seconds...', self.sleep_time)
        time.sleep(self.sleep_time)

    def clear(self):
        logger.warning('------ DUMMYDISPLAY CLEAR -------')

    def __del__(self):
        logger.warning('DUMMYDISPLAY __del__')
