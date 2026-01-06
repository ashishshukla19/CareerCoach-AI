"""
UI Components - Reusable Streamlit UI elements.
"""
import streamlit as st
from pathlib import Path
from app.core.config import InterviewMode

def render_header():
    """Render the main application header."""
    st.title("🎙️ AI Interview Coach")
    st.markdown("### Professional Voice-Based Interview Practice")

def render_sidebar_controls(interview_active: bool, session_id: int, interview_mode: str = None):
    """
    Render sidebar control buttons.
    Returns: 'start', 'end', 'mode_technical', 'mode_hr', or None.
    """
    with st.sidebar:
        st.header("🎮 Controls")
        
        if not interview_active and st.session_state.get("mode_selected", True):
            if st.button("🚀 Start New Interview", use_container_width=True):
                return "start"
        
        # Mode selection buttons (shown when mode_selected is False)
        if not st.session_state.get("mode_selected", True) and not interview_active:
            st.divider()
            st.subheader("Choose Interview Type")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💻 Technical", use_container_width=True, help="Coding & System Design"):
                    return "mode_technical"
            with col2:
                if st.button("🤝 HR", use_container_width=True, help="Behavioral & Soft Skills"):
                    return "mode_hr"
        
        if interview_active:
            if st.button("📊 End & Review", use_container_width=True):
                return "end"
        
        st.divider()
        status_text = "Active" if interview_active else "Idle"
        if interview_mode:
            mode_emoji = "💻" if interview_mode == InterviewMode.TECHNICAL else "🤝"
            status_text = f"{mode_emoji} {interview_mode.capitalize()}"
        st.info(f"Status: {status_text}")
        
        if session_id:
            st.info(f"Session ID: {session_id}")
    return None

def render_replay_section(session_id: int, audio_files: list):
    """Render the replay section in the sidebar."""
    with st.sidebar:
        st.divider()
        st.subheader("📼 Replay Interviews")
        if session_id and audio_files:
            for turn_data in audio_files:
                with st.expander(f"Turn {turn_data['turn']}"):
                    st.write("**Your Response:**")
                    user_audio = turn_data.get('user_audio')
                    if user_audio and Path(user_audio).exists():
                        st.audio(user_audio)
                    else:
                        st.warning("User recording missing.")
                        
                    st.write("**AI Response:**")
                    ai_audio = turn_data.get('ai_audio')
                    if ai_audio and Path(ai_audio).exists():
                        st.audio(ai_audio)
                    else:
                        st.warning("AI audio missing.")
