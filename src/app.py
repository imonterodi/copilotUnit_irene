"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}

# Additional activities (2 sports, 2 artistic, 2 intellectual)
activities.update({
    "Soccer Team": {
        "description": "Join the school soccer team for training and matches",
        "schedule": "Mondays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 22,
        "participants": ["alex@mergington.edu"]
    },
    "Swimming Club": {
        "description": "Swim training and pool sessions for all levels",
        "schedule": "Wednesdays, 5:00 PM - 6:30 PM",
        "max_participants": 15,
        "participants": []
    },
    "Art Club": {
        "description": "Explore drawing, painting and mixed media projects",
        "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
        "max_participants": 20,
        "participants": ["mia@mergington.edu"]
    },
    "Choir": {
        "description": "Vocal training and performance group for students",
        "schedule": "Fridays, 3:45 PM - 5:15 PM",
        "max_participants": 30,
        "participants": []
    },
    "Debate Club": {
        "description": "Practice debating skills and participate in competitions",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 16,
        "participants": ["liam@mergington.edu"]
    },
    "Math Olympiad": {
        "description": "Advanced problem solving and contest preparation",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": []
    }
})


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate and normalize email
    if not isinstance(email, str) or not email.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    normalized = email.strip().lower()

    # Check for duplicate registration (case-insensitive)
    if any(p.strip().lower() == normalized for p in activity.get("participants", [])):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered for this activity")

    # Check capacity
    max_participants = activity.get("max_participants", float("inf"))
    if len(activity.get("participants", [])) >= max_participants:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Activity is full")

    # Add student (store normalized email)
    activity.setdefault("participants", []).append(normalized)
    return {"message": f"Signed up {normalized} for {activity_name}"}
