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
import threading
import time

logger = logging.getLogger(__name__)


class LedController(threading.Thread):

    def __init__(self, stopper, data, datalock, led_class, pinA, pinB):
        """
        Thread that handles controlling the LEDs.

        :param stopper: Event used to signal when threads should clean up
          and exit
        :type stopper: threading.Event
        :param data: thread-shared instance that stores GPS data
        :type data: pizero_gpslog.gpsdata.GpsData
        :param datalock: Lock for accessing data
        :type datalock: threading.Lock
        :param led_class: class to use for controlling LEDs
        :param pinA: primary LED GPIO pin number
        :type pinA: int
        :param pinB: secondary LED GPIO pin number
        :type pinB: int
        """
        super(LedController, self).__init__()
        self.data = data
        self.datalock = datalock
        self.stopper = stopper
        self._led_class = led_class
        self._pin_a_num = pinA
        self._pin_b_num = pinB

    def run(self):
        self.pinA = self._led_class(self._pin_a_num)
        self.pinB = self._led_class(self._pin_b_num)
        while not self.stopper.is_set():
            datacopy = None
            with self.datalock:
                datacopy = self.data.getcopy()
            self.pinA.toggle()
            time.sleep(10)
        logger.warning('LedController thread got exit event.')
