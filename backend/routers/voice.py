from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from typing import Optional
from backend.services.voice.voice_service import process_voice_request, process_text_synthesize, process_voice_stream
import json

router = APIRouter()

@router.post("/process")
async def process_voice(
    audio: UploadFile = File(...),
    state: str = Form(...),
    district: str = Form(...),
    user_profile: Optional[str] = Form(None), # JSON string
    language: str = Form("Auto Detect"),
    current_page: str = Form("Dashboard"),
    response_mode: str = Form("voice"),
    gender: str = Form("Female"),
    speed: float = Form(1.0),
    voice_on: bool = Form(True)
):
    """
    Endpoint for Voice Interaction.
    Takes an audio file + context, runs STT -> Copilot -> TTS, and returns JSON.
    """
    audio_bytes = await audio.read()
    
    parsed_user = None
    if user_profile:
        try:
            parsed_user = json.loads(user_profile)
        except Exception:
            pass

    response = await process_voice_request(
        audio_bytes=audio_bytes,
        state=state,
        district=district,
        user_profile=parsed_user,
        language=language,
        current_page=current_page,
        response_mode=response_mode,
        gender=gender,
        speed=speed,
        voice_on=voice_on
    )
    return response

@router.post("/stream")
async def process_voice_streaming(
    audio: UploadFile = File(...),
    state: str = Form(...),
    district: str = Form(...),
    user_profile: Optional[str] = Form(None), # JSON string
    language: str = Form("Auto Detect"),
    current_page: str = Form("Dashboard"),
    response_mode: str = Form("voice"),
    gender: str = Form("Female"),
    speed: float = Form(1.0),
    voice_on: bool = Form(True)
):
    """
    Streaming endpoint for Voice Interaction.
    Yields SSE chunks of progress.
    """
    audio_bytes = await audio.read()
    
    parsed_user = None
    if user_profile:
        try:
            parsed_user = json.loads(user_profile)
        except Exception:
            pass

    return StreamingResponse(
        process_voice_stream(
            audio_bytes=audio_bytes,
            state=state,
            district=district,
            user_profile=parsed_user,
            language=language,
            current_page=current_page,
            response_mode=response_mode,
            gender=gender,
            speed=speed,
            voice_on=voice_on
        ), 
        media_type="text/event-stream"
    )

@router.post("/synthesize")
async def synthesize_text(
    text: str = Form(...),
    language: str = Form("English"),
    gender: str = Form("Female"),
    speed: float = Form(1.0)
):
    """
    Endpoint for TTS-only (when user types but Voice is ON).
    """
    return await process_text_synthesize(text, language, gender, speed)
