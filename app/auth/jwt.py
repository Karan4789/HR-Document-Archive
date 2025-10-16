# app/auth/jwt.py

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from pydantic import BaseModel

# --- TEMPORARILY HARDCODE SETTINGS FOR DEBUGGING ---
JWT_SECRET_KEY = "your_jwt_secret_key" # Use your actual secret key
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
# --- END OF HARDCODED SETTINGS ---

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_naive = expire.replace(tzinfo=None)
    to_encode.update({"exp": expire_naive})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        if user_id is None:
            return TokenData()
        return TokenData(user_id=user_id, role=role)
    except JWTError:
        return TokenData()
