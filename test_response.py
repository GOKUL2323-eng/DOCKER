import asyncio
import sys
sys.path.insert(0, "shadow-ai/backend")
from dotenv import load_dotenv
load_dotenv("shadow-ai/backend/.env")

from services.openai_service import generate_chat_response

async def test():
    try:
        messages = [{"role": "user", "content": "what is the ipl 2026 final result"}]
        async for chunk in generate_chat_response(messages):
            print(chunk)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
