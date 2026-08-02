import os
from dotenv import load_dotenv
load_dotenv() # reads .env file into environment variables
# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALLOWED_USERS = [
int(os.getenv('TELEGRAM_USER_ID_YOU', 0)),
int(os.getenv('TELEGRAM_USER_ID_WIFE', 0)),
]
# Weather
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
CITY = os.getenv('CITY', 'London')
WEATHER_UNITS = os.getenv('WEATHER_UNITS', 'metric')
# Google Drive
GOOGLE_DRIVE_FOLDER_ID = os.getenv('GOOGLE_DRIVE_FOLDER_ID')
PHOTOS_DIR = 'data/photos'
PHOTO_REFRESH_HOURS = 6
# Display
SLIDESHOW_INTERVAL_SECONDS = 3600
# Schedule
SHUTDOWN_TIME = os.getenv('SHUTDOWN_TIME', '23:00')
GOOD_MORNING_TIME = os.getenv('GOOD_MORNING_TIME', '07:05')
# MQTT / IoT
MQTT_BROKER = os.getenv('MQTT_BROKER', '192.168.1.100')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))
MQTT_USERNAME = os.getenv('MQTT_USERNAME')
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD')
# IoT command map: telegram text -> (mqtt_topic, payload)
IOT_DEVICES = {
'lights on': ('home/living/lights', 'ON'),
'lights off': ('home/living/lights', 'OFF'),
'fan on': ('home/bedroom/fan', 'ON'),
'fan off': ('home/bedroom/fan', 'OFF'),
}
#ProKerala astrocalender API
PROKERALA_CLIENT_ID     = os.getenv('PROKERALA_CLIENT_ID')
PROKERALA_CLIENT_SECRET = os.getenv('PROKERALA_CLIENT_SECRET')
PROKERALA_LATITUDE      = os.getenv('PROKERALA_LATITUDE')
PROKERALA_LONGITUDE     = os.getenv('PROKERALA_LONGITUDE')
