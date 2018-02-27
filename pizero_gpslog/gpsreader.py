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
import threading
import time

from pizero_gpslog.gpsd_gps.gps import gps

if os.environ.get('USE_SYSTEMD_DAEMON', '') != 'false':
    USE_SYSTEMD = True
    from systemd.daemon import notify, Notification
else:
    USE_SYSTEMD = False

logger = logging.getLogger(__name__)


class GpsReader(threading.Thread):

    def __init__(self, stopper, data, datalock):
        """
        Thread that handles actually reading data from the GPS.

        :param stopper: Event used to signal when threads should clean up
          and exit
        :type stopper: threading.Event
        :param data: thread-shared instance that stores GPS data
        :type data: pizero_gpslog.gpsdata.GpsData
        :param datalock: Lock for accessing data
        :type datalock: threading.Lock
        """
        super(GpsReader, self).__init__()
        self.data = data
        self.datalock = datalock
        self.stopper = stopper

    def run(self):
        while not self.stopper.is_set():
            t = time.time()
            logger.info('Set data to: %s', t)
            with self.datalock:
                self.data.set(t)
            if USE_SYSTEMD:
                notify(Notification.STATUS, "GpsReader running")
            time.sleep(1)
        logger.warning('GpsReader thread got exit event.')
