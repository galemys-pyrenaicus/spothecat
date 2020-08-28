import gmplot
import json
import subprocess
import signal
import psycopg2
from psycopg2 import sql
import paramiko
import time
import traceback
import logging
import configparser

config = configparser.ConfigParser()
config.read('spothecat.conf')
dbcred = config['DATABASE']
ffoncred = config['PHONE']
gmapcred = config['GMAP']

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=ffoncred['ip'], port=int(ffoncred['port']), key_filename='/home/desman/.ssh/id_rsa', banner_timeout=300)
stdin, stdout, stderr = client.exec_command('sh /data/data/com.termux/files/home/scrt/myloc.sh')
time.sleep(15)
sftp = client.open_sftp()
remotepath = '/data/data/com.termux/files/home/storage/loca'
localpath = 'loca'
sftp.get(remotepath, localpath)
client.close()

connlocadb = psycopg2.connect(dbname=dbcred['dbname'], user=dbcred['dbuser'], password=dbcred['dbpass'], host=dbcred['dbhost'])
cursor = connlocadb.cursor()

with open('loca', "r") as read_file:
    loca = json.load(read_file, strict=False)
    query = "INSERT INTO location_parsed (lat, lon, tme, prv, spd) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
    cursor.execute(query, (loca['latitude'], loca['longitude'], loca['date'], loca['provider'], loca['speed']))
    connlocadb.commit()

gmap = gmplot.GoogleMapPlotter(60.000000, 30.000000, 10, apikey=gmapcred['apikey'])

cursor.execute('SELECT * FROM location_parsed')
queryres = cursor.fetchall()
for row in queryres:
    gmap.marker(row[0],row[1], color='cornflowerblue', title=row[2])
gmap.draw('whereami_map.html')
