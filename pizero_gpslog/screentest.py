#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
from importlib import import_module
import time
from datetime import datetime
from pizero_gpslog.version import VERSION

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - %(name)s.%(funcName)s() ] %(message)s")


try:
    logging.info("epd2in13bc Demo")
    mod = import_module('pizero_gpslog.displays.epd2in13bc')
    cls = getattr(mod, 'EPD2in13bc')
    epd = cls()
    epd.set_line(0, f'pizero-gpslog v{VERSION}')
    epd.set_line(1, '')
    epd.set_line(2, '012345678901234567890')
    epd.set_line(3, '012345678901234567890')
    epd.set_line(4, '012345678901234567890')
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    for _ in range(0, 10):
        epd.set_line(1, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        start = time.time()
        logging.info("display")
        epd.update_display()
        logging.info("display done; ran in %s seconds", time.time() - start)
        time.sleep(5)
    logging.info('DONE.')
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    del epd
    exit()
