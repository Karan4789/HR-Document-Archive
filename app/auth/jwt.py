# app/auth/jwt.py

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from app.config import settings

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

def create_access_token(data: dict) -> str:
    """Creates a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # Pydantic v2 requires converting datetime to be timezone-aware
    # or using .replace(tzinfo=None) to make it naive, matching python-jose expectations
    expire_naive = expire.replace(tzinfo=None)
    to_encode.update({"exp": expire_naive})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    """Decodes a JWT token and returns the payload as TokenData."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            return TokenData() # Return empty object if no sub
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return TokenData() # Return empty object on any JWT error
