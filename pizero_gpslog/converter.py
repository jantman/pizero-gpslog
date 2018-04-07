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

import sys
import argparse
import json

import pint
from gpxpy.gpx import GPX, GPXTrack, GPXTrackSegment, GPXTrackPoint
from gpxpy.gpxfield import TIME_TYPE

from pizero_gpslog.version import VERSION


class GpxConverter(object):

    def __init__(self, input_fpath, output_fpath, imperial=False):
        self._in_fpath = input_fpath
        self._out_fpath = output_fpath
        self._imperial = imperial
        self._ureg = pint.UnitRegistry()

    def convert(self, stats=True):
        logs = []
        with open(self._in_fpath, 'r') as fh:
            lineno = 0
            for line in fh.readlines():
                lineno += 1
                line = line.strip()
                if len(line) == 0:
                    continue
                try:
                    j = json.loads(line)
                except json.decoder.JSONDecodeError as ex:
                    sys.stderr.write(
                        'Unable to decode JSON on line %s; skipping. '
                        '(ERROR: %s)\n' % (
                            lineno, ex
                        )
                    )
                    continue
                if 'tpv' not in j:
                    continue
                if j['tpv'][0].get('mode', 0) < 2:
                    continue
                j['lineno'] = lineno
                logs.append(j)
        gpx = self._gpx_for_logs(logs)
        with open(self._out_fpath, 'w') as fh:
            fh.write(gpx.to_xml())
        if not stats:
            return
        stats = 'GPX file written to: %s\n' % self._out_fpath
        stats += 'Track Start: %s UTC\n' % gpx.get_time_bounds().start_time
        stats += 'Track End: %s UTC\n' % gpx.get_time_bounds().end_time
        stats += 'Track Duration: %s\n' % seconds(gpx.get_duration())
        stats += '%d points in track\n' % gpx.get_points_no()
        cloned_gpx = gpx.clone()
        cloned_gpx.reduce_points(2000, min_distance=10)
        cloned_gpx.smooth(vertical=True, horizontal=True)
        cloned_gpx.smooth(vertical=True, horizontal=False)
        moving_time, stopped_time, moving_distance, stopped_distance, \
            max_speed_ms = cloned_gpx.get_moving_data()
        stats += 'Moving time: %s\n' % seconds(moving_time)
        stats += 'Stopped time: %s\n' % seconds(stopped_time)
        stats += 'Max Speed: %s\n' % self._ms_mph(max_speed_ms)
        stats += '2D (Horizontal) distance: %s\n' % self._m_ftmi(
            gpx.length_2d()
        )
        ud = gpx.get_uphill_downhill()
        stats += 'Total elevation increase: %s\n' % self._m_ft(ud.uphill)
        stats += 'Total elevation decrease: %s\n' % self._m_ft(ud.downhill)
        elev = gpx.get_elevation_extremes()
        stats += 'Minimum elevation: %s\n' % self._m_ft(elev.minimum)
        stats += 'Maximum elevation: %s\n' % self._m_ft(elev.maximum)
        sys.stderr.write(stats)

    def _gpx_for_logs(self, logs):
        g = GPX()
        track = GPXTrack()
        track.source = 'pizero-gpslog %s' % VERSION
        g.tracks.append(track)
        seg = GPXTrackSegment()
        track.segments.append(seg)

        for item in logs:
            try:
                tpv = item['tpv'][0]
                sky = item['sky'][0]
                p = GPXTrackPoint(
                    latitude=tpv['lat'],
                    longitude=tpv['lon'],
                    elevation=tpv['alt'],
                    time=TIME_TYPE.from_string(tpv['time']),
                    speed=tpv['speed'],
                    horizontal_dilution=sky.get('hdop', None),
                    vertical_dilution=sky.get('vdop', None),
                    position_dilution=sky.get('pdop', None)
                )
                if tpv['mode'] == 2:
                    p.type_of_gpx_fix = '2d'
                elif tpv['mode'] == 3:
                    p.type_of_gpx_fix = '3d'
                if 'satellites' in sky:
                    p.satellites = len(sky['satellites'])
                seg.points.append(p)
            except Exception:
                sys.stderr.write(
                    'Exception loading line %d:\n' % item['lineno']
                )
                raise
        return g

    def _ms_mph(self, n):
        if not self._imperial:
            return '%.4f m/s' % n
        val = n * self._ureg.meter / self._ureg.second
        return '%.4f MPH' % val.to(self._ureg.mile / self._ureg.hour).magnitude

    def _m_ftmi(self, n):
        if not self._imperial:
            return '%.4f m' % n
        val = n * self._ureg.meter
        val = val.to(self._ureg.mile)
        return '%.4f Mi' % val.magnitude

    def _m_ft(self, n):
        if not self._imperial:
            return '%.4f m' % n
        val = n * self._ureg.meter
        val = val.to(self._ureg.foot)
        return '%.4f ft' % val.magnitude


def seconds(s):
    res = []
    if s > 3600:
        h, s = divmod(s, 3600)
        res.append('%dh' % h)
    if s > 60:
        m, s = divmod(s, 60)
        res.append('%dm' % m)
    res.append('%ds' % s)
    return ' '.join(res)


def main(argv=sys.argv[1:]):
    args = parse_args(argv)
    if args.output is None:
        if '.' not in args.JSON_FILE:
            args.output = args.JSON_FILE + '.' + args.format
        else:
            args.output = args.JSON_FILE.rsplit('.', 1)[0] + '.' + args.format
    GpxConverter(args.JSON_FILE, args.output, imperial=args.imperial).convert(
        stats=args.stats
    )


def parse_args(argv):
    """parse arguments/options"""
    p = argparse.ArgumentParser(
        description='Convert pizero-gpslog (gpsd POLL format) output files to '
                    'common GPS formats.'
    )
    p.add_argument('-f', '--format', dest='format', action='store', type=str,
                   choices=['gpx'], default='gpx',
                   help='destination format (default: gpx)')
    p.add_argument('-o', '--output', dest='output', action='store', type=str,
                   default=None,
                   help='Output file path. By default, will be the input '
                        'file path with the file extension replaced with the '
                        'correct one for the output format.')
    p.add_argument('-S', '--no-stats', dest='stats', action='store_false',
                   default=True,
                   help='do not print stats to STDERR'
    )
    p.add_argument('-i', '--imperial', dest='imperial', action='store_true',
                   default=False, help='output stats in imperial units')
    p.add_argument('JSON_FILE', action='store', type=str,
                   help='Input file to convert')
    args = p.parse_args(argv)
    return args


if __name__ == '__main__':
    main(sys.argv[1:])
