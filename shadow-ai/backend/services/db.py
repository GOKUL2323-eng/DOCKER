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

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    # Convert standard postgres/postgresql URL to use asyncpg driver if not already specified
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
    elif DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
else:
    if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
        DATABASE_URL = "sqlite+aiosqlite:////tmp/shadow_ai.db"
    else:
        DATABASE_URL = "sqlite+aiosqlite:///./shadow_ai.db"


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

# Append query param to disable prepared statements on PgBouncer
if DATABASE_URL.startswith("postgresql"):
    if "prepared_statement_cache_size" not in DATABASE_URL:
        if "?" in DATABASE_URL:
            DATABASE_URL += "&prepared_statement_cache_size=0"
        else:
            DATABASE_URL += "?prepared_statement_cache_size=0"

engine_kwargs = {"echo": True}
if DATABASE_URL.startswith("postgresql"):
    import ssl
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    engine_kwargs["connect_args"] = {
        "ssl": ssl_context,
        "statement_cache_size": 0
    }

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
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
