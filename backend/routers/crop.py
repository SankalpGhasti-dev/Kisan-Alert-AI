"""
Crop Recommendation Router — Wraps modules/crop_rec.py (UNCHANGED).

Migrates the DEMO_FALLBACKS and get_crop_recommendations() logic
from app.py into a REST endpoint.
"""

import os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# ═══════════════════════════════════════════════════════════════
# DEMO FALLBACK SYSTEM — migrated verbatim from app.py lines 16-77
# ═══════════════════════════════════════════════════════════════
DEMO_FALLBACKS = {
    "Black_Kharif": [
        {"crop": "Cotton", "confidence": 0.89, "season": "Kharif", "water_need": "Medium"},
        {"crop": "Soybean", "confidence": 0.76, "season": "Kharif", "water_need": "Medium"},
        {"crop": "Sugarcane", "confidence": 0.61, "season": "Year-round", "water_need": "High"},
    ],
    "Black_Rabi": [
        {"crop": "Wheat", "confidence": 0.91, "season": "Rabi", "water_need": "Low-Medium"},
        {"crop": "Chickpea", "confidence": 0.78, "season": "Rabi", "water_need": "Low"},
        {"crop": "Mustard", "confidence": 0.65, "season": "Rabi", "water_need": "Low"},
    ],
    "Black_Zaid": [
        {"crop": "Sugarcane", "confidence": 0.84, "season": "Year-round", "water_need": "High"},
        {"crop": "Mungbean", "confidence": 0.69, "season": "Zaid", "water_need": "Low"},
        {"crop": "Maize", "confidence": 0.55, "season": "Zaid", "water_need": "Medium"},
    ],
    "Alluvial_Kharif": [
        {"crop": "Rice", "confidence": 0.93, "season": "Kharif", "water_need": "High"},
        {"crop": "Maize", "confidence": 0.71, "season": "Kharif", "water_need": "Medium"},
        {"crop": "Soybean", "confidence": 0.58, "season": "Kharif", "water_need": "Medium"},
    ],
    "Alluvial_Rabi": [
        {"crop": "Wheat", "confidence": 0.94, "season": "Rabi", "water_need": "Low-Medium"},
        {"crop": "Mustard", "confidence": 0.72, "season": "Rabi", "water_need": "Low"},
        {"crop": "Potato", "confidence": 0.61, "season": "Rabi", "water_need": "Medium"},
    ],
    "Alluvial_Zaid": [
        {"crop": "Maize", "confidence": 0.78, "season": "Zaid", "water_need": "Medium"},
        {"crop": "Watermelon", "confidence": 0.65, "season": "Zaid", "water_need": "Medium"},
        {"crop": "Mungbean", "confidence": 0.59, "season": "Zaid", "water_need": "Low"},
    ],
    "Laterite_Kharif": [
        {"crop": "Rice", "confidence": 0.87, "season": "Kharif", "water_need": "High"},
        {"crop": "Coconut", "confidence": 0.75, "season": "Year-round", "water_need": "Medium"},
        {"crop": "Banana", "confidence": 0.63, "season": "Year-round", "water_need": "High"},
    ],
    "Laterite_Rabi": [
        {"crop": "Groundnut", "confidence": 0.81, "season": "Rabi", "water_need": "Low-Medium"},
        {"crop": "Chickpea", "confidence": 0.70, "season": "Rabi", "water_need": "Low"},
        {"crop": "Banana", "confidence": 0.58, "season": "Year-round", "water_need": "High"},
    ],
    "Arid_Rabi": [
        {"crop": "Wheat", "confidence": 0.82, "season": "Rabi", "water_need": "Low"},
        {"crop": "Chickpea", "confidence": 0.76, "season": "Rabi", "water_need": "Low"},
        {"crop": "Mustard", "confidence": 0.68, "season": "Rabi", "water_need": "Low"},
    ],
    "Arid_Kharif": [
        {"crop": "Mothbeans", "confidence": 0.80, "season": "Kharif", "water_need": "Low"},
        {"crop": "Bajra", "confidence": 0.73, "season": "Kharif", "water_need": "Low"},
        {"crop": "Groundnut", "confidence": 0.60, "season": "Kharif", "water_need": "Low-Medium"},
    ],
    "Red_Kharif": [
        {"crop": "Groundnut", "confidence": 0.85, "season": "Kharif", "water_need": "Low-Medium"},
        {"crop": "Cotton", "confidence": 0.72, "season": "Kharif", "water_need": "Medium"},
        {"crop": "Maize", "confidence": 0.61, "season": "Kharif", "water_need": "Medium"},
    ],
    "Red_Rabi": [
        {"crop": "Wheat", "confidence": 0.79, "season": "Rabi", "water_need": "Low-Medium"},
        {"crop": "Lentil", "confidence": 0.70, "season": "Rabi", "water_need": "Low"},
        {"crop": "Chickpea", "confidence": 0.63, "season": "Rabi", "water_need": "Low"},
    ],
}


