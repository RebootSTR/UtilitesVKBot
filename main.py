# @rebootstr

import os
import time

if __name__ == '__main__':
    start_time = int(time.time())
    while True:
        os.system(f"python3.8 bot.py -start_time {start_time}")
        os.system("git pull")
