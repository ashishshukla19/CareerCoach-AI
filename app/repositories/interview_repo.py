from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional
from app.models.interview import InterviewSession
from app.core.logger import logger

class InterviewRepository:
    """Handles all database operations for interview sessions."""
    
    def __init__(self, db: Session):
        self.db = db

    def create_session(
        self, 
        user_id: int = 1, 
        interview_type: str = "technical",
        difficulty_level: int = 5
    ) -> InterviewSession:
        """Create a new interview session with specified type and difficulty."""
        try:
            session = InterviewSession(
                user_id=user_id,
                interview_type=interview_type,
                difficulty_level=difficulty_level,
                status="active",
                started_at=datetime.utcnow()
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            logger.info(f"Created new {interview_type} (level {difficulty_level}) interview session: {session.id}")
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating interview session: {e}")
            raise

    def get_session(self, session_id: int) -> InterviewSession:
        """Retrieve a session by ID."""
        return self.db.query(InterviewSession).filter(InterviewSession.id == session_id).first()

    def update_session(self, session_id: int, **kwargs):
        """Update session attributes."""
        try:
            session = self.get_session(session_id)
            if session:
                for key, value in kwargs.items():
                    setattr(session, key, value)
                self.db.commit()
                logger.info(f"Updated session {session_id}")
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating session {session_id}: {e}")
            raise

    def complete_session(
        self, 
        session_id: int, 
        transcript: str, 
        score: int,
        speech_analytics: Optional[Dict] = None,
        technical_accuracy: Optional[int] = None
    ):
        """Mark session as completed with final data and analytics."""
        return self.update_session(
            session_id,
            status="completed",
            completed_at=datetime.utcnow(),
            transcript=transcript,
            overall_score=score,
            speech_analytics=speech_analytics,
            technical_accuracy=technical_accuracy
        )
