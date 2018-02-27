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

import logging

logger = logging.getLogger(__name__)


class FakeLed(object):

    def __init__(self, pin_num, **kwargs):
        self.pin_num = pin_num
        self._lit = False

    def on(self):
        logger.warning('%s ON' % self)
        self._lit = True

    def off(self):
        logger.warning('%s OFF' % self)
        self._lit = False

    def blink(self, on_time=1, off_time=1, n=None, background=True):
        if n is None:
            raise RuntimeError('ERROR: method would never return!')
        if not background:
            raise RuntimeError(
                'ERROR: LED.blink not called from background!'
            )
        logger.warning('%s BLINK on=%s off=%s n=%s background=%s',
                       self, on_time, off_time, n, background)
        self._lit = False

    def toggle(self):
        logger.warning('%s TOGGLE' % self)
        self._lit = not self._lit

    @property
    def is_lit(self):
        return self._lit

    @property
    def pin(self):
        return self.pin_num

    def __repr__(self):
        return '<FakeLed pin_num=%d>' % self.pin_num
