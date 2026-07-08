from backend.services.dashboard_service import build_dashboard_data
from backend.main import app_state
from backend.schemas.copilot import ConversationContext
from backend.services.copilot.intent_router import get_required_modules

async def build_context(req: ConversationContext) -> dict:
    """
    Build the full context for the Copilot.
    Uses the intent_router to only include modules relevant to the query.
    """
    state = req.selected_state
    district = req.selected_district
    
    # 1. Determine which modules we actually need
    required = get_required_modules(req.user_message, req.current_page)
    
    context = {
        "user": req.user_profile,
        "location": {
            "state": state,
            "district": district
        }
    }
    
    # 2. Fetch dashboard data (the shared business logic)
    try:
        dashboard_data = await build_dashboard_data(state, district)
        context["location"]["lat"] = dashboard_data.get("location", {}).get("lat")
        context["location"]["lon"] = dashboard_data.get("location", {}).get("lon")
        
        # Only inject required modules to save Gemini tokens
        if "weather" in required:
            context["weather"] = dashboard_data.get("weather")
            context["dry_spell"] = dashboard_data.get("dry_spell")
        if "soil" in required:
            context["soil"] = dashboard_data.get("soil")
        if "crop_recommendation" in required:
            context["crop_recommendation"] = dashboard_data.get("crop_recommendations")
        if "irrigation" in required:
            context["irrigation"] = dashboard_data.get("irrigation")
            
    except Exception as e:
        context["dashboard_error"] = str(e)

    # 3. Fetch disease if required
    if "disease" in required:
        latest_disease = app_state.get("latest_disease", None)
        if latest_disease:
            context["disease"] = latest_disease

    return context
