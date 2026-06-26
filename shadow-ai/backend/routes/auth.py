from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import timedelta
from core.config import settings
from core.security import verify_password, get_password_hash, create_access_token
from models.user import UserCreate, UserResponse, Token
from models.orm import User
from services.db import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing user
    result = await db.execute(select(User).where(User.username == user.username))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    result = await db.execute(select(User).where(User.email == user.email))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and store
    hashed_password = get_password_hash(user.password)
    
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login/{provider}")
async def social_login(provider: str):
    # This would normally redirect to the provider's OAuth page
    # For now, we'll return a placeholder redirect URL or handle it via a mock
    if provider not in ["google", "facebook", "github"]:
        raise HTTPException(status_code=400, detail="Invalid provider")
    
    # In a real implementation, you'd use a library like Authlib to generate the redirect
    return {"message": f"Redirecting to {provider} OAuth interface...", "url": f"https://{provider}.com/oauth/authorize?client_id=PLACEHOLDER"}

@router.get("/callback/{provider}")
async def social_callback(provider: str, code: str, db: AsyncSession = Depends(get_db)):
    # This endpoint receives the code from the provider
    # 1. Exchange code for access token
    # 2. Get user info from provider
    # 3. Create or update user in DB
    # 4. Generate JWT for the user
    
    # Placeholder logic:
    username = f"social_user_{provider}"
    email = f"{username}@example.com"
    
    # Check existing or create
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    
    if not user:
        new_user = User(
            username=username,
            email=email,
            hashed_password="SOCIAL_PW_PLACEHOLDER"
        )
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        user = new_user

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
