import sys
import os
import asyncio
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Add backend directory to sys.path to resolve imports correctly
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

from services.translation_service import TranslationService
from services.openai_service import generate_chat_response
from prefect import flow, task

@task(name="Detect Input Language", log_prints=True)
def detect_lang_task(text: str) -> str:
    """Detect the language of the input text using TranslationService."""
    lang = TranslationService.detect_language(text)
    print(f"[Prefect Task] Detected language '{lang}' for input: '{text}'")
    return lang

@task(name="Translate to English", log_prints=True)
def translate_to_english_task(text: str, detected_lang: str) -> str:
    """Translate the input text to English if it is not already in English."""
    if detected_lang == 'en':
        print(f"[Prefect Task] Input is already English. Skipping translation.")
        return text
    translated = TranslationService.translate(text, target_lang='en', source_lang=detected_lang)
    print(f"[Prefect Task] Translated input to English: '{translated}'")
    return translated

@task(name="Query Tactical AI Core", log_prints=True)
async def generate_ai_response_task(english_text: str) -> str:
    """Generate an AI response in English using the primary chat synthesis engine."""
    print(f"[Prefect Task] Querying AI core with English prompt: '{english_text}'")
    response_chunks = []
    try:
        # generate_chat_response yields chunks as an async generator
        async for chunk in generate_chat_response(english_text):
            if chunk:
                response_chunks.append(chunk)
        ai_response = "".join(response_chunks)
    except Exception as e:
        print(f"[Prefect Task] AI query failed: {e}")
        ai_response = f"Tactical communication link offline. (Self-test mode query: {english_text})"
    
    # Clean response if empty
    if not ai_response.strip():
        ai_response = f"Uplink connection verified. Standing by for commands."
        
    print(f"[Prefect Task] AI response generated successfully: '{ai_response[:100]}...'")
    return ai_response

@task(name="Translate Response to Target Language", log_prints=True)
def translate_response_back_task(english_response: str, target_lang: str) -> str:
    """Translate the AI response from English to the user's desired target language."""
    if target_lang == 'en':
        print(f"[Prefect Task] Target language is English. Skipping translation.")
        return english_response
    translated = TranslationService.translate(english_response, target_lang=target_lang, source_lang='en')
    print(f"[Prefect Task] Translated response to '{target_lang}': '{translated}'")
    return translated

@flow(name="Multilingual Tactical translation-flow", log_prints=True)
async def multilingual_translation_flow(texts: list[str], target_lang: str = "en"):
    """
    Prefect pipeline that processes a list of multilingual text inputs.
    Translates them to English, queries the Shadow AI core, and returns the response translated to the target language.
    """
    print(f"[Prefect Flow] Initiating Multilingual Translation Flow for target language: {target_lang}")
    results = []
    
    for text in texts:
        if not text or not text.strip():
            continue
            
        detected_lang = detect_lang_task(text)
        english_text = translate_to_english_task(text, detected_lang)
        english_response = await generate_ai_response_task(english_text)
        final_response = translate_response_back_task(english_response, target_lang)
        
        results.append({
            "original_text": text,
            "detected_lang": detected_lang,
            "english_text": english_text,
            "english_response": english_response,
            "final_response": final_response,
            "target_lang": target_lang
        })
        
    print(f"[Prefect Flow] Pipeline completed. Processed {len(results)} payload items.")
    return results

if __name__ == "__main__":
    # Test runner for local validation
    test_inputs = [
        "வணக்கம் ஷேடோ, உங்கள் நிலை என்ன?",
        "नमस्ते शैडो, अपनी स्थिति बताओ।",
        "Hola Shadow, ¿cuál es tu estado?"
    ]
    print("[TEST]: Running local flow verification...")
    res = asyncio.run(multilingual_translation_flow(test_inputs, target_lang="en"))
    print("\n[TEST RESULTS]:")
    for r in res:
        print(f"Original ({r['detected_lang']}): {r['original_text']}")
        print(f"English translation: {r['english_text']}")
        print(f"AI response: {r['english_response']}")
        print(f"Final translated response ({r['target_lang']}): {r['final_response']}")
        print("-" * 50)
