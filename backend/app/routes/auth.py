from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

class RegisterIn(BaseModel):
    email: EmailStr
    password: str

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class AuthOut(BaseModel):
    token: str; email: str; user_id: int

@router.post("/register", response_model=AuthOut)
async def register(data: RegisterIn, db: AsyncSession = Depends(get_db)):
    if len(data.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters")
    if (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    user = User(email=data.email, password_hash=hash_password(data.password))
    db.add(user); await db.flush(); await db.refresh(user)
    return AuthOut(token=create_access_token({"sub": str(user.id)}), email=user.email, user_id=user.id)

@router.post("/login", response_model=AuthOut)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    return AuthOut(token=create_access_token({"sub": str(user.id)}), email=user.email, user_id=user.id)

@router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}
