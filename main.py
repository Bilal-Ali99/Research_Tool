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
from ui_components  import UIComponents
from config import Config

class ReasearchToolApp:
    """Main Class for the reaseach tool"""

    def __init__(self):
        self.initialize_session_state()
        UIComponents.setup_page_config()


    def initialize_session_state(self):
        """Initializing Streamlit session"""
        session_default = {
            'vector_store':None,
            'qa_chain':None,
            'processed_urls':[],
            'document_processor':None,
            'vector_store_manager':None,
            'qa_chain_manager':None,
            'api_key_configured':False
        }

        for key, default_value in session_default.items():
            if key not in st.session_state:
                st.session_state[key] = default_value

    def setup_managers(self, api_key:str,chunk_size:int,chunk_overlap:int):
        
        try:
            if setup_gemini_api(api_key):
                Config.set_api_key(api_key)
                st.session_state.api_key_configured = True

            else:
                st.session_state.api_key_configured = False
                return False
            
            st.session_state.document_processor = create_document_processor(
                chunk_size = chunk_size,
                chunk_overlap = chunk_overlap
            )
            
            st.session_state.vector_store_manager = create_vector_store_manager(
                api_key = api_key
            )


            st.session_state.qa_chain_manager = create_qa_chain_manager(
                api_key = api_key
            )

            return True
    
        except Exception as e:
            show_error_message(e,"Manager Setup")
            return False
        
    def process_urls(self,urls: List[str]) -> bool:
        try:
            if not st.session_state.document_processor:
                show_error_message(ValueError("Document processor not initialized"),"URL Processing")
                return False
            
            chunks = st.session_state.document_processor.process_url(urls)
            if not chunks:
                return False
            
            vector_store = st.session_state.vector_store_manager.create_vector_store(chunks)
            if not vector_store:
                return False
            
            if not st.session_state.qa_chain_manager.setup_qa_chain(st.session_state.vector_store_manager):
                return False
            

            st.session_state.vector_store = vector_store
            st.session_state.qa_chain = st.session_state.qa_chain_manager.qa_chain
            st.session_state.processed_urls = urls


            show_success_message(
                "Processing Completed Successfully!",
                f"Ready to answer question about content from {len(urls)} URLs"
            )
            return True
        

        except Exception as e:
            show_error_message(e,"URL Processing Pipeline")
            return False
        
    def handle_query(self, query: str):
        try:
            if not st.session_state.qa_chain_manager:
                show_error_message(ValueError("QA Chain not ready"), "Query Processing")
                return
            
            respone = st.session_state.qa_chain_manager.ask_question(query)

            if respone:
                UIComponents.render_answer_selection(respone)

            else:
                st.error("Failed to get answer. Please Try Again")

        except Exception as e:
            show_error_message(e,"Query Processing")

    def run(self):
        UIComponents.render_header()

        api_key, chunk_size, chunk_overlap, search_k = UIComponents.render_sidebar()

        if not api_key:
            st.warning("Please Enter the API_KEY Correctly in the Sidebar")
            UIComponents.render_footage()
            return
        
        if not st.session_state.api_key_configured or api_key != Config.get_api_key():
            with st.spinner("Setting up API and Initializing components..."):
                if not self.setup_managers(api_key,chunk_size, chunk_overlap):
                    st.error("Failed to setup you api key. Please check you API-KEY")
                    UIComponents.render_footer()
                    return
                


        if st.session_state.document_processor:
            st.session_state.document_processor.update_chunk_settings(chunk_size,chunk_overlap)

        if st.session_state.qa_chain_manager:
            st.session_state.qa_chain_manager.manager_update_retrival(search_k)


        col1 , col2 = st.columns([1,1])

        with col1:
            urls_input, process_button = UIComponents.render_url_input_section()

            if process_button:
                if urls_input.strip():

                    urls = parse_urls_from_input(urls_input)
                    valid_urls,invalid_urls = validate_urls(urls)

                    if invalid_urls:
                        st.error(f"Invalid URLs found: {','.join(invalid_urls)}")

                    if valid_urls:
                        st.info(f"Processing {len(valid_urls)} valid URLs..")

                    else:
                        st.error("No Valid URLs to Process")
                else:
                    st.error("Please enter at least one URL.")


            UIComponents.render_processing_status(st.session_state.processed_urls)
        
        with col2:
            if st.session_state.qa_chain:
                query, ask_button = UIComponents.render_query_section()

                if ask_button and query.strip():
                    self.handle_query(query.strip())
                elif ask_button:
                    st.error("Please enter a question")
            else:
                st.info("Please Process The URLs First to enable Querying")

                st.markdown("What you can do:")
                st.markdown("""
                1) Analyze Financial Data from Multiple Resources
                2) Compare Market Trends across different website
                3) Extract specific information with intelligent search
                4) Get Sourced Answer with proper attribution
                5) Ask complex question Spanning Multiple Documents

                """)

                    
        UIComponents.render_system_status()
        UIComponents.render_footer()

def main():

    try:
        app = ReasearchToolApp()
        app.run()
    except Exception as e:
        st.error(f"Application Error: {str(e)}")
        st.info("Please refresh the page and try again")

if __name__ == "__main__":
    main()