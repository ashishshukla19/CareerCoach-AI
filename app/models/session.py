from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from app.db.session import Base

class InterviewSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    
    # Media info
    media_path = Column(String)  # Path to saved .mp4 or .wav
    media_type = Column(String)  # "video" or "audio"
    
    # Analysis results (to be filled in Iteration 2/3)
    transcript = Column(String, nullable=True)
    ai_feedback = Column(String, nullable=True) # "Practice eye contact", etc.
    score = Column(Float, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)