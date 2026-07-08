def get_irrigation_advisory(crop, stage, et0_avg, rainfall_7day, soil_type, district):
    """
    Calculates simplified FAO-56 irrigation advisory.
    """
    # Normalize inputs
    crop = str(crop).lower().strip()
    stage = str(stage).lower().strip()
    
    # FAO-56 Crop Coefficients (Kc) for top 12 Indian crops
    kc_lookup = {
        "wheat": {"initial": 0.30, "vegetative": 0.75, "flowering": 1.15, "maturity": 0.40},
        "rice": {"initial": 1.05, "vegetative": 1.10, "flowering": 1.20, "maturity": 0.90},
        "maize": {"initial": 0.30, "vegetative": 0.80, "flowering": 1.20, "maturity": 0.35},
        "sugarcane": {"initial": 0.40, "vegetative": 0.85, "flowering": 1.25, "maturity": 0.70},
        "cotton": {"initial": 0.35, "vegetative": 0.75, "flowering": 1.15, "maturity": 0.70},
        "soybean": {"initial": 0.40, "vegetative": 0.75, "flowering": 1.15, "maturity": 0.50},
        "groundnut": {"initial": 0.40, "vegetative": 0.75, "flowering": 1.15, "maturity": 0.60},
        "onion": {"initial": 0.70, "vegetative": 0.90, "flowering": 1.05, "maturity": 0.75},
        "tomato": {"initial": 0.60, "vegetative": 0.80, "flowering": 1.15, "maturity": 0.80},
        "potato": {"initial": 0.50, "vegetative": 0.75, "flowering": 1.15, "maturity": 0.75},
        "banana": {"initial": 0.50, "vegetative": 0.80, "flowering": 1.10, "maturity": 1.20},
        "chickpea": {"initial": 0.40, "vegetative": 0.70, "flowering": 1.00, "maturity": 0.35}
    }
    
    # Default generic crop Kc if the specific crop isn't in the top 12
    crop_data = kc_lookup.get(crop, {"initial": 0.4, "vegetative": 0.8, "flowering": 1.05, "maturity": 0.6})
    
    # Fallback to vegetative if an unknown stage is provided
    kc = crop_data.get(stage, crop_data["vegetative"])
    
    # Daily crop water demand (mm)
    etc_daily = kc * float(et0_avg)
    
    # Effective rainfall (75% efficiency)
    effective_rainfall = float(rainfall_7day) * 0.75
    
    # Water deficit over 7 days
    water_deficit = max(0.0, (etc_daily * 7) - effective_rainfall)
    
    # Determine irrigation recommendation and urgency
    if water_deficit > 40:
        recommendation = f"Irrigate now — apply {water_deficit:.0f}mm within 2 days"
        urgency = "HIGH"
    elif water_deficit > 20:
        recommendation = f"Irrigate soon — apply {water_deficit:.0f}mm within 4-5 days"
        urgency = "MEDIUM"
    elif water_deficit > 0:
        recommendation = f"Monitor — light irrigation {water_deficit:.0f}mm if no rain"
        urgency = "LOW"
    else:
        recommendation = "No irrigation needed — rainfall sufficient"
        urgency = "NONE"
        
    # Determine soil adjustment note
    soil = str(soil_type).lower()
    if "sandy" in soil:
        soil_note = "Sandy soil — irrigate more frequently, less quantity"
    elif "clay" in soil:
        soil_note = "Clay soil — longer interval, deeper watering"
    elif "black" in soil:
        soil_note = "Black soil — excellent water retention, reduce frequency"
    elif "alluvial" in soil:
        soil_note = "Alluvial soil — standard irrigation schedule"
    elif "arid" in soil:
        soil_note = "Arid soil — mulching recommended to reduce evaporation"
    else:
        # Default fallback for unhandled soil types like Laterite/Red
        if "laterite" in soil or "red" in soil:
            soil_note = f"{soil_type} soil — standard monitoring recommended, drains moderately"
        else:
            soil_note = f"{soil_type} soil — standard irrigation schedule"
            
    return {
        "etc_daily": round(etc_daily, 2),
        "water_deficit_7day": round(water_deficit, 2),
        "recommendation": recommendation,
        "urgency": urgency,
        "soil_note": soil_note,
        "kc_used": kc
    }
