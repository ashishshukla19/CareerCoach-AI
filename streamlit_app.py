"""
AI Interview Coach - Main Entry Point.
This is a thin router that initializes the app and routes to the correct page.
Supports Technical and HR interview modes.
"""
import streamlit as st
import asyncio

# Core Initialization
from app.core.config import InterviewMode
from app.core.logger import logger
from app.db.session import init_db
from app.ui.state import init_state, reset_state, set_interview_mode
from app.ui.components import render_header, render_sidebar_controls, render_replay_section
from app.ui.pages.interview_page import render_interview_page, render_welcome_page, render_mode_selection
from app.ui.pages.dashboard_page import render_dashboard_page
from app.logic.interview_handler import (
    start_new_interview, 
    end_interview_and_review, 
    get_replay_audio_files
)

# --- INITIALIZATION ---
try:
    init_db()
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

st.set_page_config(page_title="AI Interview Coach", page_icon="🎙️", layout="wide")
init_state()

# --- HEADER ---
render_header()

# --- SIDEBAR CONTROLS ---
action = render_sidebar_controls(
    st.session_state.interview_active, 
    st.session_state.session_id,
    st.session_state.get("interview_mode")
)

if action == "start":
    reset_state()
    st.rerun()
elif action == "end":
    with st.spinner("Generating your detailed performance review..."):
        asyncio.run(end_interview_and_review())
    st.rerun()
elif action and action.startswith("mode_"):
    # User selected a mode
    mode = action.replace("mode_", "")
    start_new_interview(mode=mode)
    st.rerun()

# --- REPLAY SIDEBAR ---
if st.session_state.session_id:
    audio_files = get_replay_audio_files(st.session_state.session_id)
    render_replay_section(st.session_state.session_id, audio_files)

# --- PAGE ROUTING ---
if st.session_state.review_data:
    # Dashboard Page
    if render_dashboard_page(st.session_state.review_data, st.session_state.get("interview_mode")):
        st.session_state.review_data = None
        st.rerun()
elif st.session_state.interview_active:
    # Interview Page
    render_interview_page()
elif not st.session_state.get("mode_selected", True):
    # Mode Selection Page
    render_mode_selection()
else:
    # Welcome Page
    render_welcome_page()
