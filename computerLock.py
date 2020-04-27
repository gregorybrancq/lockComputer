#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path
import subprocess
import sys
import time
import logging.config
from optparse import OptionParser
from datetime import datetime, timedelta

sys.path.append('/home/greg/Greg/work/env/pythonCommon')
from progDisEn import ProgEnDis
from basic import getScriptDir, getLogDir

##############################################
#              Line Parsing                  #
##############################################

parser = OptionParser()

parser.add_option(
    "--debug",
    action="store_true",
    dest="debug",
    default=False,
    help="Display all debug information."
)

parser.add_option(
    "-b",
    "--block",
    action="store_true",
    dest="block",
    default=False,
    help="Block keyboard and mouse."
)

parser.add_option(
    "-u",
    "--unblock",
    action="store_true",
    dest="unblock",
    default=False,
    help="Unblock keyboard and mouse."
)

parser.add_option(
    "-e",
    "--enable",
    action="store_true",
    dest="enable",
    default=False,
    help="Block and unblock keyboard and mouse depending time part."
)

parser.add_option(
    "-d",
    "--disable",
    action="store_true",
    dest="disable",
    default=False,
    help="Disable this program."
)

parser.add_option(
    "-i",
    "--info",
    action="store_true",
    dest="info",
    default=False,
    help="Give different information for this program."
)

(parsedArgs, args) = parser.parse_args()

##############################################


##############################################
# Global variables
##############################################

progName = "computerLock"

# directory
scriptDir = getScriptDir()
logDir = getLogDir()

# logging
# load config
logging.config.fileConfig(os.path.join(scriptDir, 'logging.conf'))
# disable logging
logging.disable(sys.maxsize)
# create logger
log = logging.getLogger(progName)

logFile = os.path.join(logDir, progName + "_"
                       + str(datetime.today().isoformat("_") + ".log"))
disableFile = os.path.join("/tmp", progName + ".disable")
runningFile = os.path.join("/tmp/backupNight.running")

# True will suspend pc

# Holidays
userSlot = [
    ["lundi", {"00:30": True, "06:00": False}],
    ["mardi", {"00:30": True, "06:00": False}],
    ["mercredi", {"00:30": True, "06:00": False}],
    ["jeudi", {"00:30": True, "06:00": False}],
    ["vendredi", {"00:30": True, "06:00": False}],
    ["samedi", {"02:00": True, "06:00": False}],
    ["dimanche", {"02:00": True, "06:00": False}]
]


# Work week
# userSlot = [
#     ["lundi",    {"00:00": True, "06:00": False, "23:45": True}],
#     ["mardi",    {"00:00": True, "06:00": False, "23:45": True}],
#     ["mercredi", {"00:00": True, "06:00": False, "23:45": True}],
#     ["jeudi",    {"00:00": True, "06:00": False, "23:45": True}],
#     ["vendredi", {"00:00": True, "06:00": False}],
#     ["samedi",   {"00:00": False, "02:00": True, "07:00": False}],
#     ["dimanche", {"00:00": False, "02:00": True, "07:00": False, "23:45": True}]
# ]

##############################################


##############################################
#                  CLASS                     #
##############################################

class HardwareElements:
    def __init__(self):
        self.hardwareList = list()

    def __str__(self):
        res = str()
        i = 1
        for hardware in self.hardwareList:
            res += "## Hardware " + str(i) + "\n"
            res += str(hardware) + "\n"
            i += 1
        return res

    def init(self, *hardwares):
        for hardware in hardwares:
            self.hardwareList.append(Hardware(hardware[0], hardware[1]))

    def block(self):
        for hardware in self.hardwareList:
            hardware.block()

    def unblock(self):
        for hardware in self.hardwareList:
            hardware.unblock()


class Hardware:
    def __init__(self, short_name, full_name):
        self.short = short_name
        self.full = full_name
        self.id = int()
        self.getId()

    def __str__(self):
        res = str()
        res += "#    short name = " + str(self.short) + "\n"
        res += "#    full name  = " + str(self.full) + "\n"
        res += "#    id         = " + str(self.id)
        return res

    def getId(self):
        try:
            self.id = subprocess.check_output(["xinput", "list", "--id-only", str(self.full)]).strip()
        except subprocess.CalledProcessError:
            log.error("In getId : error with " + str(self.short))

    def block(self):
        log.info("In  block " + self.short)
        subprocess.call(["xinput", "disable", str(self.id)])
        log.info("Out block")

    def unblock(self):
        log.info("In  unblock " + self.short)
        subprocess.call(["xinput", "enable", str(self.id)])
        log.info("Out unblock")


