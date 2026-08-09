import uuid
from datetime import datetime
from typing import Any, Dict


class Complaint:
    """MongoDB-backed complaint document represented as a Python object."""

    collection_name = "complaints"

    def __init__(self, **data: Any):
        self.complaint_id = data.get("complaint_id", str(uuid.uuid4()))
        self.citizen_name = data.get("citizen_name", "Anonymous Citizen")
        self.citizen_email = data.get("citizen_email", "citizen@civicservices.org")
        self.citizen_phone = data.get("citizen_phone")
        self.description = data["description"]
        self.location = data["location"]
        self.category = data.get("category", "General Administration")
        self.priority = data.get("priority", "Medium")
        self.status = data.get("status", "Open")
        self.assigned_department = data.get("assigned_department", "Central Helpdesk")
        self.ai_summary = data.get("ai_summary")
        self.ai_reason = data.get("ai_reason")
        self.ai_confidence = data.get("ai_confidence", 0.0)
        self.image_url = data.get("image_url")
        self.is_duplicate = data.get("is_duplicate", False)
        self.duplicate_of_id = data.get("duplicate_of_id")
        self.created_at = data.get("created_at", datetime.utcnow())
        self.updated_at = data.get("updated_at", self.created_at)
        self.resolved_at = data.get("resolved_at")

    @classmethod
    def from_document(cls, document: Dict[str, Any]) -> "Complaint":
        document = dict(document)
        document.pop("_id", None)
        return cls(**document)

    def to_document(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if key != "_id"}
