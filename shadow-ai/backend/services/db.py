from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os
from sqlalchemy.orm import declarative_base
from dotenv import load_dotenv

# Ensure environment variables are loaded from backend/.env
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./shadow_ai.db")

# Automatically create the parent directory for SQLite databases if it doesn't exist
if DATABASE_URL.startswith("sqlite"):
    if ":///" in DATABASE_URL:
        db_path = DATABASE_URL.split(":///", 1)[1]
    elif "://" in DATABASE_URL:
        db_path = DATABASE_URL.split("://", 1)[1]
    else:
        db_path = DATABASE_URL
        
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created database directory: {db_dir}")
        except Exception as e:
            print(f"Warning: Could not create database directory {db_dir}: {e}")

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    import models.orm
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
