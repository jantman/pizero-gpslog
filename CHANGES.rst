Changelog
=========

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
