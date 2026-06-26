import asyncio
import os
import sys
from unittest.mock import MagicMock

# Add current directory to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__)))

async def test_google_tts():
    print("--- [DIAGNOSTIC]: Testing Google Neural TTS Service ---")
    
    # We'll try to import the service
    try:
        from services.google_tts_service import GoogleTTSService
        print("[SUCCESS]: GoogleTTSService imported successfully.")
    except ImportError as e:
        print(f"[FAILURE]: Could not import GoogleTTSService: {e}")
        return

    # Check for credentials
    creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        print("[WARNING]: GOOGLE_APPLICATION_CREDENTIALS not set in environment.")
    else:
        print(f"[INFO]: Credentials path: {creds}")

    # Attempt synthesis (English)
    print("[PROCESS]: Synthesizing 'Hello Boss, Neural TTS is online.' in English...")
    audio_b64 = await GoogleTTSService.synthesize("Hello Boss, Neural TTS is online.", "en-US")
    
    if audio_b64:
        print(f"[SUCCESS]: Received audio content (Length: {len(audio_b64)} chars)")
    else:
        print("[FAILURE]: Synthesis returned no audio. (This is expected if credentials are not yet configured by the user)")

    # Attempt synthesis (Tamil)
    print(f"[PROCESS]: Synthesizing Tamil greeting...")
    audio_b64_ta = await GoogleTTSService.synthesize("வணக்கம் பாஸ்", "ta-IN")
    
    if audio_b64_ta:
        print(f"[SUCCESS]: Received Tamil audio content (Length: {len(audio_b64_ta)} chars)")
    else:
        print("[FAILURE]: Tamil synthesis failed.")

    print("--- [DIAGNOSTIC COMPLETE] ---")

if __name__ == "__main__":
    asyncio.run(test_google_tts())
