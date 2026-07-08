"""
Irrigation Router — Wraps modules/irrigation.py (UNCHANGED).

Provides irrigation advisory based on crop, stage, location.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class IrrigationRequest(BaseModel):
    crop: str
    stage: str  # "Initial", "Vegetative", "Flowering", "Maturity"
    state: str
    district: str


@router.post("/advisory")
async def get_advisory(req: IrrigationRequest):
    """
    Get irrigation advisory for a crop at a specific growth stage.
    Wraps: modules.irrigation.get_irrigation_advisory()
    """
    from backend.main import app_state
    from modules import weather, irrigation

    soil_df = app_state["soil_df"]
    dist_df = app_state["dist_df"]

    # Look up soil type
    soil_row = soil_df[
        (soil_df["state"] == req.state) & (soil_df["district"] == req.district)
    ]
    if soil_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Soil data not found for {req.district}, {req.state}",
        )
    soil_type = soil_row.iloc[0]["soil_type"]

    # Look up coordinates for weather
    dist_row = dist_df[
        (dist_df["state"] == req.state) & (dist_df["district"] == req.district)
    ]
    if dist_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"District not found: {req.district}, {req.state}",
        )
    lat = float(dist_row.iloc[0]["latitude"])
    lon = float(dist_row.iloc[0]["longitude"])

    # Fetch weather for ET0 and rainfall
    weather_data = weather.get_weather(lat, lon)
    daily_data = weather_data.get("daily", []) if weather_data else []

    avg_et0 = (
        sum(d.get("et0", 0) for d in daily_data) / len(daily_data)
        if daily_data
        else 3.0
    )
    rain_7d = weather_data.get("total_7day_rain", 0) if weather_data else 0

    # Call existing irrigation module — completely unchanged
    advisory = irrigation.get_irrigation_advisory(
        crop=req.crop,
        stage=req.stage,
        et0_avg=avg_et0,
        rainfall_7day=rain_7d,
        soil_type=soil_type,
        district=req.district,
    )

    return {"success": True, "data": advisory}
