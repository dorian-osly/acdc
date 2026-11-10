import json
import time
import urllib.parse
import urllib.request

KEYWORDS_SNOW = [
    "snow", "blizzard", "snowstorm", "flurries", "sleet", "ice", "hail", "neige"
]

KEYWORDS_RAIN = [
    "rain", "mist", "shower", "drizzle", "thunderstorm", "downpour", "pluie", "bruine", "orage"
]

WMO_WEATHER_MAP = {
    0: ("Clear sky", "clear"),
    1: ("Mainly clear", "clear"),
    2: ("Partly cloudy", "clear"),
    3: ("Overcast", "clear"),
    45: ("Fog", "rain"),
    48: ("Depositing rime fog", "rain"),
    51: ("Light drizzle", "rain"),
    53: ("Moderate drizzle", "rain"),
    55: ("Dense drizzle", "rain"),
    56: ("Light freezing drizzle", "rain"),
    57: ("Dense freezing drizzle", "rain"),
    61: ("Slight rain", "rain"),
    63: ("Moderate rain", "rain"),
    65: ("Heavy rain", "rain"),
    66: ("Light freezing rain", "rain"),
    67: ("Heavy freezing rain", "rain"),
    71: ("Slight snow fall", "snow"),
    73: ("Moderate snow fall", "snow"),
    75: ("Heavy snow fall", "snow"),
    77: ("Snow grains", "snow"),
    80: ("Slight rain showers", "rain"),
    81: ("Moderate rain showers", "rain"),
    82: ("Violent rain showers", "rain"),
    85: ("Slight snow showers", "snow"),
    86: ("Heavy snow showers", "snow"),
    95: ("Thunderstorm", "rain"),
    96: ("Thunderstorm with slight hail", "rain"),
    99: ("Thunderstorm with heavy hail", "rain")
}

# Cache to avoid hammering weather servers, otherwise they may block requests
_cached_weather = {
    "category": "clear",
    "description": "Clear sky",
    "city": "Automatic",
    "temp": "--°C",
    "timestamp": 0
}

CACHE_DURATION = 600


def detect_city() -> str:
    endpoints = [
        ("https://ipapi.co/json/", lambda d: d.get("city", "")),
        ("http://ip-api.com/json/", lambda d: d.get("city", ""))
    ]

    for url, extractor in endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))
                city = extractor(data)
                if city:
                    return city
        except Exception:
            continue
    return ""


def categorize_weather(description: str) -> str:
    desc_lower = description.lower()
    if any(k in desc_lower for k in KEYWORDS_SNOW):
        return "snow"
    if any(k in desc_lower for k in KEYWORDS_RAIN):
        return "rain"
    return "clear"


def _fetch_open_meteo(city: str) -> dict | None:
    try:
        # 1: Geocode city name to lat/lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1&language=en&format=json"
        geo_req = urllib.request.Request(geo_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(geo_req, timeout=5) as res:
            geo_data = json.loads(res.read().decode("utf-8"))
            results = geo_data.get("results")
            if not results:
                return None
            lat = results[0]["latitude"]
            lon = results[0]["longitude"]
            resolved_name = results[0].get("name", city)

        # 2: Fetch current weather
        fc_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code"
        fc_req = urllib.request.Request(fc_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(fc_req, timeout=5) as res:
            fc_data = json.loads(res.read().decode("utf-8"))
            curr = fc_data.get("current", {})
            temp_c = f"{curr.get('temperature_2m', '--')}°C"
            wmo_code = curr.get("weather_code", 0)
            desc, category = WMO_WEATHER_MAP.get(wmo_code, ("Clear sky", "clear"))

            return {
                "category": category,
                "description": desc,
                "city": resolved_name,
                "temp": temp_c,
                "timestamp": time.time()
            }
    except Exception:
        return None


def get_current_weather(city: str = "", force: bool = False) -> dict:
    global _cached_weather

    now = time.time()
    if not force and _cached_weather["timestamp"] > 0 and (now - _cached_weather["timestamp"] < CACHE_DURATION):
        return dict(_cached_weather)

    city_param = city.strip()
    target_url = f"https://wttr.in/{urllib.parse.quote(city_param)}?format=j1" if city_param else "https://wttr.in/?format=j1"

    try:
        req = urllib.request.Request(target_url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

            curr = data["current_condition"][0]
            raw_desc = curr["weatherDesc"][0]["value"].strip()
            temp_c = f"{curr.get('temp_C', '--')}°C"

            resolved_city = city_param
            if not resolved_city:
                try:
                    resolved_city = data["nearest_area"][0]["areaName"][0]["value"]
                except Exception:
                    resolved_city = "Local location"

            category = categorize_weather(raw_desc)

            _cached_weather = {
                "category": category,
                "description": raw_desc,
                "city": resolved_city,
                "temp": temp_c,
                "timestamp": now
            }
            return dict(_cached_weather)
    except Exception:
        pass

    if city_param:
        om_res = _fetch_open_meteo(city_param)
        if om_res:
            _cached_weather = om_res
            return dict(_cached_weather)

    if _cached_weather["timestamp"] > 0:
        return dict(_cached_weather)

    return {
        "category": "clear",
        "description": "Clear sky",
        "city": city_param or "Unknown",
        "temp": "--°C",
        "timestamp": now
    }
