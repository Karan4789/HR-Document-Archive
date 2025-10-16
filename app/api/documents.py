# app/api/documents.py

import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from bson import ObjectId

# Import models
from app.models.document import Document
from app.models.user import User

# Import database and security dependencies
from app.db.database import document_collection
from app.api.auth import get_current_user, require_hr_or_admin

# Import the core business logic function
from app.core.document import create_document_version

router = APIRouter()

@router.post("/documents/upload", response_model=Document)
async def upload_document(
    employee_id: str,
    document_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_hr_or_admin)
):
    """
    API endpoint to upload a document for a specific employee.
    This handles HTTP logic and calls the core business logic.
    """
    try:
        # Convert string ID to MongoDB ObjectId
        employee_id_obj = ObjectId(employee_id)
        
        # Call the core function to do the actual work
        document = await create_document_version(
            file=file,
            user=current_user,
            employee_id=employee_id_obj,
            document_type=document_type,
            original_filename=file.filename,
        )
        return document
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid employee ID format.")
    except Exception as e:
        # Generic error handler
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")


@router.get("/documents/my-documents", response_model=List[Document])
async def get_my_documents(current_user: User = Depends(get_current_user)):
    """Retrieves all documents belonging to the currently logged-in user."""
    documents = await document_collection.find({"employee_id": current_user.id}).to_list(100)
    return documents

@router.get("/documents/user/{employee_id}", response_model=List[Document])
async def get_user_documents(employee_id: str, current_user: User = Depends(require_hr_or_admin)):
    """Retrieves all documents for a specific employee. HR and Admin only."""
    documents = await document_collection.find({"employee_id": ObjectId(employee_id)}).to_list(100)
    return documents

@router.get("/documents/download/{doc_id}/version/{version_num}")
async def download_document_version(
    doc_id: str, 
    version_num: int, 
    current_user: User = Depends(get_current_user)
):
    """
    Downloads a specific version of a document.
    """
    document = await document_collection.find_one({"_id": ObjectId(doc_id)})

    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    # Security Check
    is_owner = document["employee_id"] == current_user.id
    is_privileged = current_user.role in ["HR Manager", "Admin"]
    if not is_owner and not is_privileged:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this document")
    
    # Find version
    version_to_download = next((v for v in document["versions"] if v["version_number"] == version_num), None)
    
    if not version_to_download or not os.path.exists(version_to_download["file_path"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found or file is missing")

    return FileResponse(
        path=version_to_download["file_path"],
        filename=document["original_filename"],
        media_type='application/octet-stream'
    )
