from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String) # 'student' or 'teacher'

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    deadline = Column(DateTime)
    max_marks = Column(Integer)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    submissions = relationship("Submission", back_populates="assignment")

class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    file_url = Column(String)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="SUBMITTED") # SUBMITTED, LATE, GRADED
    marks = Column(Integer, nullable=True)
    feedback = Column(Text, nullable=True)
    
    assignment = relationship("Assignment", back_populates="submissions")