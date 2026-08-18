# System Notes — The Kiosk Boot Chain

This document exists because none of what follows is captured in code
comments or commit messages, and a lot of it does not look logical on
paper. It was arrived at by testing directly on the physical Pi, watching
what actually happened on the screen, and adjusting from real evidence —
not from theory. If you are rebuilding this project, or debugging a
similar Pi kiosk setup, this is the part that will actually save you time.

---

## The goal

The Pi should power on and, with zero keyboard, zero mouse, and zero
manual commands, end up showing the dashboard full screen — no address
bar, no visible cursor, nothing else on screen.

## The short version of what works

1. **lightdm** manages login and starts a graphical session automatically
   as a specific user, with no password prompt.
2. That session runs **Openbox** — a minimal window manager.
3. Openbox's `autostart` file launches **Epiphany** in incognito mode
   pointed at `http://localhost:5000`.
4. The script actively waits for the *real* browser window to exist
   (not a hidden helper window Epiphany also creates), waits for the
   page to fully settle, then uses **wmctrl** to force it fullscreen and
   **xdotool** to send the F11 key directly to that window.
5. The mouse cursor is then moved to the bottom of the screen on purpose,
   because moving it near the top edge re-reveals the browser's own
   hover overlay — an intended browser feature, not a bug, but one that
   looks exactly like "fullscreen turned off" if you don't know that's
   what it is.

Every one of the five steps above replaced something that looked
reasonable but genuinely did not work on this hardware. What follows is
why, in the order it was actually discovered.

---

## Attempt 1 — plain `startx` from `.bash_profile`, no window manager

**What was tried:** a script in `~/.bash_profile`, triggered only when
logging in on the physical console (tty1), that ran
`startx -- :0 vt1 &`, waited for the X server to respond, then launched
Epiphany directly with `DISPLAY=:0`.

**What actually happened, over several separate failures:**

- `xf86OpenConsole: Cannot open virtual console 1 (Permission denied)`
  — the console device (`/dev/tty0`, and later `/dev/tty1`/`/dev/tty2`)
  did not have the permission bits needed for a normal user session to
  claim it. Fixed once with a `udev` rule granting the `tty` group
  read/write on the console devices — but this was a one-off manual fix,
  not something that survives a fresh setup, and later resurfaced in a
  different form.
- `xf86OpenConsole: Switching VT failed` — a race between the login
  shell still finishing its own setup on tty1 and X trying to claim that
  same VT at almost the same moment.
- Fullscreen itself was unreliable even once X started, because **there
  was no window manager running at all.** `xdotool windowactivate`
  failed outright with:
  `Your windowmanager claims not to support _NET_ACTIVE_WINDOW`
  — this is not an Epiphany or xdotool bug. Fullscreen, window
  activation, and window focus are all responsibilities that belong to a
  window manager in X11. The raw X server does not implement any of it.
  Running Epiphany with nothing managing its window meant every
  fullscreen attempt was fighting against having nothing to actually
  execute the request.

**Why this whole approach was abandoned:** it is possible to make a
window manager-free X session work, but every one of X11's window
placement and state conventions needs to be either simulated by hand or
skipped, and that meant fixing an ever-growing list of edge cases one at
a time. The actual fix was to stop avoiding a window manager and use one
properly.

---

## Attempt 2 — Matchbox window manager

**What was tried:** `matchbox-window-manager`, a genuinely minimal
window manager built for embedded kiosk displays, launched from the same
`.bash_profile` script right after `startx`.

**What happened:** X itself began failing to start at all on this
attempt, with the same VT permission and VT-switching errors as before,
now compounded by a second process (Matchbox) also trying to attach to
the session at a moment when X's own console ownership was still
unstable. When X did start, Matchbox sometimes exited immediately
(`matchbox: can't open display!`) because it was launched before X had
genuinely finished initializing, despite an active wait loop checking
`xset q` for readiness — the readiness check itself was not sufficient
proof that the console handoff had fully completed.

**Why this was abandoned:** the underlying instability was in the
hand-rolled `startx`/VT ownership chain, not in Matchbox itself. Adding
a second process on top of an already-fragile boot sequence made
failures harder to isolate, not easier.

---

## The actual fix — lightdm

**What changed:** stop hand-building the console/VT/session ownership
logic entirely, and use `lightdm` — a real, standard display manager
built specifically to own this responsibility correctly.

```bash
sudo apt install -y lightdm
```

`/etc/lightdm/lightdm.conf`:

