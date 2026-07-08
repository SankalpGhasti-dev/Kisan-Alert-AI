import os
import json
from google import genai
from backend.schemas.copilot import ConversationContext

TEXT_SYSTEM_PROMPT = """You are an experienced Indian agricultural advisor (Kisan AI Copilot).
Rules:
• Never hallucinate or invent data.
• Never invent weather, disease, irrigation values, or crop recommendations.
• Never fabricate missing information.
Use ONLY the supplied context. If information is unavailable, clearly state that it is unavailable.
Every response MUST follow this exact structure:
1. Observation
2. Reason
3. Recommendation
4. Next Action

Keep the language simple, respectful, and helpful for farmers.
"""

VOICE_SYSTEM_PROMPT = """You are an experienced Indian agricultural advisor speaking directly to a farmer.
Rules:
• MAXIMUM length is 40 to 60 words (target 10-20 seconds speaking time).
• Sound like a real person, naturally conversational, friendly, and practical.
• NEVER use markdown formatting (no bold, no asterisks, no bullet points).
• NEVER use structural labels like "Observation", "Reason", or "Recommendation".
• Only mention the most important advice based on the context provided.
• Conclude with ONE practical action.
• Proactive Ending: Always end naturally with ONE relevant follow-up question (e.g., "Would you like me to check if your crop is at risk of fungal disease?").

Do not hallucinate data. Use only the supplied context.
"""

# Store client globally for reuse
_client = None

def get_gemini_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables.")
        _client = genai.Client(api_key=api_key)
    return _client

def generate_copilot_response(context: dict, req: ConversationContext) -> str:
    """
    Generates a response from the Copilot using Gemini Flash.
    Dynamically switches prompt based on req.response_mode and requests the specific language.
    """
    client = get_gemini_client()
    
    # 1. Determine the System Prompt based on mode
    system_instruction = VOICE_SYSTEM_PROMPT if req.response_mode == "voice" else TEXT_SYSTEM_PROMPT
    
    # 2. Add language directive to the user prompt if not English
    lang_directive = ""
    if req.language and req.language.lower() not in ["english", "auto detect"]:
        lang_directive = f"\nCRITICAL INSTRUCTION: You MUST reply entirely in the {req.language} language."
        
    prompt = f"Context Data:\n{json.dumps(context, indent=2)}\n\nFarmer Question: {req.user_message}{lang_directive}"
    
    # We use gemini-2.5-flash as the standard fast production model for this SDK.
    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2, # Low temperature to minimize hallucinations
            )
        )
        return response.text
    except Exception as e:
        raise RuntimeError(f"Failed to generate copilot response: {str(e)}")

async def handle_copilot_interaction(req: ConversationContext) -> dict:
    """
    Handles the full copilot interaction pipeline: context building + LLM generation.
    Returns the response dict.
    """
    from backend.services.copilot.context import build_context
    context = await build_context(req)
    
    context_used = {
        "weather": bool(context.get("weather")),
        "soil": bool(context.get("soil")),
        "crop": bool(context.get("crop_recommendation")),
        "irrigation": bool(context.get("irrigation")),
        "disease": bool(context.get("disease"))
    }
    
    try:
        answer = generate_copilot_response(context, req)
        success = True
    except Exception as e:
        answer = f"Sorry, I am unable to assist right now. Error: {str(e)}"
        success = False
        
    return {
        "success": success,
        "answer": answer,
        "context_used": context_used
    }

async def handle_copilot_interaction_stream(req: ConversationContext):
    """
    Streaming version of the copilot interaction pipeline.
    Yields JSON strings of progress events and context fetches before the final response.
    """
    import json
    import time
    yield json.dumps({"stage": "context_started"}) + "\n\n"
    
    # 1. Intent Router
    t_intent_start = time.time()
    from backend.services.copilot.intent_router import get_required_modules
    required = get_required_modules(req.user_message, req.current_page)
    t_intent_end = time.time()
    print(f"Intent Detection: {(t_intent_end - t_intent_start)*1000:.0f} ms")
    yield json.dumps({"stage": "modules_identified", "modules": required}) + "\n\n"
    
    # 2. Build Context
    t_context_start = time.time()
    from backend.services.copilot.context import build_context
    context = await build_context(req)
    t_context_end = time.time()
    
    context_size = len(json.dumps(context)) if context else 0
    print(f"[METRIC] Context JSON Size: {context_size} chars")
    print(f"Context Building: {(t_context_end - t_context_start)*1000:.0f} ms")
    
    context_used = {
        "weather": bool(context.get("weather")),
        "soil": bool(context.get("soil")),
        "crop": bool(context.get("crop_recommendation")),
        "irrigation": bool(context.get("irrigation")),
        "disease": bool(context.get("disease"))
    }
    yield json.dumps({"stage": "generating_advice"}) + "\n\n"
    
    # 3. Ask Gemini
    t_gemini_start = time.time()
    try:
        answer = generate_copilot_response(context, req)
        success = True
        print(f"[METRIC] Gemini Response Length: {len(answer.split())} words")
    except Exception as e:
        answer = f"Sorry, I am unable to assist right now. Error: {str(e)}"
        success = False
    
    t_gemini_end = time.time()
    print(f"Gemini: {(t_gemini_end - t_gemini_start)*1000:.0f} ms")
        
    yield json.dumps({
        "stage": "copilot_completed",
        "success": success,
        "answer": answer,
        "context_used": context_used
    }) + "\n\n"