class TimeSlot:
    def __init__(self):
        self.curDOW = datetime.now().weekday()

    def __str__(self):
        res = str()
        res += "# current day of week = " + str(self.curDOW) + "\n"
        return res

    def sortUserSlot(self):
        user_sort = userSlot[self.curDOW][1].keys()
        log.debug("UserTime before sort =" + str(user_sort))
        user_sort.sort(reverse=True)
        log.debug("UserTime after sort =" + str(user_sort))
        return user_sort

    # Check if current time + 4mn is in timeSlot defined by user
    def checkBeforeTS(self):
        log.info("Check before time slot")
        cur_t5 = datetime.now() + timedelta(minutes=4)
        cur_time5 = format(cur_t5, '%H:%M')
        log.debug("Check real time slot cur_time5=" + str(cur_time5))
        log.debug("Check user times=" + str(userSlot[self.curDOW][1]))
        for user_time in self.sortUserSlot():
            log.debug("Check user time slot user_time=" + str(user_time))
            if cur_time5 > user_time:
                return userSlot[self.curDOW][1][user_time]

    # Check if datetime is in timeSlot defined by user
    def inTS(self):
        log.info("Check time slot")
        cur_time = time.strftime("%H:%M")
        log.debug("Check real time slot cur_time =" + str(cur_time))
        log.debug("Check user times=" + str(userSlot[self.curDOW][1]))
        for user_time in self.sortUserSlot():
            log.debug("Check user time slot user_time=" + str(user_time))
            if cur_time > user_time:
                return userSlot[self.curDOW][1][user_time]


##############################################


##############################################
#                FUNCTIONS                   #
##############################################

def suspend():
    log.info("Suspend machine")
    subprocess.call(["systemctl", "suspend"])


def message():
    log.info("Echo user")
    subprocess.call(['zenity', '--info', '--timeout=300', '--no-wrap',
                     '--text=Il est temps d\'aller faire dodo\nT\'as 5mn avant l\'extinction des feux…'])


def printInfo():
    locution = ""
    if not os.path.isfile(disableFile):
        locution = " not"
    print("The disable file (%s) is%s present.\n" % (disableFile, locution))
    print("True will suspend the PC.")
    for (day, timeList) in userSlot:
        print("    %s : %s" % (str(day), str(timeList)))


##############################################


##############################################
#                 MAIN                       #
##############################################

def main():
    log.info("In  main")

    hardware_elts = HardwareElements()
    # To get the good names : xinput list
    hardware_elts.init(["keyboard", "keyboard:Logitech MK700"],
                       ["mouseJuju", "pointer:MOSART Semi. 2.4G Wireless Mouse"])
    # ["mouseJuju", "pointer:MOSART Semi. 2.4G Wireless Mouse"], \
    # ["mouseHanna", "pointer:Logitech M505/B605"])
    log.debug("Hardwares :\n" + str(hardware_elts))

    enable_disable = ProgEnDis(disable_file=disableFile)

    if parsedArgs.block:
        hardware_elts.block()
    elif parsedArgs.unblock:
        hardware_elts.unblock()
    elif parsedArgs.enable:
        enable_disable.progEnable()
    elif parsedArgs.disable:
        enable_disable.progDisable()
    elif parsedArgs.info:
        printInfo()
    else:
        if enable_disable.isEnable():
            ts = TimeSlot()
            log.debug("TimeSlot :\n" + str(ts))
            if ts.inTS():
                # when lock file was created after the TS
                # this trick to have the user message
                if enable_disable.isJustRemoveFile():
                    message()
                else:
                    if not (os.path.isfile(runningFile)):
                        hardware_elts.block()
                        suspend()
            elif ts.checkBeforeTS():
                message()
            else:
                log.info("not in a suspend time slot")
                # hardware_elts.unblock()

    log.info("Out main")


if __name__ == '__main__':
    main()
