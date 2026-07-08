"""
Weather Router — Wraps modules/weather.py (UNCHANGED).

Provides REST endpoints for:
  - 7-day weather forecast
  - Dry spell detection
"""

from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


def _lookup_coords(state: str, district: str) -> tuple:
    """Look up lat/lon from districts.csv via app_state."""
    from backend.main import app_state

    dist_df = app_state["dist_df"]
    row = dist_df[
        (dist_df["state"] == state) & (dist_df["district"] == district)
    ]
    if row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"District '{district}' in state '{state}' not found",
        )
    return float(row.iloc[0]["latitude"]), float(row.iloc[0]["longitude"])


@router.get("/forecast")
async def get_forecast(
    state: str = Query(..., description="State name"),
    district: str = Query(..., description="District name"),
):
    """
    Fetch 7-day weather forecast for the given state + district.
    Wraps: modules.weather.get_weather(lat, lon)
    """
    from modules import weather

    lat, lon = _lookup_coords(state, district)
    weather_data = weather.get_weather(lat, lon)

    if not weather_data:
        # Return fallback data (same logic as app.py lines 268-276)
        from datetime import datetime

        weather_data = {
            "current_temp": 25.0,
            "current_humidity": 60.0,
            "current_wind": 5.0,
            "daily": [
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "rain_mm": 0.0,
                    "tmax": 30.0,
                    "tmin": 20.0,
                    "et0": 4.0,
                }
            ]
            * 7,
            "total_7day_rain": 0.0,
            "avg_temp": 25.0,
        }

    return {"success": True, "data": weather_data}


@router.get("/dry-spell")
async def get_dry_spell(
    state: str = Query(..., description="State name"),
    district: str = Query(..., description="District name"),
):
    """
    Detect dry spell risk for the given state + district.
    Wraps: modules.weather.detect_dry_spell(daily_data)
    """
    from modules import weather

    lat, lon = _lookup_coords(state, district)
    weather_data = weather.get_weather(lat, lon)

    if not weather_data:
        daily_data = []
    else:
        daily_data = weather_data.get("daily", [])

    dry_spell = weather.detect_dry_spell(daily_data)
    return {"success": True, "data": dry_spell}
