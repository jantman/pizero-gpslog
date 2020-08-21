from abc import ABC, abstractmethod
import logging
from PIL import ImageFont
from pkg_resources import resource_filename

logger = logging.getLogger(__name__)


class BaseDisplay(ABC):
    """
    Base class for all displays.
    """

    def __init__(self):
        """
        Initialize the display. This should do everything that's required to
        get the display ready to call :py:meth:`~.display`, including clearing
        the display if required.
        """
        self._lines = ['' for x in range(0, self.height_lines)]

    @staticmethod
    def font(size_pts: int = 20) -> ImageFont.FreeTypeFont:
        f = resource_filename('pizero_gpslog', 'DejaVuSansMono.ttf')
        return ImageFont.truetype(f, size_pts)

    @property
    @abstractmethod
    def width_chars(self) -> int:
        """
        Return the width of the display in characters.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def height_lines(self) -> int:
        """
        Return the height of the display in lines.
        """
        raise NotImplementedError()

    def set_line(self, line_num: int, content: str):
        """
        Set the zero-indexed display line to the given string content.
        You must still call :py:meth:`~.display` after calling this.
        Content will be truncated at :py:prop:`~.width_chars` characters.
        """
        if line_num > len(self._lines):
            raise RuntimeError(
                f'ERORR: Display only has {len(self._lines)} lines.'
            )
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
