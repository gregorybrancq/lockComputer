#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os.path
import subprocess
import sys
import time
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from optparse import OptionParser

sys.path.append('/home/greg/Greg/work/env/pythonCommon')
from log_and_parse import createLog
from program import Program

##############################################
# Global variables
##############################################

progName = "computerLock"

# configuration files
runningBackupFile = os.path.join("/tmp/backupNight.running")

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
    help="Enable automatic behavior depending on time."
)

parser.add_option(
    "-d",
    "--disable",
    action="store_true",
    dest="disable",
    default=False,
    help="Disable this program for one day."
)

parser.add_option(
    "-i",
    "--info",
    action="store_true",
    dest="info",
    default=False,
    help="Give different information for this program."
)

(parsed_args, args) = parser.parse_args()


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
            id_bytes = subprocess.check_output(["xinput", "list", "--id-only", str(self.full)]).strip()
            self.id = id_bytes.decode()
        except subprocess.CalledProcessError:
            logger.error("In getId : error with " + str(self.short))

    def block(self):
        if self.id != 0 :
            subprocess.call(["xinput", "disable", str(self.id)])
            logger.info("Block " + self.short)

    def unblock(self):
        if self.id != 0 :
            subprocess.call(["xinput", "enable", str(self.id)])
            logger.info("Unblock " + self.short)


class TimeSlot:
    def __init__(self):
        self.curDOW = datetime.now().weekday()

    def __str__(self):
        res = str()
        res += "# current day of week = " + str(self.curDOW) + "\n"
        return res

    def sortUserSlot(self):
        user_sort = sorted(userSlot[self.curDOW][1].keys(), reverse=True)
        logger.debug("UserTime after sort = %s" % str(user_sort))
        return user_sort

    # Check if current time + 6mn is in timeSlot defined by user
    def checkBeforeTS(self):
        logger.info("Check before time slot")
        cur_time_plus_timedelta = datetime.now() + timedelta(minutes=6)
        cur_time_plus_delta = format(cur_time_plus_timedelta, '%H:%M')
        logger.debug("Check real time slot cur_time_plus_delta = %s" % str(cur_time_plus_delta))
        for user_time in self.sortUserSlot():
            if cur_time_plus_delta > user_time:
                logger.debug("cur_time_plus_delta (%s) > user_time (%s)" % (str(cur_time_plus_delta), str(user_time)))
                return userSlot[self.curDOW][1][user_time]

    # Check if datetime is in timeSlot defined by user
    def inTS(self):
        logger.info("Check time slot")
        cur_time = time.strftime("%H:%M")
        logger.debug("Check real time slot cur_time = %s" % str(cur_time))
        logger.debug("Check user times=" + str(userSlot[self.curDOW][1]))
        for user_time in self.sortUserSlot():
            logger.debug("Check user time slot user_time = %s" % str(user_time))
            if cur_time > user_time:
                logger.debug("cur_time (%s) > user_time (%s)" % (str(cur_time), str(user_time)))
                return userSlot[self.curDOW][1][user_time]


##############################################


##############################################
#                FUNCTIONS                   #
##############################################

def suspend():
    logger.info("Suspend machine")
    subprocess.call(["systemctl", "suspend"])


def message():
    logger.info("Display message to prevent user")
    subprocess.call(['zenity', '--info', '--timeout=300', '--no-wrap',
                     '--text=Il est temps d\'aller faire dodo\nT\'as 5mn avant l\'extinction des feux…'],
                     stderr=subprocess.DEVNULL)


def printInfo():
    print(program.getInfo())
    print("True will suspend the PC.")
    for (day, timeList) in userSlot:
        print("    %s : %s" % (str(day), str(timeList)))


##############################################


##############################################
#                 MAIN                       #
##############################################

def main():
    logger.info("START")

    hardware_elts = HardwareElements()
    # To get the good names : xinput list
    hardware_elts.init(["keyboard", "keyboard:Logitech MK700"],
                       ["mouseJuju", "pointer:MOSART Semi. 2.4G Wireless Mouse"])
    logger.debug("Hardwares :\n" + str(hardware_elts))

    if parsed_args.block:
        hardware_elts.block()
    elif parsed_args.unblock:
        hardware_elts.unblock()
    elif parsed_args.enable:
        program.progEnable()
    elif parsed_args.disable:
        program.progDisable()
    elif parsed_args.info:
        printInfo()
    else:
        if program.isEnable():
            ts = TimeSlot()
            logger.debug("TimeSlot :\n" + str(ts))
            if ts.inTS():
                # when lock file was created after the TS
                # this trick to have the user message
                if program.isJustRemoveFile():
                    message()
                else:
                    if not (os.path.isfile(runningBackupFile)):
                        hardware_elts.block()
                        suspend()
                    else :
                        logger.info("Backup is running.\n")
            elif ts.checkBeforeTS():
                message()
            else:
                logger.info("Not in a suspend time slot")
                # hardware_elts.unblock()

    logger.info("STOP\n")


if __name__ == '__main__':
    logger = createLog(progName, parsed_args)
    program = Program(prog_name=progName)
    main()
