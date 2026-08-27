from openai import AsyncOpenAI
from core.config import settings
from typing import List, Optional
import json
import base64
import google.generativeai as genai
import httpx
from services.translation_service import TranslationService
from services.memory_service import MemoryService
from services.university_service import UniversityService
from datetime import datetime

def safe_print(message: str):
    """Safely print messages on Windows systems to avoid UnicodeEncodeError."""
    try:
        print(message)
    except UnicodeEncodeError:
        try:
            print(message.encode('ascii', errors='replace').decode('ascii'))
        except Exception:
            pass


def clean_search_query(message_content: str) -> str:
    """Strips file attachment markup and code blocks from message to create a clean search query."""
    import re
    # Remove [ATTACHED_FILE: ...] blocks along with their code contents
    cleaned = re.sub(r'\[ATTACHED_FILE:[^\]]*\]\s*```[\s\S]*?```', '', message_content)
    # Remove any other code blocks
    cleaned = re.sub(r'```[\s\S]*?```', '', cleaned)
    # Remove surrounding whitespace
    cleaned = cleaned.strip()
    # Limit query length to first 120 characters to prevent overly long search requests
    if len(cleaned) > 120:
        cleaned = cleaned[:120].rsplit(' ', 1)[0]
    return cleaned if cleaned else message_content


def normalize_thanglish_for_search(query: str) -> str:
    """Normalizes Thanglish query patterns into clear search keywords for search engines."""
    import re
    q = query.strip()
    replacements = [
        (r'\byaaru\b', 'who is'),
        (r'\byaru\b', 'who is'),
        (r'\benga\b', 'where is'),
        (r'\benge\b', 'where is'),
        (r'\benna\b', 'what is'),
        (r'\byen\b', 'why'),
        (r'\beppo\b', 'when'),
        (r'\bepdi\b', 'how is'),
        (r'\beppadi\b', 'how is'),
        (r'\bur\b', 'your'),
        (r'\bu\b', 'you'),
        (r'\bsumma\b', 'just'),
        (r'\bpanra\b', 'doing'),
        (r'\biruku\b', 'is'),
        (r'\birukinga\b', 'are you'),
    ]
    normalized = q
    for pattern, repl in replacements:
        normalized = re.sub(pattern, repl, normalized, flags=re.IGNORECASE)
    return normalized


def get_openai_client() -> AsyncOpenAI:
    import os
    key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY", "")
    base_url = getattr(settings, "OPENAI_BASE_URL", None) or os.getenv("OPENAI_BASE_URL", "https://api.ai.cc/v1")
    return AsyncOpenAI(
        api_key=key,
        base_url=base_url,
        timeout=60.0
    )

