import os
import sys
import uuid
from datetime import datetime, timedelta
import random

# Add project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import database, initialize_database
from app.models.complaint import Complaint
from app.services.ai_analyzer import ai_analyzer

SEED_COMPLAINTS = [
    {
        "description": "Main water supply pipeline burst on MG Road near Metro Station 4. Water flooding into basement shops.",
        "location": "MG Road, Ward 12",
        "citizen_name": "Aarav Sharma",
        "citizen_email": "aarav.sharma@gmail.com",
        "status": "Resolved",
        "hours_ago": 72,
        "resolved_after_hours": 8.5
    },
    {
        "description": "Deep pothole near St. Jude School entrance. Several vehicles damaged, severe traffic risk for school children.",
        "location": "St. Jude Avenue, Ward 5",
        "citizen_name": "Priya Nair",
        "citizen_email": "priya.nair@yahoo.com",
        "status": "In Progress",
        "hours_ago": 48,
        "resolved_after_hours": None
    },
    {
        "description": "Garbage dump accumulated behind Green Park Community Hall. Foul smell and breeding mosquitoes.",
        "location": "Green Park, Ward 8",
        "citizen_name": "Rohan Patel",
        "citizen_email": "r.patel@outlook.com",
        "status": "Resolved",
        "hours_ago": 96,
        "resolved_after_hours": 18.0
    },
    {
        "description": "Streetlight pole flickering and dead for 5 consecutive nights on 7th Cross Street. Dark alley causing safety concern.",
        "location": "7th Cross Street, Ward 3",
        "citizen_name": "Ananya Gupta",
        "citizen_email": "ananya.g@gmail.com",
        "status": "Open",
        "hours_ago": 24,
        "resolved_after_hours": None
    },
    {
        "description": "High voltage transformer sparks heard during thunderstorm near Market Square. Fire hazard risk.",
        "location": "Central Market Square, Ward 1",
        "citizen_name": "Vikram Singh",
        "citizen_email": "vikram.singh@gmail.com",
        "status": "Resolved",
        "hours_ago": 120,
        "resolved_after_hours": 4.2
    },
    {
        "description": "Sewage water overflowing from manhole outside Block B apartments. Health hazard for residents.",
        "location": "Block B, Sunrise Enclave, Ward 14",
        "citizen_name": "Meera Joshi",
        "citizen_email": "m_joshi@hotmail.com",
        "status": "Resolved",
        "hours_ago": 150,
        "resolved_after_hours": 26.5
    },
    {
        "description": "Fallen tree branch blocking two lanes of 100ft Ring Road after heavy wind.",
        "location": "Outer Ring Road, Ward 10",
        "citizen_name": "Siddharth Rao",
        "citizen_email": "sid.rao@gmail.com",
        "status": "Resolved",
        "hours_ago": 60,
        "resolved_after_hours": 6.0
    },
    {
        "description": "Illegal construction debris dumped on public sidewalk blocking pedestrian access.",
        "location": "Nehrunagar 2nd Main, Ward 7",
        "citizen_name": "Kavita Reddy",
        "citizen_email": "kavita.r@gmail.com",
        "status": "Open",
        "hours_ago": 18,
        "resolved_after_hours": None
    },
    {
        "description": "No municipal water supply for 3 days in Indira Nagar Zone 4.",
        "location": "Indira Nagar, Ward 4",
        "citizen_name": "Rajesh Kumar",
        "citizen_email": "rajesh.k@gmail.com",
        "status": "Resolved",
        "hours_ago": 200,
        "resolved_after_hours": 32.0
    },
    {
        "description": "Traffic signal lights turned off at busy 4-way intersection causing jams.",
        "location": "Commercial Street Junction, Ward 2",
        "citizen_name": "Deepa Verma",
        "citizen_email": "dverma@gmail.com",
        "status": "Resolved",
        "hours_ago": 80,
        "resolved_after_hours": 12.0
    },
    {
        "description": "Contaminated yellowish drinking water coming from public taps in Shastri Nagar.",
        "location": "Shastri Nagar, Ward 9",
        "citizen_name": "Amitabh Sen",
        "citizen_email": "asen@gmail.com",
        "status": "In Progress",
        "hours_ago": 30,
        "resolved_after_hours": None
    },
    {
        "description": "Open storm water drain without safety grill near public park. Risk to children.",
        "location": "Children's Park Road, Ward 11",
        "citizen_name": "Neha Kapoor",
        "citizen_email": "nkapoor@gmail.com",
        "status": "Resolved",
        "hours_ago": 300,
        "resolved_after_hours": 110.0 # Outlier resolution time for IQR demonstration!
    },
    {
        "description": "Overflowing public waste bin near bus terminus attracting stray animals.",
        "location": "Central Bus Terminus, Ward 1",
        "citizen_name": "Suresh Pillai",
        "citizen_email": "spillai@gmail.com",
        "status": "Resolved",
        "hours_ago": 110,
        "resolved_after_hours": 14.0
    },
    {
        "description": "Dangling electric cables hanging dangerously low over footpath near house #42.",
        "location": "Gandhi Nagar 3rd Cross, Ward 6",
        "citizen_name": "Sunita Das",
        "citizen_email": "sdas@gmail.com",
        "status": "Open",
        "hours_ago": 12,
        "resolved_after_hours": None
    },
    {
        "description": "Potholes formed after recent rain causing vehicle skidding on airport bypass road.",
        "location": "Airport Bypass Expressway, Ward 15",
        "citizen_name": "Tarun Roy",
        "citizen_email": "troy@gmail.com",
        "status": "Resolved",
        "hours_ago": 180,
        "resolved_after_hours": 42.0
    }
]

def seed_database():
    print("Recreating MongoDB complaint data...")
    initialize_database()
    database.complaints.delete_many({})
    try:
        count = 0
        now = datetime.utcnow()

        for item in SEED_COMPLAINTS:
            created = now - timedelta(hours=item["hours_ago"])
            resolved = created + timedelta(hours=item["resolved_after_hours"]) if item["resolved_after_hours"] else None
            updated = resolved if resolved else created

            ai_res = ai_analyzer.analyze(item["description"])

            comp = Complaint(
                complaint_id=str(uuid.uuid4()),
                citizen_name=item["citizen_name"],
                citizen_email=item["citizen_email"],
                description=item["description"],
                location=item["location"],
                category=ai_res["category"],
                priority=ai_res["priority"],
                assigned_department=ai_res["assigned_department"],
                ai_summary=ai_res["ai_summary"],
                ai_reason=ai_res["ai_reason"],
                ai_confidence=ai_res["ai_confidence"],
                status=item["status"],
                created_at=created,
                updated_at=updated,
                resolved_at=resolved
            )
            database.complaints.insert_one(comp.to_document())
            count += 1

        print(f"Successfully seeded database with {count} realistic civic complaints!")
    except Exception as e:
        print(f"Seeding error: {e}")

if __name__ == "__main__":
    seed_database()
