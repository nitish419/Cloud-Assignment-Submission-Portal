from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
import models, database, auth, storage
from database import engine

# Initialize DB tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Cloud Assignment Portal API")

# Allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/register")
def register(email: str = Form(...), password: str = Form(...), name: str = Form(...), role: str = Form(...), db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = auth.get_password_hash(password)
    new_user = models.User(email=email, password_hash=hashed_pw, name=name, role=role)
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

@app.post("/api/auth/login")
def login(email: str = Form(...), password: str = Form(...), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not auth.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer", "role": user.role, "name": user.name}

@app.get("/api/assignments")
def get_assignments(db: Session = Depends(database.get_db), user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Assignment).all()

@app.post("/api/assignments")
def create_assignment(title: str = Form(...), description: str = Form(...), deadline: str = Form(...), max_marks: int = Form(...), db: Session = Depends(database.get_db), teacher: models.User = Depends(auth.require_role("teacher"))):
    deadline_dt = datetime.fromisoformat(deadline)
    new_assign = models.Assignment(title=title, description=description, deadline=deadline_dt, max_marks=max_marks, teacher_id=teacher.id)
    db.add(new_assign)
    db.commit()
    return {"message": "Assignment created"}

@app.post("/api/assignments/{assign_id}/submit")
def submit_assignment(assign_id: int, file: UploadFile = File(...), db: Session = Depends(database.get_db), student: models.User = Depends(auth.require_role("student"))):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assign_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # 1. Upload to Cloud Storage
    file_url = storage.upload_to_cloud(file, assign_id, student.id)
    
    # 2. Check Deadline Logic
    current_time = datetime.utcnow()
    status = "SUBMITTED" if current_time <= assignment.deadline else "LATE"
    
    # 3. Save Metadata to Cloud Database
    submission = models.Submission(assignment_id=assign_id, student_id=student.id, file_url=file_url, submitted_at=current_time, status=status)
    db.add(submission)
    db.commit()
    return {"message": f"File uploaded successfully. Status: {status}"}

@app.get("/api/submissions")
def get_all_submissions(db: Session = Depends(database.get_db), teacher: models.User = Depends(auth.require_role("teacher"))):
    return db.query(models.Submission).all()

@app.put("/api/submissions/{sub_id}/grade")
def grade_submission(sub_id: int, marks: int = Form(...), feedback: str = Form(...), db: Session = Depends(database.get_db), teacher: models.User = Depends(auth.require_role("teacher"))):
    sub = db.query(models.Submission).filter(models.Submission.id == sub_id).first()
    sub.marks = marks
    sub.feedback = feedback
    sub.status = "GRADED"
    db.commit()
    return {"message": "Graded successfully"}