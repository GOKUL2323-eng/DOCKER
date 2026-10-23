from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import asyncio
from models.user import UserInDB
from models.chat import ChatMessageRequest
from models.orm import ChatSessionDB, MessageDB
from services.db import get_db
import services.db as db_service
from services.openai_service import generate_chat_response, get_openai_client
from services.google_tts_service import GoogleTTSService
from datetime import datetime
from pydantic import BaseModel
import json
import subprocess
import tempfile
import sys
import re
import os

class TTSRequest(BaseModel):
    text: str
    lang: str = "en-US"

class CodeExecuteRequest(BaseModel):
    code: str
    lang: str

router = APIRouter()

@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Neural TTS endpoint using Google Cloud.
    Returns base64 encoded MP3 audio.
    """
    try:
        audio_b64 = await GoogleTTSService.synthesize(request.text, request.lang)
        if audio_b64:
            return {"audioContent": audio_b64}
        else:
            raise HTTPException(status_code=500, detail="TTS synthesis failed or credentials missing.")
    except Exception as e:
        print(f"[ROUTE_ERROR]: TTS Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stt")
async def speech_to_text(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Speech to text endpoint using OpenAI Whisper or Gemini fallback.
    Accepts uploaded audio file and returns transcribed text.
    """
    try:
        # Read audio file bytes
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="Empty audio payload.")

        mime_type = file.content_type or "audio/webm"
        
        # Determine appropriate file extension for Whisper API
        ext = ".webm"
        if "wav" in mime_type:
            ext = ".wav"
        elif "mp3" in mime_type:
            ext = ".mp3"
        elif "m4a" in mime_type:
            ext = ".m4a"
        elif "ogg" in mime_type:
            ext = ".ogg"
        elif "mpeg" in mime_type:
            ext = ".mpeg"

        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name

        try:
            from core.config import settings
            stt_errors = []
            
            # Tier 1: Primary OpenAI client (Whisper)
            if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip():
                try:
                    client = get_openai_client()
                    with open(temp_path, "rb") as f:
                        transcription = await client.audio.transcriptions.create(
                            model="whisper-1",
                            file=f
                        )
                    if transcription and hasattr(transcription, "text") and transcription.text and transcription.text.strip():
                        return {"text": transcription.text.strip()}
                except Exception as e:
                    print(f"[STT_WARNING]: Primary OpenAI whisper-1 failed: {e}")
                    stt_errors.append(f"OpenAI Primary: {str(e)}")

                # Tier 2: Direct Official OpenAI (if custom base_url was set and failed)
                base_url = getattr(settings, "OPENAI_BASE_URL", "")
                if base_url and base_url != "https://api.openai.com/v1":
                    try:
                        from openai import AsyncOpenAI
                        direct_client = AsyncOpenAI(
                            api_key=settings.OPENAI_API_KEY,
                            base_url="https://api.openai.com/v1",
                            timeout=30.0
                        )
                        with open(temp_path, "rb") as f:
                            transcription = await direct_client.audio.transcriptions.create(
                                model="whisper-1",
                                file=f
                            )
                        if transcription and hasattr(transcription, "text") and transcription.text and transcription.text.strip():
                            return {"text": transcription.text.strip()}
                    except Exception as e:
                        print(f"[STT_WARNING]: Direct OpenAI whisper-1 failed: {e}")
                        stt_errors.append(f"OpenAI Direct: {str(e)}")
            
            # Tier 3: Gemini Audio Transcription Fallback
            if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip():
                try:
                    import google.generativeai as genai
                    genai.configure(api_key=settings.GEMINI_API_KEY)
                    for model_name in ['gemini-1.5-flash', 'gemini-2.0-flash', 'gemini-1.5-pro']:
                        try:
                            model = genai.GenerativeModel(model_name)
                            loop = asyncio.get_running_loop()
                            response = await loop.run_in_executor(
                                None,
                                lambda m=model: m.generate_content([
                                    {
                                        "mime_type": mime_type,
                                        "data": audio_bytes
                                    },
                                    "Please transcribe this audio recording exactly. Output ONLY the transcription text and nothing else, no annotations, no preamble."
                                ])
                            )
                            if response and hasattr(response, "text") and response.text and response.text.strip():
                                return {"text": response.text.strip()}
                        except Exception as ge:
                            print(f"[STT_WARNING]: Gemini ({model_name}) STT failed: {ge}")
                            stt_errors.append(f"Gemini {model_name}: {str(ge)}")
                except Exception as e:
                    print(f"[STT_WARNING]: Gemini STT setup failed: {e}")
                    stt_errors.append(f"Gemini Setup: {str(e)}")
            
            # If all providers fail
            print(f"[STT_ERROR]: All speech-to-text providers failed. Errors: {stt_errors}")
            raise HTTPException(
                status_code=503, 
                detail="Speech to text transcription failed. Please check backend API keys or try typing your message."
            )
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ROUTE_ERROR]: STT Failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process speech input. Please try again.")

