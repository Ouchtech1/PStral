"""
Authentication module for Pstral.
Handles JWT token creation, validation, and user management.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import sqlite3
import os

from .config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "infrastructure", "database", "users.db")


# Models
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str = "user"  # admin, user, viewer
    disabled: bool = False


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: str


class UserInDB(User):
    hashed_password: str


# Database initialization
def init_users_db():
    """Initialize the users database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            disabled INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    
    # Create default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        hashed = get_password_hash("admin123")  # Default password - should be changed!
        cursor.execute(
            "INSERT INTO users (username, email, full_name, hashed_password, role) VALUES (?, ?, ?, ?, ?)",
            ("admin", "admin@pack-solutions.com", "Administrateur", hashed, "admin")
        )
        conn.commit()
    
    conn.close()


# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return TokenData(username=username)
    except JWTError:
        return None


# User database operations
def get_user(username: str) -> Optional[UserInDB]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UserInDB(
            id=row[0],
            username=row[1],
            email=row[2],
            full_name=row[3],
            hashed_password=row[4],
            role=row[5],
            disabled=bool(row[6])
        )
    return None


def get_user_by_email(email: str) -> Optional[UserInDB]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return UserInDB(
            id=row[0],
            username=row[1],
            email=row[2],
            full_name=row[3],
            hashed_password=row[4],
            role=row[5],
            disabled=bool(row[6])
        )
    return None


def create_user(user: UserCreate) -> User:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    hashed_password = get_password_hash(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, full_name, hashed_password) VALUES (?, ?, ?, ?)",
        (user.username, user.email, user.full_name, hashed_password)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    return User(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role="user"
    )


def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = get_user(username)
    if not user:
        # Try by email
        user = get_user_by_email(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Dependency for protected routes
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    
    return User(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        disabled=user.disabled
    )


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Utilisateur désactivé")
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )
    return current_user

