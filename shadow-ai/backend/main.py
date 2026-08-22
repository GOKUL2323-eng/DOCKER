from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
from contextlib import asynccontextmanager

# Add current directory to path for serverless import resolution
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.db import init_db
from routes import auth, chat

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    
    # Retrieve local network IP
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        local_ip = "127.0.0.1"
        
    port = os.getenv("PORT", "8000")
    
    print("\n" + "="*70)
    print(" SHADOW AI IS ONLINE & TACTICAL PROTOCOLS INITIATED")
    print(f" Access the neural interface from any device on your local network:")
    print(f" - Local:          http://localhost:{port}/ui")
    print(f" - Network (LAN):   http://{local_ip}:{port}/ui")
    print("="*70 + "\n")
    
    yield


from starlette.middleware.sessions import SessionMiddleware
from routes import auth, chat, university
from core.config import settings

app = FastAPI(title="Shadow AI Backend", version="1.0.0", lifespan=lifespan)

# Session middleware for Authlib OAuth 2.0 state management
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Application Firewall Middleware (WAF)
from fastapi.responses import JSONResponse
from fastapi import Request

@app.middleware("http")
async def shadow_ai_firewall(request: Request, call_next):
    # 1. Path scanning for traversal attacks, environment access, and exploits
    path = request.url.path.lower()
    suspicious_patterns = [
        "wp-admin", "wp-login", ".env", "phpinfo", "xmlrpc", 
        "config.php", "etc/passwd", "..", "boot.ini",
        ".git", ".svn", "admin.php", "setup.php", "config.json"
    ]
    
    if any(pattern in path for pattern in suspicious_patterns):
        client_ip = request.client.host if request.client else "unknown"
        print(f"[SECURITY FIREWALL]: Blocked exploit attempt on path: {path} from IP: {client_ip}")
        return JSONResponse(
            status_code=403,
            content={"detail": "Security Firewall Protocol: Request rejected. Malicious scan pattern detected."}
        )

    # 2. Proceed and inject Security Headers
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self' https: 'unsafe-inline' 'unsafe-eval' data:; img-src 'self' data: https:;"
    return response

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(university.router, prefix="/api/university", tags=["university"])

# Serve frontend files statically
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/files", StaticFiles(directory=frontend_path), name="frontend")

from fastapi.responses import RedirectResponse
from fastapi import Depends
from services.db import get_db
from sqlalchemy import text
from services.auth_service import get_current_user

@app.get("/api/db-check")
async def db_check(db = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        # Get count of users
        res_users = await db.execute(text("SELECT COUNT(*) FROM users"))
        users_count = res_users.scalar()
        
        # Get count of sessions
        res_sessions = await db.execute(text("SELECT COUNT(*) FROM chat_sessions"))
        sessions_count = res_sessions.scalar()
        
        return {
            "status": "connected",
            "stats": {
                "users": users_count,
                "chat_sessions": sessions_count
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/")
async def root():
    return RedirectResponse(url="/ui")


@app.get("/ui")
async def get_ui():
    from fastapi.responses import HTMLResponse
    path = os.path.join(frontend_path, "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
    return HTMLResponse(content="<h1>Frontend Files Not Found</h1>")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
