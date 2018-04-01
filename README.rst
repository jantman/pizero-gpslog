pizero-gpslog
=============

.. image:: http://www.repostatus.org/badges/latest/active.svg
   :alt: Project Status: Active – The project has reached a stable, usable state and is being actively developed.
   :target: http://www.repostatus.org/#active

Raspberry Pi Zero gpsd logger with status LEDs.

.. image:: http://blog.jasonantman.com/GFX/pizero_gpslogger_1_sm.jpg
   alt: Photograph of finished hardware next to playing card deck for size comparison
   target: http://blog.jasonantman.com/GFX/pizero_gpslogger_1.jpg

A longer description of the motivation behind this and the specific hardware that I used is available on my blog: `DIY Raspberry Pi Zero GPS Track Logger <http://blog.jasonantman.com/2018/03/diy-raspberry-pi-zero-gps-track-logger/>`_.

Introduction and Goals
----------------------

This is a trivial (and not really "supported") project of mine to couple a Raspberry Pi Zero with a USB GPS receiver and a battery pack to GPS track my hikes. The hardware decision was mainly based on what I had lying around: a Raspberry Pi Zero, a 10,000mAh external battery pack for my cell phone, and a USB GPS (well, I thought I had one, and got far enough into the project when I decided it was missing for good that I bought another).

