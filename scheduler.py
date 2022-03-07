from subprocess import call

import time
import os
from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler



def job():
    print("In job")
    call(['python', 'blurred_test/blurred_test.py'])

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.configure(timezone=utc)
    scheduler.add_job(job, trigger='cron', week="*")
    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(5)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()