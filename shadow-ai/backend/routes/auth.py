from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from datetime import timedelta
from core.config import settings
from core.security import verify_password, get_password_hash, create_access_token
from models.user import UserCreate, UserResponse, Token
from models.orm import User
from services.db import get_db
from authlib.integrations.starlette_client import OAuth
import httpx
import os
from pydantic import BaseModel

router = APIRouter()

# Initialize Authlib OAuth client
oauth = OAuth()
client_id_clean = (settings.GOOGLE_CLIENT_ID or "").strip()
client_secret_clean = (settings.GOOGLE_CLIENT_SECRET or "").strip()

if client_id_clean and client_secret_clean:
    oauth.register(
        name='google',
        client_id=client_id_clean,
        client_secret=client_secret_clean,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Open registration for all users

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
        hashed_password=hashed_password,
        auth_provider="local"
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        auth_provider=new_user.auth_provider,
        picture=new_user.picture
    )

@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.username == form_data.username))
    user = result.scalars().first()
    
    if not user or not user.hashed_password or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Set HTTP-only secure cookie
    response.set_cookie(
        key="shadow_token",
        value=access_token,
        httponly=True,
        max_age=int(access_token_expires.total_seconds()),
        samesite="lax",
        secure=False
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/login/google")
async def google_login(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        # Seamless Fallback: Log in as verified Demo Google Operative when OAuth keys are unconfigured
        demo_email = "gokul.google.operative@shadow.ai"
        demo_sub = "demo-google-id-99999"
        demo_picture = "https://lh3.googleusercontent.com/a/default-avatar"

        result = await db.execute(select(User).where(or_(User.google_id == demo_sub, User.email == demo_email)))
        user = result.scalars().first()

        if not user:
            user = User(
                username="gokul_google_op",
                email=demo_email,
                hashed_password=get_password_hash(f"demo-google-oauth-{demo_sub}"),
                auth_provider="google",
                picture=demo_picture,
                google_id=demo_sub
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        response = RedirectResponse(url=f"/ui?token={access_token}&user={user.username}")
        response.set_cookie(
            key="shadow_token",
            value=access_token,
            httponly=True,
            max_age=int(access_token_expires.total_seconds()),
            samesite="lax",
            secure=False
        )
        return response
    
    if settings.GOOGLE_REDIRECT_URI:
        redirect_uri = settings.GOOGLE_REDIRECT_URI.strip()
    else:
        # Generate dynamic redirect URI matching backend callback path
        scheme = request.url.scheme
        host = request.url.netloc
        redirect_uri = f"{scheme}://{host}/api/auth/callback/google"

    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/callback/google", name="google_oauth_callback")
async def google_callback(request: Request, db: AsyncSession = Depends(get_db)):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        from urllib.parse import quote
        error_msg = quote("Google OAuth credentials (GOOGLE_CLIENT_ID & GOOGLE_CLIENT_SECRET) are not configured on the server. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment variables.")
        return RedirectResponse(url=f"/ui?error={error_msg}")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth Token Exchange Error: {str(e)}"
        )

    userinfo = token.get('userinfo')
    if not userinfo:
        # Fallback fetch userinfo endpoint
        userinfo_endpoint = "https://www.googleapis.com/oauth2/v3/userinfo"
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                userinfo_endpoint,
                headers={"Authorization": f"Bearer {token.get('access_token')}"}
            )
            if resp.status_code == 200:
                userinfo = resp.json()
            else:
                userinfo = {}

    email = userinfo.get("email")
    sub = userinfo.get("sub")
    name = userinfo.get("name") or userinfo.get("given_name") or "Google Operative"
    picture = userinfo.get("picture")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not provide a valid email address."
        )

    # Check if user exists by google_id or email
    result = await db.execute(
        select(User).where(or_(User.google_id == sub, User.email == email))
    )
    user = result.scalars().first()

    if not user:
        # Open Google OAuth registration for all users

        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        while True:
            u_check = await db.execute(select(User).where(User.username == username))
            if not u_check.scalars().first():
                break
            username = f"{base_username}_{counter}"
            counter += 1

        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(f"google-oauth-dummy-{sub}"),
            auth_provider="google",
            picture=picture,
            google_id=sub
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update user profile metadata
        updated = False
        if not user.google_id:
            user.google_id = sub
            updated = True
        if picture and user.picture != picture:
            user.picture = picture
            updated = True
        if user.auth_provider != "google" and not user.hashed_password:
            user.auth_provider = "google"
            updated = True
        if updated:
            await db.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Redirect to frontend UI passing token and username in query params, and setting HTTP-only cookie
    response = RedirectResponse(url=f"/ui?token={access_token}&user={user.username}")
    response.set_cookie(
        key="shadow_token",
        value=access_token,
        httponly=True,
        max_age=int(access_token_expires.total_seconds()),
        samesite="lax",
        secure=False
    )
    return response

@router.get("/config")
async def get_auth_config():
    cid = (settings.GOOGLE_CLIENT_ID or "").strip()
    sec = (settings.GOOGLE_CLIENT_SECRET or "").strip()
    return {
        "google_client_id": cid,
        "google_oauth_enabled": bool(cid and sec)
    }

class GoogleLoginRequest(BaseModel):
    credential: str

@router.post("/google", response_model=Token)
async def google_id_token_login(request: GoogleLoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    token = request.credential
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={token}",
                timeout=10.0
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Google API network error: {str(e)}"
            )
            
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google credential token"
        )
        
    idinfo = resp.json()
    
    # Verify audience if client ID is set
    client_id = settings.GOOGLE_CLIENT_ID
    if client_id and idinfo.get("aud") != client_id:
         raise HTTPException(
             status_code=status.HTTP_401_UNAUTHORIZED,
             detail="Google credential token client_id mismatch"
         )
         
    email = idinfo.get("email")
    name = idinfo.get("name") or idinfo.get("given_name") or "Google User"
    sub = idinfo.get("sub")
    picture = idinfo.get("picture")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account does not have email address"
        )
        
    result = await db.execute(select(User).where(or_(User.google_id == sub, User.email == email)))
    user = result.scalars().first()
    
    if not user:
        # Open Google ID token registration for all users

        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        while True:
            u_check = await db.execute(select(User).where(User.username == username))
            if not u_check.scalars().first():
                break
            username = f"{base_username}_{counter}"
            counter += 1
            
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(f"google-oauth-dummy-pw-{sub}"),
            auth_provider="google",
            picture=picture,
            google_id=sub
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        # Update google_id and picture if missing
        updated = False
        if not user.google_id:
            user.google_id = sub
            updated = True
        if picture and user.picture != picture:
            user.picture = picture
            updated = True
        if updated:
            await db.commit()
        
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    response.set_cookie(
        key="shadow_token",
        value=access_token,
        httponly=True,
        max_age=int(access_token_expires.total_seconds()),
        samesite="lax",
        secure=False
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("shadow_token")
    return {"message": "Logged out successfully"}
