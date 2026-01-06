# app/models/interview.py
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Text
from datetime import datetime
from app.db.session import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    interview_type = Column(String, default="technical")  # technical, hr
    difficulty_level = Column(Integer, default=5)  # 1 (Startup) to 10 (FAANG)
    status = Column(String, default="active")  # active, completed
    
    # Conversation Data
    transcript = Column(Text, nullable=True)
    
    # Scoring
    overall_score = Column(Integer, nullable=True)
    feedback = Column(JSON, nullable=True)
    
    # Speech Analytics (per-session aggregates)
    speech_analytics = Column(JSON, nullable=True)
    
    # Technical Interview Specific
    technical_accuracy = Column(Integer, nullable=True)
    questions_asked = Column(JSON, nullable=True)  # List of questions and correctness
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)