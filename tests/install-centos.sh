#!/usr/bin/env bash

set -e

yum install -y epel-release
yum install -y memcached libmemcached nginx mysql tomcat httpd-tools unzip vim links policycoreutils-python net-tools

echo "Fetching jspwiki"
curl -O https://www-eu.apache.org/dist/jspwiki/2.10.2/binaries/webapp/JSPWiki.war
mv JSPWiki.war wiki.war
cp wiki.war /usr/share/tomcat/webapps/wiki.war

echo "Restarting tomcat"
service tomcat restart
sleep 30

cp /vagrant/jspwiki-custom.properties /usr/share/tomcat/webapps/wiki/WEB-INF/classes/jspwiki-custom.properties

echo "Fetching wikipages"
curl -O http://www-eu.apache.org/dist/jspwiki/2.10.2/wikipages/jspwiki-wikipages-en-2.10.2.zip
unzip jspwiki-wikipages-en-2.10.2.zip
cd jspwiki-wikipages-en-2.10.2
cp * /usr/share/tomcat/webapps/wiki/
cd

echo "Restarting tomcat"
service tomcat restart
# These sleeps are to ensure that Tomcat has sufficient time to start listening on 8005 before the
# next restart call comes. FOr some reason it takes a long time to restart the 8005 after this.
sleep 180

echo "Software install complete"

echo "Configuring tomcat logs"
cp /vagrant/server.xml /usr/share/tomcat/conf/server.xml
service tomcat restart

echo "Configuring nginx"
cp /vagrant/nginx.conf /etc/nginx/nginx.conf
cp /vagrant/nginx-default.conf /etc/nginx/conf.d/default.conf
service nginx start

sleep 30

# This curl request is to populate the audit.log required in the next step
curl --verbose http://localhost/wiki/ > /dev/null
cat /var/log/audit/audit.log | grep nginx | grep denied | audit2allow -M mynginx
semodule -i mynginx.pp

echo "Wiki available at http://localhost:80/wiki/"

echo "Installing xcollector"
yum install -y /vagrant/xcollector.rpm
cp /vagrant/xcollector.yml /usr/local/xcollector/conf/xcollector.yml
sed -i "s/access_token:.*$/access_token: ${TOKEN}/g" /usr/local/xcollector/conf/xcollector.yml
echo "Restarting xcollector"
service xcollector restart

echo "Completed!"