```ini
[Seat:*]
autologin-user=YOUR_USERNAME
autologin-user-timeout=0
user-session=openbox
```

**One real mistake made while setting this up, worth noting exactly
because it wastes time if you hit it too:** this file already had a
`[Seat:*]` section with several commented-out example lines. Adding a
second `[Seat:*]` block further down the file, with the actual settings
crammed onto one line, produced:

```
Failed to load configuration from /etc/lightdm/lightdm.conf:
Invalid key name: [Seat:*] autologin-user
```

lightdm does not merge duplicate section headers gracefully in this
version — the fix was deleting the second, malformed block entirely and
adding the three real settings directly under the *first* `[Seat:*]`
header instead.

Set boot mode:

```bash
sudo raspi-config
# System Options → Boot / Auto Login → Desktop Autologin
```

This single change resolved the VT ownership problem, the console
permission problem, and the "no window manager" problem all at once,
because all three were really the same underlying gap — the hand-built
script was trying to do lightdm's actual job.

---

## Openbox autostart — the working sequence

`~/.config/openbox/autostart`, arrived at after multiple rounds of
watching exactly what happened on the physical screen:

```bash
xset s off
xset -dpms
xset s noblank
unclutter -idle 0.5 -root &

pkill -9 -f epiphany
sleep 1

epiphany --incognito-mode http://localhost:5000 &
echo "$(date +%T) epiphany launched"

WIN_ID=""
for i in $(seq 1 40); do
    for id in $(xdotool search --class "Epiphany"); do
        W=$(xdotool getwindowgeometry --shell "$id" 2>/dev/null | grep WIDTH | cut -d= -f2)
        if [ -n "$W" ] && [ "$W" -gt 10 ]; then
            WIN_ID="$id"
            break
        fi
    done
    if [ -n "$WIN_ID" ]; then
        break
    fi
    sleep 1
done

sleep 40

wmctrl -r "" -b add,fullscreen
sleep 2
xdotool windowfocus "$WIN_ID"
sleep 2
xdotool key F11

sleep 30
xdotool windowfocus "$WIN_ID"
xdotool key F11

sleep 10
xdotool mousemove_relative -- 30 30
```

### Why each odd-looking piece is actually there

**Skipping windows with `WIDTH` of exactly 1.** Epiphany creates more
than one X window internally — the real, visible content window, and at
least one invisible 1×1 pixel helper window used for its own internal
purposes. `xdotool search --class "Epiphany"` returns both. Grabbing
whichever one comes back "last" or "first" is not reliable — the actual
fix is filtering by real width, and only trusting a window once its
width is genuinely larger than 10 pixels.

**The 40-second wait after finding the window.** The window existing is
not the same as the page being fully loaded and settled. WebKit on this
hardware repeatedly logs `Unable to create a GL context` and falls back
to software rendering — this fallback itself takes real time. Sending
F11 before that settles does nothing visible, with no error at all; it
is simply too early for the fullscreen request to be honored
consistently.

**Sending F11 a second time, 30 seconds later.** The very first time
fullscreen genuinely worked end-to-end, a small on-screen notification
appeared confirming F11 had been received — and the address bar still
returned a short time afterward. Repeated testing, including a script
that logged the window's actual X/Y/width/height every 5 seconds over a
full two-and-a-half-minute window with nothing touching the mouse or
keyboard, proved the window's geometry never changed — width and height
stayed exactly at the screen's real resolution the entire time. What
looked like "fullscreen turning off" was the browser's own built-in
hover-reveal toolbar, a completely normal browser feature that shows the
address bar temporarily when the mouse moves near the top edge of the
screen. It was not a bug. The second F11 press was added defensively
while this was still being diagnosed, and left in because it does no
harm and adds a small margin of safety.

**Moving the mouse cursor a small, fixed amount at the very end.** This
is the piece that looks the most arbitrary and is actually the real,
final fix, once the hover-reveal explanation was confirmed with hard
data. On this specific setup, `unclutter` hides the cursor after a short
idle period, but the cursor's *position* is still wherever it last was —
and if that happens to be near the top of the screen, even an invisible
cursor sitting there can trigger the hover-reveal toolbar. Deliberately
moving the cursor to the bottom of the screen, once, right after
fullscreen is confirmed, keeps it permanently away from the one screen
region that causes the toolbar to reappear. This was found by direct
trial after ruling out every other explanation with actual window
geometry data — not guessed, and not something a general troubleshooting
guide would suggest, because it is specific to this exact combination of
Epiphany's hover-reveal behavior and `unclutter`'s idle-based hiding.

