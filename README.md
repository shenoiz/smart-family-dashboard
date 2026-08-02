![CI](https://github.com/YOUR_USERNAME/smart-family-dashboard/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3-black?logo=flask)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-Zero%202W-C51A4A?logo=raspberrypi&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-In%20Progress-orange)

# 🏠 Smart Family Dashboard

> A Raspberry Pi Zero 2W powered smart home dashboard for our family —
> built entirely from scratch as my first hardware + software project.

![Dashboard Preview](docs/dashboard-photo.jpg)

---

## About

This is a wall-mounted smart dashboard running on a Raspberry Pi Zero 2W
connected to a 15" display. It shows live weather, a shared family to-do list
managed via Telegram from our phones, and a rotating slideshow of family
photos pulled automatically from Google Drive.

The Pi uses a radar sensor to detect when someone enters the room and turns
the screen on — turning it off again after two minutes of no presence.
Everything is controlled from Telegram: adding and completing tasks,
controlling smart home devices, and receiving Good Morning updates.

The entire project is deployed automatically — pushing code to GitHub triggers
tests, and a passing merge to `main` auto-deploys to the Pi via SSH.

---

## Features

- 📋 **Shared family to-do lists** — managed via Telegram bot (`/add`, `/done`, `/list`)
- 🌤️ **Live weather display** — fetches from OpenWeatherMap every 30 minutes
- 📸 **Family photo slideshow** — auto-syncs from a shared Google Drive folder
- 📡 **Presence detection** — LD2410C radar sensor turns screen on/off automatically
- ☀️ **Good Morning routine** — banner + audio cheer every day at 7:05 AM
- 🔊 **Audio alerts** — plays a sound when a new task is added
- 🏠 **Smart home control** — plain-text MQTT commands via Telegram (`lights on`, `fan off`)
- 🌙 **Auto shutdown** — Pi shuts down at 11 PM, back on at 7 AM via Wake-on-LAN
- 🤖 **Full CI/CD pipeline** — GitHub Actions tests + auto-deploys on every merge to `main`

---

## Tech Stack

### Hardware
| Component | Purpose |
|-----------|---------|
| Raspberry Pi Zero 2W | Main compute unit |
| 15" HDMI LCD Display | Dashboard display |
| LD2410C Radar Sensor | Presence detection via UART serial |
| USB Sound Card + Speaker | Audio alerts and Good Morning music |

### Software
| Technology | Role |
|-----------|------|
| Python 3.11 | All backend services |
| Flask + Flask-SocketIO | Local web server + real-time browser push |
| python-telegram-bot | Telegram bot — todos and IoT commands |
| Google Drive API | Photo sync via service account (no OAuth popup) |
| OpenWeatherMap API | Live weather data |
| paho-mqtt | Smart home device control |
| pygame | Audio playback |
| pyserial | Radar sensor UART communication |
| schedule | Timed jobs — good morning, auto shutdown |

### Infrastructure
| Technology | Role |
|-----------|------|
| systemd | Auto-start service on every boot |
| GitHub Actions | CI (lint + tests) and CD (deploy to Pi) |
| Tailscale | Secure network tunnel for remote deployment |
| Chromium kiosk mode | Full-screen browser on the Pi display |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│             YOUR PHONE (Telegram)           │
│   /add me Buy milk  ·  /done me 0           │
│   lights on  ·  fan off                     │
└───────────────────┬─────────────────────────┘
                    │ Telegram API (polling)
┌───────────────────▼─────────────────────────┐
│           RASPBERRY PI ZERO 2W              │
│                                             │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  Flask Server   │  │  Telegram Bot   │  │
│  │  :5000          │◄─│  todos + IoT    │  │
│  └────────┬────────┘  └─────────────────┘  │
│           │                                 │
│  ┌────────▼────────┐  ┌─────────────────┐  │
│  │  Chromium       │  │  Sensor Manager │  │
│  │  (kiosk mode)   │  │  (radar UART)   │  │
│  └─────────────────┘  └─────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Scheduler · Drive Sync · Audio     │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
         │                        │
    15" Display             Smart Home
    (dashboard UI)    (MQTT → lights, fan, TV)
```

---

## CI/CD Pipeline

This project uses GitHub Actions for automated testing and deployment.

### Continuous Integration — runs on every Pull Request

1. Spins up a clean Ubuntu environment on GitHub's servers
2. Installs all Python dependencies from `requirements.txt`
3. Runs `flake8` for code style checking
4. Runs `black --check` for consistent formatting
5. Scans source files for accidentally hardcoded secrets
6. Runs `pytest` unit tests

If any step fails, the PR is blocked from merging.

### Continuous Deployment — runs on merge to `main`

1. GitHub Actions SSH's into the Pi via Tailscale (private network tunnel)
2. Runs `git pull origin main`
3. Runs `pip install -r requirements.txt`
4. Restarts the `dashboard` systemd service
5. Sends a Telegram message confirming the deploy

**Result:** Code change on laptop → tested → live on the Pi within ~2 minutes, zero manual steps.

---

## Getting Started

> 📄 Full step-by-step build guide: [`docs/build-guide.pdf`](docs/build-guide.pdf)

### Prerequisites

- Raspberry Pi Zero 2W with Raspberry Pi OS Lite (64-bit)
- Python 3.11+
- Telegram account and bot token (from [@BotFather](https://t.me/botfather))
- [OpenWeatherMap](https://openweathermap.org) free API key
- Google Cloud service account with Drive API enabled

### Quick Setup

```bash
# Clone the repo
git clone git@github.com:YOUR_USERNAME/smart-family-dashboard.git
cd smart-family-dashboard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .env.example .env
nano .env   # fill in your API keys and credentials

# Run
python main.py
```

Open `http://localhost:5000` in your browser.

### Environment Variables

See [`.env.example`](.env.example) for the full list of required variables.

### Telegram Commands

| Command | Example | What it does |
|---------|---------|-------------|
| `/add me <task>` | `/add me Buy milk` | Adds to your list, updates screen instantly |
| `/add wife <task>` | `/add wife Book dentist` | Adds to wife's list |
| `/done me <number>` | `/done me 0` | Marks your item 0 as done |
| `/done wife <number>` | `/done wife 2` | Marks wife's item 2 as done |
| `/list` | `/list` | Shows both lists with item numbers |
| `/clear all` | `/clear all` | Removes completed items |
| `<device command>` | `lights on` | Sends MQTT command to smart device |

---

## Project Structure

```
smart-family-dashboard/
├── .github/workflows/
│   ├── ci.yml            # lint + tests on every PR
│   └── deploy.yml        # auto-deploy to Pi on merge to main
├── docs/
│   ├── architecture.png
│   ├── dashboard-photo.jpg
│   └── build-guide.pdf
├── static/               # CSS, JS, sound files
├── templates/
│   └── dashboard.html    # the display UI
├── tests/
│   └── test_todos.py
├── app.py                # Flask server + API routes
├── audio_manager.py      # sound alerts
├── config.py             # reads from .env
├── google_drive_sync.py  # Drive photo downloader
├── iot_controller.py     # MQTT smart home commands
├── main.py               # starts all services
├── scheduler.py          # good morning + auto shutdown
├── sensor_manager.py     # radar presence detection
├── telegram_bot.py       # Telegram command handler
├── requirements.txt
├── .env.example          # config template (never commit .env)
├── .gitignore
├── LICENSE
└── README.md
```

---

## What I Learned

I started this project as a complete beginner with no prior coding experience.
Here is what building it taught me:

- **Linux & the terminal** — navigating files, managing processes with systemd, SSH as a daily workflow
- **Python** — from variables and functions through to threading, file I/O, JSON, and calling external APIs
- **Web fundamentals** — how HTTP works, what a web server actually does, and how Flask ties Python to a browser
- **Real-time communication** — how SocketIO creates a live connection so the screen updates the moment a Telegram message is sent
- **APIs** — fetching data from OpenWeatherMap, communicating with Telegram's API, downloading files from Google Drive programmatically
- **Hardware** — UART serial communication, GPIO, wiring sensors, understanding the Pi's pin layout
- **Git & GitHub** — branching, pull requests, commit conventions, managing code across two machines
- **CI/CD** — writing YAML workflows, what automated testing means in practice, and deploying to physical hardware remotely

The hardest part was understanding how all the pieces connect simultaneously — Flask serving a webpage to Chromium on the same Pi, while a Telegram bot thread updates the data that page shows in real time. That mental model took the longest to build.

---

## Roadmap

- [x] Project structure and base Flask server
- [x] Dashboard UI — clock, weather, todo lists, photo slideshow
- [x] Telegram bot — `/add`, `/done`, `/list`, `/clear`
- [ ] Google Drive photo sync
- [ ] Radar sensor wiring and screen on/off
- [ ] Audio alerts and Good Morning routine
- [ ] IoT MQTT device control
- [ ] GitHub Actions CI pipeline
- [ ] Auto-deploy CD pipeline to Pi
- [ ] Physical build — mount display on wall

---

## About Me

I am [Your Name], building this project as my entry into software development
and hardware. I started with zero coding experience and am learning Python,
Linux, and web development by building real things I actually use at home.

📍 [Your City]  
🐙 [github.com/YOUR_USERNAME](https://github.com/YOUR_USERNAME)

---

_Built with ❤️ — and many evenings of learning_
