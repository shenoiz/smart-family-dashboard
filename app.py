from flask import Flask, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO
import json
import requests
import psutil
import os
import glob
import socket
import time
from config import PROKERALA_CLIENT_ID, PROKERALA_CLIENT_SECRET
from datetime import datetime
from config import OPENWEATHER_API_KEY, CITY, WEATHER_UNITS, PHOTOS_DIR
from datetime import datetime as dt

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route("/")
def index():
    return render_template("dashboard.html")


@app.route("/api/todos")
def get_todos():
    try:
        with open("data/todos.json") as f:
            return jsonify(json.load(f))
    except Exception:
        return jsonify({"him": [], "her": []})


@app.route("/api/weather")
def get_weather():
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={CITY}&appid={OPENWEATHER_API_KEY}&units={WEATHER_UNITS}"
        )

        r = requests.get(url, timeout=5)
        d = r.json()

        return jsonify(
            {
                "temp": round(d["main"]["temp"]),
                "feels_like": round(d["main"]["feels_like"]),
                "description": d["weather"][0]["description"].title(),
                "icon": d["weather"][0]["icon"],
                "humidity": d["main"]["humidity"],
                "wind": round(d["wind"]["speed"] * 3.6),
                "city": d["name"],
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/photos")
def get_photos():
    photos = (
        glob.glob(f"{PHOTOS_DIR}/*.jpg")
        + glob.glob(f"{PHOTOS_DIR}/*.jpeg")
        + glob.glob(f"{PHOTOS_DIR}/*.png")
    )

    return jsonify([os.path.basename(p) for p in photos])


@app.route("/photos/<filename>")
def serve_photo(filename):
    return send_from_directory(PHOTOS_DIR, filename)


@app.route("/api/forecast")
def get_forecast():
    # 5-day forecase, one reading per day (picked from the ~midday slot)
    try:
        url = (
            f"https://api.openweathermap.org/data/2.5/forecast"
            f"?q={CITY}&appid={OPENWEATHER_API_KEY}&units={WEATHER_UNITS}"
        )

        r = requests.get(url, timeout=5)
        d = r.json()

        daily = {}
        for entry in d["list"]:
            date = entry["dt_txt"].split(" ")[0]  # e.g. '2026-08-01'
            hour = entry["dt_txt"].split(" ")[1]  # e.g. '12:00:00'
            # Keep the reading closet to midday for each date
            if date not in daily or hour == "12:00:00":
                daily[date] = entry

        days = list(daily.values())[:5]
        result = []
        for day in days:
            dt = datetime.fromtimestamp(day["dt"])
            result.append(
                {
                    "day": dt.strftime("%a"),
                    "temp": round(day["main"]["temp"]),
                    "icon": day["weather"][0]["icon"],
                }
            )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/network")
def get_network():
    # Gets the Pi's actual local IP address on the LAN
    try:
        # this trick doesn't actually send data anywhere - it just asks the OS
        # which local interface it would use to reach an  external address,
        # which realiability gives the realLAN IP even with multiple interfaces
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return jsonify({"ip": ip})
    except Exception as e:
        return jsonify({"ip": None, "error": str(e)}), 500


@app.route("/api/system")
def get_system():
    # Real CPU and RAM usage from the Pi itself
    try:
        cpu = psutil.cpu_percent(interval=0.3)
        ram = psutil.virtual_memory().percent
        return jsonify({"cpu": round(cpu), "ram": round(ram)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Simple in-memory cashe so we only call Wikipedia once per day, not on every poll
_today_cache = {"date": None, "data": None}


#@app.route("/api/today")
#def get_today():
#    today = dt.now().strftime("%m/%d")
#    global _today_cache

    # Return cached result if we already fetched it today
#    if _today_cache["date"] == today and _today_cache["data"]:
#        return jsonify(_today_cache["data"])
#    try:
#        month, day = today.split("/")
#        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/{month}/{day}"
#        r = requests.get(url, timeout=6, headers={"User-Agent": "SmartDashboard/1.0"})
#        events = r.json().get("selected", [])[:3]  # top 3 highlights

#        result = {
#            "events": [
#                {"year": e.get("year"), "text": e.get("text", "")[:90]} for e in events
#            ]
#        }
#        _today_cache = {"date": today, "data": result}
#        return jsonify(result)
#    except Exception as e:
#        return jsonify({"events": [], "error": str(e)}), 500


@app.route('/api/today')
def get_today():
    today = dt.now().strftime('%m/%d')
    global _today_cache

    if _today_cache['date'] == today and _today_cache['data']:
        return jsonify(_today_cache['data'])

    try:
        month, day = today.split('/')
        url = f'https://en.wikipedia.org/api/rest_v1/feed/onthisday/selected/{month}/{day}'
        r = requests.get(url, timeout=6, headers={'User-Agent': 'SmartDashboard/1.0'})
        raw_events = r.json().get('selected', [])

        # Filter out war/violence/death-heavy content — not appropriate
        # for a family display. Better to show fewer, gentler facts than
        # a grim one every single day.
        BLOCKED_WORDS = [
            'killed', 'dead', 'death', 'war', 'bomb', 'attack', 'massacre',
            'assassinat', 'terror', 'genocide', 'invasion', 'execution',
            'shooting', 'explosion', 'coup', 'battle', 'casualties',
            'wounded', 'militant', 'airstrike', 'conflict', 'uprising'
        ]

        safe_events = []
        for e in raw_events:
            text = e.get('text', '').lower()
            if not any(word in text for word in BLOCKED_WORDS):
                safe_events.append(e)

        events = safe_events[:3]

        result = {
            'events': [
                {'year': e.get('year'), 'text': e.get('text', '')[:90]}
                for e in events
            ]
        }
        _today_cache = {'date': today, 'data': result}
        return jsonify(result)
    except Exception as e:
        return jsonify({'events': [], 'error': str(e)}), 500



# ── Prokerala OAuth2 token cache ─────────────────────────────────────────
_prokerala_token = {"value": None, "expires_at": 0}


def get_prokerala_token():
    """Get a cached access token, or fetch a new one if expired."""
    global _prokerala_token
    if _prokerala_token["value"] and time.time() < _prokerala_token["expires_at"]:
        return _prokerala_token["value"]

    resp = requests.post(
        "https://api.prokerala.com/token",
        data={
            "grant_type": "client_credentials",
            "client_id": PROKERALA_CLIENT_ID,
            "client_secret": PROKERALA_CLIENT_SECRET,
        },
        timeout=6,
    )
    data = resp.json()
    token = data["access_token"]
    expires_in = data.get("expires_in", 3600)

    # Refresh 60 seconds before actual expiry, as a safety margin
    _prokerala_token = {"value": token, "expires_at": time.time() + expires_in - 60}
    return token


# ── Panchang cache — one call per day, same pattern as /api/today ───────
_panchang_cache = {"date": None, "data": None}


@app.route("/api/panchang")
def get_panchang():
    from config import PROKERALA_LATITUDE, PROKERALA_LONGITUDE

    today = datetime.now().strftime("%Y-%m-%d")
    global _panchang_cache

    if _panchang_cache["date"] == today and _panchang_cache["data"]:
        return jsonify(_panchang_cache["data"])

    try:
        token = get_prokerala_token()
        resp = requests.get(
            "https://api.prokerala.com/v2/astrology/panchang",
            headers={"Authorization": f"Bearer {token}"},
            params={
                "ayanamsa": 1,
                "coordinates": f"{PROKERALA_LATITUDE},{PROKERALA_LONGITUDE}",
                "datetime": datetime.now().astimezone().isoformat(),
            },
            timeout=6,
        )
        raw = resp.json()
        data = raw.get("data", {})

        result = {
            "tithi": (
                data.get("tithi", [{}])[0].get("name") if data.get("tithi") else None
            ),
            "nakshatra": (
                data.get("nakshatra", [{}])[0].get("name")
                if data.get("nakshatra")
                else None
            ),
            "vaara": data.get("vaara"),
            "festivals": (
                [f.get("name") for f in data.get("festivals", [])]
                if data.get("festivals")
                else []
            ),
        }

        # Ekadashi is simply the 11th tithi of each lunar fortnight — it's a
        # fixed, well-known rule, so we can detect it directly from the tithi
        # name we already have instead of needing a second, separate API.
        tithi_name = result["tithi"] or ""
        if "ekadashi" in tithi_name.lower():
            result["festivals"].append("Ekadashi Vrat")

        _panchang_cache = {"date": today, "data": result}
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@socketio.on("connect")
def on_connect():
    print(f"Browser connected at {datetime.now()}")


def notify_todo_update():
    # Called by telegram_bot.py — pushes instant update to browser
    socketio.emit("todo_update", {"ts": datetime.now().isoformat()})


if __name__ == "__main__":
    socketio.run(
        app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True
    )
