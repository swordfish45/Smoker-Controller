# Smoker-Controller

Charcoal smoker temperatrue controller. Monitor code and webgui based of Tim Wilhoit's project.

http://pibbqmonitor.blogspot.com/2014/09/three-probe-temperature-monitor-for.html
https://github.com/talltom/PiThermServer

See build log here https://imgur.com/gallery/9hchw

Installation

./install.sh

Legacy instructions below. Should not need to perform any of this.

Install node sudo wget http://node-arm.herokuapp.com/node_latest_armhf.deb sudo dpkg -i node_latest_armhf.deb Make sure node install was good by checking "sudo node-v". Should return node version.
Install python and other packages:
sudo apt-get upgrade sudo apt-get update sudo apt-get install python-dev
sudo apt-get install python-setuptools
sudo easy_install rpi.gpio
sudo apt-get install alsa-utils
sudo apt-get install mpg321
sudo apt-get install sqlite3
sudo apt-get install libsqlite3-dev
sudo apt-get install npm
Install node dependencies with NPM npm install -g node-gyp npm install node-static npm install node-sqlite3
Clone git repository to /home/pi. i.e. logger.py should be in /home/pi directory git clone git://github.com/tilimil/PIBBQMonitor.git cp -R ~pi/PIBBQMonitor/* ~pi/
Run command to create DB. Build_db.sh is not working currently sudo sqlite3 /home/pi/templog.db SQLite version 3.7.13 2012-06-11 02:05:22 Enter ".help" for instructions Enter SQL statements terminated with a ";" sqlite> drop table temps; Error: no such table: temps sqlite> CREATE TABLE temps(timestamp timestamp default (strftime('%s', 'now')), sensnum numeric, temp numeric); sqlite> .quit
Disable any webserver that may already be running on port 80. sudo update-rc.d apache2 disable
Setup the thermserv node app as a service sudo cp /home/pi/thermserv_initfile /etc/init.d/thermserv sudo chmod 755 /etc/init.d/thermserv update-rc.d thermserv defaults
Execute "sudo crontab -e" and paste the following lines into your crontab. Logger will log the temp to the DB every minute. The dbcleanup.sh will limit the DB to 24 hours worth of data:
*/1 * * * * /home/pi/logger.py
0 * * * * /home/pi/dbcleanup.sh
*/1 * * * * /home/pi/alert.py
