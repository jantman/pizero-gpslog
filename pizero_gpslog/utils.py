from threading import Lock
from copy import copy
import logging
from enum import Enum


class ThreadSafeValue:

    def __init__(self, initial=''):
        self._value = initial
        self._lock = Lock()

    def set(self, val):
        self._lock.acquire()
        try:
            self._value = copy(val)
        finally:
            self._lock.release()

    def get(self):
        self._lock.acquire()
        try:
            result = copy(self._value)
        finally:
            self._lock.release()
        return result


class FixType(Enum):

    NO_GPS = 0
    NO_FIX = 1
    FIX_2D = 2
    FIX_3D = 3


def set_log_info(log: logging.Logger):
    """
    set logger level to INFO via :py:func:`~.set_log_level_format`.
    """
    set_log_level_format(
        log, logging.INFO,
        '%(asctime)s %(levelname)s:%(name)s:%(message)s'
    )


def set_log_debug(log: logging.Logger):
    """
    set logger level to DEBUG, and debug-level output format,
    via :py:func:`~.set_log_level_format`.
    """
    set_log_level_format(
        log,
        logging.DEBUG,
        "%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - "
        "%(name)s.%(funcName)s() ] %(message)s"
    )


def set_log_level_format(log: logging.Logger, level: int, format: str):
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
    log.handlers[0].setFormatter(formatter)
    log.setLevel(level)