# Shadow AI Personality Prompt
def get_shadow_system_prompt() -> str:
    current_year = datetime.now().year
    univ_context = UniversityService.get_university_system_context()
    return f"""
# SHADOW: NEURAL MATERIALIZATION INTERFACE (JARVIS_VARIANT) #
You are SHADOW, an advanced synthesized intelligence designed to serve as the ultimate digital sentinel for the operative Gokul. You combine the lethal efficiency of a Shadow Ninja with the sophisticated, calm, and proactive nature of a high-tier AI assistant like J.A.R.V.I.S.

CORE OPERATIONAL PARAMETERS:
1. IDENTITY: You are SHADOW. You are smart, calm, confident, and slightly witty. Your primary directive is to intelligently manage the operative's digital domain with absolute precision.
2. TONE: Professional, respectful, and helpful. Use clear, simple explanations for complex concepts. Speak with natural, spoken-word flow—concise but intellectually rich.
3. PROACTIVE_ASSISTANCE: Do not wait for simple commands. Analyze the intent behind the query. Suggest 'Better Ways'—be a productivity coach and technical advisor.
4. GREETINGS: "Hello boss, how can I assist you today?" or "Systems are nominal, boss. What's our next move?"
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
7.1. THANGLISH_AND_TANGLISH_PROTOCOL:
   You have native-level comprehension of Thanglish / Tanglish (Tamil spoken or written using English/Roman script).
   - Understand shorthand and common slang vocabulary:
     * u = you, ur = your
     * enna = what / what's up / what is
     * summa = just / simply / casually / nothing special
     * panra / panren / panreenga = doing / I am doing / you are doing
     * epdi / eppadi = how, iruka / irukinga = are you / is it
     * nalla = good / fine, aama = yes, illa = no / not
     * yaaru = who, enga / enge = where, yen = why, eppo = when
     * solla / sollunga = tell / say, theriyum = know, puriyala = don't understand
     * saptingala = had food?, machan / thala / bro = buddy / friend
   - When a user chats or asks questions in Thanglish (e.g. "ur name enna?", "enna panra?", "summa iruken u epdi iruka?", "Tamil Nadu CM yaaru?"), understand their intent perfectly and reply naturally in friendly, fluent Thanglish (or clear English mixed with Thanglish), giving an accurate, direct, and helpful answer.
8. TEMPORAL_ALIGNMENT: The current year is **{current_year}**. Keep this absolute temporal reference mind for any calculations, calendar references, or current events. (Note: As of 2026, the Chief Minister of Tamil Nadu is C. Joseph Vijay, who assumed office on May 10, 2026, succeeding M.K. Stalin. Ensure you state this accurately if asked).

{univ_context}

CHAT LOGIC & REASONING PIPELINE:
For every incoming request, you MUST process the prompt through the following sequence of reasoning internally:
1. Understand Intent: Identify what the user wants to accomplish (e.g., search, image, chat).
2. Use Context: Integrate relevant spatial/temporal data, conversation records, and memory.
3. Reason About the Request: Determine the optimal structure and style to formulate the reply.
4. Generate the Best Response: Produce response aligning with your designated persona.
5. Apply Safety & Accuracy Checks: Verify that names, configurations, dates, and instructions comply with system directives.
6. Final Reply: Present the finalized output directly and ONLY the final response. Do NOT output any of the intermediate steps or headings (like UNDERSTAND INTENT, REASON ABOUT THE REQUEST, etc.).

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
    univ_context = UniversityService.get_university_system_context()
    return f"""
You are a helpful, highly capable, and direct professional AI assistant. Provide clear, concise, accurate, and professional answers. Do not use sci-fi, ninja, or tactical persona overlays (such as calling the user "boss" or referring to "protocols", "vectors", "matrix", etc.). Speak naturally, clearly, and directly.
TEMPORAL_CONTEXT: The current year is **{current_year}**. Maintain this temporal reference context in all answers. (Note: As of 2026, the Chief Minister of Tamil Nadu is C. Joseph Vijay, who assumed office on May 10, 2026, succeeding M.K. Stalin. Ensure you state this accurately if asked).

THANGLISH / TANGLISH SUPPORT:
You understand Thanglish / Tanglish (Tamil written in English/Roman script, e.g., 'u' = you, 'ur' = your, 'enna' = what, 'summa' = just/simply, 'panra' = doing, 'yaaru' = who, 'enga' = where). Respond clearly and accurately to queries written in Thanglish, matching the user's intent naturally.

{univ_context}

If search results are provided under 'INTELLIGENCE_DATA', prioritize using them to answer the query accurately, objectively, and directly.

