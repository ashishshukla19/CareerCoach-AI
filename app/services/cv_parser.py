"""
CV Parser Service - Extracts text from uploaded PDF resumes.
"""
import io
from PyPDF2 import PdfReader
from app.core.logger import logger


def parse_cv(file_bytes: bytes) -> str:
    """
    Extract text content from a PDF file.
    Returns the extracted text or an error message.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = PdfReader(pdf_file)
        
        text_content = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_content.append(page_text)
        
        full_text = "\n".join(text_content)
        
        if not full_text.strip():
            logger.warning("CV parsing resulted in empty text.")
            return ""
        
        # Limit to ~3000 characters to avoid overwhelming the LLM context
        if len(full_text) > 3000:
            full_text = full_text[:3000] + "..."
        
        logger.info(f"Successfully parsed CV: {len(full_text)} characters extracted.")
        return full_text.strip()
    
    except Exception as e:
        logger.error(f"Error parsing CV: {e}")
        return ""


def summarize_cv_for_prompt(cv_text: str) -> str:
    """
    Prepare CV content for inclusion in the AI system prompt.
    Formats it in a way that's easy for the LLM to use.
    """
    if not cv_text:
        return ""
    
    return f"""
## CANDIDATE'S RESUME/CV:
The following is the content extracted from the candidate's uploaded CV. Use this to personalize your questions.
Ask about specific projects, technologies, companies, or experiences mentioned here.

---
{cv_text}
---
"""
