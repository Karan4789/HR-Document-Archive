# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from bson import ObjectId

# Import all necessary components
from app.models.user import User, UserCreate
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token, TokenData
from app.db.database import user_collection

router = APIRouter()

# --- Security Dependencies ---

# This object is a callable class that will look for the `Authorization`
# header and check if it contains a `Bearer` token.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency to get the current user from a JWT token.
    This function is the core of your API's security.
    """
    token_data = decode_access_token(token)
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await user_collection.find_one({"_id": ObjectId(token_data.user_id)})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Return the user data as a Pydantic model for type safety
    return User(**user)

def require_hr_or_admin(current_user: User = Depends(get_current_user)):
    """
    Dependency that can be used on endpoints to require the current user
    to have the role of 'HR Manager' or 'Admin'.
    """
    if current_user.role not in ["HR Manager", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this user role",
        )
    return current_user

# --- Authentication Endpoints ---

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    """Registers a new user."""
    existing_user = await user_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    hashed = hash_password(user_data.password)
    
    user_object = {
        "email": user_data.email,
        "hashed_password": hashed,
        "role": user_data.role
    }

    new_user = await user_collection.insert_one(user_object)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    return created_user

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Logs in a user and returns an access token."""
    user = await user_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
