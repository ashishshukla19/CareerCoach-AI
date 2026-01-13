"""
Interview Handler - Core Business Logic.
Orchestrates the interview flow: starting sessions, processing audio, ending reviews.
Contains NO UI code. Supports Technical and HR interview modes with difficulty levels and speech analytics.
"""
import asyncio
import streamlit as st
from app.core.config import InterviewMode, DIFFICULTY_LABELS
from app.core.logger import logger
from app.db.session import SessionLocal
from app.repositories.interview_repo import InterviewRepository
from app.services.groq_service import GroqService
from app.services.review_service import ReviewService
from app.services.tts_service import TTSService
from app.services.storage_service import StorageService
from app.services.speech_analytics import SpeechAnalyticsService

# Service Instances (created once)
_groq_service = None
_review_service = None
_tts_service = None
_storage_service = None
_speech_analytics = None

def get_services():
    """Lazy initialization of services."""
    global _groq_service, _review_service, _tts_service, _storage_service, _speech_analytics
    if _groq_service is None:
        _groq_service = GroqService()
        _review_service = ReviewService()
        _tts_service = TTSService()
        _storage_service = StorageService()
        _speech_analytics = SpeechAnalyticsService()
    return _groq_service, _review_service, _tts_service, _storage_service, _speech_analytics

def start_new_interview(mode: str = InterviewMode.TECHNICAL, difficulty: int = 5):
    """
    Initialize a new interview session with the specified mode and difficulty.
    Creates a DB record and sets up the initial AI greeting (with RAG context if available).
    """
    groq, review, tts, storage, analytics = get_services()
    db = SessionLocal()
    repo = InterviewRepository(db)
    
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "Unknown")
    
    try:
        session = repo.create_session(interview_type=mode, difficulty_level=difficulty)
        st.session_state.session_id = session.id
        st.session_state.interview_mode = mode
        st.session_state.difficulty_level = difficulty
        st.session_state.turn_number = 0
        st.session_state.messages = []
        st.session_state.interview_active = True
        st.session_state.review_data = None
        st.session_state.turn_analytics = []
        
        # Generate difficulty-aware greeting
        if difficulty <= 3:
            company_type = "a growing startup"
        elif difficulty <= 6:
            company_type = "an established tech company"
        elif difficulty <= 8:
            company_type = "a top tech company"
        else:
            company_type = "a FAANG company"
        
        # Check for RAG context to personalize the greeting
        rag_context = ""
        rag_active = False
        try:
            from app.services.rag_service import RAGService
            rag_service = RAGService()
            if rag_service.has_documents():
                rag_active = True
                rag_context = rag_service.get_context_for_prompt("job requirements skills qualifications")
                logger.info(f"RAG Active: Using {rag_service.get_document_count()} knowledge nodes for interview")
        except Exception as e:
            logger.error(f"RAG Error in start_new_interview: {e}")
        
        # Store RAG status in session for UI display
        st.session_state.rag_active = rag_active
        
        # Mode-specific greeting with difficulty context and RAG personalization
        if rag_active and rag_context:
            # Use RAG context to personalize the greeting
            if mode == InterviewMode.HR:
                initial_msg = (
                    f"Hello! I'm your HR Interviewer. Based on the job requirements I've reviewed, "
                    f"this is a {difficulty_label} level interview. "
                    "I'll be assessing your communication skills and how well you fit this specific role. "
                    "Let's start—tell me about yourself and why you're interested in this position."
                )
            else:
                initial_msg = (
                    f"Hello! I'm your Technical Interviewer. I've reviewed the job description for this role. "
                    f"This is a {difficulty_label} level interview. "
                    "I'll be evaluating your technical skills based on the specific requirements. "
                    "To begin, tell me about a project that demonstrates your expertise relevant to this role."
                )
        else:
            # Generic greeting without RAG
            if mode == InterviewMode.HR:
                initial_msg = (
                    f"Hello! I'm your HR Interviewer from {company_type}. "
                    f"This is a {difficulty_label} level interview. "
                    "I'll be assessing your communication skills and cultural fit. "
                    "Let's start—tell me about yourself and your career journey."
                )
            else:
                initial_msg = (
                    f"Hello! I'm your Technical Interviewer from {company_type}. "
                    f"This is a {difficulty_label} level interview. "
                    "I'll be evaluating your problem-solving and technical skills. "
                    "To begin, tell me about your most challenging technical project."
                )
        
        st.session_state.last_ai_message = initial_msg
        st.session_state.messages.append({"role": "assistant", "content": initial_msg})
        st.session_state.recorder_key += 1
        
        # Generate initial voice
        asyncio.run(tts.text_to_speech(initial_msg, f"welcome_{session.id}"))
        logger.info(f"Started new {mode} interview (difficulty {difficulty}, RAG={rag_active}) session: {session.id}")
    finally:
        db.close()

