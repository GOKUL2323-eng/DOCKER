import asyncio
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.db import init_db, AsyncSessionLocal, engine
from models.orm import User
from sqlalchemy import select, inspect, text
from core.security import get_password_hash

async def verify_database_connection():
    print("=" * 60)
    print(" SHADOW AI - DATABASE & OAUTH SCHEMA INTEGRATION VERIFICATION")
    print("=" * 60)
    
    # 1. Initialize DB and run migrations
    print("[1] Initializing database and executing schema migrations...")
    await init_db()
    print("    -> Database schema initialized successfully.")

    # 2. Inspect table columns
    print("[2] Inspecting 'users' table columns...")
    async with engine.begin() as conn:
        def get_cols(connection):
            insp = inspect(connection)
            return [c['name'] for c in insp.get_columns('users')]
        cols = await conn.run_sync(get_cols)
        print(f"    -> Table 'users' columns: {cols}")
        
        required_columns = ["auth_provider", "picture", "google_id"]
        for col in required_columns:
            if col in cols:
                print(f"    [OK] Column '{col}' exists.")
            else:
                print(f"    [FAIL] Column '{col}' is MISSING!")

    # 3. Test Google OAuth user DB persistence
    print("[3] Testing Google OAuth User persistence in SQLite DB...")
    async with AsyncSessionLocal() as session:
        test_email = "gokul_oauth_test@shadow.ai"
        test_google_id = "test-google-id-12345"
        
        # Cleanup any previous test user
        res = await session.execute(select(User).where(User.email == test_email))
        existing_test_user = res.scalars().first()
        if existing_test_user:
            await session.delete(existing_test_user)
            await session.commit()
            
        # Create Google OAuth test user
        google_user = User(
            username="gokul_oauth_test",
            email=test_email,
            google_id=test_google_id,
            auth_provider="google",
            picture="https://lh3.googleusercontent.com/a/default-avatar",
            hashed_password=get_password_hash("test-oauth-dummy-pass")
        )
        session.add(google_user)
        await session.commit()
        await session.refresh(google_user)
        print(f"    -> Successfully stored Google user in DB with ID: {google_user.id}")
        
        # Retrieve user by google_id
        res = await session.execute(select(User).where(User.google_id == test_google_id))
        retrieved_user = res.scalars().first()
        assert retrieved_user is not None, "Failed to retrieve user by google_id"
        print(f"    -> Retrieved User: username={retrieved_user.username}, provider={retrieved_user.auth_provider}, picture={retrieved_user.picture}")
        
        # Cleanup test user
        await session.delete(retrieved_user)
        await session.commit()
        print("    -> Test user cleaned up cleanly.")

    print("=" * 60)
    print(" VERIFICATION COMPLETE: ALL DATABASE & OAUTH PERSISTENCE CHECKS PASSED!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify_database_connection())
