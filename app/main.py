# app/main.py

from fastapi import FastAPI
from app.api import auth, documents

app = FastAPI(title="HR Document Management System")

app.include_router(auth.router, tags=["Authentication"])
app.include_router(documents.router, tags=["Documents"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the HR Document Management System API"}
