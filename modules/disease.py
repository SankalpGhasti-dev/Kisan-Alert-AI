import os
import io
import json
import traceback
from google import genai
from PIL import Image

print("================================")
print("DISEASE MODULE LOADED")
print(__file__)
print("================================")

def kvk_url(state):
    """
    Returns a Google search URL for the local Krishi Vigyan Kendra (KVK).
    """
    state_query = str(state).replace(" ", "+")
    return f"https://www.google.com/search?q=KVK+{state_query}+Krishi+Vigyan+Kendra+contact"

def diagnose_crop(image_bytes, crop_name, district, state):
    """
    Diagnoses crop disease using Gemini 1.5 Flash Vision based on the provided image bytes.
    """
    print("================================")
    print("DIAGNOSE FUNCTION CALLED")
    print("crop:", crop_name)
    print("district:", district)
    print("state:", state)
    print("================================")
    
    # Attempt to load the API key safely
    api_key = os.getenv("GEMINI_API_KEY")
    print("========== STEP 1 ==========")
    print("Loaded API Key?", "Yes" if api_key else "No")
    if not api_key:
        return {
            "health_status": "Uncertain",
            "disease_name": None,
            "severity": None,
            "symptoms_observed": "API key missing.",
            "treatment": "Please consult your local KVK (Krishi Vigyan Kendra)",
            "market_product": None,
            "kvk_referral": True,
            "confidence": "Low",
            "kvk_url": kvk_url(state)
        }
        
    client = genai.Client(api_key=api_key)
    
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        print("========== STEP 2 ==========")
        print("Image Successfully Loaded?")
        print(f"Format: {image.format}, Size: {image.size}")
    except Exception:
        return {
            "health_status": "Uncertain", 
            "disease_name": None, 
            "treatment": "Please consult your local KVK (Krishi Vigyan Kendra)",
            "kvk_referral": True, 
            "confidence": "Low",
            "kvk_url": kvk_url(state)
        }

    # Strict JSON formatting prompt with Chain of Thought
    prompt = f"""
You are a senior Indian agricultural scientist,
plant pathologist and crop disease expert.

Analyze this crop image.

Farmer Location:
District: {district}
State: {state}

Crop:
{crop_name}

TASK:

Classify this image into ONE of the following:

- Healthy
- Leaf Spot
- Early Blight
- Late Blight
- Rust
- Powdery Mildew
- Downy Mildew
- Anthracnose
- Bacterial Spot
- Wilt Disease
- Nutrient Deficiency
- Pest Damage
- Unknown Disease

Rules:

1. Always provide the MOST LIKELY diagnosis.
2. Never use "Uncertain" unless the image
   quality is unusable.
3. If confidence is medium, still provide
   the best probable disease.
4. Suggest treatment commonly available
   in Indian agricultural markets.
5. Suggest a KVK referral only if confidence
   is very low.

Return ONLY valid JSON:

{{
  "health_status":
    "Healthy" |
    "Diseased" |
    "Likely Diseased" |
    "Uncertain",

  "disease_name":
    "best probable disease",

  "severity":
    "Mild" |
    "Moderate" |
    "Severe",

  "symptoms_observed":
    "short description",

  "treatment":
    "recommended treatment",

  "market_product":
    "common Indian agricultural product",

  "kvk_referral":
    true | false,

  "confidence":
    "High" |
    "Medium" |
    "Low"
}}
"""

    try:
        print("========== STEP 3 ==========")
        print("Sending request to Gemini...")
        # Generate the vision response
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image]
        )
        
        print("========== STEP 4 ==========")
        print("Raw Gemini Response")
        print("Response object:", response)
        print("Response text:", response.text)

        # Clean up the response to handle potential markdown formatting
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        text = text.strip()
        print("========== STEP 5 ==========")
        print("Cleaned Response")
        print(text)

        print("========== STEP 6 ==========")
        print("JSON Parsing Started")
        
        # Parse the JSON
        result = json.loads(text)
        
        # Preserve original parsed for debugging
        parsed_response = json.dumps(result, indent=2)
        
        print("========== STEP 7 ==========")
        print("Parsed JSON")
        print(parsed_response)
        
        # Response Logic Mapping
        raw_status = result.get("health_status")
        confidence = result.get("confidence")
        disease_name = result.get("disease_name")

        if raw_status != "Healthy" and raw_status != "Uncertain":
            if confidence == "High":
                result["health_status"] = "Diseased"
            elif confidence == "Medium":
                result["health_status"] = "Likely Diseased"
            elif confidence == "Low":
                result["health_status"] = "Likely Diseased"

        if result.get("health_status") in [
            "Likely Diseased",
            "Possibly Diseased",
            "Suspected Disease",
            "Disease Suspected"
        ]:
            result["health_status"] = "Diseased"

        # KVK Referral Mapping
        if confidence == "Low" or disease_name == "Unknown Disease":
            result["kvk_referral"] = True
        else:
            result["kvk_referral"] = False
            
        # Optionally attach the KVK URL for convenience 
        result["kvk_url"] = kvk_url(state)
        
        # DEBUGGING: Print to logs
        print("========== STEP 8 ==========")
        print("Final Response Returned to FastAPI")
        print(json.dumps(result, indent=2))
        
        return result
        
    except Exception as e:
        print("========== GEMINI EXCEPTION ==========")
        print(f"Exception Type: {type(e)}")
        print(f"Exception Message: {str(e)}")
        print("Full Traceback:")
        traceback.print_exc()
        print("======================================")
        # Fallback dictionary upon JSON parsing failure or API exception
        return {
            "health_status": "Uncertain", 
            "disease_name": None, 
            "treatment": "Please consult your local KVK (Krishi Vigyan Kendra)",
            "kvk_referral": True, 
            "confidence": "Low",
            "kvk_url": kvk_url(state)
        }
