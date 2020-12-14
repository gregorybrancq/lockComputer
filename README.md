 computerLock

This program allows to block hardware component (as keyboard and mouse) and set pc in sleep mode.

You can planify it in cron, no need that it works during the day :\
 - 0,5,45,50,55 0-6,23   *   *   *    export DISPLAY=:0.0 && /home/greg/Config/env/bin/computerLock
