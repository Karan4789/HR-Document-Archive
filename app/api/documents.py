# app/api/documents.py
import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from bson import ObjectId

from app.models.document import Document
from app.models.document import DocumentVersion
from app.models.user import User

from app.db.database import document_collection, version_collection
from app.api.auth import get_current_user, require_hr_or_admin

from app.core.document import (
    handle_document_upload,
    check_out_document,
    check_in_document
)
from app.core.validator import validate_object_id

router = APIRouter()


@router.post("/documents/upload")
async def upload_document(
    employee_id: str,
    document_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_hr_or_admin)
):
    """
    Upload a new document or new version (handled in core).
    """
    result = await handle_document_upload(
        file,
        employee_id,
        document_type,
        uploader_id=str(current_user.id)
    )
    return result


@router.get("/documents/my-documents", response_model=List[Document])
async def get_my_documents(current_user: User = Depends(get_current_user)):
    docs = await document_collection.find({"employee_id": current_user.id}).to_list(100)
    return docs

@router.get("/documents/{doc_id}", response_model=Document)
async def get_document(doc_id: str, current_user: User = Depends(get_current_user)):
    """
    Get details of a specific document by ID.
    Only the document owner, HR Manager, or Admin can access it.
    """
    try:
        doc = await document_collection.find_one({"_id": ObjectId(doc_id)})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID format",
        )
    
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )
    
    # Check authorization
    is_owner = str(doc["employee_id"]) == str(current_user.id)
    is_privileged = current_user.role in ["HR Manager", "Admin"]
    
    if not is_owner and not is_privileged:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this document",
        )
    
    return Document(**doc)

@router.get("/documents/user/{employee_id}", response_model=List[Document])
async def get_user_documents(employee_id: str, current_user: User = Depends(require_hr_or_admin)):
    docs = await document_collection.find({"employee_id": ObjectId(employee_id)}).to_list(100)
    return docs

@router.get("/documents/{doc_id}/versions", response_model=List[DocumentVersion]) # Keep response_model
async def list_document_versions(doc_id: str, current_user: User = Depends(get_current_user)):
    """
    Returns all versions for a given document.
    """
    # Fetch raw data from MongoDB
    versions_cursor = version_collection.find({"document_id": ObjectId(doc_id)}).sort("version_number", -1)
    versions_list = await versions_cursor.to_list(100)

    if not versions_list:
        raise HTTPException(status_code=404, detail="No versions found for this document.")

    # Explicitly parse the list of dicts into a list of DocumentVersion models
    # This ensures Pydantic's json_encoders are properly applied
    response_data = [DocumentVersion(**v) for v in versions_list]
    
    return response_data

@router.get("/documents/download/{doc_id}/version/{version_num}")
async def download_document_version(
    doc_id: str, 
    version_num: int, 
    current_user: User = Depends(get_current_user)
):
    doc = await document_collection.find_one({"_id": ObjectId(doc_id)})
    if not doc:
        raise HTTPException(404, "Document not found")
    is_owner = doc["employee_id"] == current_user.id
    is_privileged = current_user.role in ["HR Manager", "Admin"]
    if not is_owner and not is_privileged:
        raise HTTPException(403, "Not authorized")

    version = await version_collection.find_one({
        "document_id": ObjectId(doc_id),
        "version_number": version_num
    })
    if not version or not os.path.exists(version["file_path"]):
        raise HTTPException(404, "Version/file missing")
    
    file_ext = os.path.splitext(doc["original_filename"])[1].lower()
    media_type_map = {
        ".doc": "application/msword",
        ".txt": "text/plain"
    }
    
    media_type = media_type_map.get(file_ext, "application/octet-stream")
    
    return FileResponse(
        path=version["file_path"],
        filename=doc["original_filename"],
        media_type=media_type
    )

@router.post("/documents/{doc_id}/checkout")
async def checkout_document(doc_id: str, current_user: User = Depends(get_current_user)):
    """
    Locks a document for exclusive editing, if not already checked out.
    """
    data, status = await check_out_document(doc_id, user_id=str(current_user.id))
    if status == 409:
        raise HTTPException(409, detail=data["error"])
    elif status == 404:
        raise HTTPException(404, detail=data["error"])
    return data

@router.post("/documents/{doc_id}/checkin")
async def checkin_document(
    doc_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    data, status = await check_in_document(
        document_id=doc_id,
        uploader_id=str(current_user.id),
        file=file,
        original_filename=file.filename
    )
    if status != 200:
        raise HTTPException(status_code=status, detail=data["error"])
    return data