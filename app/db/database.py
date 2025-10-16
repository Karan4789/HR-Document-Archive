# app/db/database.py

import motor.motor_asyncio

# --- TEMPORARILY HARDCODE SETTINGS FOR DEBUGGING ---
# Replace these with your actual values.
MONGODB_URI = "mongodb+srv://myAtlasDBUser:ErenYeager@myatlasclusteredu.i5k4g9n.mongodb.net/?retryWrites=true&w=majority&appName=myAtlasClusterEDU"
DATABASE_NAME = "hr_dms"
# --- END OF HARDCODED SETTINGS ---

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
database = client[DATABASE_NAME]

user_collection = database.get_collection("users")
document_collection = database.get_collection("documents")
