"""
Speech Analytics Service.
Analyzes audio for pauses, filler words, speech pace, and fluency metrics.
"""
import re
from typing import Dict, List
from app.core.logger import logger

# Common filler words to detect
FILLER_WORDS = ["um", "uh", "like", "you know", "basically", "actually", "literally", "so", "well"]

class SpeechAnalyticsService:
    """Analyzes transcribed speech for fluency metrics."""
    
    def __init__(self):
        self.filler_patterns = [re.compile(rf'\b{word}\b', re.IGNORECASE) for word in FILLER_WORDS]
    
    def analyze_transcript(self, transcript: str, audio_duration_seconds: float = None) -> Dict:
        """
        Analyze a transcript for speech metrics.
        
        Args:
            transcript: The transcribed text.
            audio_duration_seconds: Duration of the audio in seconds.
        
        Returns:
            Dictionary with speech analytics.
        """
        if not transcript or transcript.strip() == "":
            return self._empty_analytics()
        
        # Word count and pace
        words = transcript.split()
        word_count = len(words)
        
        words_per_minute = 0
        if audio_duration_seconds and audio_duration_seconds > 0:
            words_per_minute = int((word_count / audio_duration_seconds) * 60)
        
        # Filler word detection
        filler_counts = {}
        total_fillers = 0
        for i, pattern in enumerate(self.filler_patterns):
            count = len(pattern.findall(transcript))
            if count > 0:
                filler_counts[FILLER_WORDS[i]] = count
                total_fillers += count
        
        # Fluency score (simplified: penalize for fillers)
        filler_ratio = total_fillers / max(word_count, 1)
        fluency_score = max(0, int(100 - (filler_ratio * 200)))  # Heavy penalty for fillers
        
        # Confidence indicators
        confidence_phrases = ["I believe", "I think", "definitely", "certainly", "absolutely"]
        hesitation_phrases = ["I'm not sure", "maybe", "I guess", "probably"]
        
        confidence_count = sum(1 for phrase in confidence_phrases if phrase.lower() in transcript.lower())
        hesitation_count = sum(1 for phrase in hesitation_phrases if phrase.lower() in transcript.lower())
        
        analytics = {
            "word_count": word_count,
            "words_per_minute": words_per_minute,
            "filler_word_count": filler_counts,
            "total_fillers": total_fillers,
            "fluency_score": fluency_score,
            "confidence_indicators": confidence_count,
            "hesitation_indicators": hesitation_count,
            "audio_duration_seconds": audio_duration_seconds or 0
        }
        
        logger.info(f"Speech analytics: WPM={words_per_minute}, Fillers={total_fillers}, Fluency={fluency_score}")
        return analytics
    
    def aggregate_session_analytics(self, turn_analytics: List[Dict]) -> Dict:
        """
        Aggregate analytics from multiple turns into session-level metrics.
        """
        if not turn_analytics:
            return self._empty_analytics()
        
        total_words = sum(t.get("word_count", 0) for t in turn_analytics)
        total_duration = sum(t.get("audio_duration_seconds", 0) for t in turn_analytics)
        total_fillers = sum(t.get("total_fillers", 0) for t in turn_analytics)
        
        # Aggregate filler counts
        all_fillers = {}
        for t in turn_analytics:
            for word, count in t.get("filler_word_count", {}).items():
                all_fillers[word] = all_fillers.get(word, 0) + count
        
        avg_wpm = int((total_words / max(total_duration, 1)) * 60) if total_duration > 0 else 0
        avg_fluency = sum(t.get("fluency_score", 0) for t in turn_analytics) // len(turn_analytics)
        
        return {
            "total_words": total_words,
            "avg_words_per_minute": avg_wpm,
            "total_fillers": total_fillers,
            "filler_word_count": all_fillers,
            "avg_fluency_score": avg_fluency,
            "total_turns": len(turn_analytics),
            "total_duration_seconds": total_duration
        }
    
    def _empty_analytics(self) -> Dict:
        """Return empty analytics structure."""
        return {
            "word_count": 0,
            "words_per_minute": 0,
            "filler_word_count": {},
            "total_fillers": 0,
            "fluency_score": 0,
            "confidence_indicators": 0,
            "hesitation_indicators": 0,
            "audio_duration_seconds": 0
        }
