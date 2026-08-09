from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ComplaintCreate(BaseModel):
    description: str = Field(..., min_length=5, description="Detailed problem description")
    location: str = Field(..., min_length=2, description="Location or landmark")
    citizen_name: Optional[str] = "Anonymous Citizen"
    citizen_email: Optional[str] = "citizen@civicservices.org"
    citizen_phone: Optional[str] = None
    image_url: Optional[str] = None

class ComplaintUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_department: Optional[str] = None

class AIAnalysisResult(BaseModel):
    category: str
    priority: str
    assigned_department: str
    ai_summary: str
    ai_reason: str
    ai_confidence: float
    is_duplicate: Optional[bool] = False
    similarity_score: Optional[float] = 0.0
    matched_complaint_id: Optional[str] = None

class ComplaintResponse(BaseModel):
    complaint_id: str
    citizen_name: Optional[str] = "Anonymous Citizen"
    citizen_email: Optional[str] = "citizen@civicservices.org"
    citizen_phone: Optional[str] = None
    description: str
    location: str
    category: str
    priority: str
    status: str
    assigned_department: str
    ai_summary: Optional[str] = None
    ai_reason: Optional[str] = None
    ai_confidence: float
    image_url: Optional[str] = None
    is_duplicate: bool = False
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationResponse(BaseModel):
    type: str
    recipient: str
    message: str
    status: str
