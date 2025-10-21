from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId

from app.models.user import User, UserCreate
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token, decode_access_token, TokenData
from app.db.database import user_collection

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    # Improved decoding with logging
    try:
        token_data = decode_access_token(token)
    except Exception as e:
        print("JWT decode error:", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (decode error)",
            headers={"WWW-Authenticate": "Bearer"},
        )

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
    print(f"User role from token: {current_user.role}")
    if current_user.role not in ["HR Manager", "Admin"]:  # fixed role string "HR Manager"
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Operation not permitted for this user role: {current_user.role}",
        )
    return current_user

@router.post("/register", response_model=User)
async def register_user(user_data: UserCreate):
    existing_user = await user_collection.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this username already exists",
        )

    hashed = hash_password(user_data.password)
    user_object = {
        "username": user_data.username,
        "email": user_data.email,
        "full_name": user_data.full_name,
        "hashed_password": hashed,
        "role": user_data.role,
        "disabled": False
    }

    new_user = await user_collection.insert_one(user_object)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    return User(**created_user)

@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await user_collection.find_one({"username": form_data.username})
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.get("disabled"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")

    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]}
    )
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}
