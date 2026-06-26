import asyncio
import sys
import os
import io

# Ensure UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.translation_service import TranslationService
from services.openai_service import generate_chat_response

async def demo_loop():
    print("--- SHADOW V2.0 MULTILINGUAL DEMO ---")
    print("Supports: Tamil, Hindi, Spanish, French, English, etc.")
    print("Type 'exit' to terminate.")
    
    while True:
        user_input = input("\n[OPERATIVE]: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        # Detect language for demo output
        lang = TranslationService.detect_language(user_input)
        print(f"[SYSTEM]: Detected Language: {lang}")
        
        # Process through integrated AI (which now handles translation internally)
        try:
            response = await generate_chat_response(user_input)
            print(f"[SHADOW]: {response}")
        except Exception as e:
            print(f"[ERROR]: Protocol failure: {e}")

if __name__ == "__main__":
    asyncio.run(demo_loop())
