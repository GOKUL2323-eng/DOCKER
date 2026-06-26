import asyncio
import sys
import os
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.openai_service import generate_chat_response

async def test_multilingual():
    test_cases = [
        ("Tamil", "வணக்கம் ஷேடோ, உங்கள் நிலை என்ன?"),
        ("Hindi", "नमस्ते शैडो, अपनी स्थिति बताओ।"),
        ("Spanish", "Hola Shadow, ¿cuál es tu estado?"),
        ("English", "Hello Shadow, report status.")
    ]
    
    for lang, query in test_cases:
        print(f"\n[TESTING {lang}]: {query}")
        try:
            response_chunks = []
            async for chunk in generate_chat_response(query):
                if chunk:
                    response_chunks.append(chunk)
            print(f"[SHADOW]: {''.join(response_chunks)}")
        except Exception as e:
            print(f"[ERROR]: {e}")

if __name__ == "__main__":
    asyncio.run(test_multilingual())
