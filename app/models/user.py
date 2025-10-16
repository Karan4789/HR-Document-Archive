# app/models/user.py

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from bson import ObjectId

class User(BaseModel):
    id: ObjectId = Field(alias="_id")
    username: str
    email: EmailStr
    full_name: str | None = None
    role: str
    disabled: bool | None = None

    # --- THIS IS THE FIX ---
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True, # Allow ObjectId
        json_encoders={ObjectId: str}
    )

class UserInDB(User):
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str | None = None
    role: str
