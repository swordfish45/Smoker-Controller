#!/bin/bash
sqlite3 /home/pi/Smoker-Controller/templog.db "delete from temps where timestamp <= strftime('%s', 'now') - 86400;"
