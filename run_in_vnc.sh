#!/bin/bash

# Set the VNC display (change to match the session number)
export DISPLAY=:1

# Set any other necessary environment variables for X11 or VNC session
export XAUTHORITY=/root/.Xauthority

source /root/.bashrc

# Run the Python script
/root/my_uscis_env/bin/python /root/check_uscis_status/main.py >> /root/check_uscis_status/logfile.log 2>&1
