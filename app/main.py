import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

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
        app.state.mongodb_connected = True
    except PyMongoError:
        logger.warning("MongoDB is unavailable on startup. Database endpoints will retry when MongoDB becomes reachable.")

    try:
        initialize_database()
    except PyMongoError:
        logger.warning("MongoDB index initialization failed. Database may still be reachable.")

@app.on_event("shutdown")
def shutdown() -> None:
    client.close()

# Configure CORS using environment-driven settings. Prefer explicit origins
# for security in production. If no origins provided, allow all for dev.
allowed_origins = []
if settings.ALLOWED_ORIGINS:
    # comma separated list
    allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
elif settings.FRONTEND_URL:
    allowed_origins = [settings.FRONTEND_URL.rstrip('/')]

if not allowed_origins:
    # development fallback (not recommended for production)
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if allowed_origins and allowed_origins != ["*"] else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaints, prefix="/api/complaints", tags=["Complaints"])
app.include_router(analytics, prefix="/api/analytics", tags=["Analytics"])

@app.get("/")
def root():
    mongodb_connected = False
    try:
        client.admin.command("ping")
        mongodb_connected = True
    except PyMongoError:
        logger.warning("MongoDB health check ping failed.")

    return {
        "status": "Online",
        "platform": settings.PROJECT_NAME,
        "mongodb_connected": mongodb_connected,
    }
