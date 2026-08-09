from typing import List, Optional
from datetime import datetime
import re
from pymongo.database import Database
from app.services.db_manager import DatabaseManager
from app.models.complaint import Complaint
from app.services.notification_manager import notification_manager

class ComplaintManager(DatabaseManager[Complaint]):
    """
    OOP Service for handling complaint lifecycle management, search/filtering,
    status updating, and citizen notifications.
    """
    def __init__(self):
        super().__init__(Complaint)

    def create_complaint(self, db: Database, complaint_data: dict) -> Complaint:
        complaint = self.create(db, complaint_data)
        
        # Trigger notification ack
        notification_manager.notify_citizen_submission(
            complaint_id=complaint.complaint_id,
            email=complaint.citizen_email,
            category=complaint.category,
            priority=complaint.priority
        )

        if complaint.priority in ["High", "Critical"]:
            notification_manager.notify_department_alert(
                department=complaint.assigned_department,
                complaint_id=complaint.complaint_id,
                priority=complaint.priority,
                summary=complaint.ai_summary or complaint.description[:50]
            )

        return complaint

    def update_status(self, db: Database, complaint_id: str, new_status: str, priority: Optional[str] = None, department: Optional[str] = None) -> Optional[Complaint]:
        comp = self.get_by_id(db, complaint_id)
        if not comp:
            return None

        update_dict = {"status": new_status, "updated_at": datetime.utcnow()}
        if new_status == "Resolved" and not comp.resolved_at:
            update_dict["resolved_at"] = datetime.utcnow()
        if priority:
            update_dict["priority"] = priority
        if department:
            update_dict["assigned_department"] = department

        updated_comp = self.update(db, comp, update_dict)

        # Trigger notification update
        notification_manager.notify_status_change(
            complaint_id=updated_comp.complaint_id,
            email=updated_comp.citizen_email,
            new_status=new_status
        )

        return updated_comp

    def search_and_filter(
        self, 
        db: Database, 
        query: Optional[str] = None, 
        status: Optional[str] = None, 
        category: Optional[str] = None,
        priority: Optional[str] = None,
        department: Optional[str] = None,
        limit: int = 500
    ) -> List[Complaint]:
        filters = {}
        if query:
            pattern = {"$regex": re.escape(query), "$options": "i"}
            filters["$or"] = [{field: pattern} for field in ["description", "location", "ai_summary", "complaint_id"]]
        if status and status != "All":
            filters["status"] = status
        if category and category != "All":
            filters["category"] = category
        if priority and priority != "All":
            filters["priority"] = priority
        if department and department != "All":
            filters["assigned_department"] = department

        cursor = self.collection(db).find(filters).sort("created_at", -1).limit(limit)
        return [Complaint.from_document(document) for document in cursor]

complaint_manager = ComplaintManager()
