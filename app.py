import os

from flask import Flask, render_template, jsonify, request
import requests
from collections import defaultdict

app = Flask(__name__)


API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5"


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/visualization")
def visualization():
    return render_template("visualization.html")

@app.route("/api/live-weather")
def live_weather():
    city = request.args.get("city")

    if not city:
        return jsonify({"error": "City name is required"}), 400

    try:
        
        current_resp = requests.get(
            f"{BASE_URL}/weather",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )

        if current_resp.status_code != 200:
            return jsonify({"error": "Invalid city or API error"}), 400

        current = current_resp.json()

        
        forecast_resp = requests.get(
            f"{BASE_URL}/forecast",
            params={
                "q": city,
                "appid": API_KEY,
                "units": "metric"
            },
            timeout=10
        )

        if forecast_resp.status_code != 200:
            return jsonify({"error": "Forecast data unavailable"}), 400

        forecast_raw = forecast_resp.json()

        forecast = []
        next_24h = []
        daily_temp = defaultdict(list)

        
        for index, item in enumerate(forecast_raw["list"]):
            entry = {
                "time": item["dt_txt"],
                "temp": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "rain": item.get("rain", {}).get("3h", 0)
            }

            forecast.append(entry)

            
            if index < 8:
                next_24h.append(entry)

            
            date = item["dt_txt"].split(" ")[0]
            daily_temp[date].append(item["main"]["temp"])

        
        daily_avg = {
            date: round(sum(temps) / len(temps), 2)
            for date, temps in daily_temp.items()
        }

        
        return jsonify({
            "city": city.title(),
            "coordinates": {
                "lat": current["coord"]["lat"],
                "lon": current["coord"]["lon"]
            },
            "current": {
                "temp": current["main"]["temp"],
                "feels_like": current["main"]["feels_like"],
                "humidity": current["main"]["humidity"],
                "pressure": current["main"]["pressure"],
                "condition": current["weather"][0]["description"],
                "icon": current["weather"][0]["icon"]
            },
            "forecast": forecast,
            "next_24h": next_24h,
            "daily_avg": daily_avg
        })

    except requests.exceptions.Timeout:
        return jsonify({"error": "Weather service timeout"}), 500

    except requests.exceptions.RequestException:
        return jsonify({"error": "Network error while contacting weather service"}), 500

    except Exception:
        return jsonify({"error": "Unexpected server error"}), 500



@app.route("/api/heatmap")
def heatmap():
    cities = [
        "Delhi",
        "Mumbai",
        "Bengaluru",
        "Chennai",
        "Kolkata",
        "Hyderabad",
        "Pune",
        "Patna"
    ]

    heat_points = []

    for city in cities:
        try:
            resp = requests.get(
                f"{BASE_URL}/weather",
                params={
                    "q": city,
                    "appid": API_KEY,
                    "units": "metric"
                },
                timeout=5
            )

            if resp.status_code == 200:
                data = resp.json()
                heat_points.append([
                    data["coord"]["lat"],
                    data["coord"]["lon"],
                    data["main"]["temp"] / 40  # normalize intensity
                ])
        except:
            continue

    return jsonify(heat_points)



@app.route("/favicon.ico")
def favicon():
    return "", 204


if __name__ == "__main__":
    app.run(debug=True)
