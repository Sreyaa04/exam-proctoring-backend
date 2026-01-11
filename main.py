import json
import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# Enable CORS (for React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------
# File storage
# ------------------------
STUDENTS_FILE = "students.json"
LOGS_FILE = "proctoring_logs.json"

def load_file(file):
    if os.path.exists(file):
        with open(file, "r") as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_file(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

students_db = load_file(STUDENTS_FILE)
proctoring_logs = load_file(LOGS_FILE)

# ------------------------
# Models
# ------------------------
class Student(BaseModel):
    name: str
    email: str
    role: str

# ------------------------
# Routes
# ------------------------

@app.post("/register")
def register(student: Student):
    students_db.append(student.dict())
    save_file(STUDENTS_FILE, students_db)

    return {
        "message": "Student registered successfully",
        "total_students": len(students_db)
    }

@app.get("/students")
def get_students():
    return students_db

@app.post("/login")
def login(email: str = Query(...)):
    for student in students_db:
        if student["email"] == email:
            return {
                "message": "Login successful",
                "role": student["role"],
                "student": student
            }

    raise HTTPException(status_code=404, detail="Student not found")

@app.post("/start_exam")
def start_exam(email: str = Query(...)):
    for student in students_db:
        if student["email"] == email:
            return {
                "message": "Exam started",
                "email": email,
                "status": "monitoring"
            }
    raise HTTPException(status_code=404, detail="Student not found")

@app.post("/flag_event")
def flag_event(email: str = Query(...), event: str = Query(...)):
    log = {
        "email": email,
        "event": event
    }
    proctoring_logs.append(log)
    save_file(LOGS_FILE, proctoring_logs)

    return {"message": "Event logged", "log": log}

@app.get("/proctoring_logs")
def get_logs():
    return proctoring_logs

@app.get("/risk_score")
def risk_score(email: str):
    count = sum(1 for log in proctoring_logs if log["email"] == email)

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
