"""Authentication endpoints. Accounts are provisioned locally by an administrator."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.core.auth import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from app.core.config import settings


router = APIRouter()


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=1, max_length=256)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str


@router.post("/login", response_model=Token)
async def login(form_data: LoginRequest):
    user = authenticate_user(form_data.username, form_data.password)
    if not user or user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom d'utilisateur ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return Token(access_token=token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return UserResponse(**current_user.model_dump())


@router.post("/verify")
async def verify_token(current_user: User = Depends(get_current_active_user)):
    """Small authenticated health check used by the demo client and probes."""
    return {"valid": True, "user": UserResponse(**current_user.model_dump())}
