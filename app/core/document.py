# app/core/document.py

import os
import uuid
from typing import List
from bson import ObjectId
from datetime import datetime

# Import database and models
from app.db.database import document_collection
from app.models.document import Document, DocumentVersion
from app.models.user import User

# --- File Storage Setup ---
UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

async def create_document_version(
    file: 'UploadFile',
    user: User,
    employee_id: ObjectId,
    document_type: str,
    original_filename: str,
) -> Document:
    """
    Core business logic to save a file and manage document versioning.
    """
    # 1. Save the physical file to a secure, unique path
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # 2. Create the version object
    new_version = DocumentVersion(
        version_number=1,  # Default to 1
        file_path=file_path,
        uploader_id=user.id,
        created_at=datetime.utcnow()
    )

    # 3. Check if a document with this original name already exists for the employee
    existing_document = await document_collection.find_one({
        "employee_id": employee_id,
        "original_filename": original_filename
    })

    if existing_document:
        # Document exists: Add a new version
        latest_version_number = 0
        if existing_document.get("versions"):
            latest_version_number = existing_document["versions"][-1]["version_number"]
        
        new_version.version_number = latest_version_number + 1

        await document_collection.update_one(
            {"_id": existing_document["_id"]},
            {"$push": {"versions": new_version.dict()}}
        )
        updated_document = await document_collection.find_one({"_id": existing_document["_id"]})
        return Document(**updated_document)
    else:
        # Document is new: Create it with its first version
        document_data_model = Document(
            employee_id=employee_id,
            document_type=document_type,
            original_filename=original_filename,
            versions=[new_version]
        )
        
        # Convert the Pydantic model to a dictionary
        document_to_insert = document_data_model.dict(by_alias=True)
        
        # **THE FIX:** If the _id is None, remove it before inserting.
        if document_to_insert.get("_id") is None:
            del document_to_insert["_id"]

        result = await document_collection.insert_one(document_to_insert)
        created_document = await document_collection.find_one({"_id": result.inserted_id})
        return Document(**created_document)
