"""
Interview Page - Premium Interview Interface.
Modern, polished design with glassmorphism and professional styling.
"""
import streamlit as st
import asyncio
import textwrap
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
    
    # Optional CV Upload Section
    st.markdown("### 📄 Upload Your CV (Optional)")
    st.markdown("""
    <div style="background: rgba(99, 102, 241, 0.1); border: 1px dashed rgba(99, 102, 241, 0.4); 
                border-radius: 16px; padding: 20px; text-align: center; margin-bottom: 20px;">
        <p style="color: #a0aec0; margin-bottom: 10px;">
            Upload your resume for a <strong>personalized interview</strong>. 
            Questions will be based on your experience, projects, and skills.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_cv = st.file_uploader(
        "Upload CV (PDF only)", 
        type=["pdf"], 
        key="cv_uploader",
        label_visibility="collapsed"
    )
    
    if uploaded_cv is not None:
        # Parse the CV
        from app.services.cv_parser import parse_cv, summarize_cv_for_prompt
        cv_bytes = uploaded_cv.read()
        cv_text = parse_cv(cv_bytes)
        
        if cv_text:
            cv_summary = summarize_cv_for_prompt(cv_text)
            st.session_state.cv_content = cv_summary
            st.success(f"✅ CV uploaded successfully! ({len(cv_text)} characters extracted)")
            
            with st.expander("📋 Preview extracted CV content"):
                st.text(cv_text[:1500] + ("..." if len(cv_text) > 1500 else ""))
        else:
            st.warning("⚠️ Could not extract text from the PDF. Try a different file or proceed without CV.")
            st.session_state.cv_content = ""
    else:
        st.session_state.cv_content = ""
    
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
    
    # Only show audio player if user is NOT ready to record yet
    # This prevents audio playback from interfering with mic access
    if os.path.exists(audio_path) and not st.session_state.get("ready_to_record", False):
        st.audio(audio_path, autoplay=True)
        st.info("🔊 Listen to the AI's question above, then click the button below when you're ready to respond.")

    # User Recording Section
    st.markdown("### 🎤 Your Response")
    
    # Two-step flow to avoid audio/mic conflicts
    if not st.session_state.get("ready_to_record", False):
        # Step 1: User clicks "Ready to Respond" after hearing AI
        st.markdown("""
        <div style="background: rgba(99, 102, 241, 0.1); border: 1px solid rgba(99, 102, 241, 0.3); 
                    border-radius: 12px; padding: 20px; text-align: center; margin: 15px 0;">
            <p style="color: #a0aec0; margin-bottom: 10px; font-size: 0.95rem;">
                ⏸️ Finished listening? Click below to enable your microphone.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("✅ I'm Ready to Respond", key="ready_btn", use_container_width=True, type="primary"):
            st.session_state.ready_to_record = True
            st.session_state.recorder_key += 1  # Reset recorder for fresh state
            st.rerun()
    else:
        # Step 2: Show microphone recorder
        st.caption("💡 If the button doesn't respond, check your browser's microphone permissions (click the 🔒 icon in the address bar).")
        
        audio = mic_recorder(
            start_prompt="🎙️ Start Recording",
            stop_prompt="⏹️ Submit Answer",
            just_once=True,  # Reset after each recording for reliability
            format="webm",   # Explicit format for Whisper API compatibility
            key=f"mic_{st.session_state.recorder_key}",
            use_container_width=True
        )

        if audio and audio.get('bytes'):
            # Reset ready_to_record for next turn
            st.session_state.ready_to_record = False
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
    """Render a premium welcome page using st.html for bulletproof rendering."""
    
    # Define HTML separately with NO LEADING SPACES to avoid markdown issues
    welcome_styles = """
<style>
@keyframes glowFade {
    0% { opacity: 0; transform: translateY(20px); }
    100% { opacity: 1; transform: translateY(0); }
}

.welcome-container { 
    animation: glowFade 0.8s ease-out;
    max-width: 1100px; 
    margin: 0 auto; 
    text-align: center; 
    padding: 20px; 
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

.hero-box { 
    background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), rgba(0,0,0,0) 50%),
                rgba(255, 255, 255, 0.02);
    backdrop-filter: blur(25px); 
    border-radius: 48px; 
    border: 1px solid rgba(255, 255, 255, 0.1); 
    padding: 80px 40px;
    box-shadow: 0 40px 100px -20px rgba(0, 0, 0, 0.6);
}

.hero-title { 
    font-size: 4.5rem; 
    font-weight: 900; 
    background: linear-gradient(135deg, #a5b4fc 0%, #c084fc 100%); 
    -webkit-background-clip: text; 
    -webkit-text-fill-color: transparent; 
    margin-bottom: 24px;
    letter-spacing: -2px;
}

.hero-subtitle { 
    font-size: 1.6rem; 
    color: #94a3b8; 
    margin-bottom: 60px;
    font-weight: 400;
}

.feat-grid { 
    display: grid; 
    grid-template-columns: repeat(2, 1fr); 
    gap: 32px; 
}

.feat-card { 
    background: rgba(255, 255, 255, 0.03); 
    border: 1px solid rgba(255, 255, 255, 0.05); 
    border-radius: 32px; 
    padding: 35px; 
    text-align: left;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.feat-card:hover {
    transform: translateY(-12px);
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(99, 102, 241, 0.5);
    box-shadow: 0 20px 40px -10px rgba(99, 102, 241, 0.2);
}

.feat-icon { 
    font-size: 3rem; 
    margin-bottom: 24px; 
    display: block;
    filter: drop-shadow(0 10px 15px rgba(0,0,0,0.2));
}

.feat-title { 
    font-size: 1.7rem; 
    font-weight: 700; 
    color: #f8fafc; 
    margin-bottom: 12px; 
}

.feat-desc { 
    color: #cbd5e1; 
    font-size: 1.1rem; 
    line-height: 1.6; 
}
</style>
"""
    welcome_content = """
<div class="welcome-container">
    <div class="hero-box">
        <h1 class="hero-title">AI Interview Coach</h1>
        <p class="hero-subtitle">Master the art of high-stakes interviews with elite AI-powered vocal simulations.</p>
        <div class="feat-grid">
            <div class="feat-card">
                <span class="feat-icon">🎯</span>
                <div class="feat-title">FAANG Scenarios</div>
                <p class="feat-desc">Practice with hyper-realistic challenges designed for world-class technical and leadership roles.</p>
            </div>
            <div class="feat-card">
                <span class="feat-icon">🎙️</span>
                <div class="feat-title">Vocal Analysis</div>
                <p class="feat-desc">Uncover hidden verbal blindspots with instant metrics on pace, tone, and confidence.</p>
            </div>
            <div class="feat-card">
                <span class="feat-icon">📊</span>
                <div class="feat-title">Precision Analytics</div>
                <p class="feat-desc">Follow deep-learning feedback on filler words, fluency, and technical accuracy per turn.</p>
            </div>
            <div class="feat-card">
                <span class="feat-icon">📈</span>
                <h3 class="feat-title">Adaptive Growth</h3>
                <p class="feat-desc">Experience an evolving challenge that scales from early-career to executive intensity levels.</p>
            </div>
        </div>
    </div>
</div>
"""
    # Use st.html for guaranteed rendering
    st.html(welcome_styles + welcome_content)

    # Use native Streamlit button for functionality
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        if st.button("🚀 UNLOCK YOUR POTENTIAL", use_container_width=True, type="primary"):
            st.session_state.mode_selected = False
            st.rerun()
    
    st.info("💡 Pro-tip: Access previous sessions and analytics in the sidebar.")
