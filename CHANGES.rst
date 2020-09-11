Changelog
=========

1.1.0 (2020-09-11)
------------------

* Fix ``pizero_gpslog.extradata.gq_gmc500plus:GqGMC500plus`` to handle disconnect/reconnect of USB device.
* Add support for the Adafruit 4567 OLED display.
* Major refactor of display support; instead of taking a list of lines, ``BaseDisplay`` subclasses now take separate values for each piece of data that can be displayed and are free to format them however works best for that particular display.

1.0.0 (2020-08-25)
------------------

* Update README for current Raspberry Pi OS install instructions
* Add ``setup_pi.sh`` setup script, based on the one at https://github.com/jantman/pi2graphite/blob/master/setup_raspbian.sh
* Add development documentation
* Add support for displays. Begin with the Waveshare 2.13-inch e-Ink Display Hat B; allow users to implement their own display driver classes.
* Implement support for extra data providers.

0.1.4 (2020-07-23)
------------------

* Merge `PR #5 <https://github.com/jantman/pizero-gpslog/pull/5>`__ to have converter ignore corrupt lines. Thanks to `@markus-k <https://github.com/markus-k>`__.
* Use TravisCI for releases; document release process
* PEP8 fixes

0.1.3 (2019-12-01)
------------------

* Refactor ``pizero-gpslog-convert`` to allow use from other Python programs.

0.1.2 (2018-11-03)
------------------

* ``pizero-gpslog-convert`` - Handle logs that are missing altitude (``alt``) from TPV
  reports by falling back to GST altitude, the previous altitude measurement, or 0.0 (in that order).

0.1.1 (2018-04-08)
------------------

* Log version at startup
* RPi RTC fix - don't start writing output until we have a fix; use GPS time instead of system time for filename
* Numerous bugfixes in ``converter.py``
* README fixes

0.1.0 (2018-03-06)
------------------

* Initial Release
