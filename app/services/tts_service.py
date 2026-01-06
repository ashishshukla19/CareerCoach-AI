import asyncio
import edge_tts
import os
from pathlib import Path

class TTSService:
    """Text-to-Speech service using Microsoft Edge TTS (free, natural voices)."""
    
    def __init__(self):
        # Professional, natural-sounding voice
        self.voice = "en-US-AriaNeural"  # Professional female voice
        # Alternative voices:
        # "en-US-GuyNeural" - Professional male
        # "en-US-JennyNeural" - Friendly female
        
        # Create audio directory if it doesn't exist
        self.audio_dir = Path("audio_outputs")
        self.audio_dir.mkdir(exist_ok=True)
    
    async def text_to_speech(self, text: str, output_filename: str) -> str:
        """
        Convert text to speech and save to file.
        
        Args:
            text: The text to convert to speech
            output_filename: Name for the output file (without extension)
            
        Returns:
            Path to the generated audio file
        """
        try:
            output_path = self.audio_dir / f"{output_filename}.mp3"
            
            # Generate speech
            communicate = edge_tts.Communicate(text, self.voice)
            await communicate.save(str(output_path))
            
            return str(output_path)
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def text_to_speech_sync(self, text: str, output_filename: str) -> str:
        """Synchronous wrapper for text_to_speech."""
        return asyncio.run(self.text_to_speech(text, output_filename))
