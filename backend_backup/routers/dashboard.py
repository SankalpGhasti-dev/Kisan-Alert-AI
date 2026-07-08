"""
Dashboard Router — Orchestrates ALL modules into a single dashboard payload.

Provides:
  - Location endpoints (states, districts) for dropdowns
  - Master dashboard generation endpoint
"""

from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


# ─────────────────────────────────────────────────────────────
# Location Endpoints — for populating dropdowns
# ─────────────────────────────────────────────────────────────


@router.get("/states")
async def get_states():
    """Return list of all unique states from soil_npk.csv."""
    from backend.main import app_state

    return {"success": True, "states": app_state["states"]}


@router.get("/districts")
async def get_districts(state: str = Query(..., description="State name")):
    """Return districts for a given state from soil_npk.csv."""
    from backend.main import app_state

    soil_df = app_state["soil_df"]
    districts = sorted(
        soil_df[soil_df["state"] == state]["district"].unique().tolist()
    )
    if not districts:
        raise HTTPException(
            status_code=404, detail=f"No districts found for state '{state}'"
        )
    return {"success": True, "districts": districts}


# ─────────────────────────────────────────────────────────────
# Master Dashboard Generation
# ─────────────────────────────────────────────────────────────


class DashboardRequest(BaseModel):
    state: str
    district: str


@router.post("/generate")
async def generate_dashboard(req: DashboardRequest):
    """
    Generate all dashboard data in a single call.

    Orchestrates:
      1. Soil lookup from soil_npk.csv
      2. Coordinates from districts.csv
      3. Weather forecast via modules/weather.py
      4. Crop recommendations via modules/crop_rec.py + fallbacks
      5. Irrigation advisory via modules/irrigation.py
      6. Dry spell detection via modules/weather.py

    Returns a consolidated JSON payload for the frontend dashboard.
    """
    from backend.main import app_state
    from backend.routers.crop import get_crop_recommendations, get_current_season
    from modules import weather, irrigation

    soil_df = app_state["soil_df"]
    dist_df = app_state["dist_df"]

    # ── 1. Soil lookup ──
    soil_row = soil_df[
        (soil_df["state"] == req.state) & (soil_df["district"] == req.district)
    ]
    if soil_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Soil data not found for {req.district}, {req.state}",
        )
    soil_row = soil_row.iloc[0]

    N = float(soil_row["N"])
    P = float(soil_row["P"])
    K = float(soil_row["K"])
    pH = float(soil_row["pH"])
    soil_type = str(soil_row["soil_type"])

    soil_data = {
        "N": N,
        "P": P,
        "K": K,
        "pH": pH,
        "soil_type": soil_type,
    }

    # ── 2. Coordinates lookup ──
    dist_row = dist_df[
        (dist_df["state"] == req.state) & (dist_df["district"] == req.district)
    ]
    if dist_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Coordinates not found for {req.district}, {req.state}",
        )
    dist_row = dist_row.iloc[0]
    lat = float(dist_row["latitude"])
    lon = float(dist_row["longitude"])

    soil_data["lat"] = lat
    soil_data["lon"] = lon

    # ── 3. Weather ──
    weather_data = weather.get_weather(lat, lon)
    if not weather_data:
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

    # ── 4. Crop recommendations ──
    temp = weather_data.get("current_temp", 25.0)
    humidity = weather_data.get("current_humidity", 60.0)
    rainfall = weather_data.get("total_7day_rain", 0.0)

    crop_results, used_ai = get_crop_recommendations(
        N=N, P=P, K=K, ph=pH,
        temp=temp, humidity=humidity,
        rainfall=rainfall, soil_type=soil_type,
    )

    # ── 5. Irrigation advisory (for top crop, default Vegetative stage) ──
    top_crop = crop_results[0]["crop"] if crop_results else "Wheat"
    daily_data = weather_data.get("daily", [])

    avg_et0 = (
        sum(d.get("et0", 0) for d in daily_data) / len(daily_data)
        if daily_data
        else 3.0
    )
    rain_7d = weather_data.get("total_7day_rain", 0)

    irrigation_data = irrigation.get_irrigation_advisory(
        crop=top_crop,
        stage="Vegetative",
        et0_avg=avg_et0,
        rainfall_7day=rain_7d,
        soil_type=soil_type,
        district=req.district,
    )

    # ── 6. Dry spell detection ──
    dry_spell = weather.detect_dry_spell(daily_data)

    # ── Build response ──
    return {
        "success": True,
        "location": {
            "state": req.state,
            "district": req.district,
            "lat": lat,
            "lon": lon,
        },
        "season": get_current_season(),
        "soil": soil_data,
        "weather": weather_data,
        "crop_recommendations": {
            "used_ai_model": used_ai,
            "recommendations": crop_results,
        },
        "irrigation": irrigation_data,
        "dry_spell": dry_spell,
    }
