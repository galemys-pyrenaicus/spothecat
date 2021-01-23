#!/usr/bin/env bash
dbuser_pass=$(openssl rand -base64 12)

if VERB="$( which apt )" 2> /dev/null; then
  sudo apt install git python3.6 postgresql93 postgresql93-contrib
elif VERB="$( which yum )" 2> /dev/null; then
  sudo dnf install -y epel-release git python36 glibc-locale-source glibc-langpack-ru
  sudo dnf install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm
  sudo dnf -qy module disable postgresql
  sudo dnf install -y postgresql96-server
  sudo /usr/pgsql-9.6/bin/postgresql96-setup initdb
  sudo systemctl enable postgresql-9.6
  sudo systemctl start postgresql-9.6
fi
cd /opt
sudo git clone https://github.com/galemys-pyrenaicus/spothecat
sudo groupadd www-data
sudo useradd -M -b /opt/spothecat -G www-data -s /sbin/nologin spothecat
sudo mkdir -p /var/www/spothecat
sudo chown -R spothecat /opt/spothecat
sudo chown -R spothecat /var/www/spothecat
sudo chgrp -R spothecat /opt/spothecat
sudo chgrp -R www-data /var/www
sudo touch /var/log/spothecat.log
sudo chown spothecat /var/log/spothecat.log
sudo ln -s /opt/spothecat/templates /var/www/spothecat
sudo mkdir /etc/spothecat
sudo mv /opt/spothecat/spothecat.conf.sample /etc/spothecat/spothecat.conf.sample
sudo -u spothecat pip3 install Flask flask-login gmplot configparser psycopg2-binary paramiko --user
#echo postgres:"$dbuser_pass" | chpasswd
#echo "$dbuser_pass" >> ~/.dbpasswd
sudo sed -E -i '/all/s/md5|peer|ident/trust/g' /var/lib/pgsql/9.6/data/pg_hba.conf
sudo sed -E -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /var/lib/pgsql/9.6/data/postgresql.conf
sudo systemctl restart postgresql-9.6
psql -h localhost -U postgres -c "CREATE DATABASE location WITH OWNER = postgres ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8' TABLESPACE = pg_default CONNECTION LIMIT = -1;"
psql -h localhost -U postgres -d location -c 'CREATE TABLE public.location_parsed (lat real NOT NULL, lon real NOT NULL, tme text COLLATE pg_catalog."default" NOT NULL, prv text COLLATE pg_catalog."default" NOT NULL, spd real NOT NULL, CONSTRAINT location_parsed_pkey PRIMARY KEY (tme)) TABLESPACE pg_default;'
psql -h localhost -U postgres -d location -c 'CREATE TABLE public.users (login text COLLATE pg_catalog."default" NOT NULL, pass_hash text COLLATE pg_catalog."default", role text COLLATE pg_catalog."default" NOT NULL, active boolean NOT NULL, address text COLLATE pg_catalog."default", connected text[] COLLATE pg_catalog."default", CONSTRAINT users_pkey PRIMARY KEY (login)) TABLESPACE pg_default;'
psql -h localhost -U postgres -d location -c 'ALTER TABLE public.location_parsed OWNER to postgres;'
psql -h localhost -U postgres -d location -c 'ALTER TABLE public.users OWNER to postgres;'
psql -h localhost -U postgres -d location -c "INSERT INTO users (login, pass_hash, role, active) VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', 'True')"

cat > ~/spothecat.service << EOL
[Unit]
Description=Spothecat App
After=multi-user.target

[Service]
Type=simple
User=spothecat
Group=www-data
ExecStart=/usr/bin/python3.6 /opt/spothecat/server.py
StandartInput=tty-force

[Install]
WantedBy=multi-user.target
EOL

sudo mv ~/spothecat.service /etc/systemd/system/spothecat.service

sudo systemctl daemon-reload
sudo systemctl enable spothecat.service
sudo systemctl start spothecat.service
