"""Local user accounts and JWT authentication for the demo."""

from datetime import datetime, timedelta, timezone
from typing import Optional
import sqlite3

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field

from .config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class User(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str = "user"
    disabled: bool = False


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=64, pattern=r"^[a-zA-Z0-9._-]+$")
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=12, max_length=256)
    full_name: str = Field(min_length=2, max_length=120)


class UserInDB(User):
    hashed_password: str


def _connect() -> sqlite3.Connection:
    settings.users_db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(settings.users_db_path)


def init_users_db() -> None:
    """Create the account store. Accounts are provisioned through the CLI only."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                disabled INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def _user_from_row(row: tuple | None) -> Optional[UserInDB]:
    if not row:
        return None
    return UserInDB(
        id=row[0], username=row[1], email=row[2], full_name=row[3],
        hashed_password=row[4], role=row[5], disabled=bool(row[6]),
    )


def get_user(username: str) -> Optional[UserInDB]:
    with _connect() as conn:
        return _user_from_row(conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone())


def get_user_by_email(email: str) -> Optional[UserInDB]:
    with _connect() as conn:
        return _user_from_row(conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone())


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_user(user: UserCreate, role: str = "user") -> User:
    if role not in {"user", "admin"}:
        raise ValueError("Rôle utilisateur invalide")
    if get_user(user.username) or get_user_by_email(user.email):
        raise ValueError("Un compte utilise déjà cet identifiant ou cet email")
    with _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (username, email, full_name, hashed_password, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user.username, user.email, user.full_name, get_password_hash(user.password), role),
        )
        user_id = cursor.lastrowid
    return User(id=user_id, username=user.username, email=user.email, full_name=user.full_name, role=role)


def authenticate_user(username_or_email: str, password: str) -> Optional[UserInDB]:
    user = get_user(username_or_email) or get_user_by_email(username_or_email)
    if not user or not pwd_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    expiration = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return jwt.encode({**data, "exp": expiration}, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[TokenData]:
    try:
        username = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]).get("sub")
        return TokenData(username=username) if username else None
    except JWTError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_token(token)
    user = get_user(token_data.username) if token_data and token_data.username else None
    if not user:
        raise credentials_exception
    return User(**user.model_dump(exclude={"hashed_password"}))


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Utilisateur désactivé")
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé aux administrateurs")
    return current_user
