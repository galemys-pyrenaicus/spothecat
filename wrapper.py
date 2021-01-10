import getinfo
import os
import subprocess
import loop
import sys

def main():
    stop()

def start():
    f = open('/tmp/spot', 'w+')
    f.write("d63d0e21fdc05f618d55ef306c54af82:13288442151473")
    p = subprocess.Popen([sys.executable, 'loop.py'])

def stop():
    try:
        os.remove('/tmp/spot')
    except:
        print("Nice")

if __name__ == "__main__":
    main()
