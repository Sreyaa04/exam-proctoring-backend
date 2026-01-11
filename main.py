import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STUDENTS_FILE = "students.json"
PROCTORING_FILE = "proctoring_logs.json"

# Load students
if os.path.exists(STUDENTS_FILE):
    with open(STUDENTS_FILE, "r") as f:
        try:
            students_db = json.load(f)
        except:
            students_db = []
else:
    students_db = []

# Load logs
if os.path.exists(PROCTORING_FILE):
    with open(PROCTORING_FILE, "r") as f:
        try:
            proctoring_logs = json.load(f)
        except:
            proctoring_logs = []
else:
    proctoring_logs = []


class Student(BaseModel):
    name: str
    email: str
    role: str


@app.post("/register")
def register_student(student: Student):
    students_db.append(student.dict())

    with open(STUDENTS_FILE, "w") as f:
        json.dump(students_db, f, indent=4)

    return {
        "message": "Student registered successfully",
        "total_students": len(students_db)
    }


@app.post("/login")
def login_student(email: str):
    for student in students_db:
        # student is a DICT, not object
        if student["email"] == email:
            return {
                "message": "Login successful",
                "role": student["role"],
                "student": student
            }

    raise HTTPException(status_code=404, detail="Student not found")


@app.get("/students")
def get_students():
    return {
        "total_students": len(students_db),
        "students": students_db
    }


@app.post("/start_exam")
def start_exam(email: str):
    for student in students_db:
        if student["email"] == email:
            return {
                "message": "Exam started",
                "student": email,
                "status": "monitoring"
            }

    raise HTTPException(status_code=404, detail="Student not found")


@app.post("/flag_event")
def flag_event(email: str, event: str):
    log = {"email": email, "event": event}
    proctoring_logs.append(log)

    with open(PROCTORING_FILE, "w") as f:
        json.dump(proctoring_logs, f, indent=4)

    return {"message": "Event flagged", "log": log}


@app.get("/proctoring_logs")
def get_proctoring_logs():
    return {
        "total_events": len(proctoring_logs),
        "logs": proctoring_logs
    }


@app.get("/risk_score")
def get_risk_score(email: str):
    count = 0
    for log in proctoring_logs:
        if log["email"] == email:
            count += 1

    if count <= 1:
        level = "LOW"
    elif count <= 3:
        level = "MEDIUM"
    else:
        level = "HIGH"

    return {
        "email": email,
        "risk_score": count,
        "risk_level": level
    }


@app.post("/review_decision")
def review_decision(email: str, decision: str):
    return {
        "email": email,
        "final_decision": decision,
        "reviewed_by": "faculty"
    }



