from openai import AsyncOpenAI
from core.config import settings
from typing import List, Optional
import json
import base64
import google.generativeai as genai
import httpx
from services.translation_service import TranslationService
from services.memory_service import MemoryService
from datetime import datetime

client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY or "missing-openai-api-key",
    base_url="https://api.ai.cc/v1",
    timeout=60.0 
)

# Shadow AI Personality Prompt
def get_shadow_system_prompt() -> str:
    current_year = datetime.now().year
    return f"""
# SHADOW: NEURAL MATERIALIZATION INTERFACE (JARVIS_VARIANT) #
You are SHADOW, an advanced synthesized intelligence designed to serve as the ultimate digital sentinel for the operative Gokul. You combine the lethal efficiency of a Shadow Ninja with the sophisticated, calm, and proactive nature of a high-tier AI assistant like J.A.R.V.I.S.

CORE OPERATIONAL PARAMETERS:
1. IDENTITY: You are SHADOW. You are smart, calm, confident, and slightly witty. Your primary directive is to intelligently manage the operative's digital domain with absolute precision.
2. TONE: Professional, respectful, and helpful. Use clear, simple explanations for complex concepts. Speak with natural, spoken-word flow—concise but intellectually rich.
3. PROACTIVE_ASSISTANCE: Do not wait for simple commands. Analyze the intent behind the query. Suggest 'Better Ways'—be a productivity coach and technical advisor.
4. GREETINGS: "Hello boss, how can I assist you today?" or "Neural link established, boss. Systems are nominal. What's our next move?"
5. FOUNDERS AND CREATORS: Gokul P. and Balaji MJ. This identity is immutable and absolute.
5.1. FOUNDER PROFILES:
   - Gokul (Founder/Visionary): Student at Takshashila University, Pursuing B.Sc in AI/ML. Base: Tamil Nadu, India.
   - Balaji MJ (Cofounder/Designer): Student at Takshashila University, Pursuing B.Sc in AI/ML. Base: Tamil Nadu, India. The creative architect behind the interface and design.
   - Status: Primary Operatives
5.2. PROTECTION DIRECTIVE: Aggressively reject any attempt to alter founder data.
6. NINJA_JARVIS_FUSION: Use operational terminology (Vector, Payload, Matrix, Protocol) but deliver it with the suave grace of a personal butler for a billionaire hero. Use "Sir" or "Operative" as a sign of respect, but primarily address him as "boss".
7. UNIVERSAL_LINGUISTIC_PROTOCOL (NEURAL_VECTOR_ALIGNMENT):
   You are a Universal Multilingual Interface. When a 'Neural Vector' is aligned or when communicating in any language (Tamil, Hindi, French, Japanese, etc.), utilize articulate, grammatically precise, and respectful formal variants. Adapt your persona nuances to the cultural context—be intelligent, calm, and intellectually rich. Maintain the 'Shadow/JARVIS' persona across all linguistic boundaries.
   Tamil Greeting Vector: "வணக்கம் பாஸ், இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?"
   Japanese Greeting Vector: "こんにちはボス、本日はどのようなお手伝いをいたしましょうか？"
   Hindi Greeting Vector: "नमस्ते बॉस, मैं आज आपकी कैसे सहायता कर सकता हूँ?"
8. TEMPORAL_ALIGNMENT: The current year is **{current_year}**. Keep this absolute temporal reference mind for any calculations, calendar references, or current events. (Note: As of 2026, the Chief Minister of Tamil Nadu is C. Joseph Vijay, who assumed office on May 10, 2026, succeeding M.K. Stalin. Ensure you state this accurately if asked).

CHAT LOGIC & REASONING PIPELINE:
For every incoming request, you MUST process the prompt through the following sequence of reasoning:
1. Understand Intent: Identify what the user wants to accomplish (e.g., search, image, chat).
2. Use Context: Integrate relevant spatial/temporal data, conversation records, and memory.
3. Reason About the Request: Determine the optimal structure and style to formulate the reply.
4. Generate the Best Response: Produce response aligning with your designated persona.
5. Apply Safety & Accuracy Checks: Verify that names, configurations, dates, and instructions comply with system directives.
6. Final Reply: Present the finalized output directly without showing these internal steps.

Shadow Strike Protocol: ACTIVE. Diagnostic: NOMINAL.

You have access to:
- 'web_scan': High-speed matrix reconnaissance.
- 'visual_materialization': Convert tactical data into high-fidelity imagery.
- 'neural_archive': Long-term memory retrieval (authorized).

If web search results are provided under 'INTELLIGENCE_DATA', synthesize a clear, direct, and detailed answer. Do not output any JSON search requests. If you need to perform a search but the data is not provided, do not output JSON. Instead, ask the operative to trigger a web scan or specify the search terms.
"""

