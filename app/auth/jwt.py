# app/auth/jwt.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

# Import the central settings object
from app.config import settings

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    # Use the expiration time from the settings object
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    expire_naive = expire.replace(tzinfo=None)
    to_encode.update({"exp": expire_naive})
    
    # Use the secret key and algorithm from the settings object
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    try:
        # Use the secret key and algorithm from the settings object
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            return TokenData()
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return TokenData()
