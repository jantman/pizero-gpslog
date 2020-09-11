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

from abc import ABC, abstractmethod
import logging
from PIL import ImageFont
from pkg_resources import resource_filename
from typing import ClassVar, List

logger = logging.getLogger(__name__)


class BaseDisplay(ABC):
    """
    Base class for all displays.
    """

    #: width of the display in characters
    width_chars: ClassVar[int] = 0

    #: height of the display in lines
    height_lines: ClassVar[int] = 0

    #: the minimum number of seconds between refreshes of the display
    min_refresh_seconds: ClassVar[int] = 0

    def __init__(self):
        """
        Initialize the display. This should do everything that's required to
        get the display ready to call :py:meth:`~.display`, including clearing
        the display if required.
        """
        self._lines: List[str] = ['' for x in range(0, 5)]

    @staticmethod
    def font(size_pts: int = 20) -> ImageFont.FreeTypeFont:
        f = resource_filename('pizero_gpslog', 'DejaVuSansMono.ttf')
        return ImageFont.truetype(f, size_pts)

    def set_line(self, line_num: int, content: str):
        """
        Set the zero-indexed display line to the given string content.
        You must still call :py:meth:`~.display` after calling this.
        Content will be truncated at :py:prop:`~.width_chars` characters.
        """
        if line_num > len(self._lines):
            logger.error(
                'Display only has %d lines.', len(self._lines)
            )
            return
        if len(content) > self.width_chars:
            logger.info('Truncating content "%s"', content)
            content = content[:self.width_chars]
        self._lines[line_num] = content

    @abstractmethod
    def update_display(self):
        """
        Write ``self._lines`` to the display.
        """
        raise NotImplementedError()

    @abstractmethod
    def clear(self):
        """
        Clear the display.
        """
        raise NotImplementedError()

    @abstractmethod
    def __del__(self):
        """
        Do everything that is needed to cleanup the display.
        """
        raise NotImplementedError()