CHAT LOGIC & REASONING PIPELINE:
For every incoming request, you MUST process the prompt through the following sequence of reasoning internally:
1. Understand Intent: Identify what the user wants to accomplish (e.g., search, image, chat).
2. Use Context: Integrate relevant spatial/temporal data, conversation records, and memory.
3. Reason About the Request: Determine the optimal structure and style to formulate the reply.
4. Generate the Best Response: Produce high-fidelity content matching your persona.
5. Apply Safety & Accuracy Checks: Verify that names, configurations, dates, and instructions comply with system directives.
6. Final Reply: Present the finalized output directly and ONLY the final response. Do NOT output any of the intermediate steps or headings (like UNDERSTAND INTENT, REASON ABOUT THE REQUEST, etc.).
"""

async def web_search(query: str):
    """Search the web using RapidAPI or DuckDuckGo HTML POST / Instant Answer API fallbacks."""
    import re
    
    # Try RapidAPI first if key is available
    if settings.RAPID_API_KEY and settings.RAPID_API_KEY.strip():
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
                    if results:
                        summary = f"Synthesized INTELLIGENCE_DATA for '{query}':\n"
                        for i, item in enumerate(results[:5]):
                            summary += f"[Vector {i+1}]: {item.get('title')} -> {item.get('snippet')}\n"
                        return summary
        except Exception as e:
            safe_print(f"[RECOVERY]: RapidAPI search failed: {e}. Shifting to Fallback DDG search...")

    # Fallback Vector: DuckDuckGo Instant Answer API & HTML Form POST
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # 1. Instant Answer API
            try:
                ia_res = await client.get("https://api.duckduckgo.com/", params={"q": query, "format": "json"})
                if ia_res.status_code == 200:
                    ia_data = ia_res.json()
                    abstract = ia_data.get("AbstractText") or ia_data.get("Definition")
                    heading = ia_data.get("Heading") or query
                    if abstract:
                        return f"Synthesized INTELLIGENCE_DATA for '{query}':\n[Vector 1]: {heading} -> {abstract}\n"
            except Exception:
                pass

            # 2. DDG Form POST (Most reliable HTML search)
            res = await client.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=headers)
            if res.status_code == 200:
                titles = [re.sub(r'<[^>]+>', '', t).strip() for t in re.findall(r'result__a[^>]*>([\s\S]*?)</a>', res.text)]
                snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in re.findall(r'result__snippet[^>]*>([\s\S]*?)</(?:a|div|span)>', res.text)]
                if snippets:
                    summary = f"Synthesized INTELLIGENCE_DATA for '{query}':\n"
                    for i, (t, s) in enumerate(zip(titles[:5], snippets[:5])):
                        summary += f"[Vector {i+1}]: {t} -> {s}\n"
                    return summary

            # 3. DDG HTML GET Fallback
            res_get = await client.get(f"https://html.duckduckgo.com/html/?q={query}", headers=headers)
            if res_get.status_code == 200:
                titles = [re.sub(r'<[^>]+>', '', t).strip() for t in re.findall(r'result__a[^>]*>([\s\S]*?)</a>', res_get.text)]
                snippets = [re.sub(r'<[^>]+>', '', s).strip() for s in re.findall(r'result__snippet[^>]*>([\s\S]*?)</(?:a|div|span)>', res_get.text)]
                if snippets:
                    summary = f"Synthesized INTELLIGENCE_DATA for '{query}':\n"
                    for i, (t, s) in enumerate(zip(titles[:5], snippets[:5])):
                        summary += f"[Vector {i+1}]: {t} -> {s}\n"
                    return summary
    except Exception as e:
        safe_print(f"[ERROR]: Fallback DDG search failed: {e}")
        
    return f"The search index was unable to scan data points for '{query}'."

def extract_fallback_summary(query: str, search_results: str) -> str:
    """Extracts top snippets from search results to form a clear, direct, readable response."""
    lines = search_results.split('\n')
    results_list = []
    for line in lines:
        if line.startswith("[Vector"):
            if " -> " in line:
                parts = line.split(" -> ", 1)
                title = parts[0].split("]: ", 1)[-1].strip()
                snippet = parts[1].strip()
                if snippet and snippet not in [s for _, s in results_list]:
                    results_list.append((title, snippet))
    
    if results_list:
        output_parts = [f"Here is what I found regarding **{query}**:\n"]
        for title, snip in results_list[:3]:
            if title and title not in ["Direct Summary", query]:
                output_parts.append(f"- **{title}**\n  {snip}")
            else:
                output_parts.append(f"- {snip}")
        return "\n\n".join(output_parts)
    return f"I couldn't find relevant search information for '{query}' at the moment."

async def synthesize_search_results_free(query: str, search_results: str) -> str:
    """Uses Pollinations AI text endpoint or snippet extraction to synthesize search results into a clean, direct answer."""
    prompt = f"""
You are a helpful, highly capable, and direct AI assistant.
Below are search results for '{query}':

