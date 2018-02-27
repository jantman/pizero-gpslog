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
import sys
import logging
import argparse
from distutils.spawn import find_executable
from textwrap import dedent
from subprocess import run

FORMAT = "[%(asctime)s %(levelname)s] %(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT)
logger = logging.getLogger()


class Installer(object):

    def __init__(self, args):
        self._systemctl = find_executable('systemctl')
        if self._systemctl is None:
            raise SystemExit(
                'ERROR: Cannot find "systemctl" executable. This installer '
                'can only be used on systems with systemd running.'
            )
        self.args = args

    def run(self):
        if self.args.dry_run:
            print(self.unit_file)
            return
        unitpath = '/etc/systemd/system/pizero-gpslog.service'
        if os.path.exists(unitpath):
            logger.warning(
                'Unit file at %s already exists; replacing', unitpath
            )
        logger.info('Writing systemd unit file:\n%s', self.unit_file)
        with open(unitpath, 'w') as fh:
            fh.write(self.unit_file)
        logger.info('systemd unit file written to: %s', unitpath)
        logger.info('Running "%s daemon-reload"' % self._systemctl)
        run([self._systemctl, 'daemon-reload'], check=True)
        logger.info('Running "%s enable pizero-gpslog"' % self._systemctl)
        run([self._systemctl, 'enable', 'pizero-gpslog'], check=True)
        logger.info('Installation complete. Service enabled.')

    @property
    def unit_file(self):
        return dedent("""
        [Unit]
        Description=pizero-gpslog service
        Documentation=https://github.com/jantman/pizero-gpslog
        Requires=gpsd.service
        After=gpsd.service
        AssertArchitecture=arm
        [Service]
        Type=simple
        ExecStart={python} {fpath}
        WorkingDirectory={dirpath}
        User={user}
        Group={group}
        Environment=OUT_DIR={dirpath} FLUSH_FILE={flush} GPS_INTERVAL_SEC={intvl} LOG_LEVEL={log} {red} {green}
        RestartSec=10
        Restart=always
        [Install]
        WantedBy=default.target
        """.format(
            fpath=find_executable('pizero-gpslog'),
            python=sys.executable,
            user=self.args.user,
            group=self.args.group,
            dirpath=self.args.OUT_DIR,
            flush=('false' if self.args.FLUSH_FILE else 'true'),
            intvl=self.args.GPS_INTERVAL_SEC,
            log=self.args.LOG_LEVEL,
            red=(
                'LED_PIN_RED=%s' % self.args.LED_PIN_RED
                if self.args.LED_PIN_RED is not None else ''
            ),
            green=(
                'LED_PIN_GREEN=%s' % self.args.LED_PIN_GREEN
                if self.args.LED_PIN_GREEN is not None else ''
            )
        )).strip()


def parse_args(argv):
    """parse arguments/options"""
    p = argparse.ArgumentParser(description='pizero-gpslog installer - sets up '
                                            'systemd service')
    p.add_argument('-D', '--dry-run', dest='dry_run', action='store_true',
                   default=False,
                   help='Print generated systemd unit file to STDOUT and exit')
    p.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                   default=False,
                   help='enable debug-level output.')
    p.add_argument(
        '-l', '--log-level', dest='LOG_LEVEL', action='store', type=str,
        choices=['WARNING', 'INFO', 'DEBUG'], default='WARNING',
        help='Log level to run daemon with; defaults to WARNING'
    )
    p.add_argument(
        '-r', '--red-pin', dest='LED_PIN_RED', action='store', type=int,
        default=None,
        help='GPIO Pin number for Red (primary) LED; omit to use fake '
             '(log to STDOUT) LEDs. Defaults to None (omitted).'
    )
    p.add_argument(
        '-g', '--green-pin', dest='LED_PIN_GREEN', action='store', type=int,
        default=None,
        help='GPIO Pin number for Green (secondary) LED; omit to use fake '
             '(log to STDOUT) LEDs. Defaults to None (omitted).'
    )
    p.add_argument(
        '-i', '--interval', dest='GPS_INTERVAL_SEC', action='store', type=int,
        default=5,
        help='Interval in seconds to poll gpsd and write to file. Defaults '
             'to 5.'
    )
    p.add_argument(
        '--no-flush', dest='FLUSH_FILE', action='store_true', default=False,
        help='Do not explicitly flush file after writing each record.'
    )
    cwd = os.getcwd()
    p.add_argument(
        '-d', '--out-dir', dest='OUT_DIR', action='store', type=str,
        default=cwd,
        help='Directory to write output files in. Default is your current '
             'working directory (%s)' % cwd
    )
    user = os.environ.get('SUDO_UID', '%d' % os.geteuid())
    p.add_argument(
        '-u', '--user', dest='user', action='store', type=str, default=user,
        help='User to run daemon as (default: %s)' % user
    )
    group = os.environ.get('SUDO_GID', '%d' % os.getegid())
    p.add_argument(
        '-G', '--group', dest='group', action='store', type=str, default=group,
        help='Group to run daemon as (default: %s)' % group
    )
    args = p.parse_args(argv)
    return args


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
    args = parse_args(sys.argv[1:])

    # set logging level
    if args.verbose:
        set_log_debug()

    Installer(args).run()


if __name__ == "__main__":
    main()
