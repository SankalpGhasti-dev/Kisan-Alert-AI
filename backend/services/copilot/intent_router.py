import re
from typing import List

def get_required_modules(user_message: str, current_page: str) -> List[str]:
    """
    Lightweight Intent Router.
    Analyzes the user's message and current page to determine which
    dashboard modules are actually needed to answer the question.
    Returns a list of module names to fetch.
    """
    user_message = user_message.lower()
    current_page = current_page.lower()
    
    required_modules = set()
    
    # 1. Page Awareness - automatically include context for the page they are on
    if "disease" in current_page:
        required_modules.add("disease")
        required_modules.add("weather")
    elif "weather" in current_page:
        required_modules.add("weather")
    elif "dashboard" in current_page:
        # Give them a minimal baseline, but wait for intent
        pass
    
    # 2. Intent Routing via Keyword Mapping
    weather_keywords = ["weather", "rain", "temperature", "hot", "cold", "wind", "humidity", "sun", "forecast", "mausam", "baarish", "paus", "hava", "hawa", "tapa", "tapman"]
    irrigation_keywords = ["irrigate", "water", "irrigation", "pani", "paani", "sinchai", "et0", "dry", "moisture", "sukha"]
    disease_keywords = ["disease", "spot", "yellow", "pest", "fungus", "rot", "sick", "bimari", "rog", "kida", "keeda"]
    crop_keywords = ["crop", "grow", "plant", "sow", "season", "fertilizer", "npk", "soil", "recommendation", "fasal", "pik", "mati", "maati", "mitti", "khad"]
    
    if any(k in user_message for k in weather_keywords):
        required_modules.update(["weather"])
        
    if any(k in user_message for k in irrigation_keywords):
        required_modules.update(["weather", "irrigation"])
        
    if any(k in user_message for k in disease_keywords):
        required_modules.update(["disease", "weather"])
        
    if any(k in user_message for k in crop_keywords):
        required_modules.update(["soil", "crop_recommendation", "weather"])
        
    # If no specific intent found, provide a minimal set
    if not required_modules:
        required_modules.update(["weather"])
        
    return list(required_modules)
