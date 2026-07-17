import os
import asyncio
import functools
import base64
from google.cloud import texttospeech
from core.config import settings

class GoogleTTSService:
    _client = None

    @classmethod
    def get_client(cls):
        if cls._client is None:
            # The client automatically looks for GOOGLE_APPLICATION_CREDENTIALS in env
            try:
                cls._client = texttospeech.TextToSpeechClient()
            except Exception as e:
                print(f"[GOOGLE_TTS]: Failed to initialize client. Ensure GOOGLE_APPLICATION_CREDENTIALS is set. Error: {e}")
                return None
        return cls._client

    @staticmethod
    def _synthesize_sync(text: str, lang_code: str = "en-US"):
        """Synchronous synthesis call to be run in executor."""
        client = GoogleTTSService.get_client()
        if not client:
            return None

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        # Auto-detect language of the response text
        detected_lang = lang_code
        try:
            from langdetect import detect
            code2 = detect(text).split("-")[0].lower()
            lang_mapping = {
                "en": "en-US",
                "es": "es-ES",
                "fr": "fr-FR",
                "de": "de-DE",
                "it": "it-IT",
                "ja": "ja-JP",
                "ko": "ko-KR",
                "zh": "zh-CN",
                "ru": "ru-RU",
                "pt": "pt-BR",
                "hi": "hi-IN",
                "ta": "ta-IN",
                "te": "te-IN",
                "kn": "kn-IN",
                "ml": "ml-IN",
                "ar": "ar-XA",
                "tr": "tr-TR",
                "nl": "nl-NL",
                "pl": "pl-PL",
                "vi": "vi-VN"
            }
            if code2 in lang_mapping:
                detected_lang = lang_mapping[code2]
            else:
                detected_lang = f"{code2}-{code2.upper()}"
        except Exception as e:
            print(f"[GOOGLE_TTS]: Language detection failed: {e}")
            detected_lang = lang_code

        # Build the voice request
        voice_params = {
            "language_code": detected_lang,
            "ssml_gender": texttospeech.SsmlVoiceGender.NEUTRAL
        }

        # Specific high-quality voice overrides
        if detected_lang.startswith("en"):
            voice_params["name"] = "en-US-Neural2-F"
        elif detected_lang.startswith("ta"):
            voice_params["name"] = "ta-IN-Wavenet-A"
        elif detected_lang.startswith("hi"):
            voice_params["name"] = "hi-IN-Neural2-A"

        voice = texttospeech.VoiceSelectionParams(**voice_params)

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=1.0,
            pitch=0.0
        )

        try:
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            return response.audio_content
        except Exception as e:
            print(f"[GOOGLE_TTS]: Synthesis error for {detected_lang}: {e}. Retrying with en-US fallback.")
            fallback_params = {
                "language_code": "en-US",
                "ssml_gender": texttospeech.SsmlVoiceGender.NEUTRAL
            }
            voice = texttospeech.VoiceSelectionParams(**fallback_params)
            response = client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            return response.audio_content

    @classmethod
    async def synthesize(cls, text: str, lang_code: str = "en-US"):
        """Asynchronous wrapper for the TTS synthesis."""
        if not text:
            return None

        loop = asyncio.get_running_loop()
        try:
            audio_content = await loop.run_in_executor(
                None,
                functools.partial(cls._synthesize_sync, text, lang_code)
            )
            
            if audio_content:
                # Return as base64 for easy transport to frontend
                return base64.b64encode(audio_content).decode("utf-8")
            return None
        except Exception as e:
            print(f"[GOOGLE_TTS]: Synthesis error: {e}")
            return None
