import os
import sys
import json
import platform
import subprocess

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, '_MEIPASS', APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR

CONFIG_PATH = os.path.join(APP_DIR, "config.json")
FILES_DIR = os.path.join(APP_DIR, "files")

_local_assets = os.path.join(APP_DIR, "assets")
ASSETS_DIR = _local_assets if os.path.isdir(_local_assets) else os.path.join(BUNDLE_DIR, "assets")

DEFAULT_CONFIG = {
    "game": "acnh",
    "city": "",             # This string is empty by default, but IP localization will detect the city automatically
    "volume": 50,           
    "paused": False,
    "roost": False,
    "notifications": True,
    "autostart": False
}

GAMES = [
    {
        "name": "Animal Crossing: New Horizons",
        "shortname": "New Horizons",
        "code": "acnh",
        "size": "250 MB",
        "type": "normal",
        "roost": True
    },
    {
        "name": "Animal Crossing: New Leaf",
        "shortname": "New Leaf",
        "code": "acnl",
        "size": "120 MB",
        "type": "normal",
        "roost": True
    },
    {
        "name": "Animal Crossing: City Folk",
        "shortname": "City Folk",
        "code": "accf",
        "size": "230 MB",
        "type": "normal",
        "roost": True
    },
    {
        "name": "Animal Crossing (GameCube)",
        "shortname": "Animal Crossing",
        "code": "ac",
        "size": "130 MB",
        "type": "norain",
        "roost": False
    },
    {
        "name": "Animal Crossing: Pocket Camp",
        "shortname": "Pocket Camp",
        "code": "acpc",
        "size": "40 MB",
        "type": "periodic",
        "roost": False
    }
]


class Config:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"Error loading config.json: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_game_info(self, code=None):
        target = code or self.get("game")
        for g in GAMES:
            if g["code"] == target:
                return g
        return GAMES[0]


def open_music_folder(game_code: str = ""):
    target_dir = os.path.join(FILES_DIR, game_code) if game_code else FILES_DIR
    os.makedirs(target_dir, exist_ok=True)
    try:
        if platform.system() == "Windows":
            os.startfile(target_dir)
        elif platform.system() == "Darwin":
            subprocess.run(["open", target_dir])
        else:
            subprocess.run(["xdg-open", target_dir])
    except Exception as e:
        print(f"Failed to open music folder: {e}")



APP_NAME = "AnimalCrossingDynamicClock"


def get_launch_command():
    if getattr(sys, 'frozen', False):
        return sys.executable
    if platform.system() == "Windows":
        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
        if os.path.exists(pythonw):
            main_script = os.path.join(APP_DIR, "main.py")
            return f'"{pythonw}" "{main_script}"'
    return f'"{sys.executable}" "{os.path.join(APP_DIR, "main.py")}"'


def set_autostart(enable: bool) -> bool:
    os_name = platform.system()
    cmd = get_launch_command()

    try:
        if os_name == "Windows":
            return _set_autostart_windows(enable, cmd)
        elif os_name == "Darwin":
            return _set_autostart_macos(enable, cmd)
        elif os_name == "Linux":
            return _set_autostart_linux(enable, cmd)
    except Exception as e:
        print(f"Failed to set autostart: {e}")
    return False


def is_autostart_enabled() -> bool:
    os_name = platform.system()
    try:
        if os_name == "Windows":
            return _is_autostart_windows()
        elif os_name == "Darwin":
            return _is_autostart_macos()
        elif os_name == "Linux":
            return _is_autostart_linux()
    except Exception:
        pass
    return False


def _set_autostart_windows(enable: bool, cmd: str) -> bool:
    reg_success = False
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            if enable:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                try:
                    winreg.DeleteValue(key, APP_NAME)
                except FileNotFoundError:
                    pass
        reg_success = True
    except Exception:
        reg_success = False

    startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_vbs = os.path.join(startup_dir, f"{APP_NAME}.vbs")
    try:
        if enable and not reg_success:
            if os.path.isdir(startup_dir):
                vbs_content = f'Set WshShell = CreateObject("WScript.Shell")\nWshShell.Run {json.dumps(cmd)}, 0, False\n'
                with open(shortcut_vbs, "w", encoding="utf-8") as f:
                    f.write(vbs_content)
                return True
        elif not enable and os.path.exists(shortcut_vbs):
            os.remove(shortcut_vbs)
    except Exception:
        pass

    return reg_success


def _is_autostart_windows() -> bool:
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except Exception:
        pass
    startup_dir = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_vbs = os.path.join(startup_dir, f"{APP_NAME}.vbs")
    return os.path.exists(shortcut_vbs)


def _set_autostart_macos(enable: bool, cmd: str) -> bool:
    plist_dir = os.path.expanduser("~/Library/LaunchAgents")
    plist_path = os.path.join(plist_dir, f"com.acdc.{APP_NAME}.plist")

    if enable:
        os.makedirs(plist_dir, exist_ok=True)
        parts = [p.strip('"') for p in cmd.split('" "') if p.strip()]
        args_xml = "\n".join(f"        <string>{p}</string>" for p in parts)
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.acdc.{APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
{args_xml}
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(plist_content)
        return True
    else:
        if os.path.exists(plist_path):
            os.remove(plist_path)
        return True


def _is_autostart_macos() -> bool:
    plist_path = os.path.expanduser(f"~/Library/LaunchAgents/com.acdc.{APP_NAME}.plist")
    return os.path.exists(plist_path)


def _set_autostart_linux(enable: bool, cmd: str) -> bool:
    autostart_dir = os.path.expanduser("~/.config/autostart")
    desktop_file = os.path.join(autostart_dir, f"{APP_NAME}.desktop")

    if enable:
        os.makedirs(autostart_dir, exist_ok=True)
        content = f"""[Desktop Entry]
Type=Application
Exec={cmd}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=Animal Crossing Dynamic Clock
Comment=Dynamic Animal Crossing music player based on weather and time
Icon={os.path.join(ASSETS_DIR, 'icon.png')}
"""
        with open(desktop_file, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    else:
        if os.path.exists(desktop_file):
            os.remove(desktop_file)
        return True


def _is_autostart_linux() -> bool:
    desktop_file = os.path.expanduser(f"~/.config/autostart/{APP_NAME}.desktop")
    return os.path.exists(desktop_file)
