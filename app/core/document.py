# app/core/documents.py

import os
from datetime import datetime
from bson import ObjectId
from fastapi import UploadFile
from app.models.document import Document, DocumentVersion
from app.db.database import document_collection, version_collection

UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


async def handle_document_upload(file, employee_id: str, document_type: str, uploader_id: str):
    """
    Handles upload logic for a new or existing document.
    Creates new master record for first uploads or increments version for existing docs.
    """

    # Step 1: Check if document already exists for this employee & doc type
    existing_doc = await document_collection.find_one({
        "employee_id": ObjectId(employee_id),
        "document_type": document_type
    })

    # Generate unique file name
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{ObjectId()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    # Save to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    if existing_doc is None:
        # --- CASE 1: New document, create new master ---
        new_doc = Document(
            employee_id=ObjectId(employee_id),
            document_type=document_type,
            original_filename=file.filename,
            latest_version=1
        )
        doc_insert = await document_collection.insert_one(new_doc.model_dump(by_alias=True))
        document_id = doc_insert.inserted_id

        # Create first version entry
        version = DocumentVersion(
            document_id=document_id,
            version_number=1,
            file_path=file_path,
            uploader_id=ObjectId(uploader_id)
        )
        await version_collection.insert_one(version.model_dump(by_alias=True))

        return {"message": "New document created", "version": 1, "document_id": str(document_id)}

    else:
        # --- CASE 2: Existing document, create new version ---
        document_id = existing_doc["_id"]
        current_version = existing_doc.get("latest_version", 1)
        new_version_number = current_version + 1

        version = DocumentVersion(
            document_id=document_id,
            version_number=new_version_number,
            file_path=file_path,
            uploader_id=ObjectId(uploader_id),
        )
        await version_collection.insert_one(version.model_dump(by_alias=True))

        # Update master with new version number and timestamp
        await document_collection.update_one(
            {"_id": document_id},
            {"$set": {"latest_version": new_version_number, "updated_at": datetime.utcnow()}}
        )

        return {"message": "New version added", "version": new_version_number, "document_id": str(document_id)}
async def check_out_document(document_id: str, user_id: str):
    """
    Checks out a document (locks it) for exclusive editing.
    Error if already checked out by someone else.
    """
    doc = await document_collection.find_one({"_id": ObjectId(document_id)})

    if doc is None:
        return {"error": "Document not found"}, 404

    if doc.get("is_checked_out", False):
        # Already locked
        checked_by = str(doc.get("checked_out_by"))
        checked_at = doc.get("checked_out_at")
        return {
            "error": "Document is already checked out.",
            "checked_out_by": checked_by,
            "checked_out_at": checked_at
        }, 409

    # Perform check-out
    await document_collection.update_one(
        {"_id": ObjectId(document_id)},
        {
            "$set": {
                "is_checked_out": True,
                "checked_out_by": ObjectId(user_id),
                "checked_out_at": datetime.utcnow()
            }
        }
    )
    return {"message": "Document checked out. You now have exclusive edit access."}, 200

async def check_in_document(
    document_id: str,
    uploader_id: str,
    file: UploadFile,
    original_filename: str
):
    document = await document_collection.find_one({"_id": ObjectId(document_id)})

    if document is None:
        return {"error": "Document not found"}, 404
    
    # Verify document is checked out by the current user
    if not document.get("is_checked_out") or str(document.get("checked_out_by")) != uploader_id:
        return {"error": "Document is not checked out by this user"}, 403

    # Save uploaded file
    file_extension = os.path.splitext(original_filename)[1]
    unique_filename = f"{ObjectId()}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # Create new document version
    new_version_number = document.get("latest_version", 1) + 1

    version = DocumentVersion(
        document_id=document["_id"],
        version_number=new_version_number,
        file_path=file_path,
        uploader_id=ObjectId(uploader_id),
        created_at=datetime.utcnow()
    )
    await version_collection.insert_one(version.model_dump(by_alias=True))

    # Update master document to unlock and update version info
    await document_collection.update_one(
        {"_id": document["_id"]},
        {
            "$set": {
                "latest_version": new_version_number,
                "updated_at": datetime.utcnow(),
                "is_checked_out": False,
                "checked_out_by": None,
                "checked_out_at": None
            }
        }
    )

    return {"message": "Document checked in successfully", "version": new_version_number}, 200