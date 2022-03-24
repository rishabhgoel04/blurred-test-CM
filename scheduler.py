import time
import os
from pytz import utc
from import_modules import *
from helper import *
from blurred_test import run
from apscheduler.schedulers.background import BackgroundScheduler

# def job():
#     print("In job")
#     call(['python', 'blurred_test.py'])

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(func=run, trigger='cron', day_of_week=3, hour=9, minute=38)
    # scheduler.add_job(, trigger='cron', day_of_week=3, hour=7, minute=13)
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()