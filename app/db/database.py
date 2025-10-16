# app/db/database.py

import motor.motor_asyncio
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from app.config import settings

class Settings(BaseSettings):
    MONGODB_URI: str
    DATABASE_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
database = client[settings.DATABASE_NAME]

# You can create collections here
user_collection = database.get_collection("users")
document_collection = database.get_collection("documents")
