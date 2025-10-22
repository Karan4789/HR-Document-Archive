# app/core/documents.py

import os
from datetime import datetime
from bson import ObjectId
from fastapi import HTTPException, UploadFile
from app.models.document import Document, DocumentVersion
from app.db.database import document_collection, version_collection

UPLOAD_DIRECTORY = "uploads"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


async def handle_document_upload(file, employee_id: str, document_type: str, uploader_id: str):
    # Step 1: Check if a document with the SAME FILENAME already exists for this employee and type
    existing_doc = await document_collection.find_one({
        "employee_id": ObjectId(employee_id),
        "document_type": document_type,
        "original_filename": file.filename  # <-- THE CRUCIAL FIX
    })
    
    if existing_doc and existing_doc.get("is_checked_out"):
        # If the document exists and is locked, block the upload
        checked_out_by_id = str(existing_doc.get("checked_out_by"))
        if checked_out_by_id != uploader_id:
            raise HTTPException(
                status_code=409,
                detail=f"Document is currently checked out by another user."
            )
        else:
            # The user trying to upload is the one who checked it out.
            # Guide them to use the correct endpoint.
            raise HTTPException(
                status_code=400,
                detail="Document is checked out by you. Please use the 'check-in' endpoint to upload a new version."
            )


    # Generate unique file name for storage
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{ObjectId()}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

    # Save the new file to disk
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    if existing_doc is None:
        # --- CASE 1: This is a brand-new master document ---
        new_doc = Document(
            employee_id=ObjectId(employee_id),
            document_type=document_type,
            original_filename=file.filename, # The original name is stored
            latest_version=1
        )
        doc_dict = new_doc.model_dump(by_alias=True)
        if doc_dict.get("_id") is None:
            del doc_dict["_id"]

        doc_insert = await document_collection.insert_one(doc_dict)
        document_id = doc_insert.inserted_id

        if document_id is None:
            raise Exception("Failed to insert new master document.")

        # Create the first version record for this new master document
        version = DocumentVersion(
            document_id=document_id,
            version_number=1,
            file_path=file_path,
            uploader_id=ObjectId(uploader_id)
        )
        version_dict = version.model_dump(by_alias=True)
        if version_dict.get("_id") is None:
            del version_dict["_id"]

        await version_collection.insert_one(version_dict)
        return {"message": "New document created", "version": 1, "document_id": str(document_id)}

    else:
        # --- CASE 2: This is a new version of an existing master document ---
        document_id = existing_doc.get("_id")
        if not document_id or not isinstance(document_id, ObjectId):
            raise Exception("Existing document is missing a valid '_id'")
        
        current_version = existing_doc.get("latest_version", 1)
        new_version_number = current_version + 1

        # Create the next version record
        version = DocumentVersion(
            document_id=document_id,
            version_number=new_version_number,
            file_path=file_path,
            uploader_id=ObjectId(uploader_id)
        )
        version_dict = version.model_dump(by_alias=True)
        if version_dict.get("_id") is None:
            del version_dict["_id"]
        
        await version_collection.insert_one(version_dict)

        # Update the master document to point to the latest version
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
    original_filename: str  # You may not need this if the file object has the filename
):
    document = await document_collection.find_one({"_id": ObjectId(document_id)})

    if document is None:
        return {"error": "Document not found"}, 404
    
    if not document.get("is_checked_out") or str(document.get("checked_out_by")) != uploader_id:
        return {"error": "Document is not checked out by this user"}, 403

    # Save uploaded file
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{ObjectId()}{file_extension}"
    file_path = os.path.join("uploads", unique_filename)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    new_version_number = document.get("latest_version", 1) + 1

    version = DocumentVersion(
        document_id=document["_id"],
        version_number=new_version_number,
        file_path=file_path,
        uploader_id=ObjectId(uploader_id),
        created_at=datetime.utcnow()
    )

    # --- THIS IS THE FIX ---
    # Prepare the dictionary for insertion and remove the null _id
    version_dict = version.model_dump(by_alias=True)
    if version_dict.get("_id") is None:
        del version_dict["_id"]
    
    await version_collection.insert_one(version_dict)
    # --- END OF FIX ---

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
