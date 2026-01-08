"""
Dashboard Page - Premium Performance Review Interface.
Modern, polished design with glassmorphism, gradients, and professional visualizations.
"""
import streamlit as st
import plotly.graph_objects as go
from app.core.config import InterviewMode, DIFFICULTY_LABELS

# Premium color palette
COLORS = {
    "primary": "#6366f1",      # Indigo
    "secondary": "#8b5cf6",    # Purple
    "success": "#10b981",      # Emerald
    "warning": "#f59e0b",      # Amber
    "danger": "#ef4444",       # Red
    "info": "#3b82f6",         # Blue
    "gradient_start": "#667eea",
    "gradient_end": "#764ba2",
}

def render_dashboard_page(review_data: dict, interview_mode: str = None) -> bool:
    """
    Render the premium performance dashboard with speech analytics.
    Returns True if user clicked 'Start New Interview'.
    """
    mode = interview_mode or InterviewMode.TECHNICAL
    mode_emoji = "💻" if mode == InterviewMode.TECHNICAL else "🤝"
    mode_name = "Technical" if mode == InterviewMode.TECHNICAL else "HR"
    difficulty = review_data.get('difficulty_level', 5)
    difficulty_label = DIFFICULTY_LABELS.get(difficulty, "Unknown")
    
    # Custom CSS for premium look
    st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label {
        color: #a0aec0;
        font-size: 0.9rem;
        margin-top: 5px;
    }
    .feedback-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(59, 130, 246, 0.1) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 25px;
    }
    .strength-item {
        background: rgba(16, 185, 129, 0.1);
        border-left: 4px solid #10b981;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }
    .weakness-item {
        background: rgba(239, 68, 68, 0.1);
        border-left: 4px solid #ef4444;
        padding: 10px 15px;
        margin: 8px 0;
        border-radius: 0 8px 8px 0;
    }
    .header-gradient {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
    }
    .exercise-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
        border: 1px solid rgba(99, 102, 241, 0.25);
        border-radius: 16px;
        padding: 20px;
        margin: 12px 0;
        transition: all 0.3s ease;
    }
    .exercise-card:hover {
        border-color: rgba(99, 102, 241, 0.5);
        transform: translateY(-2px);
    }
    .exercise-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
    }
    .exercise-icon {
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
    }
    .exercise-icon.speaking { background: rgba(59, 130, 246, 0.2); }
    .exercise-icon.cognitive { background: rgba(168, 85, 247, 0.2); }
    .exercise-icon.confidence { background: rgba(245, 158, 11, 0.2); }
    .exercise-icon.technical { background: rgba(16, 185, 129, 0.2); }
    .exercise-icon.behavioral { background: rgba(236, 72, 153, 0.2); }
    .exercise-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    .exercise-duration {
        font-size: 0.8rem;
        color: #667eea;
        background: rgba(99, 102, 241, 0.15);
        padding: 4px 10px;
        border-radius: 20px;
        margin-left: auto;
    }
    .exercise-desc {
        color: #cbd5e0;
        font-size: 0.95rem;
        line-height: 1.5;
        margin-bottom: 10px;
    }
    .exercise-science {
        font-size: 0.85rem;
        color: #a0aec0;
        font-style: italic;
        padding: 8px 12px;
        background: rgba(0,0,0,0.2);
        border-radius: 8px;
    }
    .exercise-target {
        font-size: 0.75rem;
        color: #ef4444;
        margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with gradient
    st.markdown(f"""
        <h1 class="header-gradient">📈 {mode_emoji} {mode_name} Interview Results</h1>
        <p style="color: #a0aec0; margin-bottom: 30px;">
            Difficulty: Level {difficulty} ({difficulty_label})
        </p>
    """, unsafe_allow_html=True)
    
    # Overall Score Section
    overall_score = review_data.get('overall_score', 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Radial gauge with premium styling
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=overall_score,
            number={'font': {'size': 60, 'color': '#667eea'}},
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 2, 'tickcolor': "#4a5568"},
                'bar': {'color': "#667eea", 'thickness': 0.3},
                'bgcolor': "rgba(0,0,0,0)",
                'borderwidth': 0,
                'steps': [
                    {'range': [0, 40], 'color': 'rgba(239, 68, 68, 0.2)'},
                    {'range': [40, 70], 'color': 'rgba(245, 158, 11, 0.2)'},
                    {'range': [70, 100], 'color': 'rgba(16, 185, 129, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': "#667eea", 'width': 4},
                    'thickness': 0.8,
                    'value': overall_score
                }
            }
        ))
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font={'color': "#e2e8f0"},
            height=280,
            margin=dict(l=20, r=20, t=40, b=20),
            annotations=[dict(
                text="Overall Score",
                x=0.5, y=-0.1,
                font_size=16,
                font_color="#a0aec0",
                showarrow=False
            )]
        )
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col2:
        # Feedback card
        st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
        st.markdown("### 💬 AI Feedback")
        st.write(review_data.get('feedback', 'No feedback available.'))
        
        recommendations = review_data.get('recommendations', [])
        if recommendations:
            st.markdown("#### 🎯 Action Items")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}.** {rec}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Performance Metrics - Radar Chart
    st.markdown("### 📊 Performance Breakdown")
    
    metrics = review_data.get('metrics', {})
    
    if mode == InterviewMode.HR:
        categories = ['Communication', 'STAR Method', 'Cultural Fit', 'Confidence']
        keys = ['communication', 'star_method', 'cultural_fit', 'confidence']
    else:
        categories = ['Problem Solving', 'Technical Depth', 'System Design', 'Communication']
        keys = ['problem_solving', 'technical_depth', 'system_design', 'communication']
    
    values = [metrics.get(k, 0) for k in keys]
    values.append(values[0])  # Close the radar
    categories_closed = categories + [categories[0]]
    
    fig_radar = go.Figure()
    
    fig_radar.add_trace(go.Scatterpolar(
        r=values,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.3)',
        line=dict(color='#6366f1', width=3),
        name='Your Score'
    ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10],
                tickfont=dict(size=10, color='#a0aec0'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(size=12, color='#e2e8f0'),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # Speech Analytics Section
    speech_analytics = review_data.get('speech_analytics', {})
    if speech_analytics:
        st.markdown("### 🎙️ Speech Analytics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            wpm = speech_analytics.get('avg_words_per_minute', 0)
            status_color = "#10b981" if 120 <= wpm <= 150 else "#f59e0b" if 100 <= wpm <= 170 else "#ef4444"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="background: {status_color}; -webkit-background-clip: text;">{wpm}</div>
                    <div class="metric-label">Words/Min</div>
                    <small style="color: #718096;">Ideal: 120-150</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            fillers = speech_analytics.get('total_fillers', 0)
            status_color = "#10b981" if fillers < 5 else "#f59e0b" if fillers < 15 else "#ef4444"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="background: {status_color}; -webkit-background-clip: text;">{fillers}</div>
                    <div class="metric-label">Filler Words</div>
                    <small style="color: #718096;">Target: &lt; 5</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            fluency = speech_analytics.get('avg_fluency_score', 0)
            status_color = "#10b981" if fluency >= 80 else "#f59e0b" if fluency >= 60 else "#ef4444"
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value" style="background: {status_color}; -webkit-background-clip: text;">{fluency}%</div>
                    <div class="metric-label">Fluency Score</div>
                    <small style="color: #718096;">Target: &gt; 80%</small>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_words = speech_analytics.get('total_words', 0)
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_words}</div>
                    <div class="metric-label">Total Words</div>
                    <small style="color: #718096;">Turns: {speech_analytics.get('total_turns', 0)}</small>
                </div>
            """, unsafe_allow_html=True)
        
        # Filler word breakdown - horizontal bar chart
        filler_breakdown = speech_analytics.get('filler_word_count', {})
        if filler_breakdown:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("**Filler Word Distribution**")
            
            fig_fillers = go.Figure(go.Bar(
                y=list(filler_breakdown.keys()),
                x=list(filler_breakdown.values()),
                orientation='h',
                marker=dict(
                    color=list(filler_breakdown.values()),
                    colorscale=[[0, '#667eea'], [1, '#ef4444']],
                    line=dict(width=0)
                )
            ))
            fig_fillers.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                height=max(150, len(filler_breakdown) * 40),
                margin=dict(l=100, r=20, t=10, b=10),
                xaxis=dict(
                    title="Count",
                    gridcolor='rgba(255,255,255,0.1)',
                    tickfont=dict(color='#a0aec0')
                ),
                yaxis=dict(tickfont=dict(color='#e2e8f0'))
            )
            st.plotly_chart(fig_fillers, use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Strengths and Weaknesses
    st.markdown("### 📋 Summary")
    col_s, col_w = st.columns(2)
    
    with col_s:
        st.markdown("#### ✅ Strengths")
        for s in review_data.get('strengths', []):
            st.markdown(f'<div class="strength-item">{s}</div>', unsafe_allow_html=True)
    
    with col_w:
        st.markdown("#### ⚠️ Areas for Improvement")
        for w in review_data.get('weaknesses', []):
            st.markdown(f'<div class="weakness-item">{w}</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Improvement Exercises Section
    exercises = review_data.get('improvement_exercises', [])
    if exercises:
        st.markdown("### 🏋️ Personalized Improvement Exercises")
        st.markdown("<p style='color: #a0aec0; margin-bottom: 20px;'>Evidence-based exercises tailored to your interview performance</p>", unsafe_allow_html=True)
        
        # Category icons mapping
        category_icons = {
            'speaking': '🗣️',
            'cognitive': '🧠',
            'confidence': '💪',
            'technical': '💻',
            'behavioral': '🤝'
        }
        
        # Display exercises in 2 columns
        col1, col2 = st.columns(2)
        
        for idx, exercise in enumerate(exercises):
            col = col1 if idx % 2 == 0 else col2
            
            category = exercise.get('category', 'cognitive').lower()
            icon = category_icons.get(category, '📝')
            
            with col:
                st.markdown(f'''
                <div class="exercise-card">
                    <div class="exercise-header">
                        <div class="exercise-icon {category}">{icon}</div>
                        <div class="exercise-name">{exercise.get('name', 'Exercise')}</div>
                        <div class="exercise-duration">⏱️ {exercise.get('duration', '10 min')}</div>
                    </div>
                    <div class="exercise-desc">{exercise.get('description', '')}</div>
                    <div class="exercise-science">🔬 {exercise.get('psychology_basis', 'Based on research')}</div>
                    <div class="exercise-target">🎯 Targets: {exercise.get('target_weakness', 'General improvement')}</div>
                </div>
                ''', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("🚀 Start New Interview", use_container_width=True, type="primary"):
        return True
    return False
