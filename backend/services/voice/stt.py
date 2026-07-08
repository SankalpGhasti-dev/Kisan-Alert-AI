import io
import os
from faster_whisper import WhisperModel

_model = None

def get_whisper_model():
    global _model
    if _model is None:
        _model = WhisperModel("base", device="cpu", compute_type="int8")
    return _model

def transcribe_audio(file_bytes: bytes, language: str = "Auto Detect") -> tuple[str, str]:
    """
    Transcribes audio bytes to text using faster-whisper.
    Returns a tuple of (transcribed_text, detected_language_code).
    """
    model = get_whisper_model()
    
    # Map user-friendly language names to Whisper language codes
    lang_map = {
        "English": "en",
        "Hindi": "hi",
        "Marathi": "mr"
    }
    
    transcribe_kwargs = {"beam_size": 5}
    if language in lang_map:
        transcribe_kwargs["language"] = lang_map[language]
        
    segments, info = model.transcribe(io.BytesIO(file_bytes), **transcribe_kwargs)
    text = " ".join([segment.text for segment in segments]).strip()
    
    # Return both the text and the detected (or forced) language code
    return text, info.language
