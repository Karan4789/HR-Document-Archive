# app/api/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId

# Import all necessary components
from app.models.user import User, UserCreate # <-- Use UserCreate here
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token, TokenData
from app.db.database import user_collection

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """ Dependency to get current user from JWT token. """
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
    return User(**user)

def require_hr_or_admin(current_user: User = Depends(get_current_user)):
    """ Dependency to require HR Manager or Admin role. """
    if current_user.role not in ["HR Manager", "Admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this user role",
        )
    return current_user

# --- Authentication Endpoints ---

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate): # <-- Use UserCreate
    """ Registers a new user with a plain password. """
    existing_user = await user_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    # Hash the plain password from the UserCreate model
    hashed = hash_password(user_data.password)
    
    user_object = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed, # Store the hashed password
        "role": user_data.role,
        "disabled": False # Default to not disabled
    }

    new_user = await user_collection.insert_one(user_object)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    return User(**created_user)

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """ Logs in a user via username and password. """
    # Find user by username
    user = await user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]}
    )
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}
