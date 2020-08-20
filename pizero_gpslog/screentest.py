#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
import logging
from importlib import import_module
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pkg_resources import resource_filename
from pizero_gpslog.version import VERSION

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s %(filename)s:%(lineno)s - %(name)s.%(funcName)s() ] %(message)s")


def drawtime():
    logging.info('Begin drawing time')
    HBlackimage = Image.new('1', (epd.height, epd.width), 255)  # 298*126
    drawblack = ImageDraw.Draw(HBlackimage)
    t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    drawblack.text((10, 0), f'pizero-gpslog v{VERSION}', font=font20, fill=0)
    drawblack.text((10, 20), t, font=font20, fill=0)
    drawblack.text((10, 40), '012345678901234567', font=font20, fill=0)
    drawblack.text((10, 60), '012345678901234567', font=font20, fill=0)
    drawblack.text((10, 80), '012345678901234567', font=font20, fill=0)
    logging.info('End drawing time')
    return HBlackimage


try:
    logging.info("epd2in13bc Demo")
    mod = import_module('pizero_gpslog.epd2in13bc')
    cls = getattr(mod, 'EPD')
    epd = cls()
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    # Drawing on the image
    logging.info("Drawing")
    font_file = resource_filename('pizero_gpslog', 'DejaVuSansCondensed.ttf')
    font20 = ImageFont.truetype(font_file, 20)
    # Drawing on the Horizontal image
    logging.info("1.Drawing on the Horizontal image...")
    for _ in range(0, 10):
        start = time.time()
        drawblack = drawtime()
        logging.info("displayblack")
        epd.displayblack(epd.getbuffer(drawblack))
        logging.info("displayblack done; ran in %s seconds", time.time() - start)
        time.sleep(5)
    logging.info("Goto Sleep...")
    epd.sleep()
    logging.info('DONE.')
except IOError as e:
    logging.info(e)
except KeyboardInterrupt:
    logging.info("ctrl + c:")
    del epd
    exit()
