#!/usr/bin/python
# -*- coding:utf-8 -*-
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
from datetime import datetime
from pizero_gpslog.displaymanager import DisplayManager
from pizero_gpslog.utils import set_log_debug

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
set_log_debug(logger)


def main():
    if 'DISPLAY_CLASS' not in os.environ:
        logger.warning(
            'DISPLAY_CLASS environment variable not set; using default dummy'
        )
        os.environ[
            'DISPLAY_CLASS'
        ] = 'pizero_gpslog.displays.dummy:DummyDisplay'
    modname, clsname = os.environ['DISPLAY_CLASS'].split(':')
    dm = DisplayManager(modname, clsname)
    dm.start()
    for i in range(0, 10):
        logger.info('OUTER sleep 5s')
        time.sleep(5)
        logger.info('OUTER set display')
        dm.set_heading(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        dm.set_status('A' + (f'{i}' * 19))
        dm.set_lat('B' + (f'{i}' * 19))
        dm.set_lon('C' + (f'{i}' * 19))
        dm.set_extradata('D' + (f'{i}' * 19))
    logger.info('OUTER Finished display-setting loop')


if __name__ == "__main__":
    main()
