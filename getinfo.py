import gmplot
import json
import subprocess
import signal
import psycopg2
from psycopg2 import sql
import paramiko
import time, threading
import traceback
import logging
import configparser
import os
import sys
import server

def check_availiability(host, retrying=3):
    for i in range(retrying):
        if os.system("ping -c 1 " + host+" > /dev/null") == 0:
            logging.info("Phone is online")
            return True
        time.sleep(20)
    else:
        return False

def obtain_location(oncemore=False):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=ffoncred['ip'], port=int(ffoncred['port']), key_filename=ffoncred['key'], banner_timeout=300)
        stdin, stdout, stderr = client.exec_command('sh /data/data/com.termux/files/home/scrt/myloc.sh')
        time.sleep(40)
        sftp = client.open_sftp()
        remotepath = '/data/data/com.termux/files/home/storage/loca'
        localpath = 'loca'
        sftp.get(remotepath, localpath)
        if os.path.getsize('loca') == 1:
            raise FileNotFoundError;
        client.close()
    except paramiko.ssh_exception.AuthenticationException:
        logging.critical("Auth error while connecting to %s", (ffoncred['ip']))
    except paramiko.ssh_exception.BadAuthenticationType:
        logging.critical("Auth type error while connecting to %s , check config", (ffoncred['ip']))
    except paramiko.ssh_exception.SSHException:
        logging.error("Error connecting phone")
    except FileNotFoundError:
        if oncemore == False:
            logging.warning("Phone is online, but there is a problem with location data, retrying once more in 30s")
            time.sleep(30)
            obtain_location(True)
        else:
            logging.error("Phone is online, but there is a problem with location data, probably gps signal lost")
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
            gmap.draw('templates/whereami_map.html')
    except:
        print("Exception with db")

def getdelay():
    return(config['OTHER']['period'])

def get_config():
    all_cred = server.pass_config()
    dbcred = all_cred[0]
    ffoncred = all_cred[1]
    gmapcred = all_cred[2]
    logs = all_cred[3]
    srv = all_cred[4]
    logformat = ['%(asctime)s [%(levelname)s] - %(message)s', '%d-%b-%y %H:%M:%S']
    logging.basicConfig(filename=logs['path'], format=logformat[0], level=logs['level'], datefmt=logformat[1])

def main():
    get_config()
    logging.info("Starting the script...")
    if check_availiability(ffoncred['IP']) == True:
        obtain_location() #Comment out to test without network connection and copy loca.sample to loca
        draw_map()
    else:
        logging.error("Can't reach host")
        sys.exit()
