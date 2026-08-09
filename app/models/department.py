import uuid


class Department:
    """Value object retained for future MongoDB department records."""

    collection_name = "departments"

    def __init__(self, name: str, description: str | None = None, contact_email: str | None = None, **kwargs):
        self.department_id = kwargs.get("department_id", str(uuid.uuid4()))
        self.name = name
        self.description = description
        self.contact_email = contact_email
