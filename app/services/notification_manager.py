import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NotificationManager")

class NotificationManager:
    """
    OOP Service for handling citizen notifications and civic department alerts.
    """
    def __init__(self):
        self.notification_log = []

    def notify_citizen_submission(self, complaint_id: str, email: str, category: str, priority: str) -> dict:
        msg = f"[NOTIFICATION SENT TO {email}]: Your complaint #{complaint_id[:8]} has been registered. AI Classification: {category} ({priority} Priority)."
        logger.info(msg)
        entry = {"type": "citizen_ack", "recipient": email, "message": msg, "status": "DELIVERED"}
        self.notification_log.append(entry)
        return entry

    def notify_department_alert(self, department: str, complaint_id: str, priority: str, summary: str) -> dict:
        msg = f"[ALERT TO {department}]: Urgent complaint #{complaint_id[:8]} assigned! Priority: {priority}. Summary: {summary}"
        logger.info(msg)
        entry = {"type": "dept_alert", "recipient": department, "message": msg, "status": "DELIVERED"}
        self.notification_log.append(entry)
        return entry

    def notify_status_change(self, complaint_id: str, email: str, new_status: str) -> dict:
        msg = f"[UPDATE TO {email}]: Complaint #{complaint_id[:8]} status updated to '{new_status}'."
        logger.info(msg)
        entry = {"type": "status_update", "recipient": email, "message": msg, "status": "DELIVERED"}
        self.notification_log.append(entry)
        return entry

    def get_logs(self, limit: int = 10):
        return self.notification_log[-limit:]

notification_manager = NotificationManager()
