import schedule
import time
import subprocess

from audio_manager import play_sound
from config import SHUTDOWN_TIME, GOOD_MORNING_TIME


def good_morning():
    print('Good morning routine!')
    play_sound('good_morning')

    # Visual banner is handled by the JS clock check


def auto_shutdown():
    print('Auto shutdown...')
    subprocess.run(['sudo', 'shutdown', '-h', 'now'])


def start():
    schedule.every().day.at(GOOD_MORNING_TIME).do(good_morning)
    schedule.every().day.at(SHUTDOWN_TIME).do(auto_shutdown)

    print(
        f'Scheduler: good morning {GOOD_MORNING_TIME}, '
        f'shutdown {SHUTDOWN_TIME}'
    )

    while True:
        schedule.run_pending()
        time.sleep(30)
