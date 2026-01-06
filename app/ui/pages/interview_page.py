"""
Interview Page - Premium Interview Interface.
Modern, polished design with glassmorphism and professional styling.
"""
import streamlit as st
import asyncio
import os
from streamlit_mic_recorder import mic_recorder
from app.core.config import InterviewMode, DIFFICULTY_LABELS
from app.logic.interview_handler import process_audio_turn, start_new_interview

def render_mode_selection():
    """Render the premium interview mode and difficulty selection page."""
    
    # Premium CSS
    st.markdown("""
    <style>
    .selection-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
    }
    .difficulty-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 25px;
        margin: 20px 0;
        text-align: center;
    }
    .mode-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .mode-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-5px);
    }
    .mode-icon {
        font-size: 4rem;
        margin-bottom: 15px;
    }
    .mode-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 15px;
    }
    .mode-desc {
        color: #a0aec0;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .difficulty-badge {
        display: inline-block;
        padding: 8px 20px;
        border-radius: 30px;
        font-weight: 600;
        font-size: 1.1rem;
    }
    .badge-easy { background: linear-gradient(135deg, #10b981 0%, #059669 100%); }
    .badge-medium { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
    .badge-hard { background: linear-gradient(135deg, #f87171 0%, #ef4444 100%); }
    .badge-elite { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="selection-header">🎯 Interview Setup</h1>', unsafe_allow_html=True)
    
    # Difficulty Selection
    st.markdown("### Select Difficulty Level")
    st.markdown('<div class="difficulty-card">', unsafe_allow_html=True)
    
    difficulty = st.slider(
        "Interview Difficulty",
        min_value=1,
        max_value=10,
        value=5,
        help="1 = Friendly Startup | 10 = Elite FAANG",
        key="difficulty_slider",
        label_visibility="collapsed"
    )
    
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "Unknown")
    
    # Dynamic difficulty badge
    if difficulty <= 3:
        badge_class = "badge-easy"
        diff_desc = "Friendly • Basic Questions • Hints Available"
    elif difficulty <= 6:
        badge_class = "badge-medium"
        diff_desc = "Professional • Solid Fundamentals • Standard Expectations"
    elif difficulty <= 8:
        badge_class = "badge-hard"
        diff_desc = "Challenging • Optimization Required • Edge Cases Expected"
    else:
        badge_class = "badge-elite"
        diff_desc = "Intense • Near-Perfect Answers • Deep Expertise Required"
    
    st.markdown(f"""
        <div style="text-align: center; margin-top: 20px;">
            <span class="difficulty-badge {badge_class}">Level {difficulty}: {difficulty_label}</span>
            <p style="color: #a0aec0; margin-top: 10px;">{diff_desc}</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mode Selection Cards
    st.markdown("### Choose Interview Type")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">💻</div>
            <div class="mode-title">Technical Interview</div>
            <div class="mode-desc">
                • Coding Problems & Algorithms<br>
                • System Design Questions<br>
                • Technical Deep Dives<br>
                • Problem-Solving Approach<br><br>
                <em>Best for: Engineers, Data Scientists, DevOps</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Start Technical", key="tech_btn", use_container_width=True, type="primary"):
            st.session_state.mode_selected = True
            st.session_state.interview_mode = InterviewMode.TECHNICAL
            st.session_state.difficulty_level = difficulty
            start_new_interview(mode=InterviewMode.TECHNICAL, difficulty=difficulty)
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="mode-card">
            <div class="mode-icon">🤝</div>
            <div class="mode-title">HR Interview</div>
            <div class="mode-desc">
                • Behavioral Questions (STAR)<br>
                • Communication Assessment<br>
                • Cultural Fit Evaluation<br>
                • Soft Skills Analysis<br><br>
                <em>Best for: All Roles, Leadership Positions</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚀 Start HR", key="hr_btn", use_container_width=True, type="primary"):
            st.session_state.mode_selected = True
            st.session_state.interview_mode = InterviewMode.HR
            st.session_state.difficulty_level = difficulty
            start_new_interview(mode=InterviewMode.HR, difficulty=difficulty)
            st.rerun()

def render_interview_page():
    """Render the premium interview interface."""
    
    # Premium CSS
    st.markdown("""
    <style>
    .interview-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
        padding: 15px 20px;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 16px;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .interview-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    .level-badge {
        padding: 8px 16px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .ai-card {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
    }
    .ai-avatar {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.8rem;
        margin-bottom: 15px;
    }
    .ai-speech {
        font-style: italic;
        color: #cbd5e0;
        font-size: 1.15rem;
        line-height: 1.6;
        padding: 15px;
        background: rgba(99, 102, 241, 0.1);
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    .analytics-mini {
        display: flex;
        gap: 20px;
        justify-content: center;
        margin-top: 20px;
    }
    .mini-stat {
        text-align: center;
        padding: 15px 25px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
    }
    .mini-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #667eea;
    }
    .mini-label {
        color: #a0aec0;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show current mode and difficulty
    mode = st.session_state.get("interview_mode", InterviewMode.TECHNICAL)
    difficulty = st.session_state.get("difficulty_level", 5)
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "Unknown")
    
    mode_emoji = "💻" if mode == InterviewMode.TECHNICAL else "🤝"
    mode_name = "Technical" if mode == InterviewMode.TECHNICAL else "HR"
    
    # Difficulty color coding
    if difficulty <= 3:
        diff_color = "#10b981"
    elif difficulty <= 6:
        diff_color = "#f59e0b"
    elif difficulty <= 8:
        diff_color = "#f87171"
    else:
        diff_color = "#ef4444"
    
    # Header
    st.markdown(f"""
        <div class="interview-header">
            <span class="interview-title">{mode_emoji} {mode_name} Interview</span>
            <span class="level-badge" style="background: {diff_color};">
                Level {difficulty}: {difficulty_label}
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    # AI Card
    st.markdown(f"""
        <div class="ai-card">
            <div class="ai-avatar">🎙️</div>
            <h3 style="color: #667eea; margin-bottom: 15px;">AI Interviewer</h3>
            <div class="ai-speech">
                "{st.session_state.last_ai_message}"
            </div>
        </div>
    """, unsafe_allow_html=True)

    # AI Voice Autoplay
    turn_num = st.session_state.turn_number
    session_id = st.session_state.session_id
    
    if turn_num == 0:
        audio_path = f"audio_outputs/welcome_{session_id}.mp3"
    else:
        audio_path = f"stored_interviews/ai/session_{session_id}_turn_{turn_num}_ai.mp3"
    
    if os.path.exists(audio_path):
        st.audio(audio_path, autoplay=True)

    # User Recording Section
    st.markdown("### 🎤 Your Response")
    
    audio = mic_recorder(
        start_prompt="🎙️ Start Recording",
        stop_prompt="⏹️ Submit Answer",
        key=f"mic_{st.session_state.recorder_key}",
        use_container_width=True
    )

    if audio:
        with st.spinner("🔄 Analyzing your response..."):
            asyncio.run(process_audio_turn(audio['bytes']))
        st.rerun()

    # Live Analytics (if available)
    if st.session_state.get("turn_analytics"):
        latest = st.session_state.turn_analytics[-1]
        st.markdown(f"""
            <div class="analytics-mini">
                <div class="mini-stat">
                    <div class="mini-value">{latest.get("word_count", 0)}</div>
                    <div class="mini-label">Words</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-value">{latest.get("total_fillers", 0)}</div>
                    <div class="mini-label">Fillers</div>
                </div>
                <div class="mini-stat">
                    <div class="mini-value">{latest.get("fluency_score", 0)}%</div>
                    <div class="mini-label">Fluency</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Transcript Expander
    with st.expander("📜 View Transcript"):
        for msg in st.session_state.messages:
            icon = "🤖" if msg["role"] == "assistant" else "👤"
            role_color = "#667eea" if msg["role"] == "assistant" else "#10b981"
            st.markdown(f"<span style='color: {role_color}; font-weight: 600;'>{icon} {msg['role'].capitalize()}:</span> {msg['content']}", unsafe_allow_html=True)

def render_welcome_page():
    """Render the premium welcome page."""
    st.markdown("""
    <style>
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
    }
    .welcome-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 20px;
    }
    .welcome-subtitle {
        color: #a0aec0;
        font-size: 1.3rem;
        margin-bottom: 40px;
    }
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    .feature-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .feature-title {
        color: #e2e8f0;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .feature-desc {
        color: #a0aec0;
        font-size: 0.9rem;
    }
    </style>
    
    <div class="welcome-container">
        <h1 class="welcome-title">🎙️ AI Interview Coach</h1>
        <p class="welcome-subtitle">Master your interview skills with AI-powered practice</p>
        
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-icon">🎯</div>
                <div class="feature-title">Realistic Interviews</div>
                <div class="feature-desc">Technical or HR mode with adaptive AI</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-title">Difficulty Levels</div>
                <div class="feature-desc">From Startup (1) to FAANG (10)</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">🎙️</div>
                <div class="feature-title">Voice Interaction</div>
                <div class="feature-desc">Speak naturally, get instant feedback</div>
            </div>
            <div class="feature-card">
                <div class="feature-icon">📈</div>
                <div class="feature-title">Deep Analytics</div>
                <div class="feature-desc">Track fillers, pace, and fluency</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👆 Click **Start New Interview** in the sidebar to begin!")