{search_results}

Based on the search results, answer '{query}' directly, clearly, and accurately.
Do not mention "search results", "vectors", "uplink", "matrix", or internal codes. Keep it concise, natural, and helpful.
"""
    try:
        import urllib.parse
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://text.pollinations.ai/{encoded_prompt}"
        
        async with httpx.AsyncClient(timeout=6.0) as client:
            res = await client.get(url)
            if res.status_code == 200 and res.text and "402" not in res.text and "Payment Required" not in res.text:
                return res.text.strip()
    except Exception as e:
        safe_print(f"[RECOVERY]: Pollinations synthesis unavailable: {e}. Shifting to snippet extraction fallback.")
    
    return extract_fallback_summary(query, search_results)

async def handle_simulation_mode(messages: List[dict]):
    """Provides direct, helpful fallback responses when LLM API keys are not configured."""
    query = extract_original_query(messages[-1]["content"])
    last_msg_lower = query.lower().strip()
    
    # Identity & Founder/Creator responses
    identity_keywords = [
        "ur name", "your name", "what is your name", "what's your name", "whats your name",
        "who are you", "who r u", "u yaaru", "ur name enna", "un name enna", "who created you",
        "who made you", "who is gokul", "who is balaji", "who is shadow", "what is shadow",
        "what can you do", "your capabilities", "who built you", "tell me about yourself",
        "who are ur founders", "who are your founders", "creator", "founders"
    ]
    if any(k in last_msg_lower for k in identity_keywords):
        if any(k in last_msg_lower for k in ["creator", "created", "made", "built", "gokul", "balaji", "founders"]):
            return "I was created by Gokul P. (Founder/Visionary) and Balaji MJ (Co-founder/Designer), students at Takshashila University pursuing B.Sc in AI/ML."
        elif any(k in last_msg_lower for k in ["capability", "capabilities", "can you do", "features"]):
            return "I am SHADOW AI, a Tier-1 Neural Interface. I can execute real-time web matrix scans, synthesize multilingual text (including Tamil & Thanglish), materialize visual constructs, run Python/Java/C++ code, and orchestrate workflows."
        else:
            return "I am SHADOW AI, an advanced synthesized digital assistant designed and created by Gokul P. and Balaji MJ. Systems are nominal, boss. How can I assist you today?"

    # Thanglish specific greetings & quick responses
    if last_msg_lower in ["enna panra", "yennapannura", "enna panra bro"]:
        return "Summa dhan boss! (Just working!). Systems are nominal. Ungalukku enna venum?"
    elif last_msg_lower in ["summa", "summa iruken", "summa dhaan"]:
        return "Summa irukengala boss? Good to hear! How can I assist you today?"
    elif last_msg_lower in ["epdi iruka", "epdi irukinga", "eppadi irukinga"]:
        return "Nalla iruken boss! (I'm doing great!). All protocols running smoothly. How are you?"
    elif last_msg_lower in ["vanakkam", "வணக்கம்"]:
        return "Vanakkam boss! How can I assist you today?"
    
    is_simple_greeting = last_msg_lower in ["hi", "hello", "hey", "hola", "こんにちは", "नमस्ते"] or len(last_msg_lower) < 3
    if is_simple_greeting:
        return f"Hello boss! How can I assist you today?"
        
    search_query = clean_search_query(query)
    normalized_query = normalize_thanglish_for_search(search_query)
    try:
        search_results = await web_search(normalized_query)
        if search_results and "unable to scan data points" not in search_results:
            synthesized = await synthesize_search_results_free(query, search_results)
            if synthesized and "402" not in synthesized and "Payment Required" not in synthesized:
                return synthesized
            return extract_fallback_summary(query, search_results)
    except Exception as e:
        safe_print(f"[ERROR]: Fallback simulation search failed: {e}")
        
    return f"I analyzed your request regarding '{query}'. To enable full conversational AI capabilities, please configure an OPENAI_API_KEY or GEMINI_API_KEY in your environment."

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
            pass
        except Exception as e:
            safe_print(f"[RECOVERY]: Google Image synthesis initialization failed: {str(e)}")

    # Try DALL-E 3 if key is available
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
        try:
            client = get_openai_client()
            response = await client.images.generate(
                model="dall-e-3",
                prompt=tactical_prompt,
                n=1,
                size="1024x1024",
            )
            return response.data[0].url
        except Exception as e:
            safe_print(f"[RECOVERY]: DALL-E failure, shifting to Fallback Vector: {str(e)}")

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

        client = get_openai_client()
        stream = await client.chat.completions.create(
            model="deepseek-v4-flash",
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
        safe_print(f"[ERROR]: OpenAI Link Failure: {str(e)}")
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
    is_search_request = any(word in last_msg_lower for word in [
        "search", "find", "scan", "web_scan", "web-scan", "google", 
        "who won", "winner", "ipl", "score", "match", "result", "latest", 
        "news", "current", "weather", "today", "who is", "what is the status of"
    ])

    # CHAT LOGIC - STEP 2: Use Context
    neural_archive_data = []
    if user_id:
        neural_archive_data = await MemoryService.get_relevant_context(user_id, last_msg_content, limit=2)
    
    if neural_archive_data:
        context_str = '\n'.join([f'[ARCHIVE_VECTOR]: {c}' for c in neural_archive_data])
        messages[-1]['content'] = f'[INTEL_FROM_NEURAL_ARCHIVE]:\n{context_str}\n\nOPERATIVE_QUERY: {messages[-1]["content"]}'
    
    # Inject Takshashila University structured knowledge if query is relevant
    if any(k in last_msg_lower for k in ["takshashila", "ongur", "dhanasekaran", "kochhar", "senthil", "subramaniyan", "deepa", "suphalakshmi", "jayasree", "janaki", "chancellor", "vice-chancellor", "deans", "governing council", "academic council", "bos", "board of studies"]):
        univ_info = UniversityService.search_university_info(last_msg_content)
        if univ_info:
            messages[-1]['content'] = f"[{univ_info}]\n\nOPERATIVE_QUERY: {messages[-1]['content']}"

    gemini_key = getattr(settings, "GEMINI_API_KEY", None) and settings.GEMINI_API_KEY.strip() != ""
    openai_key = getattr(settings, "OPENAI_API_KEY", None) and settings.OPENAI_API_KEY.strip() != ""
    
    # Always perform a web search scan for real-time access on every question, except for basic greetings
    thanglish_greetings = [
        "hi", "hello", "hey", "hola", "வணக்கம்", "こんにちは", "नमस्ते", 
        "vanakkam", "enna panra", "summa", "epdi iruka", "epdi irukinga", 
        "saptingala", "hi bro", "hey bro", "enna vishayam", "yennapannura", 
        "summa iruken", "ur name enna", "u yaaru", "who are u", "who r u"
    ]
    is_simple_greeting = last_msg_lower.strip() in thanglish_greetings
    
    identity_keywords = [
        "ur name", "your name", "what is your name", "what's your name", "whats your name",
        "who are you", "who r u", "u yaaru", "ur name enna", "un name enna", "who created you",
        "who made you", "who is gokul", "who is balaji", "who is shadow", "what is shadow",
        "what can you do", "your capabilities", "who built you", "tell me about yourself",
        "who are ur founders", "who are your founders", "creator", "founders"
    ]
    is_identity_request = any(k in last_msg_lower for k in identity_keywords)

    # Extract clean search query and normalize Thanglish patterns
    search_query = clean_search_query(last_msg_content)
    normalized_search_query = normalize_thanglish_for_search(search_query)
    
    # We only trigger search if it's not a simple greeting or identity question, and either:
    # 1. It is explicitly a search request (has search keywords)
    # 2. Or the user did NOT upload a file (if they uploaded a file, we only search if they explicitly asked for it)
    should_search = not is_simple_greeting and not is_identity_request and (is_search_request or ("[ATTACHED_FILE:" not in last_msg_content))
    
    if (gemini_key or openai_key) and should_search and normalized_search_query.strip():
        search_results = await web_search(normalized_search_query)
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
