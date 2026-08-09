import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import client, initialize_database
from app.routes import complaints, analytics


app = FastAPI(title=settings.PROJECT_NAME)
logger = logging.getLogger(__name__)
app.state.mongodb_connected = False

@app.on_event("startup")
def startup() -> None:
    try:
        client.admin.command("ping")
        initialize_database()
        app.state.mongodb_connected = True
    except Exception:
        logger.warning("MongoDB is unavailable. Database endpoints will retry when MongoDB becomes reachable.")

@app.on_event("shutdown")
def shutdown() -> None:
    client.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# StaticFiles removed — Vercel serverless has no persistent disk.
# To serve uploaded images, integrate Cloudinary or AWS S3.

app.include_router(complaints, prefix="/api/complaints", tags=["Complaints"])
app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
def root():
    return {
        "status": "Online",
        "platform": settings.PROJECT_NAME,
        "mongodb_connected": app.state.mongodb_connected,
    }