The goal is to package all of this together into a "small" (but not necessarily lightweight, based on the components) package that I can put in the outside pocket of my hiking pack, and record an accurate and detailed GPS track of my hikes. It writes the most recent position data from gpsd to disk at a user-defined interval, flushes IO after each write (so that it's safe to just pull the power on the Pi), and uses two LEDs to indicate status while in the field. Data is written in gpsd's native format, but a conversion tool is provided.

This program relies on `gpsd <http://www.catb.org/gpsd/>`_ to interact with the GPS itself, as it's very mature and stable software, exposes a simple JSON-based socket interface, and also has decent Python bindings. There's no reason for a logger to have to worry about the nuances of GPS communication itself.

Requirements
------------

* Raspberry Pi (tested with `Pi Zero <https://www.raspberrypi.org/products/raspberry-pi-zero/>`_ 1.3) and a MicroSD card (I'm using an `8GB SanDisk Ultra Class 10 UHS-1 <https://www.amazon.com/gp/product/B00M55C0VU/>`_, which has enough space after the OS for 240 days of 5-second-interval data).
* Raspbian Stretch with Python3 (see installation instructions below)
* `gpsd compatible <http://www.catb.org/gpsd/hardware.html>`_ GPS (I use a `GlobalSat BU-353-S4 USB <https://www.amazon.com/gp/product/B008200LHW/>`_; the gpsd folks say some pretty awful things about it, but we'll see...)
* Two GPIO-connected LEDs on the RPi, ideally different colors (see below).
* Some sort of power source for the Pi. I use a standard adapter when testing and a 10000mAh USB battery pack in the field (specifically the `Anker PowerCore Speed 10000 QA <https://www.amazon.com/gp/product/B01JIYWUBA/>`_). That battery pack is extreme overkill, and powers the unit continuously for 42 hours, when logging at a 5-second interval.

Installation
------------

Software
++++++++

This assumes you're running on Linux...

1. Download the latest `Raspbian Stretch Lite <https://www.raspberrypi.org/downloads/raspbian/>`_ image. I'm using the "November 2017" version, released 2017-11-29, kernel 4.9.
2. Verify the checksum on the file and then unzip it.
3. Put the MicroSD card in your machine and write the image to it. As root, ``dd bs=4M if=2017-11-29-raspbian-stretch-lite.img of=/dev/sdX conv=fsync status=progress`` (where ``/dev/sdX`` is the device that the SD card showed up at).
4. Wait for the copy to finish and IO to the device to stop (run ``sync``).
5. *Optional:* If you're going to be using this on a network (i.e. for setup, troubleshooting, development, etc.) then this would be a good time to mount the Raspian partition on your computer and make some changes. See `this script from pi2graphite <https://github.com/jantman/pi2graphite/blob/master/setup_raspbian.sh>`_ for some tips.

  1. Copy your authorized_keys file over to ``/home/pi``.
  2. Touch the file at ``/boot/ssh`` on the Pi boot partition to enable SSH access.
  3. Set a hostname.
  4. If desired, configure WiFi (as well as downloading the packages for any required drivers onto the OS partition).
  5. When finished, unmount, ``sync`` and remove the SD card.

6. Put the SD card in your Pi and plug it in. If you're going to be connecting directly with a keyboard and monitor, do so. If you configured WiFi (or want to use a USB Ethernet adapter) and have everything setup correctly, it should eventually connect to your network. If you have issues with a USB Ethernet adapter, try letting the Pi boot up (give it 2-3 minutes) and *then* plug in the adapter.
7. Log in. The default user is named "pi" with a default password of "raspberry".
8. ``sudo apt-get update && sudo apt-get install haveged git python3-gpiozero python3-setuptools python3-pip gpsd``
9. Run sudo `raspi-config <https://github.com/RPi-Distro/raspi-config>`_ to set things like the locale and timezone. Personally, I usually leave the ``pi`` user password at its default for devices that will never be on an untrusted network.
10. In ``/home/pi``, run ``git clone https://github.com/jantman/pizero-gpslog.git && cd pizero-gpslog && sudo python3 setup.py develop && sudo pizero-gpslog-install``. The installer, ``pizero-gpslog-install``, templates out a systemd unit file, reloads systemd, and enables the unit. Environment variables to set for the service are taken from command line arguments.
11. If you're ready, ``sudo systemctl start pizero-gpslog`` to start it. Otherwise, it will start on the next boot.
12. Find out the USB vendor and product IDs for your GPS. My BU-353S4 uses a Prolific PL2303 serial chipset (vendor 067b product 2303) which is disabled by default in the Debian gpsd udev rules. Look at ``/lib/udev/rules.d/60-gpsd.rules``. If your GPS is commented out like mine, uncomment it and save the file.

Hardware
++++++++

1. Add two LEDs to the Pi Zero. I prefer to solder a female right-angle header to the Pi, then put the LEDs on a male header so they can be removed. gpiozero, the library used for controlling the LEDs, has `pinout diagrams <https://gpiozero.readthedocs.io/en/stable/recipes.html#pin-numbering>`_ and information on the `wiring that the API expects <https://gpiozero.readthedocs.io/en/stable/api_output.html#gpiozero.LED>`_. The code this project uses expects the LEDs to be wired active-high (cathode to ground, anode to GPIO pin through a limiting resistor). I made up a small 8x20 header for my LEDs and (very sloppily) potted them in epoxy.
2. Test the LEDs.
3. Plug your GPS into the USB input on the RPi, via a "usb on the go" (USB OTG) cable. Then plug the Pi into a power source. Everything else should be automatic after the installation described below.

Configuration
-------------

pizero-gpslog's entire configuration is provided via environment variables. There are NO command-line switches.

* ``LOG_LEVEL`` - Defaults to "WARNING"; other accepted values are "INFO" and "DEBUG". All logging is to STDOUT.
* ``LED_PIN_RED`` - Integer. Specifies the GPIO pin number used for the primary ("red") LED. Leave unset if running on non-RPi hardware, in which case LED state will be logged to STDOUT. Note the number used here is the Broadcom GPIO pin number, not the physical board pin number.
* ``LED_PIN_GREEN`` - Integer. Specifies the GPIO pin number used for the secondary ("green") LED. Leave unset if running on non-RPi hardware, in which case LED state will be logged to STDOUT. Note the number used here is the Broadcom GPIO pin number, not the physical board pin number.
* ``GPS_INTERVAL_SEC`` - Integer. Interval to poll gps at, and write gps position. Defaults to every 5 seconds.
* ``FLUSH_FILE`` - String. If set to "false", do not explicitly flush output file after every write.
* ``OUT_DIR`` - Directory to write log files under. If not set, will use current working directory.

Running
-------

Configure as described above, then use the ``pizero-gpslog`` systemd service.

LED Outputs
+++++++++++

* Green Solid (at start) - connecting to gpsd. Green LED goes out when connected to gpsd and the output file is opened for writing.
* Red Solid - no active GPS (gpsd does not yet have an active gps, or no GPS is connected).
* Red 3 Fast Blinks (0.1 sec) - GPS is connected but does not yet have a fix.
* Red 2 Slow Blinks (0.5 sec) - GPS has a 2D-only fix; position data is being read.
* Red 1 Slow Blink (0.5s) - GPS has a 3D fix; position data is being read.
* Green Blink (0.25s) - Data point written to disk (and flushed, if flush not disabled).

Log Files
+++++++++

Log files will be written under the directory specified by the ``OUT_DIR`` environment variable, or the current working directory if that environment variable is not set. Log files will be written under that directory, named according to the time and date when the program started (``%Y-%m-%d_%H-%M-%S`` format).

Each line of the output file is a single raw gpsd response to the ``?POLL`` command. While this program also decodes the responses, it doesn't make sense for us to invent our own data structure for something that already has one. Each line in the output file should be valid JSON matching the `gpsd JSON ?POLL response schema <http://www.catb.org/gpsd/gpsd_json.html>`_, deserialized and reserialized to ensure that it does not contain any linebreaks.

Getting the Data
++++++++++++++++

At the moment, when I'm home from a hike and the Pi is powered down, I just pull the SD card and copy the data to my computer, then delete the data file(s) from the SD card and put it back. It would certainly be easy to automate this with a Pi Zero W or an Ethernet or WiFi connection, but it's not worth it for me for this project. If you're interested, I have some scripts and instructions that might help as part of my `pi2graphite <https://github.com/jantman/pi2graphite>`_ project.

Using the Data
--------------

The log files output by ``pizero-gpslog`` are in the `gpsd JSON ?POLL response format <http://www.catb.org/gpsd/gpsd_json.html>`_, one response per line (some responses may be empty). In order to make the output useful, this package also includes the ``pizero-gpslog-convert`` command line tool which can convert a specified JSON file to one of a variety of more-useful formats. While `gpsbabel <https://www.gpsbabel.org/>`_ is the standard for GPS data format conversion, it doesn't support the gpsd POLL response format. This utility is provided as a means of converting to some common GPS data formats. If you need other formats, please convert to one of these and then to gpsbabel.

* ``pizero-gpslog-convert YYYY-MM-DD_HH:MM:SS.json`` - convert ``YYYY-MM-DD_HH:MM:SS.json`` to GPX and write at ``YYYY-MM-DD_HH:MM:SS.gpx``
* ``pizero-gpslog-convert --stats YYYY-MM-DD_HH:MM:SS.json`` - same as above, but also print some stats to STDERR

It's up to you how to use the data, but there are a number of handy online tools that work with GPX files, including:

* `gpsvisualizer.com <http://www.gpsvisualizer.com/>`_ that has multiple output formats including `elevation and speed profiles <http://www.gpsvisualizer.com/profile_input>`_ (and other profiles including slope, climb rate, pace, etc.), plotting the track `on Google Maps <http://www.gpsvisualizer.com/map_input?form=google>`_ (including with colorization by speed, elevation, slope, climb rate, pace, etc.), converting `to Google Earth KML <http://www.gpsvisualizer.com/map_input?form=googleearth>`_, etc. Plotting can also use sources other than Google Maps, such as OpenStreetMap, ThunderForest, OpenTopoMap, USGS, USFS, etc. (and there's some `explanation <http://www.gpsvisualizer.com/examples/google_custom_backgrounds.html>`_ about how this is done).
* `utrack.crempa.net <http://utrack.crempa.net/>`_ Takes a GPX file and generates a HTML page "report" giving a map overlay (with optional elevation colorization) as well as elevation and speed profiles (against both time and distance), some statistics, a distance vs time profile, and the option to download that report as a PDF.
* `sunearthtools.com <https://www.sunearthtools.com/tools/gps-view.php>`_ has a simple tool (admittedly with a poor UI) that plots GPX data on Google maps along with a separate speed and elevation profile (by distance).
* `mygpsfiles <http://www.mygpsfiles.com/en/>`_ Is a web-based app with a native-looking tiled UI that can plot tracks on Google Maps (Satellite or Map + Topo) as well as displaying per-point statistics (distance, time, elevation, speed, pace) and a configurable profile of elevation, speed, distance, pace, etc. As far as I can tell, all units are metric.

Testing
-------

There currently aren't any code tests. But there are some scripts and tox-based helpers to aid with manual testing.

* ``pizero_gpslog/tests/data/runfake.sh`` - Runs `gpsfake <http://www.catb.org/gpsd/gpsfake.html>`_ (provided by gpsd) with sample data. Takes optional arguments for ``--nofix`` (data with no GPS fix) or ``--stillfix`` (fix but not moving).

Acknowledgements
----------------

First, many thanks to the developers of gpsd, who have put forth the massive effort to make a script like this relatively trivial.

Second, thanks to `Martijn Braam <https://github.com/MartijnBraam>`_, developer of the MIT-licensed `gpsd-py3 <https://github.com/MartijnBraam/gpsd-py3>`_ package. A modified version of that package makes up the ``gpsd.py`` module.
