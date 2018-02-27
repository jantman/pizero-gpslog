pizero-gpslog
=============

Raspberry Pi Zero gpsd logger with status LEDs.

Introduction and Goals
----------------------

This is a trivial (and not really "supported") project of mine to couple a Raspberry Pi Zero with a USB GPS receiver and a battery pack to GPS track my hikes. The hardware decision was mainly based on what I had lying around: a Raspberry Pi Zero, a 10,000mAh external battery pack for my cell phone, and a USB GPS (well, I thought I had one, and got far enough into the project when I decided it was missing for good that I bought another).

The goal is to package all of this together into a "small" (but not necessarily lightweight, based on the components) package that I can put in the outside pocket of my hiking pack, and record an accurate and detailed GPS track of my hikes.

I'll be using `gpsd <http://www.catb.org/gpsd/>`_ to interact with the GPS itself, as it's very mature and stable software, exposes a simple JSON-based socket interface, and also has decent Python bindings. There's no reason for a logger to have to worry about the nuances of GPS communication itself.

The intended feature set is:

* Read GPS data from gpsd and cache it, possibly averaging the speed readings.
* Write the most recent GPS data to disk (flash memory) at a user-defined interval. Time flushes to minimize power usage.
* Maintain status LEDs for quick visual status check.
* Make daemon notifications to systemd as appropriate.

Requirements
------------

* Raspberry Pi (tested with `Pi Zero <https://www.raspberrypi.org/products/raspberry-pi-zero/>`_ 1.3)
* Raspbian Stretch with Python3 (see installation instructions below)
* `gpsd compatible <http://www.catb.org/gpsd/hardware.html>`_ GPS (I use a `GlobalSat BU-353-S4 USB <https://www.amazon.com/gp/product/B008200LHW/>`_; the gpsd folks say some pretty awful things about it, but we'll see...)
* Two GPIO-connected LEDs on the RPi, ideally different colors (see below).
* Some sort of power source for the Pi. I use a standard adapter when testing and a 10000mAh USB battery pack in the field (specifically the `Anker PowerCore Speed 10000 QA <https://www.amazon.com/gp/product/B01JIYWUBA/>`_).

Installation
------------

Hardware
++++++++

TBD.

Software
++++++++

1. Setup Raspbian.
2. ``apt-get install build-essential libsystemd-journal-dev libsystemd-daemon-dev libsystemd-dev python35``
3. Something.

Configuration
-------------

pizero-gpslog's entire configuration is provided via environment variables. There are NO command-line switches.

* ``LOG_LEVEL`` - Defaults to "WARNING"; other accepted values are "INFO" and "DEBUG". All logging is to STDOUT.
* ``USE_SYSTEMD_DAEMON`` - Set to "false" to disable systemd daemon notifications.
* ``LED_PIN_RED`` - Specifies the GPIO pin number used for the primary ("red") LED. Leave unset if running on non-RPi hardware.
* ``LED_PIN_GREEN`` - Specifies the GPIO pin number used for the secondary ("green") LED. Leave unset if running on non-RPi hardware.

Running
-------

Configure as described above, then run ``pizero-gpslog``.

Testing
-------

There currently aren't any code tests. But there are some scripts and tox-based helpers to aid with manual testing.

* ``pizero_gpslog/tests/data/runfake.sh`` - Runs `gpsfake <http://www.catb.org/gpsd/gpsfake.html>`_ (provided by gpsd) with sample data. Takes optional arguments for ``--nofix`` (data with no GPS fix) or ``--stillfix`` (fix but not moving).