@router.post("/parse-file")
async def parse_file(
    file: UploadFile = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Parses various file types (PDF, Word, Excel, Plain Text) and extracts their textual content.
    Returns the parsed text content.
    """
    try:
        filename = file.filename or "uploaded_file"
        content_type = file.content_type or ""
        ext = os.path.splitext(filename)[1].lower()
        
        file_bytes = await file.read()
        if not file_bytes:
            return {"content": ""}

        text_content = ""
        import io

        # 1. PDF Parsing
        if ext == ".pdf" or "application/pdf" in content_type:
            try:
                from pypdf import PdfReader
                pdf_file = io.BytesIO(file_bytes)
                pdf_reader = PdfReader(pdf_file)
                pages_text = []
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_text.append(f"--- PAGE {i+1} ---\n{page_text}")
                text_content = "\n".join(pages_text)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse PDF document: {str(e)}")

        # 2. Word (DOCX) Parsing
        elif ext in [".docx", ".doc"] or "word" in content_type or "msword" in content_type:
            try:
                import docx
                docx_file = io.BytesIO(file_bytes)
                doc = docx.Document(docx_file)
                paragraphs_text = [p.text for p in doc.paragraphs]
                
                # Also extract table text
                tables_text = []
                for t_idx, table in enumerate(doc.tables):
                    table_rows = []
                    for row in table.rows:
                        row_cells = [cell.text.strip() for cell in row.cells]
                        table_rows.append(" | ".join(row_cells))
                    if table_rows:
                        tables_text.append(f"--- WORD TABLE {t_idx+1} ---\n" + "\n".join(table_rows))
                
                text_content = "\n\n".join(paragraphs_text + tables_text)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse Word document: {str(e)}")

        # 3. Excel (XLSX) Parsing
        elif ext in [".xlsx", ".xls"] or "spreadsheet" in content_type or "excel" in content_type:
            try:
                import openpyxl
                xlsx_file = io.BytesIO(file_bytes)
                wb = openpyxl.load_workbook(xlsx_file, read_only=True, data_only=True)
                sheets_text = []
                for sheet_name in wb.sheetnames:
                    sheet = wb[sheet_name]
                    rows_text = []
                    for row in sheet.iter_rows(values_only=True):
                        if any(row):  # Skip completely empty rows
                            row_str = " | ".join([str(val) if val is not None else "" for val in row])
                            rows_text.append(row_str)
                    if rows_text:
                        sheets_text.append(f"--- SHEET: {sheet_name} ---\n" + "\n".join(rows_text))
                text_content = "\n\n".join(sheets_text)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to parse Excel spreadsheet: {str(e)}")

        # 4. Fallback to Plain Text (CSV, JSON, XML, TXT, LOG, JS, PY, HTML, CSS, MD, etc.)
        else:
            try:
                # Try decoding as UTF-8
                text_content = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                try:
                    # Fallback to Latin-1
                    text_content = file_bytes.decode("latin-1")
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Unsupported binary file encoding: {str(e)}")

        return {
            "filename": filename,
            "size": len(file_bytes),
            "content": text_content
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"[ROUTE_ERROR]: File Parsing Failure: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message")
async def send_message(
    request: ChatMessageRequest, 
    session_id: Optional[str] = None,
    current_user: Optional[UserInDB] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Validate message content
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message content cannot be empty.")

    # Allow guests if current_user is None
    user_id = current_user.id if current_user else "guest-user"

    effective_session_id = request.session_id or session_id

    # Check if session exists or create new
    if effective_session_id:
        result = await db.execute(
            select(ChatSessionDB)
            .options(selectinload(ChatSessionDB.messages))
            .where(ChatSessionDB.id == effective_session_id, ChatSessionDB.user_id == user_id)
        )
        chat_session = result.scalars().first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        clean_title = request.message.strip().split("\n")[0][:30]
        title = clean_title + "..." if len(clean_title) >= 30 else clean_title
        chat_session = ChatSessionDB(
            user_id=user_id,
            title=title or "New Chat"
        )
        db.add(chat_session)
        await db.flush()
        
    # Context retrieval from prior messages
    if effective_session_id and hasattr(chat_session, "messages") and chat_session.messages:
        messages_context = [{"role": m.role, "content": m.content} for m in chat_session.messages][-10:]
    else:
        messages_context = []

    # Add user message to DB
    user_msg = MessageDB(
        session_id=chat_session.id,
        role="user", 
        content=request.message
    )
    db.add(user_msg)
    await db.commit() # Commit user message first
    
    messages_context.append({"role": "user", "content": request.message})
    
    # Generator for Streaming Response
    async def chat_generator():
        # Emit session_id immediately so frontend associates stream with session ID
        yield f"data: {json.dumps({'session_id': chat_session.id, 'started': True})}\n\n"
        full_reply = ""
        try:
            async for chunk in generate_chat_response(
                messages_context, 
                image_data=request.image_data, 
                user_id=user_id,
                response_mode=request.response_mode,
                preferred_model=request.preferred_model
            ):
                if chunk:
                    full_reply += chunk
                    yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            
            # Save AI response once complete
            if full_reply:
                async with db_service.AsyncSessionLocal() as session:
                    ai_msg = MessageDB(
                        session_id=chat_session.id,
                        role="assistant", 
                        content=full_reply
                    )
                    session.add(ai_msg)
                    
                    # Update session timestamp
                    from sqlalchemy import update
                    await session.execute(
                        update(ChatSessionDB)
                        .where(ChatSessionDB.id == chat_session.id)
                        .values(updated_at=datetime.utcnow())
                    )
                    await session.commit()
                
            yield f"data: {json.dumps({'session_id': chat_session.id, 'done': True})}\n\n"
        except Exception as e:
            print(f"[STREAM_ERROR]: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(chat_generator(), media_type="text/event-stream")

@router.get("/sessions")
async def get_sessions(current_user: UserInDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = current_user.id if current_user else "guest-user"
        
    result = await db.execute(
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == user_id)
        .order_by(ChatSessionDB.updated_at.desc())
    )
    sessions = result.scalars().all()
    
    return [
        {
            "id": session.id,
            "title": session.title,
            "updated_at": session.updated_at
        } for session in sessions
    ]

@router.get("/sessions/{session_id}")
async def get_session_details(session_id: str, current_user: UserInDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    user_id = current_user.id if current_user else "guest-user"
    
    result = await db.execute(
        select(ChatSessionDB)
        .options(selectinload(ChatSessionDB.messages))
        .where(ChatSessionDB.id == session_id, ChatSessionDB.user_id == user_id)
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    return {
        "id": session.id,
        "title": session.title,
        "updated_at": session.updated_at,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            } for msg in session.messages
        ]
    }

class SessionUpdateRequest(BaseModel):
    title: str

@router.delete("/sessions")
async def clear_all_sessions(
    current_user: UserInDB = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id if current_user else "guest-user"
    
    result = await db.execute(
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == user_id)
    )
    sessions = result.scalars().all()
    
    for session in sessions:
        await db.delete(session)
        
    await db.commit()
    return {"status": "success", "message": "All session logs terminated"}

@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str, 
    current_user: UserInDB = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id if current_user else "guest-user"
    
    result = await db.execute(
        select(ChatSessionDB)
        .where(ChatSessionDB.id == session_id, ChatSessionDB.user_id == user_id)
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    await db.delete(session)
    await db.commit()
    return {"status": "success", "message": "Session deleted"}

@router.patch("/sessions/{session_id}")
async def update_session(
    session_id: str, 
    request: SessionUpdateRequest, 
    current_user: UserInDB = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id if current_user else "guest-user"
    
    result = await db.execute(
        select(ChatSessionDB)
        .where(ChatSessionDB.id == session_id, ChatSessionDB.user_id == user_id)
    )
    session = result.scalars().first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    session.title = request.title
    session.updated_at = datetime.utcnow()
    await db.commit()
    return {"status": "success", "message": "Session updated", "title": session.title}

@router.post("/execute")
async def execute_code_payload(request: CodeExecuteRequest):
    """
    Executes Python, Java, or C++ code in a temporary sandbox.
    Returns stdout, stderr, and exit_code.
    """
    lang = request.lang.lower()
    code = request.code
    
    if lang == 'python':
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "payload.py")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            try:
                res = subprocess.run(
                    [sys.executable, file_path],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return {
                    "stdout": res.stdout,
                    "stderr": res.stderr,
                    "exit_code": res.returncode
                }
            except subprocess.TimeoutExpired as e:
                return {
                    "stdout": e.stdout or "",
                    "stderr": e.stderr or "Code execution timed out after 10 seconds.",
                    "exit_code": -1
                }
            except Exception as e:
                return {
                    "stdout": "",
                    "stderr": str(e),
                    "exit_code": -1
                }
                
    elif lang == 'java':
        match = re.search(r'public\s+class\s+(\w+)', code)
        class_name = match.group(1) if match else "Main"
        
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, f"{class_name}.java")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            
            try:
                # 1. Compile
                compile_res = subprocess.run(
                    ["javac", f"{class_name}.java"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if compile_res.returncode != 0:
                    return {
                        "stdout": compile_res.stdout,
                        "stderr": compile_res.stderr,
                        "exit_code": compile_res.returncode
                    }
                
                # 2. Run
                run_res = subprocess.run(
                    ["java", class_name],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return {
                    "stdout": run_res.stdout,
                    "stderr": run_res.stderr,
                    "exit_code": run_res.returncode
                }
            except subprocess.TimeoutExpired as e:
                return {
                    "stdout": e.stdout or "",
                    "stderr": e.stderr or "Code execution timed out after 10 seconds.",
                    "exit_code": -1
                }
            except Exception as e:
                return {
                    "stdout": "",
                    "stderr": str(e),
                    "exit_code": -1
                }
                
    elif lang == 'cpp':
        with tempfile.TemporaryDirectory() as tmpdir:
            source_path = os.path.join(tmpdir, "payload.cpp")
            exe_path = os.path.join(tmpdir, "payload.exe")
            with open(source_path, "w", encoding="utf-8") as f:
                f.write(code)
                
            try:
                # Compile
                compile_res = subprocess.run(
                    ["g++", "-o", "payload", "payload.cpp"],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if compile_res.returncode != 0:
                    return {
                        "stdout": compile_res.stdout,
                        "stderr": compile_res.stderr,
                        "exit_code": compile_res.returncode
                    }
                
                # Run
                run_res = subprocess.run(
                    [exe_path],
                    cwd=tmpdir,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return {
                    "stdout": run_res.stdout,
                    "stderr": run_res.stderr,
                    "exit_code": run_res.returncode
                }
            except FileNotFoundError:
                return {
                    "stdout": "",
                    "stderr": "g++ compiler not found. Please install a C++ compiler and add it to the system path.",
                    "exit_code": -1
                }
            except subprocess.TimeoutExpired as e:
                return {
                    "stdout": e.stdout or "",
                    "stderr": e.stderr or "Code execution timed out after 10 seconds.",
                    "exit_code": -1
                }
            except Exception as e:
                return {
                    "stdout": "",
                    "stderr": str(e),
                    "exit_code": -1
                }
    else:
        return {
            "stdout": "",
            "stderr": f"Execution of language '{lang}' is not supported on the backend.",
            "exit_code": -1
        }


class PrefectFlowRequest(BaseModel):
    texts: List[str]
    target_lang: str = "en"

@router.post("/prefect/run")
async def run_prefect_flow(request: PrefectFlowRequest, current_user: UserInDB = Depends(get_current_user)):
    """
    Triggers the Prefect multi-language flow and returns the structured execution results.
    This runs the flow inside the FastAPI request context, reporting tasks and telemetry
    to the active Prefect Server configuration automatically.
    """
    try:
        from prefect_flow import multilingual_translation_flow
        results = await multilingual_translation_flow(request.texts, request.target_lang)
        return {"success": True, "results": results}
    except Exception as e:
        print(f"[ROUTE_ERROR]: Prefect Flow Execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


