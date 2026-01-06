"""
Groq Service - AI Brain (STT + LLM).
Handles transcription and response generation with difficulty-adjusted personas.
"""
from groq import Groq
from typing import List, Dict
from app.core.config import settings, get_technical_persona, get_hr_persona, InterviewMode
from app.core.logger import logger

class GroqService:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = Groq(api_key=self.api_key)
        self.model_id = settings.LLM_MODEL
        self.stt_model = settings.STT_MODEL
    
    def get_persona(self, mode: str, difficulty: int = 5) -> str:
        """Get the appropriate AI persona based on interview mode and difficulty."""
        if mode == InterviewMode.HR:
            return get_hr_persona(difficulty)
        return get_technical_persona(difficulty)

    async def get_response_from_audio(
        self, 
        audio_bytes, 
        mode: str = InterviewMode.TECHNICAL,
        difficulty: int = 5,
        history: List[Dict] = []
    ):
        """
        Transcribes audio using Whisper and generates an AI response.
        Uses mode and difficulty-specific persona.
        """
        try:
            # 1. Transcription using Whisper on Groq
            transcription = self.client.audio.transcriptions.create(
                file=("input.webm", audio_bytes),
                model=self.stt_model,
                response_format="text"
            )
            
            candidate_text = transcription
            
            # 2. Generate LLM Response with difficulty-adjusted persona
            persona = self.get_persona(mode, difficulty)
            messages = [{"role": "system", "content": persona}]
            
            for msg in history:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})
            
            messages.append({"role": "user", "content": candidate_text})
            
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=200,
                temperature=0.7
            )
            
            ai_response = completion.choices[0].message.content
            
            return {
                "candidate_transcription": candidate_text,
                "interviewer_response": ai_response
            }
        except Exception as e:
            error_msg = str(e)
            logger.error(f"GROQ SERVICE ERROR: {type(e).__name__} - {error_msg}")
            
            if "413" in error_msg or "too large" in error_msg.lower():
                return {"candidate_transcription": "[Audio too large]", "interviewer_response": "That's a lot of detail! Could you summarize that briefly?"}
            if "429" in error_msg or "quota" in error_msg.lower():
                return {"candidate_transcription": "[Quota Limit]", "interviewer_response": "I'm processing a lot of candidates right now. Let's pause for 30 seconds."}
            if "401" in error_msg or "authentication" in error_msg.lower():
                return {"candidate_transcription": "[API Key Invalid]", "interviewer_response": "There's a configuration issue. Please check your API key."}
            
            return {
                "candidate_transcription": f"[Error: {type(e).__name__}]",
                "interviewer_response": f"I encountered an error: {error_msg[:100]}. Could you try again?"
            }

    async def get_response(self, user_input: str, mode: str = InterviewMode.TECHNICAL, difficulty: int = 5, history: List[Dict] = []):
        """Generates a text-based response with difficulty-adjusted persona."""
        try:
            persona = self.get_persona(mode, difficulty)
            messages = [{"role": "system", "content": persona}]
            
            for msg in history:
                role = "user" if msg["role"] == "user" else "assistant"
                messages.append({"role": role, "content": msg["content"]})
            
            messages.append({"role": "user", "content": user_input})
            
            completion = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=200
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq Text Error: {e}")
            return "Connection issues. Please try again in a moment."
