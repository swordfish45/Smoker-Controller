#!/bin/bash

INSTALLDIR='/home/pi/Smoker-Controller/'
cd $INSTALLDIR
#sudo wget http://node-arm.herokuapp.com/node_latest_armhf.deb 
#sudo dpkg -i node_latest_armhf.deb
#sudo apt-get upgrade 
#sudo apt-get update 
#sudo apt-get install python-dev
#sudo apt-get install python-setuptools
#sudo easy_install rpi.gpio
#sudo apt-get install alsa-utils
#sudo apt-get install mpg321
#sudo apt-get install sqlite3
#sudo apt-get install libsqlite3-dev
#sudo apt-get install npm
#npm install -g node-gyp 
#npm install node-static 
#npm install sqlite3

#$INSTALLDIR/build_db.sh
##sudo cp $INSTALLDIR/thermserv_initfile /etc/init.d/thermserv
##sudo chmod 755 /etc/init.d/thermserv
##sudo update-rc.d thermserv defaults
sudo cp $INSTALLDIR/thermserv.service /etc/systemd/system/
chmod +x /etc/systemd/system/thermserv.service
chmod +x $INSTALLDIR/thermserv_start.sh
chmod +x $INSTALLDIR/*.py
sudo systemctl enable thermserv


#(crontab -l 2>/dev/null; echo "*/1 * * * * $INSTALLDIR/logger.py") | crontab -u pi -
#(crontab -l 2>/dev/null; echo "0 * * * * $INSTALLDIR/dbcleanup.sh") | crontab -u pi -
#(crontab -l 2>/dev/null; echo "*/1 * * * * $INSTALLDIR/control.sh") | crontab -u pi -


