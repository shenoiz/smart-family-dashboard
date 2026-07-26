import pygame
import threading
import os

pygame.mixer.init()  # initialise once at startup

SOUNDS = {
    'todo_added': 'static/sounds/todo_added.wav',
    'good_morning': 'static/sounds/good_morning.wav',
    'alert': 'static/sounds/alert.mp3',
}


def play_sound(name: str):
    """Play a sound in a background thread (non-blocking)"""

    def _play():
        try:
            path = SOUNDS.get(name)

            if path and os.path.exists(path):
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()

        except Exception as e:
            print(f'Audio error: {e}')

    threading.Thread(target=_play, daemon=True).start()


def set_volume(level: float):
    pygame.mixer.music.set_volume(
        max(0.0, min(1.0, level))
    )
