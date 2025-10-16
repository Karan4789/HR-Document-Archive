# app/models/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from bson import ObjectId

class User(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    email: EmailStr
    hashed_password: str
    role: str # "Admin", "HR Manager", or "Employee"

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "role": "Employee"
            }
        }

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: str
