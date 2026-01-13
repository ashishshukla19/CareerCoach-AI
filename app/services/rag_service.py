"""
RAG Service - Fully Offline Retrieval-Augmented Generation.
Uses TF-IDF for similarity search - NO API calls required.
"""
import os
import json
import hashlib
import re
from typing import List, Dict, Set
from dataclasses import dataclass, asdict
from collections import Counter
import math

from app.core.logger import logger

# Storage directory and file (persistent across restarts)
STORAGE_DIR = "rag_data"
STORAGE_FILE = os.path.join(STORAGE_DIR, "company_knowledge.json")

# Ensure storage directory exists
os.makedirs(STORAGE_DIR, exist_ok=True)


@dataclass
class DocumentChunk:
    """A chunk of text from a document."""
    content: str
    source: str
    chunk_id: str
    keywords: List[str] = None

class RAGService:
    """
    Fully offline RAG service using TF-IDF for similarity.
    NO external API calls required - works 100% locally.
    """
    
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    
    # Common stop words to filter out
    STOP_WORDS = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                  'should', 'may', 'might', 'must', 'shall', 'can', 'need', 'dare',
                  'ought', 'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by',
                  'from', 'as', 'into', 'through', 'during', 'before', 'after',
                  'above', 'below', 'between', 'under', 'again', 'further', 'then',
                  'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                  'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
                  'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                  'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while',
                  'this', 'that', 'these', 'those', 'am', 'it', 'its', 'we', 'you',
                  'your', 'they', 'their', 'what', 'which', 'who', 'whom'}
    
    def __init__(self):
        self._chunks: List[DocumentChunk] = []
        self._idf_scores: Dict[str, float] = {}
        self._load_storage()
        self._compute_idf()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into clean words."""
        # Convert to lowercase and extract words
        words = re.findall(r'\b[a-z]{2,}\b', text.lower())
        # Filter stop words
        return [w for w in words if w not in self.STOP_WORDS]
    
    def _compute_idf(self):
        """Compute IDF scores across all documents."""
        if not self._chunks:
            return
        
        doc_count = len(self._chunks)
        word_doc_count: Dict[str, int] = Counter()
        
        for chunk in self._chunks:
            unique_words = set(self._tokenize(chunk.content))
            for word in unique_words:
                word_doc_count[word] += 1
        
        self._idf_scores = {
            word: math.log(doc_count / count)
            for word, count in word_doc_count.items()
        }
    
    def _get_tfidf_vector(self, text: str) -> Dict[str, float]:
        """Get TF-IDF vector for a text."""
        words = self._tokenize(text)
        tf = Counter(words)
        total = len(words) if words else 1
        
        return {
            word: (count / total) * self._idf_scores.get(word, 1.0)
            for word, count in tf.items()
        }
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between two TF-IDF vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        common_words = set(vec1.keys()) & set(vec2.keys())
        if not common_words:
            return 0.0
        
        dot = sum(vec1[w] * vec2[w] for w in common_words)
        norm1 = math.sqrt(sum(v * v for v in vec1.values()))
        norm2 = math.sqrt(sum(v * v for v in vec2.values()))
        
        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0
    
    def _load_storage(self):
        """Load existing chunks from JSON file."""
        if os.path.exists(STORAGE_FILE):
            try:
                with open(STORAGE_FILE, 'r') as f:
                    data = json.load(f)
                    self._chunks = [DocumentChunk(**c) for c in data]
                logger.info(f"Loaded {len(self._chunks)} chunks from storage")
            except Exception as e:
                logger.error(f"Failed to load storage: {e}")
                self._chunks = []
    
    def _save_storage(self):
        """Save chunks to JSON file."""
        try:
            with open(STORAGE_FILE, 'w') as f:
                json.dump([asdict(c) for c in self._chunks], f)
        except Exception as e:
            logger.error(f"Failed to save storage: {e}")
    
    def _chunk_text(self, text: str, source: str) -> List[DocumentChunk]:
        """Split text into overlapping chunks."""
        chunks = []
        text = text.strip()
        
        if len(text) < self.CHUNK_SIZE:
            chunk_id = hashlib.md5(f"{source}_0".encode()).hexdigest()[:12]
            keywords = self._tokenize(text)[:20]  # Top 20 keywords
            chunks.append(DocumentChunk(content=text, source=source, chunk_id=chunk_id, keywords=keywords))
        else:
            start = 0
            idx = 0
            while start < len(text):
                end = min(start + self.CHUNK_SIZE, len(text))
                if end < len(text):
                    for sep in ['. ', '\n', ' ']:
                        pos = text.rfind(sep, start, end)
                        if pos > start + self.CHUNK_SIZE // 2:
                            end = pos + 1
                            break
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunk_id = hashlib.md5(f"{source}_{idx}".encode()).hexdigest()[:12]
                    keywords = self._tokenize(chunk_text)[:20]
                    chunks.append(DocumentChunk(content=chunk_text, source=source, chunk_id=chunk_id, keywords=keywords))
                    idx += 1
                
                start = end - self.CHUNK_OVERLAP if end - self.CHUNK_OVERLAP > start else end
        
        return chunks
    
    def _parse_document(self, file_bytes: bytes, filename: str) -> str:
        """Parse document to text."""
        filename_lower = filename.lower()
        try:
            if filename_lower.endswith('.pdf'):
                import io
                from PyPDF2 import PdfReader
                reader = PdfReader(io.BytesIO(file_bytes))
                return "\n\n".join([p.extract_text() or "" for p in reader.pages])
            elif filename_lower.endswith('.docx'):
                import io
                from docx import Document
                doc = Document(io.BytesIO(file_bytes))
                return "\n\n".join([p.text for p in doc.paragraphs if p.text.strip()])
            elif filename_lower.endswith('.txt'):
                return file_bytes.decode('utf-8', errors='ignore')
        except Exception as e:
            logger.error(f"Parse error for {filename}: {e}")
        return ""
    
    def add_document(self, file_bytes: bytes, filename: str) -> int:
        """Parse, chunk and store a document - NO API calls!"""
        text = self._parse_document(file_bytes, filename)
        if not text:
            return 0
        
        chunks = self._chunk_text(text, filename)
        self._chunks.extend(chunks)
        self._compute_idf()  # Recompute IDF with new docs
        self._save_storage()
        
        logger.info(f"Added {len(chunks)} chunks from {filename}")
        return len(chunks)
    
    def query_context(self, query: str, k: int = 3) -> List[Dict]:
        """Find most relevant chunks using TF-IDF similarity."""
        if not self._chunks:
            return []
        
        query_vec = self._get_tfidf_vector(query)
        if not query_vec:
            return []
        
        scored = []
        for chunk in self._chunks:
            chunk_vec = self._get_tfidf_vector(chunk.content)
            score = self._cosine_similarity(query_vec, chunk_vec)
            if score > 0:
                scored.append((chunk, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return [
            {'content': c.content, 'source': c.source, 'score': s}
            for c, s in scored[:k]
        ]
    
    def get_context_for_prompt(self, topic: str) -> str:
        """Get formatted context for AI prompt injection."""
        if not self._chunks:
            return ""
        
        results = self.query_context(topic, k=3)
        if not results:
            return ""
        
        parts = ["## Company Research Context:"]
        for i, r in enumerate(results, 1):
            content = r['content'][:250] + "..." if len(r['content']) > 250 else r['content']
            parts.append(f"{i}. {content}")
        
        return "\n".join(parts)
    
    def get_company_summary(self) -> str:
        """Get summary of loaded documents."""
        if not self._chunks:
            return "No documents loaded."
        
        sources = set(c.source for c in self._chunks)
        return f"Loaded {len(self._chunks)} knowledge nodes from: {', '.join(sources)}"
    
    def clear_documents(self):
        """Clear all stored documents."""
        self._chunks = []
        self._idf_scores = {}
        if os.path.exists(STORAGE_FILE):
            os.remove(STORAGE_FILE)
        logger.info("Cleared all documents")
    
    def get_document_count(self) -> int:
        return len(self._chunks)
    
    def has_documents(self) -> bool:
        return len(self._chunks) > 0
