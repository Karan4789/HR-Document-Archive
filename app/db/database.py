# app/db/database.py

import motor.motor_asyncio

# Import the central settings object
from app.config import settings

# Use the URI and database name from the settings object
client = motor.motor_asyncio.AsyncIOMotorClient(settings.mongodb_uri)
database = client[settings.database_name]

user_collection = database.get_collection("users")
document_collection = database.get_collection("documents")
version_collection = database.get_collection("document_versions")