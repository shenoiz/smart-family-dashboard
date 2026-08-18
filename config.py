import os
from dotenv import load_dotenv

load_dotenv()  # reads .env file into environment variables
# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_USERS = [
    int(os.getenv("TELEGRAM_USER_ID_YOU", 0)),
    int(os.getenv("TELEGRAM_USER_ID_WIFE", 0)),
]
# Weather
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
CITY = os.getenv("CITY", "London")
WEATHER_UNITS = os.getenv("WEATHER_UNITS", "metric")
# Google Drive
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
PHOTOS_DIR = "data/photos"
PHOTO_REFRESH_HOURS = 6
# Display
SLIDESHOW_INTERVAL_SECONDS = 3600
# Schedule
SHUTDOWN_TIME = os.getenv("SHUTDOWN_TIME", "23:00")
GOOD_MORNING_TIME = os.getenv("GOOD_MORNING_TIME", "07:05")
# ProKerala astrocalender API
PROKERALA_CLIENT_ID = os.getenv("PROKERALA_CLIENT_ID")
PROKERALA_CLIENT_SECRET = os.getenv("PROKERALA_CLIENT_SECRET")
PROKERALA_LATITUDE = os.getenv("PROKERALA_LATITUDE")
PROKERALA_LONGITUDE = os.getenv("PROKERALA_LONGITUDE")
