import asyncio
import sys
import os
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.translation_service import TranslationService
from services.openai_service import normalize_thanglish_for_search, generate_chat_response, handle_simulation_mode

async def test_thanglish():
    print("=== TEST 1: Language Detection ===")
    test_phrases = [
        "enna panra bro",
        "summa iruken",
        "ur name enna",
        "epdi irukinga",
        "Hello, how are you?"
    ]
    for p in test_phrases:
        lang = TranslationService.detect_language(p)
        print(f"Phrase: '{p}' -> Detected Lang: {lang}")

    print("\n=== TEST 2: Query Normalization for Search ===")
    test_queries = [
        "ur name enna",
        "tamil nadu cm yaaru",
        "takshashila university enga iruku",
        "u epdi iruka"
    ]
    for q in test_queries:
        norm = normalize_thanglish_for_search(q)
        print(f"Original: '{q}' -> Normalized: '{norm}'")

    print("\n=== TEST 3: Chat Responses (Simulation Mode & LLM Engine) ===")
    test_messages = [
        "enna panra",
        "summa",
        "ur name enna",
        "epdi iruka",
        "tamil nadu cm yaaru"
    ]
    for m in test_messages:
        print(f"\n[USER QUERY]: {m}")
        print("[SIMULATION RESPONSE]:", await handle_simulation_mode([{"role": "user", "content": m}]))
        
        response_chunks = []
        async for chunk in generate_chat_response(m):
            if chunk:
                response_chunks.append(chunk)
        print(f"[SHADOW ENGINE RESPONSE]: {''.join(response_chunks)}")

if __name__ == "__main__":
    asyncio.run(test_thanglish())
