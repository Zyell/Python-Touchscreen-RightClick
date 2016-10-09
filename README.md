Python Touchscreen Right Click
======================

This project implements right click functionality using a touchscreen on an Ubuntu system using the [Python evdev](https://github.com/gvalkov/python-evdev) library.  Because of unity's deep integration with multitouch gestures, it disallows many other systems from implementing basic gestures that (IMHO) are missing from the default multitouch gestures.  This script will not override unity's gestures, but fill in some missing ones, working alongside unity's multitouch system. (Also tested in gnome-shell given gnome-shell's incomplete implementation of right click touch)


Implemented gestures
-----------------------

Two gesture options have been implemented for right click:

* 1 finger longpress
* 2 finger tap

Setting up script
---------------------

Install requirements (python evdev).  Will work in either Python 2.7 or 3.4+ *tested.
This has been tested on Ubuntu 14.04, 15.04, & 16.04 with an ELAN/Atmel touchscreen on Lenovo Yoga 2 pro, and Surface Pro 2.

To modify the delay for your right click, open the script in a text editor and modify the self.click_delay variable, the default is 1.5 seconds.

In order to launch the script at startup, the rc.local method may or may not work.  Using systemd, you can setup a service.  The service can be setup as follows to call a shell script:

The shell script should contain something like:
```
#!/bin/sh
python3 /(path to python script...)/Python_Touchscreen_RightClick.py
```

The service can be set up as follows:
```
[Unit]
Description=script to appropriately set right click via touch
Documentation=none

[Service]
Type=simple
ExecStart=/usr/local/bin/(sheel script from above...)

[Install]
WantedBy=multi-user.target
```

You can attempt to still use the rc.local method, mileage may vary...

Edit /etc/rc.local file to include launching this script.

```
cd /etc/dclick/
sudo python test.py
cd -
echo `date +%Y-%b-%d_%H:%M:%S` > /tmp/ran_rc_local

exit 0

```

Please note that in order to access the input device for the touchscreen, you will need sudo to run the scipt.
