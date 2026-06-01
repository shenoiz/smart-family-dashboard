from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
import json
import requests
import os
import glob
from datetime import datetime
from config import OPENWEATHER_API_KEY, CITY, WEATHER_UNITS, PHOTOS_DIR

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')


@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/api/todos')
def get_todos():
    try:
        with open('data/todos.json') as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify({
            'yours': [],
            'wife': []
        })


@app.route('/api/weather')
def get_weather():
    try:
        url = (
            f'https://api.openweathermap.org/data/2.5/weather'
            f'?q={CITY}&appid={OPENWEATHER_API_KEY}&units={WEATHER_UNITS}'
        )

        r = requests.get(url, timeout=5)
        d = r.json()

        return jsonify({
            'temp': round(d['main']['temp']),
            'feels_like': round(d['main']['feels_like']),
            'description': d['weather'][0]['description'].title(),
            'icon': d['weather'][0]['icon'],
            'humidity': d['main']['humidity'],
            'city': d['name'],
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/photos')
def get_photos():
    photos = (
        glob.glob(f'{PHOTOS_DIR}/*.jpg') +
        glob.glob(f'{PHOTOS_DIR}/*.jpeg') +
        glob.glob(f'{PHOTOS_DIR}/*.png')
    )

    return jsonify([
        os.path.basename(p)
        for p in photos
    ])


@app.route('/photos/<filename>')
def serve_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)


@socketio.on('connect')
def on_connect():
    print(f'Browser connected at {datetime.now()}')


def notify_todo_update():
    # Called by telegram_bot.py — pushes instant update to browser
    socketio.emit(
        'todo_update',
        {'ts': datetime.now().isoformat()}
    )


if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False
    )
