# app/models/document.py

from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Union # <-- Import Optional
from datetime import datetime
from bson import ObjectId

class DocumentVersion(BaseModel):
    version_number: int
    file_path: str
    uploader_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class Document(BaseModel):
    # --- THIS IS THE FIX ---
    # The ID is optional because it doesn't exist until MongoDB creates it.
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    
    employee_id: ObjectId
    document_type: str
    original_filename: str
    versions: List[DocumentVersion] = []

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
