"""
OpenF1 API Python Client
Docs: https://openf1.org/docs
Base URL: https://api.openf1.org/v1
No authentication required for historical data (2023+).
"""

import json
from urllib.request import urlopen
from urllib.parse import urlencode, quote


BASE_URL = "https://api.openf1.org/v1"


def _fetch(endpoint: str, params: dict = None) -> list[dict]:
    """Make a GET request to the OpenF1 API and return parsed JSON."""
    url = f"{BASE_URL}/{endpoint}"
    if params:
        # Build query string manually to support operators like >=, <=, >, <
        parts = []
        for key, value in params.items():
            parts.append(f"{quote(str(key))}={quote(str(value))}")
        url += "?" + "&".join(parts)
    print(f"GET {url}")
    response = urlopen(url)
    return json.loads(response.read().decode("utf-8"))


# ── Endpoints ────────────────────────────────────────────────────────────────

def get_car_data(**params) -> list[dict]:
    """
    Car telemetry at ~3.7 Hz (brake, DRS, gear, RPM, speed, throttle).
    Useful params: driver_number, session_key, speed>=315
    """
    return _fetch("car_data", params)


def get_drivers(**params) -> list[dict]:
    """
    Driver information for a session (name, team, headshot URL, etc.).
    Useful params: driver_number, session_key
    """
    return _fetch("drivers", params)


def get_intervals(**params) -> list[dict]:
    """
    Real-time gap to leader and car ahead (races only, ~4 s updates).
    Useful params: session_key, interval<0.5
    """
    return _fetch("intervals", params)


def get_laps(**params) -> list[dict]:
    """
    Detailed lap data (sector times, speeds, segments).
    Useful params: session_key, driver_number, lap_number
    """
    return _fetch("laps", params)


def get_location(**params) -> list[dict]:
    """
    Approximate car position on circuit (x, y, z) at ~3.7 Hz.
    Useful params: session_key, driver_number, date>..., date<...
    """
    return _fetch("location", params)


def get_meetings(**params) -> list[dict]:
    """
    Grand Prix / testing weekend info.
    Useful params: year, country_name, meeting_key
    """
    return _fetch("meetings", params)


def get_overtakes(**params) -> list[dict]:
    """
    Overtake events during races.
    Useful params: session_key, overtaking_driver_number, position
    """
    return _fetch("overtakes", params)


def get_pit(**params) -> list[dict]:
    """
    Pit stop data (lane duration, stop duration).
    Useful params: session_key, driver_number, stop_duration<2.5
    """
    return _fetch("pit", params)


def get_position(**params) -> list[dict]:
    """
    Driver positions throughout a session.
    Useful params: session_key, driver_number, position<=3
    """
    return _fetch("position", params)


def get_race_control(**params) -> list[dict]:
    """
    Race control messages (flags, safety car, session status, ...).
    Useful params: session_key, flag, driver_number, date>=..., date<...
    """
    return _fetch("race_control", params)


def get_sessions(**params) -> list[dict]:
    """
    Session info (practice, qualifying, sprint, race).
    Useful params: year, country_name, session_name, session_type
    """
    return _fetch("sessions", params)


def get_session_result(**params) -> list[dict]:
    """
    Final standings after a session.
    Useful params: session_key, position<=3
    """
    return _fetch("session_result", params)


def get_starting_grid(**params) -> list[dict]:
    """
    Starting grid for a race session.
    Useful params: session_key, position<=10
    """
    return _fetch("starting_grid", params)


def get_stints(**params) -> list[dict]:
    """
    Stint data (tyre compound, lap range, tyre age).
    Useful params: session_key, driver_number, compound=SOFT
    """
    return _fetch("stints", params)


def get_team_radio(**params) -> list[dict]:
    """
    Team radio recordings (URL to MP3).
    Useful params: session_key, driver_number
    """
    return _fetch("team_radio", params)


def get_weather(**params) -> list[dict]:
    """
    Track weather (temperature, humidity, rainfall, wind) updated every minute.
    Useful params: meeting_key, session_key, track_temperature>=50
    """
    return _fetch("weather", params)


def get_championship_drivers(**params) -> list[dict]:
    """
    Driver championship standings (race sessions only, beta).
    Useful params: session_key, driver_number
    """
    return _fetch("championship_drivers", params)


def get_championship_teams(**params) -> list[dict]:
    """
    Team championship standings (race sessions only, beta).
    Useful params: session_key, team_name
    """
    return _fetch("championship_teams", params)


# ── Quick-start examples ─────────────────────────────────────────────────────

if __name__ == "__main__":
    # 1. Latest meeting
    print("\n=== Latest meeting ===")
    meetings = get_meetings(**{"meeting_key": "latest"})
    for m in meetings:
        print(f"  {m['meeting_name']} ({m['year']}) — {m['location']}")

    # 2. Sessions in latest meeting
    print("\n=== Sessions in latest meeting ===")
    sessions = get_sessions(**{"meeting_key": "latest"})
    for s in sessions:
        print(f"  [{s['session_key']}] {s['session_name']} — {s['date_start'][:10]}")

    # 3. Drivers in latest session
    print("\n=== Drivers in latest session ===")
    drivers = get_drivers(**{"session_key": "latest"})
    for d in drivers:
        print(f"  #{d['driver_number']:>2}  {d['name_acronym']}  {d['team_name']}")

    # 4. Top-3 finishers in latest session
    print("\n=== Top 3 session result ===")
    results = get_session_result(**{"session_key": "latest", "position<=": "3"})
    for r in results:
        print(f"  P{r['position']} — #{r['driver_number']}")

    # 5. Weather in latest session
    print("\n=== Latest weather snapshot ===")
    weather = get_weather(**{"session_key": "latest"})
    if weather:
        w = weather[-1]  # most recent reading
        print(f"  Air: {w['air_temperature']}°C  Track: {w['track_temperature']}°C"
              f"  Humidity: {w['humidity']}%  Rain: {bool(w['rainfall'])}")
