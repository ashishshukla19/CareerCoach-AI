"""
Company Docs Page - Document Upload and Management for RAG.
Allows users to upload company research for tailored interview questions.
"""
import streamlit as st
from typing import List
from app.core.logger import logger

# Lazy import RAG service
_rag_service = None


def get_rag_service():
    """Get or create RAG service instance."""
    global _rag_service
    if _rag_service is None:
        from app.services.rag_service import RAGService
        _rag_service = RAGService()
    return _rag_service


def render_company_docs_page():
    """Render the company documents upload and management page."""
    
    # Premium CSS for better aesthetics
    st.markdown("""
    <style>
    .docs-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 10px;
    }
    .docs-subtitle {
        text-align: center;
        color: #a0aec0;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    .stats-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        backdrop-filter: blur(10px);
    }
    .stats-value {
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    .stats-label {
        color: #718096;
        font-size: 0.9rem;
    }
    .doc-card {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #667eea;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="docs-header">📚 Company Research</h1>', unsafe_allow_html=True)
    st.markdown('<p class="docs-subtitle">Upload company documents to tailor your interview questions</p>', unsafe_allow_html=True)
    
    rag_service = get_rag_service()
    
    # Stats row
    col1, col2, col3 = st.columns(3)
    doc_count = rag_service.get_document_count()
    has_docs = rag_service.has_documents()
    
    with col1:
        st.markdown(f'<div class="stats-card"><div class="stats-value">{doc_count}</div><div class="stats-label">Document Chunks</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stats-card"><div class="stats-value">{"✅" if has_docs else "❌"}</div><div class="stats-label">RAG Active</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stats-card"><div class="stats-value">🧠</div><div class="stats-label">Vector Knowledge</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Upload section
    with st.container():
        st.header("📤 Add Knowledge")
        
        # Initialize processed files tracker
        if "processed_files" not in st.session_state:
            st.session_state.processed_files = set()
        
        uploaded_files = st.file_uploader(
            "Upload Job Descriptions, Culture Pages, or Research (PDF, DOCX, TXT)",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="rag_uploader"
        )
        
        if uploaded_files:
            total_added = 0
            new_files = []
            
            for uploaded_file in uploaded_files:
                # Create unique file ID based on name and size
                file_id = f"{uploaded_file.name}_{uploaded_file.size}"
                
                # Skip if already processed
                if file_id in st.session_state.processed_files:
                    continue
                
                new_files.append((uploaded_file, file_id))
            
            # Process only new files
            for uploaded_file, file_id in new_files:
                with st.spinner(f"Analyzing {uploaded_file.name}..."):
                    file_bytes = uploaded_file.read()
                    added = rag_service.add_document(file_bytes, uploaded_file.name)
                    total_added += added
                    st.session_state.processed_files.add(file_id)
            
            if total_added > 0:
                st.success(f"Successfully added {total_added} information nodes to the knowledge base!")

    # Management section
    if has_docs:
        st.header("🔍 Current Knowledge Pool")
        summary = rag_service.get_company_summary()
        st.info(summary)
        
        if st.button("🗑️ Clear All Research", type="secondary"):
            rag_service.clear_documents()
            st.warning("All company research cleared.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Menu", use_container_width=True):
        st.session_state.show_company_docs = False
        st.rerun()
