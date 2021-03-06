This project is for Udacity course Full Stack Web Developer project 5 - 
configuring Linux for a web application.

i. The IP address and SSH port so your server can be accessed by the reviewer.
    ip: 52.38.84.59
    ssh port: 2200

ii. The complete URL to your hosted web application:
    http://ec2-52-38-84-59.us-west-2.compute.amazonaws.com/api/all
Suggestion: 
For your future projects consider configuring DNS software.  In order to get a hostname/domainname in your machine you can sign up in any free service as www.no-ip.com, and register the IP with the desired hostname and any of the free domain names available.

iii. A summary of software you installed and configuration changes made.
	sudo apt-get install apache2

Suggestion: For monitoring Apache status, you can use the Apache module mod_status.

	sudo apt-get install libapache2-mod-wsgi
	sudo apt-get install postgresql
	sudo apt-get install python-psycopg2
	sudo apt-get install python-pip
	sudo pip install Flask-SQLAlchemy
	sudo pip install bleach
	sudo pip install oauth2client
	sudo pip install requests
	sudo pip install httplib2
	sudo pip install redis
	sudo pip install passlib
	sudo pip install itsdangerous
	sudo pip install flask-httpauth
	sudo pip install werkzeug==0.8.3
	sudo pip install flask==0.9
	sudo pip install Flask=login==0.1.3

iv. A list of any third-party resources you made use of to complete this project.
	I consulted the links referenced in project videos, and the resources
	other students recommended (also linked in udacity project notes)

Suggestion: 
There is a way to accelerate your web-application by using Nginx web-server.
You can customize it for different purposes.
For instance: caching, protection against hotlinking and DDoS attacks.
You can learn how to configure it from these books: http://nginx.org/en/books.html


=======================================================================
Notes on steps taken to configure:

==== connect to Udacity/Amazon AWS linux VM ===============================

from instructions: https://www.udacity.com/account#!/development_environment

mv Downloads/udacity_key.rsa  ~/.ssh/
ls -l ~/.ssh
chmod 600 ~/.ssh/udacity_key.rsa 
ssh -i ~/.ssh/udacity_key.rsa root@52.38.84.59

==== Perform Basic Configuration ==============================

- Create a new user named grader and grant this user sudo permissions.
sudo adduser grader
cat >/etc/sudoers.d/grader
grader ALL=(ALL) NOPASSWD:ALL
^D
ls -la /etc/sudoers.d
chmod 444 /etc/sudoers.d/grader
(repeat for user "rstaehli")
(can login with "ssh rstaehli@52.38.84.59 -p 22")

- Update all currently installed packages.
sudo apt-get update
sudo apt-get upgrade
(said yes to updating /run/grub/menu.lst it said was locally modified)

- Configure the local timezone to UTC.
dpkg-reconfigure tzdata
(follow prompts to select UTC, but was preconfigured)

==== Secure your server ==============================

- Configure Firewall (UFW) to allow ssh connections on 2200:
sudo ufw status
sudo ufw allow 2200/tcp
sudo ufw status

Suggestion: UFW rate limiting can be used to prevent from brute force attacks.

- Change the SSH port from 22 to 2200
vi /etc/ssh/sshd_config
Port 2200
sudo service ssh restart

- Configure Firewall (UFW) only incoming connections for SSH, WWW, NTP:
sudo ufw disable  # so ssh isn't broken while working on firewall
sudo ufw status
sudo ufw default deny incoming
sudo ufw default allow outgoing
- SSH (port 2200), 
sudo ufw allow 2200/tcp
- HTTP (port 80), and 
sudo ufw allow www
- NTP (port 123)
sudo ufw enable
sudo ufw allow ntp
sudo ufw status
(had to "sudo ufw delete allow 22" to close old ssh port)

# support login with public key encryption : server passes GUniqueToken to client, who encodes with client secret key, server decodes with client public key to authenticate identity of client.
# create/save keys to file /Users/richardstaehli/.ssh/linuxAWSBox, with passphrase
ssh-keygen
<mysecret>

# copy and paste linuxAWSBox.pub key(value) to rstaehli@my=ubuntu-virtualbox file:
    .ssh/authorized_keys
    chmod 700 .ssh
    chmod 644 .ssh/authorized_keys
    (chown/chgrp rstaehli .ssh/authorized_keys if you created these as root)

#Then I (richardstaehli with private key) am authorized to login to my virtual box as "rstaehli":
    ssh -v -i ~/.ssh/linuxAWSBox rstaehli@52.38.84.59 -p 2200
(prompts for passphrase: <mysecret>)

# disable root login, must login as one of created users
sudo mv /root/.ssh/authorized_keys /root/save_authorized_keys

# Disable password based logins
(edit) /etc/ssh/sshd_config
(it was already configured with "PasswordAuthentication no")
sudo service ssh restart

# in response to "restart required" after kernel upgrades:
sudo reboot

==== 2 Apache Server setup =============================

# first edit Vagrantfile to forward http port 8080 to virtual box port 80:
# but don't need to do this for AWS VM as we can just use port 80 there.
   config.vm.network :forwarded_port, guest: 80, host: 8080
# have to halt/ restart virtual box to get this to happen.

sudo apt-get install apache2
# test by accessing http://52.38.84.59:80

