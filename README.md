![CI](https://github.com/shenoiz/smart-family-dashboard/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-black?logo=flask)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202W-C51A4A?logo=raspberrypi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-In%20Progress-orange)



# 🏠 Smart Family Dashboard

> A Raspberry Pi Zero 2W powered smart home dashboard
> for our family — built entirely from scratch as my
> first hardware + software project.


## About

This is a wall-mounted smart dashboard running on a Raspberry Pi Zero 2W
connected to a 15" display. It shows live weather, a shared family to-do list
(managed via Telegram from our phones), and a rotating slideshow of family
photos pulled automatically from Google Drive.

The Pi uses a radar sensor to detect when someone enters the room and turns
the screen on — turning it off again after two minutes of no presence.
Everything is controlled from Telegram: adding and completing tasks,
controlling smart home devices, and receiving Good Morning updates.

The entire project is deployed automatically — pushing code to GitHub triggers
tests, and a passing merge to `main` auto-deploys to the Pi via SSH.


## Features

- 📋 **Shared family to-do lists** — managed via Telegram bot (`/add`, `/done`, `/list`)
- 🌤️ **Live weather display** — fetches from OpenWeatherMap every 30 minutes
- 📸 **Family photo slideshow** — auto-syncs from a shared Google Drive folder
- 📡 **Presence detection** — LD2410C radar sensor turns screen on/off automatically
- ☀️ **Good Morning routine** — banner + audio cheer every day at 7:05 AM
- 🔊 **Audio alerts** — plays a sound when a new task is added
- 🏠 **Smart home control** — send plain-text MQTT commands via Telegram
- 🌙 **Auto shutdown** — Pi shuts down at 11 PM, restarts at 7 AM
- 🤖 **Full CI/CD pipeline** — GitHub Actions tests + auto-deploys on every merge

## Tech Stack

### Hardware
| Component | Purpose |
|-----------|---------|
| Raspberry Pi Zero 2W | Main compute unit |
| 15" HDMI LCD Display | Dashboard display |
| LD2410C Radar Sensor | Presence detection via UART |
| USB Sound Card + Speaker | Audio alerts |

### Software
| Technology | Role |
|-----------|------|
| Python 3.11 | All backend services |
| Flask + Flask-SocketIO | Local web server + real-time push |
| python-telegram-bot | Telegram bot (todos + IoT commands) |
| Google Drive API | Photo sync via service account |
| OpenWeatherMap API | Live weather data |
| paho-mqtt | Smart home device control |
| pygame | Audio playback |
| pyserial | Radar sensor communication |
| schedule | Timed jobs (good morning, shutdown) |

### Infrastructure
| Technology | Role |
|-----------|------|
| systemd | Auto-start service on boot |
| GitHub Actions | CI (lint + tests) + CD (deploy to Pi) |
| Tailscale | Secure network tunnel for remote deploy |
| Chromium (kiosk mode) | Full-screen browser on the Pi |


## Architecture

```
┌─────────────────────────────────────────┐
│           YOUR PHONE (Telegram)         │
│  /add me Buy milk · /done me 0          │
│  lights on · fan off                    │
└──────────────────┬──────────────────────┘
                   │ Telegram API (polling)
┌──────────────────▼──────────────────────┐
│          RASPBERRY PI ZERO 2W           │
│                                         │
│  ┌──────────────┐   ┌────────────────┐  │
│  │ Flask Server │   │ Telegram Bot   │  │
│  │ :5000        │◄──│ (todos + IoT)  │  │
│  └──────┬───────┘   └────────────────┘  │
│         │                               │
│  ┌──────▼───────┐   ┌────────────────┐  │
│  │ Chromium     │   │ Sensor Manager │  │
│  │ (kiosk mode) │   │ (radar UART)   │  │
│  └──────────────┘   └────────────────┘  │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │ Scheduler · Drive Sync · Audio  │    │
│  └─────────────────────────────────┘    │
└──────────────────────────────────────── ┘
         │                    │
    15" Display          Smart Home
    (dashboard)     (lights, fan via MQTT)
```


## CI/CD Pipeline

This project uses GitHub Actions for automated testing and deployment.

### Continuous Integration (on every Pull Request)
1. Spins up a clean Ubuntu environment
2. Installs all Python dependencies
3. Runs `flake8` for code style checking
4. Runs `black --check` for formatting
5. Scans source files for accidentally committed secrets
6. Runs `pytest` unit tests

If any step fails, the PR is blocked from merging.

### Continuous Deployment (on merge to `main`)
1. GitHub Actions SSH's into the Pi via Tailscale
2. Runs `git pull origin main`
3. Runs `pip install -r requirements.txt`
4. Restarts the `dashboard` systemd service
5. Sends a Telegram notification confirming deploy

**Result:** Push code from your laptop → tested → live on the Pi within ~2 minutes,
with zero manual steps.

## Getting Started

> Full step-by-step guide available in [`docs/build-guide.pdf`](docs/build-guide.pdf)

### Prerequisites
- Raspberry Pi Zero 2W with Raspberry Pi OS Lite (64-bit)
- Python 3.11+
- A Telegram account + bot token (from @BotFather)
- OpenWeatherMap free API key
- Google Cloud service account with Drive API enabled

### Quick Setup
```bash
# Clone the repo
git clone git@github.com:shenoiz/smart-family-dashboard.git
cd smart-family-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
nano .env  # fill in your API keys

# Run
python main.py
```

Open `http://localhost:5000` in your browser.

### Environment Variables
See [`.env.example`](.env.example) for the full list of required variables.
