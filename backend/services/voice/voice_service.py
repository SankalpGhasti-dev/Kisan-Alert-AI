import base64
import os
from fastapi import UploadFile
from backend.services.voice.stt import transcribe_audio
from backend.services.voice.tts import synthesize_speech
from backend.schemas.copilot import ConversationContext
from backend.services.copilot.copilot import handle_copilot_interaction

async def process_voice_request(
    audio_bytes: bytes, 
    state: str, 
    district: str, 
    user_profile: dict = None,
    language: str = "Auto Detect",
    current_page: str = "Dashboard",
    response_mode: str = "voice",
    gender: str = "Female",
    speed: float = 1.0,
    voice_on: bool = True
) -> dict:
    # 1. Speech to Text
    try:
        user_text, detected_lang_code = transcribe_audio(audio_bytes, language=language)
        if not user_text:
             return {
                 "success": False,
                 "error_type": "no_speech",
                 "message": "No speech detected"
             }
    except Exception as e:
        return {
            "success": False,
            "error_type": "stt_failed",
            "message": f"Transcription failed: {str(e)}"
        }

    # Map detected language code back to our formal names if Auto Detect was used
    final_language = language
    if language == "Auto Detect":
        code_map = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
        final_language = code_map.get(detected_lang_code, "English")

    # 2. Call existing Copilot logic using ConversationContext
    copilot_req = ConversationContext(
        response_mode=response_mode,
        language=final_language,
        user_message=user_text,
        current_page=current_page,
        selected_state=state,
        selected_district=district,
        user_profile=user_profile
    )
    
    copilot_response = await handle_copilot_interaction(copilot_req)
    
    if type(copilot_response) is dict and not copilot_response.get("success"):
        return {
            "success": False,
            "error_type": "copilot_failed",
            "message": copilot_response.get("answer", "Copilot processing failed"),
            "user_text": user_text
        }
        
    # the router returns a dict natively so we can access it directly
    ai_answer = copilot_response["answer"]
    
    # 3. Text to Speech (if enabled)
    audio_base64 = None
    if voice_on:
        try:
            clean_text = ai_answer.replace("**", "").replace("*", "").replace("#", "")
            audio_file_path = await synthesize_speech(
                text=clean_text, 
                language=final_language, 
                gender=gender, 
                speed=speed
            )
            
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
            os.remove(audio_file_path)
        except Exception as e:
            pass # TTS failure returns text only

    # 4. Return unified payload
    return {
        "success": True,
        "user_text": user_text,
        "answer": ai_answer,
        "audio_base64": audio_base64,
        "context_used": copilot_response.get("context_used", {})
    }

async def process_text_synthesize(
    text: str,
    language: str = "English",
    gender: str = "Female",
    speed: float = 1.0
) -> dict:
    """Used when user types but wants TTS response."""
    audio_base64 = None
    try:
        clean_text = text.replace("**", "").replace("*", "").replace("#", "")
        audio_file_path = await synthesize_speech(
            text=clean_text, 
            language=language, 
            gender=gender, 
            speed=speed
        )
        
        with open(audio_file_path, "rb") as f:
            audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
        os.remove(audio_file_path)
    except Exception:
        pass
        
    return {
        "success": True,
        "audio_base64": audio_base64
    }

async def process_voice_stream(
    audio_bytes: bytes, 
    state: str, 
    district: str, 
    user_profile: dict = None,
    language: str = "Auto Detect",
    current_page: str = "Dashboard",
    response_mode: str = "voice",
    gender: str = "Female",
    speed: float = 1.0,
    voice_on: bool = True
):
    import json
    import time
    
    t_start_total = time.time()
    print("\n" + "="*50)
    print("🎙️ KISAN AI COPILOT PERFORMANCE PROFILING 🎙️")
    print("="*50)
    
    audio_kb = len(audio_bytes) / 1024
    print(f"[METRIC] Audio File Size: {audio_kb:.2f} KB")
    
    yield json.dumps({"stage": "stt_started"}) + "\n\n"
    
    # 1. STT
    t_stt_start = time.time()
    try:
        user_text, detected_lang_code = transcribe_audio(audio_bytes, language=language)
        t_stt_end = time.time()
        print(f"Speech-to-Text: {(t_stt_end - t_stt_start)*1000:.0f} ms")
        
        if not user_text:
             yield json.dumps({
                 "stage": "error",
                 "error_type": "no_speech",
                 "message": "No speech detected"
             }) + "\n\n"
             return
        
        print(f"[STT QUALITY] Language: {detected_lang_code}")
        print(f"[STT QUALITY] Transcript: {user_text}")
    except Exception as e:
        yield json.dumps({
            "stage": "error",
            "error_type": "stt_failed",
            "message": f"Transcription failed: {str(e)}"
        }) + "\n\n"
        return

    final_language = language
    if language == "Auto Detect":
        code_map = {"en": "English", "hi": "Hindi", "mr": "Marathi"}
        final_language = code_map.get(detected_lang_code, "English")

    yield json.dumps({
        "stage": "stt_completed", 
        "user_text": user_text,
        "language_detected": final_language
    }) + "\n\n"

    # 2. Copilot Stream
    copilot_req = ConversationContext(
        response_mode=response_mode,
        language=final_language,
        user_message=user_text,
        current_page=current_page,
        selected_state=state,
        selected_district=district,
        user_profile=user_profile
    )
    
    from backend.services.copilot.copilot import handle_copilot_interaction_stream
    copilot_response_payload = None
    async for event in handle_copilot_interaction_stream(copilot_req):
        # We intercept copilot_completed to extract answer for TTS
        event_str = event.strip()
        if event_str:
            event_data = json.loads(event_str)
            if event_data.get("stage") == "copilot_completed":
                copilot_response_payload = event_data
            else:
                yield event
    
    if not copilot_response_payload or not copilot_response_payload.get("success"):
        yield json.dumps({
            "stage": "error",
            "error_type": "copilot_failed",
            "message": copilot_response_payload.get("answer", "Copilot processing failed") if copilot_response_payload else "Unknown error"
        }) + "\n\n"
        return

    ai_answer = copilot_response_payload.get("answer")
    
    # 3. TTS
    yield json.dumps({"stage": "tts_started", "answer": ai_answer}) + "\n\n"
    
    audio_base64 = None
    if voice_on:
        t_tts_start = time.time()
        try:
            clean_text = ai_answer.replace("**", "").replace("*", "").replace("#", "")
            audio_file_path = await synthesize_speech(
                text=clean_text, 
                language=final_language, 
                gender=gender, 
                speed=speed
            )
            
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
            os.remove(audio_file_path)
        except Exception as e:
            pass
        t_tts_end = time.time()
        print(f"Text-to-Speech: {(t_tts_end - t_tts_start)*1000:.0f} ms")
            
    t_end_total = time.time()
    print(f"TOTAL Backend Pipeline: {(t_end_total - t_start_total)*1000:.0f} ms")
    print("="*50 + "\n")
    
    yield json.dumps({
        "stage": "completed",
        "audio_base64": audio_base64,
        "context_used": copilot_response_payload.get("context_used", {})
    }) + "\n\n"
