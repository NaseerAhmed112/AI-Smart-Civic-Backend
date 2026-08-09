from pymongo import MongoClient
from pymongo.database import Database

from app.config import settings


# Do not resolve an Atlas SRV record during module import. This lets FastAPI
# start and report its health even when the database is temporarily offline.
client = MongoClient(
    settings.MONGODB_URL,
    serverSelectionTimeoutMS=5000,
    connect=False,
)
database: Database = client[settings.MONGODB_DB_NAME]


def get_db():
    """Provide the MongoDB database to FastAPI route dependencies."""
    yield database


def initialize_database() -> None:
    """Create the indexes used by complaint lookups and admin filtering."""
    complaints = database.complaints
    complaints.create_index("complaint_id", unique=True)
    complaints.create_index([("created_at", -1)])
    complaints.create_index("status")
    complaints.create_index("category")
    complaints.create_index("priority")
    complaints.create_index("assigned_department")
