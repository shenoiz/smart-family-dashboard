import schedule
import time
import subprocess
import RPi.GPIO as GPIO

from audio_manager import play_sound
from config import SHUTDOWN_TIME, GOOD_MORNING_TIME

RELAY_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(RELAY_PIN, GPIO.OUT)


def press_power_button():
    GPIO.output(RELAY_PIN, GPIO.HIGH)
    time.sleep(0.3)
    GPIO.output(RELAY_PIN, GPIO.LOW)


def good_morning():
    print('Good morning routine!')
    press_power_button()
    play_sound('good_morning')


def screen_off():
    print('Screen off...')
    press_power_button()


def start():
    schedule.every().day.at(GOOD_MORNING_TIME).do(good_morning)
    schedule.every().day.at(SHUTDOWN_TIME).do(screen_off)

    print(
        f'Scheduler: good morning {GOOD_MORNING_TIME}, '
        f'screen off {SHUTDOWN_TIME}'
    )

    while True:
        schedule.run_pending()
        time.sleep(30)
