"""
Review Service - Interview Performance Analysis.
Generates detailed reviews based on interview mode, difficulty, and speech analytics.
"""
import json
from typing import Dict, Optional
from groq import Groq
from app.core.config import settings, InterviewMode, DIFFICULTY_LABELS
from app.core.logger import logger

class ReviewService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.model_id = settings.LLM_MODEL

    async def analyze_interview(
        self, 
        transcript: str, 
        mode: str = InterviewMode.TECHNICAL,
        difficulty: int = 5,
        speech_analytics: Optional[Dict] = None
    ):
        """
        Analyzes the interview transcript with mode and difficulty-specific criteria.
        Includes speech analytics in the evaluation.
        """
        
        difficulty_label = DIFFICULTY_LABELS.get(difficulty, "Unknown")
        
        # Difficulty context
        difficulty_context = f"""
        DIFFICULTY LEVEL: {difficulty}/10 ({difficulty_label})
        
        Scoring Guidelines for Level {difficulty}:
        - Levels 1-3: Be lenient, focus on potential and basic competencies.
        - Levels 4-6: Standard expectations, look for solid fundamentals.
        - Levels 7-8: High bar, expect optimization and deeper knowledge.
        - Levels 9-10: FAANG standards, expect near-perfect responses.
        
        Adjust your scoring based on the difficulty level. A good answer at Level 3 
        might only be average at Level 8.
        """
        
        # Mode-specific evaluation criteria
        if mode == InterviewMode.HR:
            criteria = """
            EVALUATION CRITERIA (HR Interview):
            - Communication clarity and articulation
            - Use of STAR method in behavioral answers
            - Emotional intelligence and self-awareness
            - Cultural fit indicators
            - Confidence and professionalism
            """
            metrics_template = "{{ 'communication': 0-10, 'star_method': 0-10, 'cultural_fit': 0-10, 'confidence': 0-10 }}"
        else:
            criteria = """
            EVALUATION CRITERIA (Technical Interview):
            - Problem-solving approach
            - Technical depth and accuracy
            - System design understanding
            - Code quality thinking
            - Ability to explain trade-offs
            """
            metrics_template = "{{ 'problem_solving': 0-10, 'technical_depth': 0-10, 'system_design': 0-10, 'communication': 0-10 }}"
        
        # Include speech analytics in prompt if available
        analytics_context = ""
        if speech_analytics:
            analytics_context = f"""
            SPEECH ANALYTICS:
            - Words per minute: {speech_analytics.get('avg_words_per_minute', 'N/A')}
            - Total filler words: {speech_analytics.get('total_fillers', 0)}
            - Filler breakdown: {speech_analytics.get('filler_word_count', {})}
            - Fluency score: {speech_analytics.get('avg_fluency_score', 0)}/100
            
            Consider these speech patterns in your evaluation.
            """
        
        prompt = f"""
        Analyze the following {mode.upper()} interview transcript.
        {difficulty_context}
        {criteria}
        {analytics_context}
        
        Provide a detailed performance review in JSON format:
        1. 'overall_score': A score from 0-100 (adjusted for difficulty level {difficulty}).
        2. 'strengths': A list of top 3 strengths.
        3. 'weaknesses': A list of top 3 areas for improvement.
        4. 'feedback': A detailed qualitative summary (3-4 sentences) mentioning the difficulty level.
        5. 'metrics': {metrics_template}
        6. 'recommendations': 3 specific action items for improvement.

        Transcript:
        {transcript}
        
        Respond ONLY with valid JSON, no other text.
        """

        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {"role": "system", "content": f"You are an expert {mode} interview evaluator for {difficulty_label} level positions. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            logger.info(f"Successfully analyzed {mode} (level {difficulty}) interview transcript.")
            return json.loads(completion.choices[0].message.content)
        except Exception as e:
            logger.error(f"Error analyzing interview: {e}")
            return {
                "overall_score": 0,
                "strengths": ["Error during analysis"],
                "weaknesses": ["Error during analysis"],
                "feedback": "Analysis failed.",
                "metrics": {},
                "recommendations": []
            }
