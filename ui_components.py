"""
Streamlit UI Component for research Tool
"""

import streamlit as st
from typing import List, Dict, Any, Optional
from config import Config
from utils import truncate_text


class UIComponents:

    @staticmethod
    def setup_page_config():
        st.set_page_config(
            page_title = Config.streamlit.page_title,
            page_icon = Config.streamlit.page_icon,
            layout = Config.streamlit.layout
            )

    @staticmethod
    def render_header():
        st.title("Research Tool ")
        st.markdown("---")
        st.markdown(
            """
            **Welcome to the Research Tool**

            This Tool Allows you to:
            -> :Book: Process Multiple Web URLs
            -> Create Intelligent Embeddings
            -> Ask Questions about the Content
            -> Get Answers with source attribution

            """
        )
        st.markdown("---")


    @staticmethod
    def render_sidebar():
        with st.sidebar:
            st.header("Configuration")
            api_key = UIComponents._render_api_key_section()
            st.markdown("---")

            chunk_size, chunk_overlap = UIComponents._render_chunking_section()
            st.markdown("---")

            search_k = UIComponents._render_retrieval_section()
            st.markdown("---")

            UIComponents._render_help_section()

            return api_key,chunk_overlap,chunk_size,search_k
        
        @staticmethod
        def _render_api_key_section():
            
            st.subheader("API Configuration")

            api_key = st.text_input(
                "GEMINI_API_KEY",
                type="password",
                help="Get your API key from Google AI Studio: https://makersuite.google.com/app/apikey",
                placeholder="Enter your Google API key here..."
            )

            if api_key:
                st.success("✅ API Key provided")
            else:
                st.warning("⚠️ API Key required")
                st.info("👆 Please enter your Google API Key to continue")
        
            return api_key
        
        @staticmethod

        def _render_chunking_section():
            """Render chunking parameters section"""
            st.subheader("📝 Text Chunking")
        
            chunk_size = st.slider(
            "Chunk Size",
            min_value=500,
            max_value=2000,
            value=Config.chunking.chunk_size,
            step=100,
            help="Size of each text chunk in characters"
            )
            
            chunk_overlap = st.slider(
            "Chunk Overlap",
            min_value=50,
            max_value=500,
            value=Config.chunking.chunk_overlap,
            step=50,
            help="Overlap between consecutive chunks"
            )

            return chunk_size, chunk_overlap
        

    @staticmethod
    def _render_retrieval_section():
        """Render retrieval settings section"""
        st.subheader("🔍 Retrieval Settings")
        
        search_k = st.slider(
            "Documents to Retrieve",
            min_value=1,
            max_value=10,
            value=config.retrieval.search_k,
            help="Number of relevant documents to retrieve for each query"
        )
        
        return search_k
    
    @staticmethod
    def _render_help_section():
        """Render help and information section"""
        with st.expander("ℹ️ Help & Tips"):
            st.markdown("""
            **Getting Started:**
            1. Enter your Google API key above
            2. Add URLs in the main area
            3. Process the URLs to create vector database
            4. Ask questions about the content
            
            **Tips:**
            - Use publicly accessible URLs
            - Larger chunk sizes = fewer chunks but more context
            - Higher retrieval K = more comprehensive answers
            - Financial sites may have rate limiting
            
            **Troubleshooting:**
            - If processing fails, try fewer URLs
            - Check if URLs are accessible
            - Verify your API key is correct
            """)
    
    @staticmethod
    def render_url_input_section():
        """Render URL input and processing section"""
        st.subheader("📝 URL Processing")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            urls_input = st.text_area(
                "Enter URLs (one per line):",
                height=200,
                placeholder="https://example1.com\nhttps://example2.com\nhttps://example3.com",
                help="Enter each URL on a separate line"
            )
        
        with col2:
            st.markdown("**Example URLs:**")
            example_urls = [
                "https://en.wikipedia.org/wiki/Stock_market",
                "https://www.investopedia.com/investing-4427685",
                "https://finance.yahoo.com/news/"
            ]
            
            for url in example_urls:
                st.code(url, language=None)
        
        process_button = st.button(
            "🔄 Process URLs",
            type="primary",
            help="Load and process content from the provided URLs"
        )
        
        return urls_input, process_button
    
    @staticmethod
    def render_processing_status(processed_urls: List[str]):
        """Render processing status information"""
        if processed_urls:
            with st.expander("✅ Processed URLs", expanded=False):
                for i, url in enumerate(processed_urls, 1):
                    st.write(f"**{i}.** {url}")
                
                st.success(f"Successfully processed {len(processed_urls)} URLs")
        else:
            st.info("No URLs processed yet. Please add URLs and click 'Process URLs'.")
    
    @staticmethod
    def render_query_section():
        """Render query input section"""
        st.subheader("❓ Ask Questions")
        
        # Query input
        query = st.text_area(
            "Enter your question:",
            height=120,
            placeholder="What information can you provide about the content from these websites?",
            help="Ask specific questions about the processed content"
        )
        
        # Example questions
        with st.expander("💡 Example Questions"):
            example_questions = [
                "What are the main risks of stock market investing?",
                "How do I evaluate a stock before buying?",
                "What are the current market trends mentioned?",
                "Summarize the key points from these sources"
            ]
            
            for question in example_questions:
                if st.button(f"📝 {question}", key=f"example_{hash(question)}"):
                    st.session_state.example_query = question
        
        # Use example query if selected
        if hasattr(st.session_state, 'example_query'):
            query = st.session_state.example_query
            del st.session_state.example_query
        
        ask_button = st.button(
            "🚀 Get Answer",
            type="primary",
            help="Generate answer based on processed content"
        )
        
        return query, ask_button
    
    @staticmethod
    def render_answer_section(response: Dict[str, Any]):
        """Render the answer and sources section"""
        if not response:
            return
        
        # Main answer
        st.subheader("📄 Answer")
        st.write(response.get('answer', 'No answer available'))
        
        # Sources section
        if response.get('formatted_sources'):
            st.subheader("📚 Sources")
            st.markdown(response['formatted_sources'])
        
        # Source documents in expandable section
        source_docs = response.get('source_documents', [])
        if source_docs:
            with st.expander(f"📖 Source Documents ({len(source_docs)} documents)"):
                for i, doc in enumerate(source_docs, 1):
                    st.markdown(f"**Document {i}:**")
                    
                    # Show truncated content
                    content = truncate_text(doc.page_content, 300)
                    st.write(content)
                    
                    # Show source if available
                    if hasattr(doc, 'metadata') and doc.metadata.get('source'):
                        st.caption(f"🔗 Source: {doc.metadata['source']}")
                    
                    if i < len(source_docs):
                        st.markdown("---")
    
    @staticmethod
    def render_system_status():
        """Render system status information"""
        with st.expander("🔧 System Status"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Vector Store",
                    "Active" if st.session_state.get('vector_store') else "Inactive"
                )
            
            with col2:
                st.metric(
                    "QA Chain",
                    "Ready" if st.session_state.get('qa_chain') else "Not Ready"
                )
            
            with col3:
                urls_count = len(st.session_state.get('processed_urls', []))
                st.metric("Processed URLs", urls_count)
    
    @staticmethod
    def render_footer():
        """Render footer information"""
        st.markdown("---")
        st.markdown(
            """
            <div style='text-align: center; color: gray;'>
                <p>🔍 Research Tool powered by:</p>
                <p>🤖 Gemini AI • 🦜 LangChain • 🔍 FAISS • 🎈 Streamlit</p>
                <p><small>Built for intelligent document processing and Q&A</small></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    @staticmethod
    def show_loading_state(message: str):
        """Show loading state with spinner"""
        return st.spinner(message)
    
    @staticmethod
    def show_error_alert(message: str, details: str = None):
        """Show error alert with optional details"""
        st.error(message)
        if details:
            with st.expander("Error Details"):
                st.code(details)
    
    @staticmethod
    def show_success_alert(message: str, details: str = None):
        """Show success alert with optional details"""
        st.success(message)
        if details:
            st.info(details)
    
    @staticmethod
    def show_info_alert(message: str):
        """Show info alert"""
        st.info(message)
    
    @staticmethod
    def show_warning_alert(message: str):
        """Show warning alert"""
        st.warning(message)