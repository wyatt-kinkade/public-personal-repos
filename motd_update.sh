#!/bin/bash

#Run Cronjob regularly
HOSTNAME=`uname -n`

#Alter/Extrapolate this as needed, adjust that which is echoed into MOTD accordingly
ROOT=`df -Ph / | tail -n 1 | awk '{print $4}' | tr -d '\n'`
#HOME=`df -Ph /home | tail -n 1 | awk '{print $4}' | tr -d '\n'`

#First Adds Memory in Use, Second Adds Total Memory
MEMORY1=`free -t -m | grep "Mem" | awk '{print $3" MB";}'`
MEMORY2=`free -t -m | grep "Mem" | awk '{print $2" MB";}'`

#Process Count
PSC=`ps -Afl | wc -l`

#Service check
#Use First in CentOS7, use Latter in Debian, Arch, Ubuntu or CentOS8
NETMANSTAT=`systemctl status network | grep Active: | awk '{$1=$1};1'`
#NETMANSTAT=`systemctl status NetworkManager | grep Active | awk '{$1=$1};1'`
SSHSTAT=`systemctl status sshd | grep Active: | awk '{$1=$1};1'`
#I usually run xrdp on desktops because it's handy, there's issues, sure but I prefer it to, say, x11 forwarding
#XRDPSTAT=`systemctl status xrdp | grep Active | awk '{$1=$1};1'`

#Battery Check, Use if Laptop
#BATTLEVEL=`upower -i /org/freedesktop/UPower/devices/battery_BAT0 | grep capacity | cut -d ' ' -f 17`

# time of day
HOUR=$(date +"%H")
if [ $HOUR -lt 12  -a $HOUR -ge 0 ]
then    TIME="Morning"
elif [ $HOUR -lt 17 -a $HOUR -ge 12 ]
then    TIME="Afternoon"
else
    TIME="Evening"
fi

#System uptime
uptime=`cat /proc/uptime | cut -f1 -d.`
upDays=$((uptime/60/60/24))
upHours=$((uptime/60/60%24))
upMins=$((uptime/60%60))
upSecs=$((uptime%60))

#System load
LOAD1=`cat /proc/loadavg | awk {'print $1'}`
LOAD5=`cat /proc/loadavg | awk {'print $2'}`
LOAD15=`cat /proc/loadavg | awk {'print $3'}`

echo "

Good $TIME
it is `date`

`curl -s wttr.in/?u0`

===========================================================================
 - Hostname............: $HOSTNAME
 - Release.............: `grep PRETTY_NAME /etc/os-release | sed 's/PRETTY_NAME=//g' | sed 's/"//g'`
 - Users...............: Currently `users | wc -w` user(s) logged on
===========================================================================
 - CPU usage...........: $LOAD1, $LOAD5, $LOAD15 (1, 5, 15 min)
 - Memory used.........: $MEMORY1 / $MEMORY2
 - Swap in use.........: `free -m | tail -n 1 | awk '{print $3}'` MB
 - Processes...........: $PSC running
 - System uptime.......: $upDays days $upHours hours $upMins minutes $upSecs seconds
 - Disk space ROOT.....: $ROOT remaining
 - Networking Status...: $NETMANSTAT
 - SSH Status..........: $SSHSTAT
===========================================================================
" > /etc/motd
