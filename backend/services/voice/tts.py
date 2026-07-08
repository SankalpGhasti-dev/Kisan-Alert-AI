import tempfile
import os
import edge_tts

async def synthesize_speech(text: str, language: str = "English", gender: str = "Female", speed: float = 1.0) -> str:
    """
    Synthesizes speech using edge-tts and returns the path to a temporary audio file.
    Caller is responsible for cleaning up the file if needed.
    """
    voice_map = {
        "English": {
            "Female": "en-US-AriaNeural",
            "Male": "en-US-ChristopherNeural"
        },
        "Hindi": {
            "Female": "hi-IN-SwaraNeural",
            "Male": "hi-IN-MadhurNeural"
        },
        "Marathi": {
            "Female": "mr-IN-AarohiNeural",
            "Male": "mr-IN-ManoharNeural"
        }
    }
    
    lang_map = voice_map.get(language, voice_map["English"])
    voice = lang_map.get(gender, lang_map["Female"])
    
    rate_percent = int((speed - 1.0) * 100)
    rate_str = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    
    fd, path = tempfile.mkstemp(suffix=".mp3")
    os.close(fd)
    
    await communicate.save(path)
    return path
