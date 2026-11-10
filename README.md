# Animal Crossing Dynamic Clock (ACDC)

> ### Credits
> **Full credit goes to [@oscie57](https://github.com/oscie57) and their original project: [Animal Crossing Dynamic Player (ACDP)](https://github.com/oscie57/acdp)!**  
> This application is a modernized, GUI-driven and portable evolution of oscie57's work, utilizing their service (`cloud.oscie.net`). Huge thanks to them for creating the original concept and keeping the soundtrack available!  
> *Animal Crossing* and all related audio and assets are © **Nintendo Co., Ltd.**

---

I wanted a lightweight, portable background music player that synced with my real local time and real-time weather conditions, so I made this! It runs silently in the system tray without cluttering the screen.

---

## Available Games

| Game | Size | Weather Variants | The Roost |
| :--- | :---: | :---: | :---: |
| **Animal Crossing: New Horizons** | ~250 MB | Clear, Rain, Snow | ✅ |
| **Animal Crossing: New Leaf** | ~120 MB | Clear, Rain, Snow | ✅ |
| **Animal Crossing: City Folk** | ~230 MB | Clear, Rain, Snow | ✅ |
| **Animal Crossing (Original)** | ~130 MB | Clear, Snow | ❌ |
| **Animal Crossing: Pocket Camp** | ~40 MB | Periodic (Morning, Day, Evening, Night) | ❌ |

---

## Features

- **Accurate to your weather**: Automatically checks your local weather and shifts the soundtrack to match what's outside your window!
- **Hourly changes**: When a new hour rolls around, the music smoothly fades into the next hourly theme, just like playing the actual game!
- **The Roost coffee breaks**: Feeling lucky? You can enable an occasional chance for Brewster's iconic café theme to play and brighten up your day!
- **Portable**: No installer at all! Your settings (`config.json`) and downloaded songs stay right inside the app folder, so you can easily carry it around on a USB drive!

---

## How to Run

### Windows
- **Portable `.exe`**
  1. Download `AnimalCrossingDynamicClock.exe` from the Releases page (or find it in `dist/`).
  2. Double-click it to launch!
  3. On first launch, the download window will prompt you to grab the soundtrack for your game. Choose a game, click **Start Download**, and enjoy!

- **Running with Python:**
  Install dependencies with `pip install -r requirements.txt`, then double-click `launch.vbs` to run the app silently in the background (or run `python main.py`).

### Linux (Arch, Debian, Ubuntu, Fedora)
- **Desktop Install:**
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
- **Pause / Resume**: Quickly pause playback whenever you want to!
- **Select Game**: Switch between any supported *Animal Crossing* OST in a click.
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
