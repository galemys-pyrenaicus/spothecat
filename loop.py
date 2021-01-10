import getinfo
import time, threading
import sys

def main():
    delay = int(getinfo.getdelay())
    while True:
        try:
            f = open('/tmp/spot', 'r')
        except:
            sys.exit()

        getinfo.main()
        time.sleep(delay)

if __name__ == "__main__":
    main()
