import urllib.request

URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=37.98&longitude=23.73"
    "&hourly=temperature_2m"
    "&timezone=Europe%2FAthens"
    "&forecast_days=7"
)

with urllib.request.urlopen(URL, timeout=30) as response:
    raw = response.read().decode("utf-8")

print(raw)
