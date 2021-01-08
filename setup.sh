#!/usr/bin/env bash
if VERB="$( which apt )" 2> /dev/null; then
  apt install git python3 postgresql
elif VERB="$( which yum )" 2> /dev/null; then
  yum install git python3 postgresql
fi
cd /opt
git clone https://github.com/galemys-pyrenaicus/spothecat
mkdir /etc/spothecat
mv /opt/spothecat/spothecat.conf.sample /etc/spothecat/spothecat.conf.sample
pip3 install Flask flask-login gmplot configparser psycopg2
