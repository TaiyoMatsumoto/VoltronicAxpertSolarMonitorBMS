#!/bin/bash -e

if [ ! -f /home/pi/axpert.json ]; then
        touch /home/pi/axpert.json
        chmod 644 /home/pi/axpert.json
        chown pi:pi /home/pi/axpert.json
fi

if [ -s /home/pi/axpert.json ]; then
        timeout 15s /home/pi/axpert.json_send.py
        rm -f /home/pi/axpert.json
        touch /home/pi/axpert.json
        chmod 644 /home/pi/axpert.json
        chown pi:pi /home/pi/axpert.json
fi
