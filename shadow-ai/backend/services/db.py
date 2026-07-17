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

DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
if os.getenv("VERCEL") or os.getenv("VERCEL_ENV"):
    if DATABASE_URL and (DATABASE_URL.startswith("postgres://") or DATABASE_URL.startswith("postgresql://")):
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
    else:
        DATABASE_URL = "sqlite+aiosqlite:////tmp/shadow_ai.db"
else:
    if DATABASE_URL:
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
        elif DATABASE_URL.startswith("postgresql://"):
            DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
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

# Driver-specific connection configuration
engine_kwargs = {"echo": False}
if DATABASE_URL.startswith("postgresql+psycopg"):
    # psycopg3: sslmode as URL param, no prepared_statement_cache_size (that's asyncpg-only)
    if "sslmode" not in DATABASE_URL:
        DATABASE_URL += ("&" if "?" in DATABASE_URL else "?") + "sslmode=require"
elif DATABASE_URL.startswith("postgresql+asyncpg"):
    # asyncpg: prepared_statement_cache_size=0 needed for PgBouncer, ssl as connect_arg
    if "prepared_statement_cache_size" not in DATABASE_URL:
        DATABASE_URL += ("&" if "?" in DATABASE_URL else "?") + "prepared_statement_cache_size=0"
    engine_kwargs["connect_args"] = {
        "ssl": "require",
        "statement_cache_size": 0,
    }

engine = create_async_engine(DATABASE_URL, **engine_kwargs)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


Base = declarative_base()

_db_initialized = False

async def get_db():
    global _db_initialized
    if not _db_initialized:
        try:
            await init_db()
            _db_initialized = True
        except Exception as e:
            print(f"[DB_INIT_ERROR]: {e}")
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    import models.orm
    from models.orm import User
    from sqlalchemy import select
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed default guest user if not present to satisfy FK constraints
    async with AsyncSessionLocal() as session:
        try:
            res = await session.execute(select(User).where(User.id == "guest-user"))
            guest = res.scalars().first()
            if not guest:
                guest = User(
                    id="guest-user",
                    username="guest_operative",
                    email="guest@shadow.ai",
                    hashed_password="guest-no-password"
                )
                session.add(guest)
                await session.commit()
                print("Default guest operative seeded successfully.")
        except Exception as e:
            print(f"Warning: Could not seed guest user: {e}")
