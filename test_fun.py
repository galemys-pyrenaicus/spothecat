import gmplot
import json
import subprocess
import signal
import paramiko
import time, threading
import traceback
import logging
import configparser
import os
import sys
import server

def main():
    all_cred = server.pass_config()
    dbcred = all_cred[0]
    ffoncred = all_cred[1]
    gmapcred = all_cred[2]
    logs = all_cred[3]
    srv = all_cred[4]
    logformat = ['%(asctime)s [%(levelname)s] - %(message)s', '%d-%b-%y %H:%M:%S']

if __name__ == "__main__":
    main()
