import requests
from datetime import datetime, timedelta, date
import json

latitude = 37.5665
longitude = 126.97797

today = datetime.utcnow().date()
end_date = today - timedelta(days=2)
desired_start = end_date - timedelta(days=365*5)

min_available = date(2022, 1, 1)
start_date = max(desired_start, min_available)

url = "https://historical-forecast-api.open-meteo.com/v1/forecast"
params = {
    "latitude": latitude,
    "longitude": longitude,
    "start_date": start_date.isoformat(),
    "end_date": end_date.isoformat(),
    "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,rain,showers,snowfall",
    "timezone": "Asia/Seoul"
}

response = requests.get(url, params=params)
response.raise_for_status()
data = response.json()

times = data["hourly"]["time"]
temps = data["hourly"]["temperature_2m"]
humidity = data["hourly"]["relative_humidity_2m"]
precip_prob = data["hourly"]["precipitation_probability"]
rain = data["hourly"]["rain"]
showers = data["hourly"]["showers"]
snow = data["hourly"]["snowfall"]

with open("seoul_last_5years_hourly.jsonl", "w", encoding="utf-8") as f:
    for t, temp, hum, pp, r, sh, sn in zip(times, temps, humidity, precip_prob, rain, showers, snow):
        dt = datetime.fromisoformat(t)
        record = {
            "date": dt.date().isoformat(),
            "time": dt.time().isoformat(timespec="minutes"),
            "temperature": temp,
            "humidity": hum,
            "precip_probability": pp,
            "is_rain": 1 if (r or sh) and (r + sh) > 0 else 0,
            "is_snow": 1 if sn and sn > 0 else 0
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print("저장 완료: seoul_last_5years_hourly.jsonl")
