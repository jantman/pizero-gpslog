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

Note: for dependencies, this requires:

pyudev==0.22.0

"""

import logging
import os
from glob import iglob
from pyudev import Context, Devices
from time import sleep, time
from gmc import GMC
from pizero_gpslog.extradata.base import BaseExtraDataProvider
if not hasattr(GMC, 'get_config'):
    raise RuntimeError(
        'ERROR: gmc must be installed from jantman\'s fork on the '
        'jantman-fixes-config branch; pip install '
        'git+https://gitlab.com/jantman/gmc.git@jantman-fixes-config'
    )

logger = logging.getLogger(__name__)


class GqGMC500plus(BaseExtraDataProvider):

    _gmc_vendor_model_revision = [
        ('1a86', '7523', '0263')
    ]

    def __init__(self, devname=None):
        super().__init__()
        self._original_devname = devname
        self._gmc = None
        self._data = self._default_response()
        self._sleep_time = int(os.environ.get('GMC_SLEEP_SEC', '5'))
        logger.info(
            'Sleeping %d seconds between GMC polls; override by setting '
            'GMC_SLEEP_SEC environment variable as an int', self._sleep_time
        )
        self._init_gmc()

    def _default_response(self):
        return {
            'message': f'',
            'data': {
                'time': time(),
                'cps': None,
                'cpsl': None,
                'cpsh': None,
                'cpm': None,
                'cpml': None,
                'cpmh': None,
                'maxcps': None,
                'calibration': None
            }
        }

    def _try_init(self):
        if self._original_devname is None:
            devname = self._find_usb_device()
        else:
            devname = self._original_devname
        if devname is None:
            logger.critical(
                'ERROR: No devname given, and could not determine GMC-500+ '
                'device name using pyudev.'
            )
            self._devname = devname
            return
        self._devname = devname
        logger.info('Using device: %s', devname)
        self._gmc = None
        logger.debug('Connecting to GMC...')
        self._gmc = GMC(config_update={'DEFAULT_PORT': self._devname})
        logger.debug('Connected.')
        self._config = self._gmc.get_config()
        logger.info(
            'GMC current time: %s; version: %s; serial: %s; voltage: %s; '
            'config: %s', self._gmc.get_date_time(), self._gmc.version(),
            self._gmc.serial(), self._gmc.voltage(), self._config
        )
        calib_fields = [
            'CalibCPM_0', 'CalibuSv_0', 'CalibCPM_1', 'CalibuSv_1',
            'CalibCPM_2', 'CalibuSv_2'
        ]
        self._calibration = {
            x: self._config[x] for x in calib_fields
        }

    def _init_gmc(self):
        self._gmc = None
        self._data = self._default_response()
        try:
            self._try_init()
            return
        except Exception as ex:
            logger.critical(
                'Error initializing GMC; try again in 10s', ex
            )
            logger.debug('GMC init error: %s', ex, exc_info=True)
            sleep(10)

    def run(self):
        logger.debug('Running extra data provider...')
        while True:
            try:
                cps = self._gmc.cps(numeric=True)
                cpsl = self._gmc.cpsl(numeric=True)
                cpsh = self._gmc.cpsh(numeric=True)
                cpm = self._gmc.cpm(numeric=True)
                cpml = self._gmc.cpml(numeric=True)
                cpmh = self._gmc.cpmh(numeric=True)
                maxcps = self._gmc.max_cps(numeric=True)
                logger.debug('End querying GMC')
                self._data = {
                    'message': f'{cps} CPS | {cpm} CPM',
                    'data': {
                        'time': time(),
                        'cps': cps,
                        'cpsl': cpsl,
                        'cpsh': cpsh,
                        'cpm': cpm,
                        'cpml': cpml,
                        'cpmh': cpmh,
                        'maxcps': maxcps,
                        'calibration': self._calibration
                    }
                }
            except Exception as ex:
                logger.error(
                    'Error querying GMC; re-init. Error: %s', ex, exc_info=True
                )
                self._data = self._default_response()
                self._init_gmc()
            sleep(self._sleep_time)

    def _find_usb_device(self):
        logger.debug('Using pyudev to find GMC tty device')
        context = Context()
        for devname in iglob('/dev/ttyUSB*'):
            device = Devices.from_device_file(context, devname)
            if device.properties['ID_BUS'] != 'usb':
                continue
            k = (
                device.properties['ID_VENDOR_ID'],
                device.properties['ID_MODEL_ID'],
                device.properties['ID_REVISION']
            )
            if k in self._gmc_vendor_model_revision:
                logger.debug('Found GMC-500+ at: %s', devname)
                return devname
        return None

    def __del__(self):
        logger.info('Closing GMC device')
        self._gmc.close_device()
