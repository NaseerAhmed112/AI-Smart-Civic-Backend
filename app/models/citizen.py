import uuid
from datetime import datetime


class Citizen:
    """Value object retained for future MongoDB citizen profiles."""

    collection_name = "citizens"

    def __init__(self, name: str, email: str, phone: str | None = None, **kwargs):
        self.citizen_id = kwargs.get("citizen_id", str(uuid.uuid4()))
        self.name = name
        self.email = email
        self.phone = phone
        self.created_at = kwargs.get("created_at", datetime.utcnow())
