# app/main.py

from fastapi import FastAPI
from app.api import auth, documents  # Import both routers

app = FastAPI(title="HR Document Management System")

# Include the routers from your API files
app.include_router(auth.router, tags=["Authentication"])
app.include_router(documents.router, tags=["Documents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the HR Document Management System API"}