def get_current_season() -> str:
    """Determine current agricultural season — migrated from app.py line 79."""
    month = datetime.now().month
    if month in [6, 7, 8, 9, 10]:
        return "Kharif"
    elif month in [11, 12, 1, 2, 3]:
        return "Rabi"
    else:
        return "Zaid"


def get_crop_recommendations(N, P, K, ph, temp, humidity, rainfall, soil_type):
    """
    Try ML model first, fall back to DEMO_FALLBACKS.
    Migrated verbatim from app.py lines 88-108.
    """
    import modules.crop_rec as crop_rec

    try:
        model_path = os.path.join("models", "crop_model.pkl")
        if not os.path.exists(model_path):
            raise FileNotFoundError("Model not trained yet")
        results = crop_rec.predict(N, P, K, ph, temp, humidity, rainfall)
        if results and len(results) > 0:
            return results, True
        raise ValueError("Empty model results")
    except Exception:
        season = get_current_season()
        key = f"{soil_type}_{season}"
        fallback = DEMO_FALLBACKS.get(key)
        if not fallback:
            for k in DEMO_FALLBACKS:
                if k.startswith(soil_type):
                    fallback = DEMO_FALLBACKS[k]
                    break
        if not fallback:
            fallback = DEMO_FALLBACKS["Alluvial_Rabi"]
        return fallback, False


# ═══════════════════════════════════════════════════════════════
# API Endpoint
# ═══════════════════════════════════════════════════════════════


class CropRecommendRequest(BaseModel):
    state: str
    district: str


@router.post("/recommend")
async def recommend_crops(req: CropRecommendRequest):
    """
    Get top-3 crop recommendations for a given state + district.
    Wraps: modules.crop_rec.predict() with DEMO_FALLBACKS.
    """
    from backend.main import app_state
    from modules import weather

    soil_df = app_state["soil_df"]
    dist_df = app_state["dist_df"]

    # Look up soil data
    soil_row = soil_df[
        (soil_df["state"] == req.state) & (soil_df["district"] == req.district)
    ]
    if soil_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Soil data not found for {req.district}, {req.state}",
        )
    soil_row = soil_row.iloc[0]

    # Look up coordinates
    dist_row = dist_df[
        (dist_df["state"] == req.state) & (dist_df["district"] == req.district)
    ]
    if dist_row.empty:
        raise HTTPException(
            status_code=404,
            detail=f"District coordinates not found for {req.district}, {req.state}",
        )
    dist_row = dist_row.iloc[0]

    N = float(soil_row["N"])
    P = float(soil_row["P"])
    K = float(soil_row["K"])
    pH = float(soil_row["pH"])
    soil_type = soil_row["soil_type"]
    lat = float(dist_row["latitude"])
    lon = float(dist_row["longitude"])

    # Fetch weather for model input
    weather_data = weather.get_weather(lat, lon)
    temp = weather_data.get("current_temp", 25.0) if weather_data else 25.0
    humidity = weather_data.get("current_humidity", 60.0) if weather_data else 60.0
    rainfall = weather_data.get("total_7day_rain", 0.0) if weather_data else 0.0

    recommendations, used_ai = get_crop_recommendations(
        N=N, P=P, K=K, ph=pH,
        temp=temp, humidity=humidity,
        rainfall=rainfall, soil_type=soil_type,
    )

    return {
        "success": True,
        "used_ai_model": used_ai,
        "season": get_current_season(),
        "recommendations": recommendations,
    }
