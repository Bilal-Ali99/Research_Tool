import streamlit as st
from typing import List
from utils import (
    setup_gemini_api,
    parse_urls_from_input,
    validate_urls,
    show_error_message,
    show_success_message
)

from document_processor import create_document_processor
from vector_store import create_vector_store_manager
from qa_chain import create_qa_chain_manager
from ui_components import UIComponents
from config import config

class ResearchToolApp:
    """Main Class for the research tool"""

    def __init__(self):
        self.initialize_session_state()
        UIComponents.setup_page_config()

    def initialize_session_state(self):
        """Initializing Streamlit session"""
        session_default = {
            'vector_store': None,
            'qa_chain': None,
            'processed_urls': [],
            'document_processor': None,
            'vector_store_manager': None,
            'qa_chain_manager': None,
            'api_key_configured': False,
            'current_api_key': None
        }

        for key, default_value in session_default.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    def setup_managers(self, api_key: str, chunk_size: int, chunk_overlap: int):
        """Setup all managers with proper error handling and state management"""
        try:
            # Check if API key has changed
            if (st.session_state.current_api_key != api_key or 
                not st.session_state.api_key_configured):
                
                # Setup API
                if not setup_gemini_api(api_key):
                    st.session_state.api_key_configured = False
                    st.session_state.current_api_key = None
                    return False
                
                config.set_api_key(api_key)
                st.session_state.api_key_configured = True
                st.session_state.current_api_key = api_key
                
                # Reset all managers when API key changes
                st.session_state.vector_store = None
                st.session_state.qa_chain = None
                st.session_state.processed_urls = []
            
            # Initialize document processor
            if not st.session_state.document_processor:
                st.session_state.document_processor = create_document_processor(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            
            # Initialize vector store manager
            if not st.session_state.vector_store_manager:
                st.session_state.vector_store_manager = create_vector_store_manager(
                    api_key=api_key
                )

            # Initialize QA chain manager
            if not st.session_state.qa_chain_manager:
                st.session_state.qa_chain_manager = create_qa_chain_manager(
                    api_key=api_key
                )

            return True
    
        except Exception as e:
            show_error_message(e, "Manager Setup")
            st.session_state.api_key_configured = False
            st.session_state.current_api_key = None
            return False
        
    def process_urls(self, urls: List[str]) -> bool:
        """Process URLs and setup QA chain"""
        try:
            if not st.session_state.document_processor:
                show_error_message(ValueError("Document processor not initialized"), "URL Processing")
                return False
            
            # Process documents
            chunks = st.session_state.document_processor.process_urls(urls)
            if not chunks:
                return False
            
            # Create vector store
            if not st.session_state.vector_store_manager:
                show_error_message(ValueError("Vector store manager not initialized"), "URL Processing")
                return False
                
            vector_store = st.session_state.vector_store_manager.create_vector_store(chunks)
            if not vector_store:
                return False
            
            # Setup QA chain
            if not st.session_state.qa_chain_manager:
                show_error_message(ValueError("QA chain manager not initialized"), "URL Processing")
                return False
                
            if not st.session_state.qa_chain_manager.setup_qa_chain(st.session_state.vector_store_manager):
                return False
            
            # Update session state
            st.session_state.vector_store = vector_store
            st.session_state.qa_chain = st.session_state.qa_chain_manager.qa_chain
            st.session_state.processed_urls = urls

            show_success_message(
                "Processing Completed Successfully!",
                f"Ready to answer questions about content from {len(urls)} URLs"
            )
            return True
        
        except Exception as e:
            show_error_message(e, "URL Processing Pipeline")
            return False
        
    def handle_query(self, query: str):
        """Handle user queries with proper error checking"""
        try:
            if not st.session_state.qa_chain_manager:
                show_error_message(ValueError("QA Chain not ready"), "Query Processing")
                return
            
            if not st.session_state.qa_chain:
                show_error_message(ValueError("QA Chain not initialized - please process URLs first"), "Query Processing")
                return
            
            response = st.session_state.qa_chain_manager.ask_question(query)

            if response:
                UIComponents.render_answer_section(response)
            else:
                st.error("Failed to get answer. Please try again.")

        except Exception as e:
            show_error_message(e, "Query Processing")

    def run(self):
        """Main application runner"""
        UIComponents.render_header()

        api_key, chunk_size, chunk_overlap, search_k = UIComponents.render_sidebar()

        if not api_key:
            st.warning("Please Enter the API Key in the Sidebar to get started")
            UIComponents.render_footer()
            return
        
        # Setup managers with proper state handling
        with st.spinner("Initializing components..."):
            if not self.setup_managers(api_key, chunk_size, chunk_overlap):
                st.error("Failed to setup API key and components. Please check your API key.")
                UIComponents.render_footer()
                return

        # Update component settings
        if st.session_state.document_processor:
            st.session_state.document_processor.update_chunk_settings(chunk_size, chunk_overlap)

        if st.session_state.qa_chain_manager:
            st.session_state.qa_chain_manager.update_retrieval_settings(search_k)

        # Main interface
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("📝 URL Processing")
            urls_input, process_button = UIComponents.render_url_input_section()

            if process_button:
                if urls_input.strip():
                    urls = parse_urls_from_input(urls_input)
                    valid_urls, invalid_urls = validate_urls(urls)

                    if invalid_urls:
                        st.error(f"Invalid URLs found: {', '.join(invalid_urls)}")

                    if valid_urls:
                        st.info(f"Processing {len(valid_urls)} valid URLs...")
                        success = self.process_urls(valid_urls)
                        if success:
                            st.rerun()  # Refresh to show updated state
                    else:
                        st.error("No valid URLs to process")
                else:
                    st.error("Please enter at least one URL.")

            UIComponents.render_processing_status(st.session_state.processed_urls)
        
        with col2:
            st.subheader("❓ Ask Questions")
            if st.session_state.qa_chain and st.session_state.processed_urls:
                query, ask_button = UIComponents.render_query_section()

                if ask_button and query.strip():
                    self.handle_query(query.strip())
                elif ask_button:
                    st.error("Please enter a question")
            else:
                st.info("Please process URLs first to enable querying")

                st.markdown("**What you can do after processing URLs:**")
                st.markdown("""
                - 📊 Analyze content from multiple resources
                - 🔍 Compare information across different websites
                - 💡 Extract specific information with intelligent search
                - 📝 Get sourced answers with proper attribution
                - ❓ Ask complex questions spanning multiple documents
                """)

        UIComponents.render_system_status()
        UIComponents.render_footer()

def main():
    """Main entry point with error handling"""
    try:
        app = ResearchToolApp()
        app.run()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page and try again.")
        if st.button("🔄 Refresh Page"):
            st.rerun()

if __name__ == "__main__":
    main()