# apache serves from  /var/www/html 

# enable support for wsgi:
sudo apt-get install libapache2-mod-wsgi
# some say you have to also enbale, but I did not:
sudo a2enmod wsgi 

# add line at bottom of VirtalHost elem in /etc/apache2/sites-enabled/000-default.conf: 
	WSGIScriptAlias / /var/www/html/myapp.wsgi
restart apache: sudo apache2ctl restart

# then test with simply python wsgi app that returns hello…
http://52.38.84.59:80
tail /var/log/apache2/error.log

==== 3 Postgres setup =============================

sudo apt-get install postgresql
sudo apt-get install python-psycopg2

# login the first time as user ‘postgres’ but 
#   - protect postgres user with a new password, and
sudo -u postgres psql
ALTER USER postgres PASSWORD 'newPassword';

# Create a new user named catalog that has limited permissions to your catalog application database
sudo adduser catalog
sudo -u postgres psql
create user catalog with password 'glen,acres,rd';
create database api_ed_db;
# grant CRUD privileges to catalog;
\c api_ed_db;
grant select, insert, update, delete on all tables in schema public to catalog;

# may need to restart postgres
sudo service postgresql restart

# Do not allow remote connections (already the configured in pg_hba.conf)
# edit pg_hba.conf to use md5 authentication for local database access:
local   all             all                                     md5

==== NTP Setup =====================================

# create /etc/cron.daily/ntpdat script to run ndpdate:
#!/bin/sh
ntpdate ntp.ubuntu.com
sudo chmod 755 /etc/cron.daily/ntpdate

# schedule cron job to run it daily

==== Application Setup =============================

# Install git, clone and set up your Catalog App project (from your GitHub repository from earlier in the Nanodegree program) so that it functions correctly when visiting your server’s IP address in a browser. Remember to set this up appropriately so that your .git directory is not publicly accessible via a browser!
sudo apt-get install python-pip
sudo pip install Flask-SQLAlchemy
# do the same with the rest of these dependencies:
sudo pip install bleach
sudo pip install oauth2client
sudo pip install requests
sudo pip install httplib2
sudo pip install redis
sudo pip install passlib
sudo pip install itsdangerous
sudo pip install flask-httpauth

sudo pip install werkzeug==0.8.3
sudo pip install flask==0.9
sudo pip install Flask=login==0.1.3

# Build api_ed database by running api_ed project ORM code (as user catalog):
su catalog
python orm.py
exit

# create wsgi application file structure:
cd /var/www
sudo mkdir api_ed
cd api_ed/
sudo mkdir api_ed
cd api_ed/
sudo mkdir static templates

# in the lower level api_ed directory, create '__init__.py' to launch the app:
from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello():
    return "Hello, I love Digital Ocean!"
if __name__ == "__main__":
    app.run()

# test that this works:
sudo python __init__.py 

# configure apache to route requests to your wsgi app:
sudo nano /etc/apache2/sites-available/api_ed.conf
# and add the following content:
<VirtualHost *:80>
		ServerName 52.38.84.59
		ServerAdmin admin@52.38.84.59
		WSGIScriptAlias / /var/www/api_ed/api_ed.wsgi
		<Directory /var/www/api_ed/api_ed/>
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/api_ed/api_ed/static
		<Directory /var/www/api_ed/api_ed/static/>
			Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>

# enable this new site:
sudo a2ensite api_ed
# disable old default site:
sudo a2dissite 000-default
# then reload available sites virtualhost definitions
suto service apache2 reload

# create the .wsgi file:
cd /var/www/api_ed
sudo nano api_ed.wsgi 
# with the following code:
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/api_ed/")

from FlaskApp import app as application
application.secret_key = 'Add your secret key'

# copy actual application Flask router from project to site:
cd /var/www/api_ed
sudo cp ~rstaehli/git/api-ed/*.py api_ed
cd api_ed/
sudo cp __init__.py __init__.py.orig
sudo cp web-service.py __init__.py

# then restart apache:
sudo service apache2 restart

# had to edit __init__.py to provide full path to client_secrets.json (2 places)
# need to fix access to htmltemplates.
sudo cp ~rstaehli/git/api-ed/templates/* templates
sudo cp ~rstaehli/git/api-ed/static/* static

# edit application psycopg2 db connection info to use "catalog" user login
db_connection_info = 'postgresql+psycopg2://catalog:glen,acres,rd@localhost/api_ed_db'

# Now setup oauth2 login to api_ed webapp:
# On https://console.developers.google.com/ create new Oauth client credentials for webapp named "api-ed"
# Add my AWS virtual host URL to authorized JavaScript origins:
http://52.38.84.59
http://ec2-52-38-84-59.us-west-2.compute.amazonaws.com
# copy generated client-id and client-secret values to /var/web/api_ed/api_ed/client_secrets.json
# update client-id value in /var/web/api_ed/api_ed/templates/login.html
# update client-id value in /var/web/api_ed/api_ed/__init__.py


# Your Amazon EC2 Instance's public URL will look something like this: http://ec2-XX-XX-XXX-XXX.us-west-2.compute.amazonaws.com/ where the X's are replaced with your instance's IP address. You can use this url when configuring third party authentication. Please note the the IP address part of the AWS URL uses dashes, not dots.
