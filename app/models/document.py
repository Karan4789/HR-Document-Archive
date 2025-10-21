# app/models/document.py

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from bson import ObjectId


# === 1. VERSION MODEL (immutable historical record) ===
class DocumentVersion(BaseModel):
    """
    Represents a single version of a document.
    Each version is immutable and linked to a master Document.
    """
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    document_id: ObjectId  # Id of the master document
    version_number: int
    file_path: str
    uploader_id: ObjectId
    created_at: datetime = Field(default_factory=datetime.utcnow)
    comments: Optional[str] = None  # Optional change note

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )


# === 2. MASTER DOCUMENT MODEL (active record) ===
class Document(BaseModel):
    """
    The master document record — represents the latest state and metadata.
    """
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    employee_id: ObjectId
    document_type: str
    original_filename: str

    # Control state fields
    latest_version: int = 1
    is_checked_out: bool = False
    checked_out_by: Optional[ObjectId] = None
    checked_out_at: Optional[datetime] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )
