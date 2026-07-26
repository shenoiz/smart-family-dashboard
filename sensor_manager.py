import serial, threading, time, subprocess
from config import RADAR_SERIAL_PORT, SCREEN_TIMEOUT_SECONDS

screen_is_on = True
last_presence = time.time()

def screen_off():
    global screen_is_on
    subprocess.run(['vcgencmd', 'display_power', '0'])
    screen_is_on = False
    print('Screen OFF')

def screen_on():
    global screen_is_on
    subprocess.run(['vcgencmd', 'display_power', '1'])
    screen_is_on = True
    print('Screen ON')

def watchdog():
    """Checks every 10s whether to turn the screen off"""
    while True:
        if time.time() - last_presence > SCREEN_TIMEOUT_SECONDS and screen_is_on:
            screen_off()
        time.sleep(10)

def read_radar():
    """LD2410C sends data over UART — presence = 0xF4 byte in frame"""
    global last_presence, screen_is_on

    try:
        ser = serial.Serial(RADAR_SERIAL_PORT, 256000, timeout=1)
        print(f'Radar connected on {RADAR_SERIAL_PORT}')

        while True:
            data = ser.read(64)

            if data and b'\xf4' in data:
                last_presence = time.time()

                if not screen_is_on:
                    screen_on()

    except Exception as e:
        print(f'Radar not connected ({e}) — screen stays on')
        screen_on()  # fail safe

def start():
    threading.Thread(target=read_radar, daemon=True).start()
    threading.Thread(target=watchdog, daemon=True).start()
