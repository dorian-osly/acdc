# Animal Crossing Dynamic Clock (ACDC)

> [!IMPORTANT]
> ### Credits & Upstream Project
> **Full credit goes to [@oscie57](https://github.com/oscie57) and their original project: [Animal Crossing Dynamic Player (ACDP)](https://github.com/oscie57/acdp)!**  
> This application is a modernized, GUI-driven and portable evolution of oscie57's work, utilizing their service (`cloud.oscie.net`). Huge thanks to them for creating the original concept and keeping the soundtrack available!  
> *Animal Crossing* and all related audio and assets are © **Nintendo Co., Ltd.**

---

A lightweight, portable background music player that syncs with your real-world local **time** and real-time **weather** conditions. Runs silently in your **system tray** (taskbar notification area) without cluttering your screen with console or terminal windows.

---

## Available Games

| Game | Platform | Size | Weather Variants | The Roost |
| :--- | :--- | :---: | :---: | :---: |
| **Animal Crossing: New Horizons** | Nintendo Switch | ~250 MB | Clear, Rain, Snow | ✅ |
| **Animal Crossing: New Leaf** | Nintendo 3DS | ~120 MB | Clear, Rain, Snow | ✅ |
| **Animal Crossing: City Folk** | Nintendo Wii | ~230 MB | Clear, Rain, Snow | ✅ |
| **Animal Crossing (Original)** | Nintendo GameCube | ~130 MB | Clear, Snow | ❌ |
| **Animal Crossing: Pocket Camp** | Mobile | ~40 MB | Periodic (Morning, Day, Evening, Night) | ❌ |

---

## Features

- **Discrete**: Sits quietly in your system tray with a cute green leaf icon!
- **Accurate to your weather**: Automatically checks your local weather and shifts the soundtrack to match—sunny vibes on clear days, cozy rain layers when it pours, and peaceful bells when it snows. No API keys needed!
- **Hourly changes**: When a new hour rolls around, the music smoothly fades into the next hourly theme, just like playing the actual game!
- **The Roost coffee breaks**: Feeling lucky? You can enable an occasional chance for Brewster's iconic café theme to play and brighten up your day!
- **Starts with your PC**: Want cozy background tunes every time you log in? Just check the box in the settings and you're good to go.
- **Portable**: No installer at all! Your settings (`config.json`) and downloaded songs stay right inside the app folder, so you can easily carry it around on a USB drive!

---

## How to Run

### Windows
- **Portable `.exe` (Recommended - No Python needed):**
  1. Download `AnimalCrossingDynamicClock.exe` from the Releases page (or find it in `dist/`).
  2. Double-click it to launch!
  3. On first launch, the download window will prompt you to grab the soundtrack for your game. Choose a game, click **Start Download**, and enjoy!
  *(To build the `.exe` yourself: run `python build.py`.)*
- **Running with Python:**
  Install dependencies with `pip install -r requirements.txt`, then double-click `launch.vbs` to run silently in the background (or run `python main.py`).

### Linux (Arch, Debian, Ubuntu, Fedora)
- **Desktop Install & 1-Click Launch:**
  1. Install system packages for your distribution:
     - **Arch Linux / Manjaro:**
       ```bash
       sudo pacman -S python python-pyqt6 python-requests python-pip
       pip install pygame-ce
       ```
     - **Debian / Ubuntu / Linux Mint:**
       ```bash
       sudo apt install python3 python3-pyqt6 python3-requests python3-pip
       pip install pygame-ce
       ```
     - **Fedora / RHEL:**
       ```bash
       sudo dnf install python3 python3-pyqt6 python3-requests python3-pip
       pip install pygame-ce
       ```
  2. Add it to your desktop application menu:
     ```bash
     chmod +x launch.sh install-linux.sh
     ./install-linux.sh
     ```
     Or start it directly in the background:
     ```bash
     ./launch.sh
     ```
- **Standalone Linux Binary:**
  To compile a single portable ELF executable for Linux:
  ```bash
  python3 build.py
  ./dist/AnimalCrossingDynamicClock
  ```
  *(Automated builds for Windows and Linux x86_64 are also pre-configured in `.github/workflows/build.yml`.)*

### macOS
1. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
2. Start the application:
   ```bash
   python3 main.py
   ```

---

## System Tray Controls

Just right-click the little leaf icon in your taskbar whenever you want to interact with the player:

- **Status**: See what's currently playing, the hour, and your local weather (e.g., `New Horizons - 18h (Clear sky)`).
- **Pause / Resume**: Quickly pause playback whenever you hop on a call or need quiet, and pick right back up when you're ready.
- **Select Game**: Switch between any supported *Animal Crossing* soundtrack in a click.
- **Download Music...**: Open the download manager to grab extra games without leaving the app.
- **Settings...**: Slide the volume up or down, type in a custom city (or click *Auto-detect*), toggle *The Roost* café theme, or turn startup on/off.
- **Refresh Weather**: Force an immediate weather update if a sudden storm just rolled in. (you never know...)
- **Launch on Startup**: A quick one-click toggle to have the player start whenever your computer turns on.
- **Quit**: Closes the application completely and stops the music.

---

## Credits & Disclaimer

- **Original Creator & Concept**: [@oscie57](https://github.com/oscie57) — [Animal Crossing Dynamic Player (ACDP)](https://github.com/oscie57/acdp).
- **Audio CDN**: Hosted and provided courtesy of [cloud.oscie.net](https://cloud.oscie.net).
- **Intellectual Property**: *Animal Crossing* is a registered trademark of **Nintendo Co., Ltd.** All rights, music compositions, and associated properties belong to their respective owners.
- This project is an unofficial, non-profit fan-made utility for personal listening purposes.
