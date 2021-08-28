#!/bin/bash
ping -c1 -i15 -W10 rpi4
if [ $? -eq 0 ]; then
          echo 0 > /run/ping.fail
       else
          cnt=$(cat /run/ping.fail)
          cnt=$((cnt + 1))
          echo $cnt > /run/ping.fail
fi

if [ $(cat "/run/ping.fail") -eq 2 ] ; then
       echo -n "ON" > /home/pi/switch.json
fi

