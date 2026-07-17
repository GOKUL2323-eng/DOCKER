import sqlite3
import httpx
import asyncio
from dotenv import load_dotenv
import os

async def health_check():
    load_dotenv('.env')
    print("--- Shadow AI Health Check ---")
    
    # 1. Database Check
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///shadow_ai.db")
    if ":///" in database_url:
        db_path = database_url.split(":///", 1)[1]
    elif "://" in database_url:
        db_path = database_url.split("://", 1)[1]
    else:
        db_path = database_url

    if not os.path.isabs(db_path) and not db_path.startswith("/") and not db_path.startswith("\\"):
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), db_path))

    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            print(f"[DB]: SUCCESS. Found tables: {tables}")
            conn.close()
        except Exception as e:
            print(f"[DB]: ERROR. {e}")
    else:
        print(f"[DB]: WARNING. Database file '{db_path}' not found. It will be created on start.")

    # 3. Environment Check
    required = ['fastapi', 'uvicorn', 'sqlalchemy', 'aiosqlite', 'openai', 'python-dotenv', 'pydantic', 'mcp', 'google-generativeai']
    try:
        import pkg_resources
        installed = {pkg.key for pkg in pkg_resources.working_set}
        missing = [p for p in required if p not in installed]
        if not missing:
            print("[ENV]: SUCCESS. All core dependencies installed.")
        else:
            print(f"[ENV]: WARNING. Missing: {missing}")
    except Exception:
        print("[ENV]: SKIPPED. Could not verify installed packages.")

if __name__ == "__main__":
    asyncio.run(health_check())
