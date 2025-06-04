import streamlit as st
from typing import List
from utils import (
    setup_gemini_api,
    parse_urls_from_input,
    validate_urls,
    show_message_error,
    show_success_message
)

from document_processor import create_document_processor
from vector_store import create_vector_store_manager
from qa_chain import create_qa_chain_manager
from ui_components  import UIComponent


class ReasearchToolApp:
    """Main Class for the reaseach tool"""

    def __init__(self):
        self.initialize_session state()
        UIComponent.setup_page_config()


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