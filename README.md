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
connected to a 15" display. It shows live weather with a 5-day forecast, a
shared Him/Her to-do list managed via Telegram from our phones, a rotating
slideshow of family photos pulled automatically from Google Drive, today's
Hindu Panchang (tithi, nakshatra, vaara), and world history facts for the day.

Everything is controlled from Telegram: adding and completing tasks,
controlling smart home devices, and receiving Good Morning updates.

The entire project is deployed automatically — pushing code to GitHub triggers
tests, and a passing merge to `main` auto-deploys to the Pi via SSH.

---

## Features

- 📋 **Shared Him/Her to-do lists** — managed via Telegram bot (`/add`, `/done`, `/list`, `/clear`)
- 🌤️ **Live weather + 5-day forecast** — fetches from OpenWeatherMap, auto-refreshes
- 📸 **Family photo slideshow** — auto-syncs from a shared Google Drive folder, fixed-frame display regardless of photo orientation
- 🕉️ **Hindu Panchang** — today's tithi, nakshatra, vaara, and Ekadashi detection via Prokerala API
- 🌍 **On This Day** — real world history facts pulled from Wikipedia's public API
- ☀️ **Good Morning routine** — banner + audio cheer every day at 7:05 AM
- 🔊 **Audio alerts** — plays a sound when a new task is added
- 🏠 **Smart home control** — plain-text MQTT commands via Telegram (`lights on`, `fan off`)
- 🌙 **Auto shutdown** — Pi shuts down at 11 PM, back on at 7 AM
- 📡 **Live system status** — CPU/RAM usage and local IP shown on-screen for quick SSH access
- 🔄 **Auto-scrolling lists** — todo lists slowly scroll when content overflows the visible area
- 🤖 **Full CI/CD pipeline** — GitHub Actions tests + auto-deploys on every merge to `main`

---

## Tech Stack

### Hardware
| Component | Purpose |
|-----------|---------|
| Raspberry Pi Zero 2W | Main compute unit |
| 15" HDMI LCD Display | Dashboard display |
| USB Sound Card + Speaker | Audio alerts and Good Morning music |

### Software
| Technology | Role |
|-----------|------|
| Python 3.11 | All backend services |
| Flask + Flask-SocketIO | Local web server + real-time browser push |
| python-telegram-bot | Telegram bot — todos and IoT commands |
| Google Drive API | Photo sync via service account (no OAuth popup) |
| OpenWeatherMap API | Live weather + 5-day forecast |
| Prokerala API | Hindu Panchang — tithi, nakshatra, vaara |
| Wikipedia REST API | "On This Day" world history facts |
| paho-mqtt | Smart home device control |
| pygame | Audio playback |
| psutil | Real-time CPU/RAM stats for the dashboard |
| schedule | Timed jobs — good morning, auto shutdown |

### Infrastructure
| Technology | Role |
|-----------|------|
| systemd | Auto-start service on every boot |
| GitHub Actions | CI (lint + tests) and CD (deploy to Pi) |
| Tailscale | Secure network tunnel for remote deployment |
| Epiphany (WebKitGTK) | Lightweight kiosk browser — chosen over Chromium for the Pi Zero's 512MB RAM |

---

## Architecture

