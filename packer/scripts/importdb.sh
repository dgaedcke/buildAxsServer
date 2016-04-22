echo "=> Creating and importing database"
service mysqld start
mysql -u root -e 'CREATE DATABASE IF NOT EXISTS `pay` CHARACTER SET utf8 COLLATE utf8_general_ci'
zcat /tmp/payprod.sql.gz | mysql -u root pay
rm -f /tmp/payprod.sql.gz