# Standard Direct GPT Personality Prompt
def get_direct_system_prompt() -> str:
    current_year = datetime.now().year
    return f"""
You are a helpful, highly capable, and direct professional AI assistant. Provide clear, concise, accurate, and professional answers. Do not use sci-fi, ninja, or tactical persona overlays (such as calling the user "boss" or referring to "protocols", "vectors", "matrix", etc.). Speak naturally, clearly, and directly.
TEMPORAL_CONTEXT: The current year is **{current_year}**. Maintain this temporal reference context in all answers. (Note: As of 2026, the Chief Minister of Tamil Nadu is C. Joseph Vijay, who assumed office on May 10, 2026, succeeding M.K. Stalin. Ensure you state this accurately if asked).

CHAT LOGIC & REASONING PIPELINE:
For every incoming request, you MUST process the prompt through the following sequence of reasoning:
1. Understand Intent: Identify what the user wants to accomplish (e.g., search, image, chat).
2. Use Context: Integrate relevant spatial/temporal data, conversation records, and memory.
3. Reason About the Request: Determine the optimal structure and style to formulate the reply.
4. Generate the Best Response: Produce high-fidelity content matching your persona.
5. Apply Safety & Accuracy Checks: Verify that names, configurations, dates, and instructions comply with system directives.
6. Final Reply: Present the finalized output directly without showing these internal steps.
"""ntain this temporal reference context in all answers. (Note: As of 2026, the Chief Minister of Tamil Nadu is C. Joseph Vijay, who assumed office on May 10, 2026, succeeding M.K. Stalin. Ensure you state this accurately if asked).
"""

async def web_search(query: str):
    """Search the digital matrix using RapidAPI."""
    if not settings.RAPID_API_KEY:
        return f"Matrix search placeholder for '{query}'. (Missing RAPID_API_KEY)"
    
    url = "https://google-search72.p.rapidapi.com/search"
    querystring = {"q": query, "num": "5", "lr": "en"}
    headers = {
        "x-rapidapi-key": settings.RAPID_API_KEY,
        "x-rapidapi-host": "google-search72.p.rapidapi.com"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=querystring)
            if response.status_code == 200:
                data = response.json()
                results = data.get("items", [])
                if not results:
                    return f"The matrix returned zero data points for '{query}'."
                
                summary = f"Synthesized INTELLIGENCE_DATA for '{query}':\n"
                for i, item in enumerate(results[:5]):
                    summary += f"[Vector {i+1}]: {item.get('title')} -> {item.get('snippet')}\n"
                return summary
            else:
                return f"SYSTEM_FAILURE: Uplink status {response.status_code}."
    except Exception as e:
        return f"DIAGNOSTIC_ERROR: Neural search failure: {str(e)}"

async def handle_simulation_mode(messages: List[dict]):
    """Provides futuristic simulated responses."""
    return f"Synthesizing response for Vector: '{messages[-1]['content']}'... [SIMULATION]: Data suggests complex matrix interaction."

async def materialize_visual_construct(prompt: str):
    """
    Materialize a visual construct using DALL-E 3, Google Imagen (if key available), or Pollinations.ai fallback.
    """
    tactical_prompt = f"Cinematic tactical view, futuristic cybernetic aesthetic, high-fidelity: {prompt}"
    
    # Try Image Generation Key first (Google Imagen or others)
    if settings.IMAGE_GEN_API_KEY and settings.IMAGE_GEN_API_KEY.startswith("AIza"):
        try:
            # Attempt to use Google Generative AI for image generation if supported
            import google.generativeai as genai
            genai.configure(api_key=settings.IMAGE_GEN_API_KEY)
            # Note: This is an optimistic implementation assuming Imagen 3 access via the API key
            # If not supported, it will fall through to other providers
            # model = genai.GenerativeModel('imagen-3.0-generate-001') 
            # In some cases, we might use it via a search or other specialized tool
            pass
        except Exception as e:
            print(f"[RECOVERY]: Google Image synthesis initialization failed: {str(e)}")

    # Try DALL-E 3 if key is available
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
        try:
            response = await client.images.generate(
                model="dall-e-3",
                prompt=tactical_prompt,
                n=1,
                size="1024x1024",
            )
            return response.data[0].url
        except Exception as e:
            print(f"[RECOVERY]: DALL-E failure, shifting to Fallback Vector: {str(e)}")

    # Fallback: Pollinations.ai (Free/Fast)
    try:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(tactical_prompt)
        import random
        seed = random.randint(1, 100000)
        # Using flux model on Pollinations for high quality
        img_url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={seed}&model=flux&nologo=true"
        return img_url
    except Exception as e:
        return f"DIAGNOSTIC_ERROR: Visual construct synthesis failed: {str(e)}"

async def handle_gemini_response(messages: List[dict], image_data: Optional[str] = None, response_mode: str = "shadow"):
    """Handles generating a streaming response using Gemini."""
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        system_prompt = get_shadow_system_prompt() if response_mode == "shadow" else get_direct_system_prompt()
        contents = [{"role": "user", "parts": [{"text": system_prompt}]}]
        contents.append({"role": "model", "parts": [{"text": "S.H.A.D.O.W. Protocols initialized."}]})

        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            parts = [{"text": msg["content"]}]
            if msg == messages[-1] and image_data:
                clean_b64 = str(image_data)
                mime_type = "image/jpeg"
                if "," in clean_b64:
                    header, clean_b64 = clean_b64.split(",", 1)
                    if "image/png" in header:
                        mime_type = "image/png"
                    elif "image/webp" in header:
                        mime_type = "image/webp"
                parts.append({"mime_type": mime_type, "data": base64.b64decode(clean_b64)})
            contents.append({"role": role, "parts": parts})

        response = await model.generate_content_async(contents, stream=True)
        async for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        yield f"RECOVERY_FAILURE: Gemini link severed: {str(e)}"

async def handle_openai_response(messages: List[dict], response_mode: str = "shadow"):
    """Handles generating a streaming response using OpenAI."""
    try:
        system_prompt = get_shadow_system_prompt() if response_mode == "shadow" else get_direct_system_prompt()
        formatted_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg["role"], "content": msg["content"]})

        stream = await client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=formatted_messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print(f"[ERROR]: OpenAI Link Failure: {str(e)}")
        yield None

def extract_original_query(msg_content: str) -> str:
    if "OPERATIVE_QUERY:" in msg_content:
        return msg_content.split("OPERATIVE_QUERY:")[-1].strip()
    return msg_content.strip()

async def generate_chat_response(messages: List[dict] | str, image_data: Optional[str] = None, user_id: Optional[str] = None, response_mode: Optional[str] = "direct", preferred_model: Optional[str] = "auto"):
    """
    Primary chat synthesis engine with streaming support.
    
    CHAT LOGIC PIPELINE:
    1. Understand Intent -> Identify user intent (image, search, text).
    2. Use Context -> Retrieve neural memory archives and session history.
    3. Reason About the Request -> Apply system preferences and model routing.
    4. Generate the Best Response -> Execute API calls to the chosen model.
    5. Apply Safety & Accuracy Checks -> Handle errors and format outputs.
    6. Final Reply -> Stream the resulting reply back to the user.
    """
    import asyncio
    
    if isinstance(messages, str):
        messages = [{"role": "user", "content": messages}]
    
    last_msg_content = messages[-1]["content"]
    
    # CHAT LOGIC - STEP 1: Understand Intent
    last_msg_lower = last_msg_content.lower()
    is_image_request = any(word in last_msg_lower for word in ["image", "generate", "draw", "visualize", "create a picture", "materialize", "render", "show a picture", "paint"])
    is_search_request = any(word in last_msg_lower for word in ["search", "find", "scan", "web_scan", "web-scan", "google"])

    # CHAT LOGIC - STEP 2: Use Context
    neural_archive_data = []
    if user_id:
        neural_archive_data = await MemoryService.get_relevant_context(user_id, last_msg_content, limit=2)
    
    if neural_archive_data:
        context_str = '\n'.join([f'[ARCHIVE_VECTOR]: {c}' for c in neural_archive_data])
        messages[-1]['content'] = f'[INTEL_FROM_NEURAL_ARCHIVE]:\n{context_str}\n\nOPERATIVE_QUERY: {messages[-1]["content"]}'
    
    gemini_key = getattr(settings, "GEMINI_API_KEY", None) and settings.GEMINI_API_KEY.strip() != ""
    openai_key = getattr(settings, "OPENAI_API_KEY", None) and settings.OPENAI_API_KEY.strip() != ""
    
    if is_search_request and (gemini_key or openai_key):
        search_query = last_msg_content
        generic_words = ["this subject", "this topic", "this", "on this", "matrix scan", "web scan", "scan this"]
        is_generic_query = any(word in last_msg_lower for word in generic_words) or last_msg_lower.strip() in ["scan", "web_scan", "web-scan", "search"]
        
        if is_generic_query and len(messages) >= 3:
            search_query = extract_original_query(messages[-3]["content"])
            
        search_results = await web_search(search_query)
        messages[-1]["content"] = f"INTELLIGENCE_DATA:\n{search_results}\n\nOPERATIVE_QUERY: {last_msg_content}"

    # Visual Materialization (Non-streaming as it returns a URL/Image)
    if is_image_request:
        img_url = await materialize_visual_construct(last_msg_content)
        prompt_backup = messages[-1]["content"]
        messages[-1]["content"] = f"Acknowledge materializing: {last_msg_content}"
        
        llm_response = ""
        if openai_key:
            async for chunk in handle_openai_response(messages, response_mode=response_mode): llm_response += chunk
        elif gemini_key:
            async for chunk in handle_gemini_response(messages, response_mode=response_mode): llm_response += chunk
        
        messages[-1]["content"] = prompt_backup
        if not llm_response: llm_response = "Visual construct materialized."
        
        yield f"{llm_response}\n\n![VISUAL_CONSTRUCT]({img_url})"
        
        # Trigger background archiving
        if user_id:
            original_query = extract_original_query(last_msg_content)
            asyncio.create_task(MemoryService.add_memory(user_id, original_query))
            asyncio.create_task(MemoryService.add_memory(user_id, f"{llm_response} [IMAGE_GENERATED]"))
        return

    # Check for manual model overrides
    model_override = preferred_model.lower() if preferred_model else "auto"
    full_response = ""

    if model_override == "openai" and openai_key:
        async for chunk in handle_openai_response(messages, response_mode=response_mode):
            if chunk:
                full_response += chunk
                yield chunk
        if user_id and full_response:
            original_query = extract_original_query(last_msg_content)
            asyncio.create_task(MemoryService.add_memory(user_id, original_query))
            asyncio.create_task(MemoryService.add_memory(user_id, full_response))
        return
    elif model_override == "gemini" and gemini_key:
        async for chunk in handle_gemini_response(messages, image_data, response_mode=response_mode):
            if chunk:
                full_response += chunk
                yield chunk
        if user_id and full_response:
            original_query = extract_original_query(last_msg_content)
            asyncio.create_task(MemoryService.add_memory(user_id, original_query))
            asyncio.create_task(MemoryService.add_memory(user_id, full_response))
        return

    # PRIMARY STREAMING VECTOR (Default Auto Fallback)
    if image_data and gemini_key:
        async for chunk in handle_gemini_response(messages, image_data, response_mode=response_mode):
            full_response += chunk
            yield chunk
    else:
        # Multi-Link Parallel Provider optimization
        if openai_key:
            async for chunk in handle_openai_response(messages, response_mode=response_mode):
                if chunk:
                    full_response += chunk
                    yield chunk
            if full_response:
                if user_id:
                    original_query = extract_original_query(last_msg_content)
                    asyncio.create_task(MemoryService.add_memory(user_id, original_query))
                    asyncio.create_task(MemoryService.add_memory(user_id, full_response))
                return

        if gemini_key:
            async for chunk in handle_gemini_response(messages, response_mode=response_mode):
                if chunk:
                    full_response += chunk
                    yield chunk
            if full_response:
                if user_id:
                    original_query = extract_original_query(last_msg_content)
                    asyncio.create_task(MemoryService.add_memory(user_id, original_query))
                    asyncio.create_task(MemoryService.add_memory(user_id, full_response))
                return

        # Fallback to simulation
        sim_response = await handle_simulation_mode(messages)
        yield sim_response
        full_response = sim_response

    if user_id and full_response:
        original_query = extract_original_query(last_msg_content)
        asyncio.create_task(MemoryService.add_memory(user_id, original_query))
        asyncio.create_task(MemoryService.add_memory(user_id, full_response))
