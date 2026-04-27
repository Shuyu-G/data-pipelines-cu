from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


OUTPUT_PATH = Path("data/raw_weather.json")
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather() -> dict:
    params = {
        "latitude": 48.8566,
        "longitude": 2.3522,
        "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Paris",
    }
    url = f"{OPEN_METEO_URL}?{urlencode(params)}"
    with urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    payload = fetch_weather()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"Wrote raw Open-Meteo JSON to {OUTPUT_PATH}")
    print(f"Current observation time: {payload.get('current', {}).get('time')}")


if __name__ == "__main__":
    main()
