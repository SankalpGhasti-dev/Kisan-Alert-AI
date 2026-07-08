import requests
from datetime import datetime

def get_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "precipitation_sum,temperature_2m_max,temperature_2m_min,et0_fao_evapotranspiration",
        "current": "temperature_2m,relative_humidity_2m,windspeed_10m",
        "forecast_days": 7,
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        current = data.get("current", {})
        daily = data.get("daily", {})
        
        daily_data = []
        if daily:
            dates = daily.get("time", [])
            rain = daily.get("precipitation_sum", [])
            tmax = daily.get("temperature_2m_max", [])
            tmin = daily.get("temperature_2m_min", [])
            et0 = daily.get("et0_fao_evapotranspiration", [])
            
            for i in range(len(dates)):
                daily_data.append({
                    "date": dates[i],
                    "rain_mm": rain[i] if rain[i] is not None else 0.0,
                    "tmax": tmax[i] if tmax[i] is not None else 0.0,
                    "tmin": tmin[i] if tmin[i] is not None else 0.0,
                    "et0": et0[i] if et0[i] is not None else 0.0
                })
        
        total_rain = sum(d["rain_mm"] for d in daily_data)
        
        avg_temp = 0.0
        if daily_data:
            avg_temp = sum((d["tmax"] + d["tmin"]) / 2 for d in daily_data) / len(daily_data)
        
        return {
            "current_temp": current.get("temperature_2m", 0.0),
            "current_humidity": current.get("relative_humidity_2m", 0.0),
            "current_wind": current.get("windspeed_10m", 0.0),
            "daily": daily_data,
            "total_7day_rain": total_rain,
            "avg_temp": avg_temp
        }
        
    except Exception as e:
        print(f"Weather API Error: {e}")
        return None

def detect_dry_spell(daily_data):
    if not daily_data:
        return {
            "alert": False,
            "severity": "LOW",
            "dry_days": 0,
            "message": "No data available."
        }
        
    dry_days = sum(1 for d in daily_data if d.get("rain_mm", 0) < 1.0)
    
    if dry_days >= 5:
        severity = "HIGH"
        alert = True
    elif dry_days >= 3:
        severity = "MEDIUM"
        alert = True
    else:
        severity = "LOW"
        alert = False
        
    # The prompt explicitly asked for this format: "5 of next 7 days have no rain. Irrigation needed."
    if alert:
        message = f"{dry_days} of next 7 days have no rain. Irrigation needed."
    else:
        message = f"Only {dry_days} dry days in the next 7 days. Sufficient moisture expected."
        
    return {
        "alert": alert,
        "severity": severity,
        "dry_days": dry_days,
        "message": message
    }

def format_weather_card(day_data):
    rain = day_data.get("rain_mm", 0)
    
    if rain >= 10:
        emoji = "🌧️ Heavy Rain"
    elif rain >= 1:
        emoji = "🌦️ Light Rain"
    else:
        emoji = "☀️ Sunny/Dry"
        
    formatted = day_data.copy()
    formatted["condition"] = emoji
    return formatted
