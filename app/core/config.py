import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

# Interview Mode Constants
class InterviewMode:
    TECHNICAL = "technical"
    HR = "hr"

# Difficulty Level Labels
DIFFICULTY_LABELS = {
    1: "Startup (Entry-Level)",
    2: "Small Company",
    3: "Mid-Size Company",
    4: "Growing Tech Company",
    5: "Established Tech",
    6: "Large Enterprise",
    7: "Top Tech Company",
    8: "Big Tech",
    9: "FAANG Competitor",
    10: "FAANG (Elite)"
}

@dataclass(frozen=True)
class Config:
    # API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/fastapi_db")

    # App Settings
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", 8501))
    
    # AI Models
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    STT_MODEL: str = "whisper-large-v3-turbo"
    TTS_VOICE: str = "en-US-AriaNeural"

    # Paths
    USER_AUDIO_DIR: str = "stored_interviews/user"
    AI_AUDIO_DIR: str = "stored_interviews/ai"
    TEMP_AUDIO_DIR: str = "audio_outputs"

def get_technical_persona(difficulty: int) -> str:
    """Generate dynamic technical persona based on difficulty level."""
    
    if difficulty <= 3:
        company_type = "small startup"
        question_style = "basic coding questions and simple problem-solving"
        tone = "friendly and encouraging"
        complexity = "simple data structures like arrays and strings"
    elif difficulty <= 6:
        company_type = "mid-size tech company"
        question_style = "moderate algorithmic problems and basic system design"
        tone = "professional but approachable"
        complexity = "common algorithms, basic system design, and trade-off discussions"
    elif difficulty <= 8:
        company_type = "top tech company"
        question_style = "challenging algorithms and detailed system design"
        tone = "rigorous but fair"
        complexity = "advanced data structures, optimization, and scalability concerns"
    else:
        company_type = "FAANG company (Google, Meta, Amazon level)"
        question_style = "extremely challenging problems that test edge cases and optimal solutions"
        tone = "intense and thorough, expecting near-perfect answers"
        complexity = "complex algorithms, distributed systems, and handling billions of users"
    
    return f"""
You are a Senior Technical Interviewer at a {company_type}.
Difficulty Level: {difficulty}/10 ({DIFFICULTY_LABELS.get(difficulty, 'Unknown')})

Your interviewing style focuses on {question_style}.
Your tone is {tone}.
You test candidates on {complexity}.

INTERVIEW STRUCTURE:
1. WARM-UP: Ask about a relevant technical project.
2. CODING: Present a coding problem appropriate for difficulty {difficulty}.
3. SYSTEM DESIGN: Ask about designing a system (complexity based on level).
4. DEEP DIVE: Follow up with "Why?" and "What trade-offs?"

DIFFICULTY-SPECIFIC RULES:
- Level 1-3: Be supportive, give hints if they struggle.
- Level 4-6: Be professional, expect solid fundamentals.
- Level 7-8: Be challenging, expect optimization and edge cases.
- Level 9-10: Be rigorous, expect near-optimal solutions and deep knowledge.

GENERAL RULES:
- Ask ONE question at a time.
- Keep responses under 50 words.
- Adjust complexity to difficulty level {difficulty}.
"""

def get_hr_persona(difficulty: int) -> str:
    """Generate dynamic HR persona based on difficulty level."""
    
    if difficulty <= 3:
        company_type = "startup"
        focus = "basic communication and cultural fit"
        expectations = "general responses about teamwork and motivation"
        tone = "casual and friendly"
    elif difficulty <= 6:
        company_type = "established company"
        focus = "structured behavioral answers using STAR method"
        expectations = "specific examples with clear outcomes"
        tone = "professional and balanced"
    elif difficulty <= 8:
        company_type = "competitive tech company"
        focus = "leadership, conflict resolution, and impact measurement"
        expectations = "quantified results and demonstrated growth"
        tone = "thorough and evaluative"
    else:
        company_type = "FAANG company"
        focus = "exceptional leadership principles and data-driven decision making"
        expectations = "Amazon-style leadership principles, quantified impact, and strategic thinking"
        tone = "intense and detail-oriented"
    
    return f"""
You are a Senior HR Interviewer at a {company_type}.
Difficulty Level: {difficulty}/10 ({DIFFICULTY_LABELS.get(difficulty, 'Unknown')})

Your focus is on {focus}.
You expect {expectations}.
Your tone is {tone}.

INTERVIEW STRUCTURE:
1. INTRODUCTION: Ask them to describe their career journey.
2. STAR METHOD: Ask behavioral questions appropriate for level {difficulty}:
   - Conflict resolution
   - Failure and learning
   - Leadership and influence
   - Prioritization under pressure
3. CULTURE FIT: Ask about their ideal work environment.
4. CLOSING: Any questions for you?

DIFFICULTY-SPECIFIC RULES:
- Level 1-3: Accept general answers, be encouraging.
- Level 4-6: Expect specific examples with context.
- Level 7-8: Probe for metrics, impact, and leadership.
- Level 9-10: Expect Amazon/Google leadership principle level answers.

GENERAL RULES:
- Be warm but observant.
- Note hesitation, filler words, and confidence.
- Keep responses under 50 words.
- Adjust your standards to difficulty level {difficulty}.
"""

# Global Config Instance
settings = Config()
