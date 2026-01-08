"""
Mind Exercise Service - Logic Puzzles and Riddle Generation.
Generates unique, psychology-based questions for cognitive training.
Uses AI to create personalized challenges with varying difficulty.
"""
import json
import random
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from groq import Groq
from app.core.config import settings
from app.core.logger import logger


class MindExerciseService:
    """Service for generating and managing mind exercises."""
    
    # Question categories based on cognitive psychology
    CATEGORIES = {
        'logical': {
            'name': 'Logical Reasoning',
            'icon': '🧠',
            'description': 'Deductive and inductive reasoning puzzles',
            'cognitive_skill': 'Analytical thinking'
        },
        'pattern': {
            'name': 'Pattern Recognition',
            'icon': '🔢',
            'description': 'Sequence and pattern completion',
            'cognitive_skill': 'Sequential processing'
        },
        'verbal': {
            'name': 'Verbal Puzzles',
            'icon': '💬',
            'description': 'Riddles and word-based challenges',
            'cognitive_skill': 'Lateral thinking'
        },
        'numerical': {
            'name': 'Quick Math',
            'icon': '⚡',
            'description': 'Mental arithmetic challenges',
            'cognitive_skill': 'Numerical fluency'
        },
        'spatial': {
            'name': 'Spatial Reasoning',
            'icon': '🎯',
            'description': 'Visualization and mental rotation',
            'cognitive_skill': 'Visual-spatial processing'
        }
    }
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.model_id = settings.LLM_MODEL
    
    def _generate_session_seed(self, user_id: str = None) -> str:
        """Generate a unique seed for question randomization."""
        timestamp = datetime.now().isoformat()
        random_part = random.randint(1000, 9999)
        seed_input = f"{user_id or 'anon'}_{timestamp}_{random_part}"
        return hashlib.md5(seed_input.encode()).hexdigest()[:8]
    
    async def generate_questions(
        self,
        num_questions: int = 10,
        categories: List[str] = None,
        difficulty: int = 5,
        user_seed: str = None
    ) -> List[Dict]:
        """
        Generate a set of unique mind exercise questions.
        
        Args:
            num_questions: Number of questions to generate
            categories: List of categories to include (None = all)
            difficulty: 1-10 difficulty scale
            user_seed: Unique seed for this user's session
        
        Returns:
            List of question dictionaries
        """
        if categories is None:
            categories = list(self.CATEGORIES.keys())
        
        seed = user_seed or self._generate_session_seed()
        
        # Difficulty descriptors
        difficulty_desc = {
            (1, 3): "easy, suitable for warm-up, should take 10-20 seconds",
            (4, 6): "moderate, requires some thought, should take 20-40 seconds",
            (7, 8): "challenging, requires careful analysis, should take 40-60 seconds",
            (9, 10): "very difficult, requires deep thinking, may take over 60 seconds"
        }
        
        diff_text = next(v for k, v in difficulty_desc.items() if k[0] <= difficulty <= k[1])
        
        prompt = f"""
        Generate exactly {num_questions} unique mind exercise questions for cognitive training.
        
        REQUIREMENTS:
        1. Each question MUST have exactly 4 multiple choice options (A, B, C, D)
        2. Questions should be from these categories: {', '.join(categories)}
        3. Difficulty level: {difficulty}/10 ({diff_text})
        4. Each question must be solvable within the time frame
        5. Use randomization seed: {seed} to ensure uniqueness
        6. Questions should be based on cognitive psychology principles
        7. Mix question types evenly across categories
        
        CATEGORY DESCRIPTIONS:
        - logical: Syllogisms, if-then statements, deduction puzzles
        - pattern: Number sequences, visual patterns, series completion
        - verbal: Riddles, word puzzles, analogies
        - numerical: Mental math, quick calculations, number relationships
        - spatial: Shape folding, rotation, mirror images (describe in text)
        
        Return a JSON object with a 'questions' array. Each question object must have:
        - 'id': Unique identifier (1 to {num_questions})
        - 'category': One of {categories}
        - 'question': The question text (clear and concise)
        - 'options': Object with keys 'A', 'B', 'C', 'D' containing the options
        - 'correct_answer': The correct option letter (A, B, C, or D)
        - 'explanation': Brief explanation of why the answer is correct
        - 'time_limit': Suggested time in seconds (10-90 based on difficulty)
        - 'cognitive_skill': What mental ability this tests
        
        Respond ONLY with valid JSON, no other text.
        """
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert cognitive psychologist and puzzle designer. Create engaging, scientifically-grounded mental exercises. Always respond with valid JSON only."
                    },
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8  # Higher temperature for variety
            )
            
            result = json.loads(completion.choices[0].message.content)
            questions = result.get('questions', [])
            
            # Add category metadata
            for q in questions:
                cat_key = q.get('category', 'logical')
                cat_info = self.CATEGORIES.get(cat_key, self.CATEGORIES['logical'])
                q['category_name'] = cat_info['name']
                q['category_icon'] = cat_info['icon']
            
            logger.info(f"Generated {len(questions)} mind exercise questions (seed: {seed})")
            return questions
            
        except Exception as e:
            logger.error(f"Error generating mind exercises: {e}")
            return self._get_fallback_questions(num_questions)
    
    def _get_fallback_questions(self, count: int) -> List[Dict]:
        """Return fallback questions if AI generation fails."""
        fallback = [
            {
                'id': 1,
                'category': 'logical',
                'category_name': 'Logical Reasoning',
                'category_icon': '🧠',
                'question': 'If all roses are flowers, and some flowers fade quickly, which statement must be true?',
                'options': {
                    'A': 'All roses fade quickly',
                    'B': 'Some roses might fade quickly',
                    'C': 'No roses fade quickly',
                    'D': 'All flowers are roses'
                },
                'correct_answer': 'B',
                'explanation': 'Since some flowers fade quickly and roses are flowers, it is possible (but not certain) that some roses fade quickly.',
                'time_limit': 30,
                'cognitive_skill': 'Deductive reasoning'
            },
            {
                'id': 2,
                'category': 'pattern',
                'category_name': 'Pattern Recognition',
                'category_icon': '🔢',
                'question': 'What number comes next: 2, 6, 12, 20, 30, ?',
                'options': {
                    'A': '40',
                    'B': '42',
                    'C': '44',
                    'D': '38'
                },
                'correct_answer': 'B',
                'explanation': 'The differences increase by 2 each time: +4, +6, +8, +10, +12 = 42',
                'time_limit': 25,
                'cognitive_skill': 'Sequential pattern recognition'
            },
            {
                'id': 3,
                'category': 'verbal',
                'category_name': 'Verbal Puzzles',
                'category_icon': '💬',
                'question': 'I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?',
                'options': {
                    'A': 'A ghost',
                    'B': 'An echo',
                    'C': 'A shadow',
                    'D': 'A thought'
                },
                'correct_answer': 'B',
                'explanation': 'An echo "speaks" (repeats sounds) and "hears" (responds to sound), comes alive with wind carrying sound.',
                'time_limit': 40,
                'cognitive_skill': 'Lateral thinking'
            },
            {
                'id': 4,
                'category': 'numerical',
                'category_name': 'Quick Math',
                'category_icon': '⚡',
                'question': 'What is 17 × 6 - 12?',
                'options': {
                    'A': '88',
                    'B': '90',
                    'C': '92',
                    'D': '102'
                },
                'correct_answer': 'B',
                'explanation': '17 × 6 = 102, then 102 - 12 = 90',
                'time_limit': 15,
                'cognitive_skill': 'Mental arithmetic'
            },
            {
                'id': 5,
                'category': 'spatial',
                'category_name': 'Spatial Reasoning',
                'category_icon': '🎯',
                'question': 'If you fold a square piece of paper in half diagonally, then fold it in half again, and cut off the folded corner, what shape appears when you unfold it?',
                'options': {
                    'A': 'A circle',
                    'B': 'A square hole in the center',
                    'C': 'A diamond shape in the center',
                    'D': 'Four triangular holes'
                },
                'correct_answer': 'C',
                'explanation': 'The diagonal folds and corner cut create a diamond (rhombus) shape in the center when unfolded.',
                'time_limit': 45,
                'cognitive_skill': 'Mental visualization'
            }
        ]
        return fallback[:count]
    
    def calculate_results(
        self,
        questions: List[Dict],
        user_answers: List[Dict]
    ) -> Dict:
        """
        Calculate results from a completed exercise session.
        
        Args:
            questions: List of question dictionaries
            user_answers: List of {question_id, answer, time_taken} dicts
        
        Returns:
            Results summary dictionary
        """
        correct_count = 0
        total_time = 0
        category_scores = {}
        
        for q in questions:
            q_id = q['id']
            user_answer = next((a for a in user_answers if a['question_id'] == q_id), None)
            
            if user_answer:
                is_correct = user_answer['answer'] == q['correct_answer']
                if is_correct:
                    correct_count += 1
                
                total_time += user_answer.get('time_taken', 0)
                
                # Track by category
                cat = q['category']
                if cat not in category_scores:
                    category_scores[cat] = {'correct': 0, 'total': 0}
                category_scores[cat]['total'] += 1
                if is_correct:
                    category_scores[cat]['correct'] += 1
        
        num_questions = len(questions)
        accuracy = (correct_count / num_questions * 100) if num_questions > 0 else 0
        avg_time = total_time / num_questions if num_questions > 0 else 0
        
        return {
            'total_questions': num_questions,
            'correct_answers': correct_count,
            'accuracy_percent': round(accuracy, 1),
            'total_time_seconds': round(total_time, 1),
            'avg_time_per_question': round(avg_time, 1),
            'category_breakdown': category_scores,
            'performance_level': self._get_performance_level(accuracy, avg_time)
        }
    
    def _get_performance_level(self, accuracy: float, avg_time: float) -> str:
        """Determine performance level based on accuracy and speed."""
        if accuracy >= 90 and avg_time < 20:
            return "🏆 Elite"
        elif accuracy >= 80 and avg_time < 30:
            return "⭐ Excellent"
        elif accuracy >= 70:
            return "👍 Good"
        elif accuracy >= 50:
            return "📈 Developing"
        else:
            return "🎯 Keep Practicing"
