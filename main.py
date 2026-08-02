"""
main.py — starts all dashboard services together.
Run: python main.py
"""

import threading

import telegram_bot
import scheduler
import google_drive_sync

from app import app, socketio

if __name__ == '__main__':
    print('Starting Smart Family Dashboard...')

    services = [
        ('Telegram bot', telegram_bot.start_bot),
        ('Scheduler', scheduler.start),
        ('Drive sync', google_drive_sync.start),
    ]

    for name, fn in services:
        t = threading.Thread(
            target=fn,
            daemon=True,
            name=name
        )
        t.start()

        print(f' Started: {name}')

    print('Starting web server on port 5000...')

    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