---

## Debugging technique that actually worked

Two things made the difference between hours of guessing and finding the
real cause:

**1. Redirecting the whole autostart script's output to a log file and
timestamping every step**, instead of trying to watch a fast boot
sequence in real time:

```bash
exec > /tmp/autostart-debug.log 2>&1
echo "$(date +%T) some step happened"
```

Reading this log after the fact showed, in exact order, how long each
step actually took — including the moment `WIN_ID=` came back empty,
which was the single most useful line in the entire debugging process.

**2. Measuring window geometry over time with a script, instead of
trusting what the screen looked like at a glance:**

```bash
for i in $(seq 1 30); do
    echo "$(date +%T) $(xdotool getwindowgeometry --shell WINDOW_ID | grep -E 'WIDTH|HEIGHT')"
    sleep 5
done
```

This is what proved, with real numbers rather than an impression, that
fullscreen was never actually failing — only the visual appearance of
the toolbar was misleading.

---

## The RCWL-0516 motion sensor — wired, tested, and dropped

An RCWL-0516 microwave motion sensor was wired to a GPIO pin, intended
to turn the screen on when someone entered the room. It initially
appeared to read constant motion regardless of the room's actual state.

**Diagnosis, done in order, each step isolating one variable:**

1. Raw GPIO read in isolation, with no other project code running —
   confirmed the sensor itself, not the project's Python logic, was the
   source of the reading.
2. Moved the sensor physically away from the Pi board, its USB cables,
   and the WiFi antenna, since the RCWL-0516's own datasheet-level
   guidance warns it can pick up electrical interference from nearby
   switching electronics. This alone fixed the constant "motion
   detected" reading — confirming the sensor and the GPIO wiring were
   both fine, and the earlier readings had genuinely been interference.
3. With interference ruled out, the sensor was then tested over a
   longer period and found to still behave unpredictably in normal use.

Rather than keep an unreliable sensor in the live project, it was
removed entirely — the GPIO code, the config values, and the dependency
on `RPi.GPIO`/serial libraries it needed. The decision to drop a feature
that had already been wired up, instead of shipping something flaky, is
recorded here on purpose: it was a deliberate call, not an unfinished
task.

---

## Memory pressure and the two things that actually help

`ps aux --sort=-%mem` showed WebKit's rendering process as the largest
consumer of memory on the Pi by a wide margin — more than Flask, more
than every other service combined. `free -h` showed the system's zram
swap space regularly climbing toward 90% full.

**One thing that was tried and made this measurably worse, not
better:** setting `WEBKIT_DISABLE_COMPOSITING_MODE=1` before launching
Epiphany. Memory usage for the WebKit process rose from roughly 9% to
roughly 24% of total system memory after this change — the opposite of
the intended effect. It was reverted immediately. This is recorded here
specifically so it is not tried again as an "obvious" fix — on this
hardware, it was not.

**What actually helps, without touching the fragile boot chain:**

- **Persistent journal logging**, so that if the Pi reboots
  unexpectedly again, there is a real log to check instead of losing
  the evidence, as happened more than once during this build before the
  fix below was applied:

  ```bash
  sudo mkdir -p /var/log/journal
  sudo nano /etc/systemd/journald.conf
  # Storage=persistent
  # SystemMaxUse=200M
  sudo systemctl restart systemd-journald
  ```

- **A scheduled full page reload every 30 minutes**, added directly to
  `dashboard.html`'s JavaScript, which reliably clears up an
  occasional browser-side stall (visible as WebKitGTK's own "page
  unresponsive" dialog, which has no exposed command-line flag to
  disable) without needing to understand its root cause precisely:

  ```javascript
  setInterval(() => location.reload(), 30 * 60 * 1000);
  ```

Neither of these fixes the underlying memory ceiling of a 512MB device
running a modern browser — that is a genuine hardware limit. Both make
the visible symptoms of that limit self-heal automatically, without
manual intervention.

---

## A note on process, for anyone reading this later

A large amount of today's actual progress came from insisting on real
evidence — a log file, a geometry measurement, an exit code — instead of
accepting a plausible-sounding explanation and moving on. Several
early theories in this document (a VT race, a permissions gap, a
compositing setting) were each partially right, but the fix that
actually held up every time was the one confirmed by data collected
directly from the running system, not the one that sounded most likely
in the abstract.