async def process_audio_turn(audio_bytes: bytes):
    """
    Process a single interview turn with speech analytics.
    Uses current mode and difficulty from session state.
    """
    if not audio_bytes or len(audio_bytes) < 1000:
        logger.warning("Audio too short, skipping processing.")
        return False

    groq, review, tts, storage, analytics = get_services()
    
    st.session_state.turn_number += 1
    turn_num = st.session_state.turn_number
    session_id = st.session_state.session_id
    mode = st.session_state.get("interview_mode", InterviewMode.TECHNICAL)
    difficulty = st.session_state.get("difficulty_level", 5)
    cv_content = st.session_state.get("cv_content", "")

    # 1. Save and Repair User Audio
    storage.save_user_audio(audio_bytes, session_id, turn_num)
    
    # Estimate audio duration (rough: ~16KB per second for webm)
    estimated_duration = len(audio_bytes) / 16000
    
    # 2. Get AI Thinking (STT + LLM) with mode, difficulty, and optional CV
    # First, check if RAG has relevant context
    company_context = ""
    try:
        from app.services.rag_service import RAGService
        rag_service = RAGService()
        if rag_service.has_documents():
            # Query for context based on the current conversation topic
            # We use the candidate's last message or current transcription as query
            # For the first turn, we use the initial AI message topic
            last_ai_msg = st.session_state.get("last_ai_message", "")
            company_context = rag_service.get_context_for_prompt(last_ai_msg)
    except Exception as e:
        logger.error(f"RAG Context Error: {e}")

    result = await groq.get_response_from_audio(
        audio_bytes,
        mode=mode,
        difficulty=difficulty,
        history=st.session_state.messages,
        cv_summary=cv_content,
        company_context=company_context
    )

    
    candidate_text = result['candidate_transcription']
    ai_reply = result['interviewer_response']
    
    # 3. Analyze speech
    turn_analytics = analytics.analyze_transcript(candidate_text, estimated_duration)
    st.session_state.turn_analytics.append(turn_analytics)

    # 4. Generate and Store AI Voice
    temp_tts_path = await tts.text_to_speech(ai_reply, f"session_{session_id}_turn_{turn_num}_ai_temp")
    if temp_tts_path:
        storage.save_ai_audio(temp_tts_path, session_id, turn_num)

    # 5. Update State
    st.session_state.messages.append({"role": "user", "content": candidate_text})
    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
    st.session_state.last_ai_message = ai_reply
    st.session_state.recorder_key += 1
    
    logger.info(f"Processed turn {turn_num} for session {session_id} (mode={mode}, difficulty={difficulty})")
    return True

async def end_interview_and_review():
    """
    End the interview, generate a performance review with analytics, and save to DB.
    """
    groq, review, tts, storage, analytics = get_services()
    
    # Aggregate speech analytics
    session_analytics = analytics.aggregate_session_analytics(st.session_state.turn_analytics)
    
    transcript_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    review_data = await review.analyze_interview(
        transcript_text,
        mode=st.session_state.get("interview_mode", InterviewMode.TECHNICAL),
        difficulty=st.session_state.get("difficulty_level", 5),
        speech_analytics=session_analytics
    )
    
    # Add analytics and difficulty to review data
    review_data["speech_analytics"] = session_analytics
    review_data["difficulty_level"] = st.session_state.get("difficulty_level", 5)
    
    # Save to DB
    db = SessionLocal()
    repo = InterviewRepository(db)
    repo.complete_session(
        st.session_state.session_id, 
        transcript_text, 
        review_data.get('overall_score', 0),
        speech_analytics=session_analytics
    )
    db.close()
    
    st.session_state.review_data = review_data
    st.session_state.interview_active = False
    logger.info(f"Ended interview session: {st.session_state.session_id}")
    return review_data

def get_replay_audio_files(session_id: int):
    """Retrieve audio files for replay."""
    _, _, _, storage, _ = get_services()
    return storage.get_session_audio_files(session_id)
