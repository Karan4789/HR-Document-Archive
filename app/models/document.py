# app/models/document.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

class DocumentVersion(BaseModel):
    version_number: int
    file_path: str
    uploader_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Document(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    employee_id: ObjectId
    document_type: str
    original_filename: str
    versions: List[DocumentVersion] = []

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }
        schema_extra = {
            "example": {
                "employee_id": "60d5ec49e7b2f8a7c8b4bdf0",
                "document_type": "Employment Contract",
                "original_filename": "contract_2025.pdf"
            }
        }
