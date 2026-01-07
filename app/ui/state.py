"""
Centralized Session State Management.
All Streamlit session state keys are initialized and managed here.
"""
import streamlit as st
from app.core.config import InterviewMode

# Default values for session state
DEFAULTS = {
    "messages": [],
    "interview_active": False,
    "interview_mode": None,  # 'technical' or 'hr'
    "difficulty_level": 5,   # 1 (Startup) to 10 (FAANG)
    "mode_selected": True,   # Whether user has chosen a mode
    "review_data": None,
    "last_ai_message": "",
    "recorder_key": 0,
    "session_id": None,
    "turn_number": 0,
    "turn_analytics": [],  # List of analytics per turn
}

def init_state():
    """Initialize all session state variables with defaults."""
    for key, default_value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def get_state(key: str):
    """Safely get a session state value."""
    return st.session_state.get(key, DEFAULTS.get(key))

def set_state(key: str, value):
    """Set a session state value."""
    st.session_state[key] = value

def reset_state():
    """Reset interview-related state to defaults."""
    reset_keys = [
        "messages", "interview_active", "interview_mode", "mode_selected",
        "review_data", "last_ai_message", "turn_number", "turn_analytics",
        "difficulty_level"
    ]
    for key in reset_keys:
        st.session_state[key] = DEFAULTS[key]
    st.session_state["recorder_key"] += 1

def set_interview_mode(mode: str):
    """Set the interview mode and mark as selected."""
    st.session_state["interview_mode"] = mode
    st.session_state["mode_selected"] = True
