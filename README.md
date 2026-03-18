# CyberPower-UPS-tools
Some Linux tools to get status from a CyberPower UPS

## status_from_pwrstatd.py
Pulls status from the CyberPower PowerPanel daemon, pwrstatd, which
polls CyberPower UPSes via USB and provides status information to
clients (like this one) via a Unix socket.

## status_from_usb.py
Pulls status directly from a CyberPower UPS via a USB connection. This
program must be used without the CyberPower PowerPanel daemon, pwrstatd,
because it will "fight" with it for access to the UPS via USB and create
a comms loss for pwrstatd.

