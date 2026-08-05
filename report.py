import json
import urllib.request

URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.98&longitude=23.73"
    "&hourly=temperature_2m"
    "&timezone=Europe%2FAthens"
    "&forecast_days=7"
)

with urllib.request.urlopen(URL, timeout=30) as response:
    data = json.loads(response.read())

temps = data["hourly"]["temperature_2m"]
print(f"min {min(temps)} max {max(temps)}")
