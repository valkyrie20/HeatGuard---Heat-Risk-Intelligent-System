from flask import Flask, render_template
import requests
import math
from datetime import datetime

app = Flask(__name__)

def get_doha_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 25.2854,
            "longitude": 51.5310,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,uv_index,cloud_cover,apparent_temperature",
            "timezone": "Asia/Qatar",
            "wind_speed_unit": "kmh"
        }
        response = requests.get(url, params=params)
        data = response.json()
        current = data["current"]

        temp = current["temperature_2m"]
        humidity = current["relative_humidity_2m"]
        wind = current["wind_speed_10m"]
        uv = current["uv_index"]
        cloud = current["cloud_cover"]

        # WBGT calculation using Stull formula
        tw = temp * math.atan(0.151977 * (humidity + 8.313659) ** 0.5) + \
             math.atan(temp + humidity) - \
             math.atan(humidity - 1.676331) + \
             0.00391838 * humidity ** 1.5 * math.atan(0.023101 * humidity) - 4.686035

        # Globe temperature approximation
        if uv > 6:
            tg = temp + 4
        else:
            tg = temp + 2

        wbgt = round(0.7 * tw + 0.2 * tg + 0.1 * temp, 1)

        # Risk level
        if wbgt < 25:
            risk = "Low"
            risk_color = "#22c55e"
        elif wbgt < 32.1:
            risk = "Moderate"
            risk_color = "#f59e0b"
        else:
            risk = "High"
            risk_color = "#ef4444"

        # Safe exposure time
        if wbgt < 25:
            safe_time = 60
        elif wbgt < 28:
            safe_time = 40
        elif wbgt < 30:
            safe_time = 30
        elif wbgt < 32.1:
            safe_time = 20
        else:
            safe_time = 0

        # Work to rest ratio
        if wbgt < 25:
            work_rest = "45:15"
        elif wbgt < 28:
            work_rest = "30:30"
        elif wbgt < 30:
            work_rest = "20:40"
        elif wbgt < 32.1:
            work_rest = "15:45"
        else:
            work_rest = "Stop work"

        # Qatar MoL restricted hours check
        now = datetime.now()
        hour = now.hour
        month = now.month
        restricted = (month >= 6 and month <= 9) and (hour >= 10 and hour < 16)

        # Clothing recommendation
        if wbgt > 28 and uv > 6:
            clothing = "Light, loose, long-sleeve — light colors"
        elif wbgt > 25:
            clothing = "Light, breathable clothing — avoid dark colors"
        else:
            clothing = "Standard work clothing — light colors preferred"

        return {
            "temp": round(temp, 1),
            "humidity": round(humidity),
            "wind": round(wind, 1),
            "uv": round(uv, 1),
            "cloud": round(cloud),
            "wbgt": wbgt,
            "risk": risk,
            "risk_color": risk_color,
            "safe_time": safe_time,
            "work_rest": work_rest,
            "restricted": restricted,
            "clothing": clothing,
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        return {
            "temp": "--",
            "humidity": "--",
            "wind": "--",
            "uv": "--",
            "cloud": "--",
            "wbgt": "--",
            "risk": "Unavailable",
            "risk_color": "#555",
            "safe_time": "--",
            "work_rest": "--",
            "restricted": False,
            "clothing": "--",
        }

@app.route('/')
def home():
    weather = get_doha_weather()
    return render_template('home.html', w=weather)

@app.route('/hydration')
def hydration():
    return render_template('hydration.html')

@app.route('/map')
def map_view():
    weather = get_doha_weather()
    return render_template('map.html', w=weather)

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/emergency')
def emergency():
    return render_template('emergency.html')

if __name__ == '__main__':
    app.run(debug=True)