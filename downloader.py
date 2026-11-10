import os
import time
import requests
import random
from config import FILES_DIR, GAMES

CLOUD_URL = "https://cloud.oscie.net/acdp"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

PERIODIC_TRACKS = ["campsite", "morning", "day", "evening", "night"]


def get_pocket_period(hour_str: str) -> str:
    try:
        h = int(hour_str)
    except ValueError:
        h = 12

    if h in [0, 1, 2, 3, 4, 22, 23]:
        return "night"
    elif 5 <= h <= 11:
        return "morning"
    elif 12 <= h <= 16:
        return "day"
    elif 17 <= h <= 21:
        return "evening"
    return "campsite"


def get_game_spec(game_code: str):
    for g in GAMES:
        if g["code"] == game_code:
            return g
    return GAMES[0]


def get_required_files(game_code: str) -> list[tuple[str, str]]:
    spec = get_game_spec(game_code)
    game_type = spec.get("type", "normal")
    has_roost = spec.get("roost", False)
    files = []

    if game_type == "periodic":
        for track in PERIODIC_TRACKS:
            rel = f"{game_code}/{track}.mp3"
            url = f"{CLOUD_URL}/{game_code}/{track}.mp3"
            files.append((rel, url))
    elif game_type == "norain":
        for w in ["snow", "clear"]:
            for h in range(24):
                num = f"{h:02d}"
                rel = f"{game_code}/{w}/{num}.mp3"
                url = f"{CLOUD_URL}/{game_code}/{w}/{num}.mp3"
                files.append((rel, url))
    else:
        for w in ["rain", "snow", "clear"]:
            for h in range(24):
                num = f"{h:02d}"
                rel = f"{game_code}/{w}/{num}.mp3"
                url = f"{CLOUD_URL}/{game_code}/{w}/{num}.mp3"
                files.append((rel, url))
        if has_roost:
            files.append((f"{game_code}/roost.mp3", f"{CLOUD_URL}/{game_code}/roost.mp3"))

    return files


def is_game_downloaded(game_code: str) -> bool:
    game_dir = os.path.join(FILES_DIR, game_code)
    if not os.path.isdir(game_dir):
        return False

    required = get_required_files(game_code)
    if not required:
        return False

    existing_count = 0
    for rel_path, _ in required:
        full_path = os.path.join(FILES_DIR, rel_path)
        if os.path.isfile(full_path) and os.path.getsize(full_path) > 1024:
            existing_count += 1

    return existing_count >= len(required)


def resolve_track_file(game_code: str, weather: str, hour_str: str, roost: bool = False) -> str | None:
    spec = get_game_spec(game_code)
    game_type = spec.get("type", "normal")

    rel_base = ""

    if game_type == "periodic":
        period = get_pocket_period(hour_str)
        rel_base = f"{game_code}/{period}"
    else:
        # Check Roost chance (1 in 20) if enabled
        if roost and spec.get("roost", False) and random.randint(1, 20) == 7:
            rel_base = f"{game_code}/roost"
        else:
            w = weather
            if game_type == "norain" and w == "rain":
                w = "clear"
            rel_base = f"{game_code}/{w}/{hour_str}"

    candidate = os.path.join(FILES_DIR, f"{rel_base}.mp3")
    if os.path.isfile(candidate) and os.path.getsize(candidate) > 1024:
        return candidate

    return None


def download_game_ost(game_code: str, progress_callback=None, cancel_event=None) -> bool:
    files = get_required_files(game_code)
    total = len(files)
    headers = {"User-Agent": USER_AGENT}

    for idx, (rel_path, url) in enumerate(files, 1):
        if cancel_event and cancel_event.is_set():
            return False

        target_file = os.path.join(FILES_DIR, rel_path)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)

        if os.path.exists(target_file) and os.path.getsize(target_file) > 1024:
            if progress_callback:
                progress_callback(idx, total, os.path.basename(rel_path))
            continue

        success = False
        for attempt in range(3):
            if cancel_event and cancel_event.is_set():
                return False
            try:
                resp = requests.get(url, headers=headers, stream=True, timeout=15)
                if resp.status_code == 200:
                    with open(target_file, "wb") as f:
                        for chunk in resp.iter_content(chunk_size=32768):
                            if cancel_event and cancel_event.is_set():
                                f.close()
                                if os.path.exists(target_file):
                                    os.remove(target_file)
                                return False
                            if chunk:
                                f.write(chunk)
                    success = True
                    break
                else:
                    time.sleep(1)
            except Exception:
                time.sleep(1)

        if not success:
            print(f"Failed to download {url} after 3 attempts.")

        if progress_callback:
            progress_callback(idx, total, os.path.basename(rel_path))

    return is_game_downloaded(game_code)
