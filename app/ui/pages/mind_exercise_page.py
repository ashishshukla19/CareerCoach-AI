"""
Mind Exercise Page - Timed Logic Puzzles and Riddles.
A separate page for cognitive training with unique questions per session.
"""
import streamlit as st
import asyncio
from datetime import datetime
from app.services.mind_exercise_service import MindExerciseService

# Initialize service
_mind_service = None

def get_mind_service():
    global _mind_service
    if _mind_service is None:
        _mind_service = MindExerciseService()
    return _mind_service


def render_mind_exercise_welcome():
    """Render the welcome/setup page for mind exercises."""
    
    # Premium CSS
    st.markdown("""
    <style>
    .mind-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
    }
    .mind-subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .category-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    }
    .category-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .category-name {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e2e8f0;
    }
    .category-desc {
        font-size: 0.85rem;
        color: #a0aec0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="mind-header">🧩 Mind Gym</h1>', unsafe_allow_html=True)
    st.markdown('<p class="mind-subtitle">Sharpen your cognitive skills with AI-generated puzzles</p>', unsafe_allow_html=True)
    
    # Category display
    service = get_mind_service()
    categories = service.CATEGORIES
    
    st.markdown("### 📚 Exercise Categories")
    cols = st.columns(5)
    for idx, (key, cat) in enumerate(categories.items()):
        with cols[idx]:
            st.markdown(f"""
            <div class="category-card">
                <div class="category-icon">{cat['icon']}</div>
                <div class="category-name">{cat['name']}</div>
                <div class="category-desc">{cat['cognitive_skill']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Configuration
    st.markdown("### ⚙️ Configure Your Session")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=20,
            value=10,
            key="mind_num_questions"
        )
    
    with col2:
        difficulty = st.slider(
            "Difficulty Level",
            min_value=1,
            max_value=10,
            value=5,
            key="mind_difficulty",
            help="1 = Easy warm-up | 10 = Expert challenge"
        )
    
    # Difficulty description
    if difficulty <= 3:
        diff_text = "🟢 Warm-Up Mode - Quick, confidence-building questions"
    elif difficulty <= 6:
        diff_text = "🟡 Standard Mode - Balanced challenge for daily practice"
    elif difficulty <= 8:
        diff_text = "🟠 Challenge Mode - Push your cognitive limits"
    else:
        diff_text = "🔴 Expert Mode - Only for the mentally elite!"
    
    st.info(diff_text)
    
    # Category selection
    selected_categories = st.multiselect(
        "Select Categories (leave empty for all)",
        options=list(categories.keys()),
        format_func=lambda x: f"{categories[x]['icon']} {categories[x]['name']}",
        key="mind_categories"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Start button
    if st.button("🚀 Start Mind Exercise", use_container_width=True, type="primary"):
        # Generate unique session
        import random
        user_seed = f"user_{random.randint(10000, 99999)}_{datetime.now().timestamp()}"
        
        with st.spinner("🧠 Generating your personalized questions..."):
            service = get_mind_service()
            questions = asyncio.run(service.generate_questions(
                num_questions=num_questions,
                categories=selected_categories if selected_categories else None,
                difficulty=difficulty,
                user_seed=user_seed
            ))
        
        if questions:
            st.session_state.mind_exercise_questions = questions
            st.session_state.mind_exercise_active = True
            st.session_state.current_question_index = 0
            st.session_state.mind_exercise_answers = []
            st.session_state.question_start_time = datetime.now()
            st.rerun()
        else:
            st.error("Failed to generate questions. Please try again.")


def render_mind_exercise_question():
    """Render the current question with timer and options."""
    
    questions = st.session_state.get('mind_exercise_questions', [])
    current_idx = st.session_state.get('current_question_index', 0)
    
    if current_idx >= len(questions):
        # All questions answered, show results
        render_mind_exercise_results()
        return
    
    question = questions[current_idx]
    
    # CSS for question display
    st.markdown("""
    <style>
    .question-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .question-progress {
        color: #667eea;
        font-weight: 600;
    }
    .question-category {
        background: rgba(99, 102, 241, 0.2);
        padding: 6px 15px;
        border-radius: 20px;
        font-size: 0.9rem;
        color: #a0aec0;
    }
    .question-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
    }
    .question-text {
        font-size: 1.3rem;
        color: #e2e8f0;
        line-height: 1.6;
    }
    .timer-display {
        text-align: center;
        font-size: 1.5rem;
        color: #f59e0b;
        margin: 15px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header with progress and category
    st.markdown(f"""
    <div class="question-header">
        <span class="question-progress">Question {current_idx + 1} of {len(questions)}</span>
        <span class="question-category">{question.get('category_icon', '🧠')} {question.get('category_name', 'Logic')}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Progress bar
    progress = (current_idx) / len(questions)
    st.progress(progress)
    
    # Timer display (suggested time)
    time_limit = question.get('time_limit', 30)
    st.markdown(f"""
    <div class="timer-display">
        ⏱️ Suggested time: {time_limit} seconds
    </div>
    """, unsafe_allow_html=True)
    
    # Question box
    st.markdown(f"""
    <div class="question-box">
        <div class="question-text">{question.get('question', 'Question not available')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Options as radio buttons
    options = question.get('options', {})
    option_list = [f"{k}: {v}" for k, v in options.items()]
    
    selected = st.radio(
        "Select your answer:",
        options=option_list,
        key=f"answer_{current_idx}",
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("Submit Answer ✓", use_container_width=True, type="primary"):
            if selected:
                # Calculate time taken
                start_time = st.session_state.get('question_start_time', datetime.now())
                time_taken = (datetime.now() - start_time).total_seconds()
                
                # Extract answer letter
                answer_letter = selected.split(":")[0].strip()
                
                # Store answer
                st.session_state.mind_exercise_answers.append({
                    'question_id': question['id'],
                    'answer': answer_letter,
                    'time_taken': time_taken,
                    'correct': answer_letter == question['correct_answer']
                })
                
                # Move to next question
                st.session_state.current_question_index += 1
                st.session_state.question_start_time = datetime.now()
                st.rerun()
            else:
                st.warning("Please select an answer before submitting.")


def render_mind_exercise_results():
    """Render the results summary after completing all questions."""
    
    questions = st.session_state.get('mind_exercise_questions', [])
    answers = st.session_state.get('mind_exercise_answers', [])
    
    service = get_mind_service()
    results = service.calculate_results(questions, answers)
    
    # CSS
    st.markdown("""
    <style>
    .results-header {
        text-align: center;
        margin-bottom: 30px;
    }
    .results-title {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
    }
    .performance-badge {
        font-size: 2rem;
        margin-top: 10px;
    }
    .stat-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 25px;
        text-align: center;
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #667eea;
    }
    .stat-label {
        color: #a0aec0;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="results-header">
        <div class="results-title">🎉 Exercise Complete!</div>
        <div class="performance-badge">{results['performance_level']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{results['correct_answers']}/{results['total_questions']}</div>
            <div class="stat-label">Correct Answers</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{results['accuracy_percent']}%</div>
            <div class="stat-label">Accuracy</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{results['avg_time_per_question']}s</div>
            <div class="stat-label">Avg Time/Question</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{int(results['total_time_seconds'])}s</div>
            <div class="stat-label">Total Time</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Category breakdown
    st.markdown("### 📊 Category Performance")
    breakdown = results.get('category_breakdown', {})
    
    if breakdown:
        for cat, scores in breakdown.items():
            cat_info = service.CATEGORIES.get(cat, {'icon': '📝', 'name': cat})
            correct = scores['correct']
            total = scores['total']
            pct = (correct / total * 100) if total > 0 else 0
            
            col1, col2 = st.columns([1, 4])
            with col1:
                st.markdown(f"**{cat_info['icon']} {cat_info['name']}**")
            with col2:
                st.progress(pct / 100)
                st.caption(f"{correct}/{total} correct ({pct:.0f}%)")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Review answers
    with st.expander("📝 Review All Answers"):
        for idx, q in enumerate(questions):
            user_answer = next((a for a in answers if a['question_id'] == q['id']), None)
            if user_answer:
                is_correct = user_answer['correct']
                icon = "✅" if is_correct else "❌"
                
                st.markdown(f"**{icon} Q{idx + 1}: {q['question']}**")
                st.markdown(f"Your answer: **{user_answer['answer']}** | Correct: **{q['correct_answer']}**")
                if not is_correct:
                    st.caption(f"💡 {q['explanation']}")
                st.markdown("---")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Try Again", use_container_width=True):
            st.session_state.mind_exercise_active = False
            st.session_state.mind_exercise_questions = []
            st.session_state.mind_exercise_answers = []
            st.session_state.current_question_index = 0
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, type="primary"):
            st.session_state.mind_exercise_active = False
            st.session_state.mind_exercise_questions = []
            st.session_state.show_mind_gym = False
            st.rerun()


def render_mind_exercise_page():
    """Main entry point for the Mind Exercise page."""
    
    if st.session_state.get('mind_exercise_active', False):
        # Check if we're showing results or questions
        questions = st.session_state.get('mind_exercise_questions', [])
        current_idx = st.session_state.get('current_question_index', 0)
        
        if current_idx >= len(questions):
            render_mind_exercise_results()
        else:
            render_mind_exercise_question()
    else:
        render_mind_exercise_welcome()
