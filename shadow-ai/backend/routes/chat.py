from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List
from models.user import UserInDB
from models.chat import ChatMessageRequest
from models.orm import ChatSessionDB, MessageDB
from services.auth_service import get_current_user
from services.db import get_db, AsyncSessionLocal
from services.openai_service import generate_chat_response
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

from fastapi.responses import StreamingResponse
import asyncio

@router.post("/message")
async def send_message(
    request: ChatMessageRequest, 
    current_user: UserInDB = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Allow guests if current_user is None
    user_id = current_user.id if current_user else "guest-user"

    # Check if session exists or create new
    if request.session_id:
        result = await db.execute(
            select(ChatSessionDB)
            .options(selectinload(ChatSessionDB.messages))
            .where(ChatSessionDB.id == request.session_id, ChatSessionDB.user_id == user_id)
        )
        chat_session = result.scalars().first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        title = request.message[:30] + "..." if len(request.message) > 30 else request.message
        chat_session = ChatSessionDB(
            user_id=user_id,
            title=title
        )
        db.add(chat_session)
        await db.flush()
        
    # Add user message
    user_msg = MessageDB(
        session_id=chat_session.id,
        role="user", 
        content=request.message
    )
    db.add(user_msg)
    await db.commit() # Commit user message first
    
    # Context retrieval
    if request.session_id:
        messages_context = [{"role": m.role, "content": m.content} for m in chat_session.messages[-9:]]
    else:
        messages_context = []
    messages_context.append({"role": "user", "content": request.message})
    
    # Generator for Streaming Response
    async def chat_generator():
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
            async with AsyncSessionLocal() as session:
                ai_msg = MessageDB(
                    session_id=chat_session.id,
                    role="assistant", 
                    content=full_reply
                )
                session.add(ai_msg)
                
                # Update session timestamp
                stmt = select(ChatSessionDB).where(ChatSessionDB.id == chat_session.id)
                res = await session.execute(stmt)
                db_session = res.scalars().first()
                if db_session:
                    db_session.updated_at = datetime.utcnow()
                
                await session.commit()
                
            yield f"data: {json.dumps({'session_id': chat_session.id, 'done': True})}\n\n"
        except Exception as e:
            print(f"[STREAM_ERROR]: {str(e)}")
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(chat_generator(), media_type="text/event-stream")

@router.get("/sessions")
async def get_sessions(current_user: UserInDB = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if not current_user:
        return []
        
    result = await db.execute(
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == current_user.id)
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

