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
    from backend.services.dashboard_service import build_dashboard_data
    return await build_dashboard_data(req.state, req.district)
