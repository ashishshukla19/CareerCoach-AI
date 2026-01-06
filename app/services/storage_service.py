import os
import subprocess
from pathlib import Path
import shutil
from app.core.config import settings
from app.core.logger import logger

class StorageService:
    """Service for saving and retrieving physical audio files."""
    
    def __init__(self):
        self.user_audio_dir = Path(settings.USER_AUDIO_DIR)
        self.ai_audio_dir = Path(settings.AI_AUDIO_DIR)
        
        self.user_audio_dir.mkdir(parents=True, exist_ok=True)
        self.ai_audio_dir.mkdir(parents=True, exist_ok=True)
    
    def save_user_audio(self, audio_bytes: bytes, session_id: int, turn_number: int) -> str:
        """Save user's audio recording and fix metadata using ffmpeg."""
        temp_filename = f"session_{session_id}_turn_{turn_number}_user_raw.webm"
        final_filename = f"session_{session_id}_turn_{turn_number}_user.webm"
        
        temp_path = self.user_audio_dir / temp_filename
        final_path = self.user_audio_dir / final_filename
        
        try:
            with open(temp_path, 'wb') as f:
                f.write(audio_bytes)
            
            subprocess.run([
                'ffmpeg', '-y', '-i', str(temp_path), 
                '-c', 'copy', str(final_path)
            ], check=True, capture_output=True)
            
            temp_path.unlink()
            logger.info(f"Saved and repaired user audio: {final_filename}")
            return str(final_path)
        except Exception as e:
            logger.error(f"Error saving user audio for session {session_id}: {e}")
            return str(temp_path) if temp_path.exists() else None
    
    def save_ai_audio(self, audio_path: str, session_id: int, turn_number: int) -> str:
        """Copy AI-generated audio to permanent storage."""
        try:
            filename = f"session_{session_id}_turn_{turn_number}_ai.mp3"
            destination = self.ai_audio_dir / filename
            shutil.copy(audio_path, destination)
            logger.info(f"Stored AI audio: {filename}")
            return str(destination)
        except Exception as e:
            logger.error(f"Error storing AI audio: {e}")
            return None
    
    def get_session_audio_files(self, session_id: int) -> list:
        """Retrieve all audio files for a session, matching them by turn number."""
        import re
        user_files = list(self.user_audio_dir.glob(f"session_{session_id}_turn_*_user.webm"))
        ai_files = list(self.ai_audio_dir.glob(f"session_{session_id}_turn_*_ai.mp3"))
        
        turns = {}
        turn_pattern = re.compile(rf"session_{session_id}_turn_(\d+)_")
        
        for f in user_files:
            match = turn_pattern.search(f.name)
            if match:
                turn = int(match.group(1))
                if turn not in turns: turns[turn] = {}
                turns[turn]["user_audio"] = str(f)
                
        for f in ai_files:
            match = turn_pattern.search(f.name)
            if match:
                turn = int(match.group(1))
                if turn not in turns: turns[turn] = {}
                turns[turn]["ai_audio"] = str(f)
        
        audio_pairs = []
        for turn_num in sorted(turns.keys()):
            turn_data = turns[turn_num]
            audio_pairs.append({
                "turn": turn_num,
                "user_audio": turn_data.get("user_audio"),
                "ai_audio": turn_data.get("ai_audio")
            })
        
        return audio_pairs
