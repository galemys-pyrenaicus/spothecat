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
import os
import sys

config = configparser.ConfigParser()
config.read('spothecat.conf')
dbcred = config['DATABASE']
ffoncred = config['PHONE']
gmapcred = config['GMAP']

def check_availiability(host, retrying=3):
    for i in range(retrying):
        if os.system("ping -c 1 " + host+" > /dev/null") == 0:
            return True
        print("Testing connection")
        time.sleep(20)
    else:
        return False

def obtain_location(oncemore=False):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ffoncred['ip'], port=int(ffoncred['port']), key_filename='/home/desman/.ssh/id_rsa', banner_timeout=300)
        stdin, stdout, stderr = client.exec_command('sh /data/data/com.termux/files/home/scrt/myloc.sh')
        time.sleep(20)
        sftp = client.open_sftp()
        remotepath = '/data/data/com.termux/files/home/storage/loca'
        localpath = 'loca'
        sftp.get(remotepath, localpath)
        if os.path.getsize('loca') == 1:
            raise FileNotFoundError;
        client.close()
    except paramiko.ssh_exception.AuthenticationException:
        print("Auth error while connecting to %s", (ffoncred['ip']))
    except paramiko.ssh_exception.BadAuthenticationType:
        print("Auth type error while connecting to %s , check config", (ffoncred['ip']))
    except paramiko.ssh_exception.SSHException:
        print("Error connecting phone")
    except FileNotFoundError:
        if oncemore == False:
            print("There is a problem with location file, retrying once more in 30s")
            time.sleep(30)
            obtain_location(True)
        else:
            print("There is a problem with location data, probably gps signal lost")
            sys.exit()

def draw_map():
    connlocadb = psycopg2.connect(dbname=dbcred['dbname'], user=dbcred['dbuser'], password=dbcred['dbpass'], host=dbcred['dbhost'])
    cursor = connlocadb.cursor()
    gmap = gmplot.GoogleMapPlotter(60.000000, 30.000000, 10, apikey=gmapcred['apikey'])

    try:
        with open('loca', "r") as read_file:
            loca = json.load(read_file, strict=False)
            query = "INSERT INTO location_parsed (lat, lon, tme, prv, spd) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING"
            cursor.execute(query, (loca['latitude'], loca['longitude'], loca['date'], loca['provider'], loca['speed']))
            connlocadb.commit()
            cursor.execute('SELECT * FROM location_parsed')
            queryres = cursor.fetchall()
            for row in queryres:
                gmap.marker(row[0],row[1], color='cornflowerblue', title=row[2])
            gmap.draw('whereami_map.html')
    except:
        print("Exception with loca or db")

def main():
    if check_availiability(ffoncred['IP']) == True:
        obtain_location() #Comment out to test without network connection and copy loca.sample to loca
        draw_map()
    else:
        print ("Can't reach host")

main()
