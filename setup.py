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

from setuptools import setup, find_packages
from pizero_gpslog.version import VERSION, PROJECT_URL

with open('README.rst') as file:
    long_description = file.read()

requires = [
    'gpiozero',
    'gpxpy',
    'pint'
]

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: No Input/Output (Daemon)',
    'Intended Audience :: End Users/Desktop',
    'Natural Language :: English',
    'Operating System :: POSIX :: Linux',
    'Topic :: Other/Nonlisted Topic',
    'Topic :: System :: Logging',
    'Topic :: Utilities',
    'License :: OSI Approved :: GNU Affero General Public License '
    'v3 or later (AGPLv3+)',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]

setup(
    name='pizero-gpslog',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    url=PROJECT_URL,
    description='Raspberry Pi Zero gpsd logger with status LEDs.',
    long_description=long_description,
    install_requires=requires,
    entry_points="""
    [console_scripts]
    pizero-gpslog = pizero_gpslog.runner:main
    pizero-gpslog-install = pizero_gpslog.installer:main
    pizero-gpslog-convert = pizero_gpslog.converter:main
    """,
    keywords="raspberry pi rpi gps log logger gpsd",
    classifiers=classifiers
)
