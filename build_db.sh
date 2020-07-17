#!/bin/bash
#
# 
sqlite3 /home/pi/Smoker-Controller/templog.db  << 'END_SQL'
DROP TABLE temps;
CREATE TABLE temps(timestamp timestamp default (strftime('%s', 'now')), sensnum numeric, temp numeric);
END_SQL