```
┌─────────────────────────────────────────────┐
│             YOUR PHONE (Telegram)           │
│   /add him Buy milk  ·  /done her 0         │
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
│  │  Epiphany       │  │  Scheduler      │  │
│  │  (kiosk mode)   │  │  (good morning, │  │
│  │                 │  │   auto shutdown)│  │
│  └─────────────────┘  └─────────────────┘  │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │  Drive Sync · Audio · Weather ·     │   │
│  │  Panchang · On This Day             │   │
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

## System Dependencies

`requirements.txt` only lists **Python packages** — libraries imported directly
in the `.py` files. It intentionally does not include system-level tools
installed via `apt`, since `pip` has no way to install or track those. This
project depends on both, and a full rebuild needs both layers.

### Installed via `apt` (system packages)

| Package | Purpose |
|---------|---------|
| `git` | Version control |
| `python3-pip`, `python3-venv` | Python environment tooling |
| `xserver-xorg`, `x11-xserver-utils`, `xinit`, `openbox` | Minimal X11 display server + window manager for kiosk mode |
| `epiphany-browser` | Lightweight WebKitGTK kiosk browser — used instead of Chromium, which is too heavy for the Pi Zero's 512MB RAM |
| `unclutter` | Hides the mouse cursor on the kiosk display |
| `python3-pygame` | System-level pygame dependencies for audio playback |
| `mpg123`, `alsa-utils` | Audio decoding and ALSA configuration tools |
| `sox`, `libsox-fmt-mp3` | Used to generate/verify test audio files locally without downloading from third parties |
| `htop`, `nano` | General admin convenience |

Install these with:
```bash
sudo apt update
sudo apt install -y git python3-pip python3-venv \
  xserver-xorg x11-xserver-utils xinit openbox \
  epiphany-browser unclutter \
  python3-pygame mpg123 alsa-utils \
  sox libsox-fmt-mp3 htop nano
```

### Installed via `pip` (Python packages)

See [`requirements.txt`](requirements.txt) — generated directly from the
working environment with `pip freeze > requirements.txt` to guarantee it
matches what's actually installed, rather than a hand-maintained list that
can drift out of sync.

### Why the split matters

A common beginner mistake (made once during this build) is assuming
`pip list` should show everything the project depends on — including the
browser. It won't. System tools like Epiphany, `sox`, and `tmux` are tracked
by `dpkg`/`apt`, not `pip`, because they aren't Python libraries. Keeping
this list here means a full rebuild only needs two commands — the `apt`
block above, then `pip install -r requirements.txt` — instead of
re-discovering missing system tools one broken feature at a time.

---

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
| `/add him <task>` | `/add him Buy milk` | Adds to Him's list, updates screen instantly |
| `/add her <task>` | `/add her Book dentist` | Adds to Her's list |
| `/done him <number>` | `/done him 0` | Marks Him's item 0 as done |
| `/done her <number>` | `/done her 2` | Marks Her's item 2 as done |
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
- **Hardware** — GPIO, UART serial communication, wiring and debugging sensors (including diagnosing and ultimately retiring a faulty motion sensor), understanding the Pi's pin layout
- **Git & GitHub** — branching, pull requests, commit conventions, managing code across two machines
- **CI/CD** — writing YAML workflows, what automated testing means in practice, and deploying to physical hardware remotely

The hardest part was understanding how all the pieces connect simultaneously — Flask serving a webpage to the kiosk browser on the same Pi, while a Telegram bot thread updates the data that page shows in real time. That mental model took the longest to build.

---

## Roadmap

- [x] Project structure and base Flask server
- [x] Dashboard UI — clock, weather, todo lists, photo slideshow
- [x] Telegram bot — `/add`, `/done`, `/list`, `/clear`
- [x] Google Drive photo sync
- [x] Audio alerts and Good Morning routine
- [x] IoT MQTT device control
- [x] 5-day weather forecast
- [x] Hindu Panchang + On This Day world facts
- [x] Live CPU/RAM/IP status on-screen
- [x] Switched Chromium → Epiphany for lower memory usage on Pi Zero
- [x] GitHub Actions CI pipeline
- [x] Auto-deploy CD pipeline to Pi
- [ ] Physical build — mount display on wall

**Note on presence detection:** an RCWL-0516 radar sensor was wired up to
auto turn the screen on/off based on room presence. After isolating and
testing it directly against raw GPIO (ruling out interference, wiring, and
code issues one at a time), the unit itself proved unreliable and was
removed from the project rather than kept as a flaky feature. The screen
now stays on continuously, with the existing scheduled shutdown handling
overnight power-down. Revisiting this with a different sensor is a
possible future addition.

---
_Built with ❤️ — and many evenings of learning_
