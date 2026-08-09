import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile
from pymongo.database import Database
from typing import List, Optional
from app.database import get_db
from app.schemas.complaint import ComplaintCreate, ComplaintUpdate, ComplaintResponse, AIAnalysisResult
from app.services.complaint_manager import complaint_manager
from app.services.ai_analyzer import ai_analyzer
from app.services.notification_manager import notification_manager

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB limit

@router.post("/upload-image")
async def upload_evidence_image(file: UploadFile = File(...)):
    """
    Validates and stores evidence images uploaded by citizens.
    Requirements:
    - Allowed extensions: .jpg, .jpeg, .png, .webp
    - Max size: 5 MB
    - Non-empty payload check
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No image file selected for upload.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS or (file.content_type and file.content_type not in ALLOWED_MIME_TYPES):
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Only JPG, JPEG, PNG, and WEBP image formats are supported."
        )

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded image file is empty.")

    if len(contents) > MAX_FILE_SIZE:
        size_mb = round(len(contents) / (1024 * 1024), 2)
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the 5 MB limit (Uploaded size: {size_mb} MB). Please select a smaller image."
        )

    unique_filename = f"{uuid.uuid4()}{ext}"
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
    os.makedirs(uploads_dir, exist_ok=True)
    destination_path = os.path.join(uploads_dir, unique_filename)

    with open(destination_path, "wb") as f:
        f.write(contents)

    image_url = f"/uploads/{unique_filename}"
    return {"image_url": image_url, "filename": unique_filename}

@router.post("/analyze-preview", response_model=AIAnalysisResult)
def analyze_preview(data: ComplaintCreate, db: Database = Depends(get_db)):
    """
    Evaluates complaint text with AI and checks for duplicates prior to submission.
    Classification strictly uses the description text.
    """
    ai_result = ai_analyzer.analyze(data.description, data.image_url)
    existing = complaint_manager.get_all(db, limit=500)
    dup_info = ai_analyzer.check_duplicate(data.description, data.location, existing)
    
    ai_result["is_duplicate"] = dup_info["is_duplicate"]
    ai_result["similarity_score"] = dup_info["similarity_score"]
    ai_result["matched_complaint_id"] = dup_info["matched_complaint_id"]
    return ai_result

@router.post("/", response_model=ComplaintResponse)
def create_complaint(data: ComplaintCreate, db: Database = Depends(get_db)):
    """
    Analyzes complaint description, checks for duplicates, saves complaint record to database,
    and triggers notifications.
    """
    ai_result = ai_analyzer.analyze(data.description, data.image_url)
    existing = complaint_manager.get_all(db, limit=500)
    dup_info = ai_analyzer.check_duplicate(data.description, data.location, existing)

    complaint_dict = {
        "citizen_name": data.citizen_name or "Anonymous Citizen",
        "citizen_email": data.citizen_email or "citizen@civicservices.org",
        "citizen_phone": data.citizen_phone,
        "description": data.description,
        "location": data.location,
        "image_url": data.image_url,
        "category": ai_result.get("category", "General Administration"),
        "priority": ai_result.get("priority", "Medium"),
        "assigned_department": ai_result.get("assigned_department", "Central Civic Helpdesk"),
        "ai_summary": ai_result.get("ai_summary"),
        "ai_reason": ai_reason if (ai_reason := ai_result.get("ai_reason")) else None,
        "ai_confidence": ai_result.get("ai_confidence", 0.85),
        "is_duplicate": dup_info["is_duplicate"],
        "duplicate_of_id": dup_info["matched_complaint_id"]
    }

    return complaint_manager.create_complaint(db, complaint_dict)

@router.get("/search", response_model=List[ComplaintResponse])
def search_complaints(
    q: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    db: Database = Depends(get_db)
):
    """
    Multi-field search and filter for admin dashboard operations.
    """
    return complaint_manager.search_and_filter(
        db, query=q, status=status, category=category, priority=priority, department=department
    )

@router.get("/notifications/recent")
def get_recent_notifications():
    return notification_manager.get_logs()

@router.get("/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: str, db: Database = Depends(get_db)):
    comp = complaint_manager.get_by_id(db, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint record not found")
    return comp

@router.put("/{complaint_id}", response_model=ComplaintResponse)
def update_complaint(complaint_id: str, data: ComplaintUpdate, db: Database = Depends(get_db)):
    updated = complaint_manager.update_status(
        db, 
        complaint_id=complaint_id, 
        new_status=data.status, 
        priority=data.priority, 
        department=data.assigned_department
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint record not found")
    return updated

@router.post("/{complaint_id}/reanalyze", response_model=ComplaintResponse)
def reanalyze_complaint(complaint_id: str, db: Database = Depends(get_db)):
    comp = complaint_manager.get_by_id(db, complaint_id)
    if not comp:
        raise HTTPException(status_code=404, detail="Complaint record not found")
    
    ai_result = ai_analyzer.analyze(comp.description, comp.image_url)
    update_data = {
        "category": ai_result.get("category"),
        "priority": ai_result.get("priority"),
        "assigned_department": ai_result.get("assigned_department"),
        "ai_summary": ai_result.get("ai_summary"),
        "ai_reason": ai_result.get("ai_reason"),
        "ai_confidence": ai_result.get("ai_confidence", 0.85)
    }
    return complaint_manager.update(db, comp, update_data)
