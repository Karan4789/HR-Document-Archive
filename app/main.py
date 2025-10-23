# app/main.py

from fastapi import FastAPI
from app.api import auth, documents
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HR Document Management System")

app.include_router(auth.router, tags=["Authentication"])
app.include_router(documents.router, tags=["Documents"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the HR Document Management System API"}
