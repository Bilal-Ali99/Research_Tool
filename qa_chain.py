"""
Question answering chain module using RetrievalQAWithSourcesChain
"""

import streamlit as st
from langchain_google_genai import GoogleGenerativeAI
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional

from config import config
from utils import show_error_message, show_success_message, format_sources
from vector_store import VectorStoreManager

class QAChainManager:
    """Manages question answering operations using retrieval-based chains"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize QAChainManager
        
        Args:
            api_key (str): Google API key for LLM
        """
        self.api_key = api_key or config.get_api_key()
        self.llm = None
        self.qa_chain = None
        self.vector_store_manager = None
        
        if self.api_key:
            self._initialize_llm()
    
    def _initialize_llm(self) -> bool:
        """
        Initialize Google Generative AI LLM
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.llm = GoogleGenerativeAI(
                model=config.llm.model_name,
                google_api_key=self.api_key,
                temperature=config.llm.temperature
            )
            return True
        except Exception as e:
            show_error_message(e, "LLM Initialization")
            return False
    
    def setup_qa_chain(self, vector_store_manager: VectorStoreManager) -> bool:
        """
        Setup the RetrievalQAWithSourcesChain
        
        Args:
            vector_store_manager (VectorStoreManager): Vector store manager instance
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.llm:
                if not self._initialize_llm():
                    return False
            
            if not vector_store_manager or not vector_store_manager.vector_store:
                show_error_message(ValueError("No vector store available"), "QA Chain Setup")
                return False
            
            # Get retriever from vector store
            retriever = vector_store_manager.get_retriever()
            if not retriever:
                return False
            
            # Create QA chain
            self.qa_chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=self.llm,
                chain_type=config.retrieval.chain_type,
                retriever=retriever,
                return_source_documents=True
            )
            
            self.vector_store_manager = vector_store_manager
            
            show_success_message("QA Chain setup completed successfully!")
            return True
            
        except Exception as e:
            show_error_message(e, "QA Chain Setup")
            return False
    
    def ask_question(self, question: str) -> Optional[Dict[str, Any]]:
        """
        Ask a question and get answer with sources
        
        Args:
            question (str): Question to ask
            
        Returns:
            Optional[Dict[str, Any]]: Response with answer and sources
        """
        try:
            if not self.qa_chain:
                show_error_message(ValueError("QA Chain not initialized"), "Question Answering")
                return None
            
            if not question.strip():
                show_error_message(ValueError("Question cannot be empty"), "Question Answering")
                return None
            
            with st.spinner("Searching knowledge base and generating answer..."):
                response = self.qa_chain({"question": question})
            
            # Process and format the response
            processed_response = self._process_response(response)
            
            return processed_response
            
        except Exception as e:
            show_error_message(e, "Question Answering")
            return None
    
    def _process_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and format the chain response
        
        Args:
            response (Dict[str, Any]): Raw response from chain
            
        Returns:
            Dict[str, Any]: Processed response
        """
        processed = {
            'answer': response.get('answer', 'No answer found'),
            'sources': response.get('sources', ''),
            'source_documents': response.get('source_documents', []),
            'question': response.get('question', '')
        }
        
        # Format sources for better display
        if processed['sources']:
            processed['formatted_sources'] = format_sources(processed['sources'])
        else:
            processed['formatted_sources'] = "No sources available"
        
        # Add document count info
        processed['num_source_docs'] = len(processed['source_documents'])
        
        return processed
    
    def get_similar_documents(self, question: str, k: int = None) -> list:
        """
        Get documents similar to the question without generating answer
        
        Args:
            question (str): Question/query
            k (int): Number of documents to retrieve
            
        Returns:
            list: Similar documents
        """
        try:
            if not self.vector_store_manager:
                show_error_message(ValueError("Vector store manager not available"), "Document Retrieval")
                return []
            
            return self.vector_store_manager.similarity_search(question, k=k)
            
        except Exception as e:
            show_error_message(e, "Document Retrieval")
            return []
    
    def create_custom_prompt(self, template: str) -> bool:
        """
        Create custom prompt template for the QA chain
        
        Args:
            template (str): Custom prompt template
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            prompt = PromptTemplate(
                template=template,
                input_variables=["summaries", "question"]
            )
            
            # Update the chain with custom prompt
            if self.qa_chain:
                self.qa_chain.combine_docs_chain.llm_chain.prompt = prompt
                show_success_message("Custom prompt applied successfully!")
                return True
            else:
                show_error_message(ValueError("QA Chain not initialized"), "Custom Prompt")
                return False
                
        except Exception as e:
            show_error_message(e, "Custom Prompt Creation")
            return False
    
    def get_chain_info(self) -> Dict[str, Any]:
        """
        Get information about the current QA chain
        
        Returns:
            Dict[str, Any]: Chain information
        """
        if not self.qa_chain:
            return {"status": "QA Chain not initialized"}
        
        info = {
            "status": "Active",
            "llm_model": config.llm.model_name,
            "chain_type": config.retrieval.chain_type,
            "temperature": config.llm.temperature,
            "retrieval_k": config.retrieval.search_k
        }
        
        if self.vector_store_manager:
            vector_info = self.vector_store_manager.get_store_info()
            info.update({"vector_store": vector_info})
        
        return info
    
    def update_retrieval_settings(self, search_k: int) -> bool:
        """
        Update retrieval settings
        
        Args:
            search_k (int): Number of documents to retrieve
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Update config first
            config.retrieval.search_k = search_k
            
            # Only update the chain if both vector store manager and qa_chain exist
            if self.vector_store_manager and self.vector_store_manager.vector_store and self.qa_chain:
                # Create new retriever with updated settings
                retriever = self.vector_store_manager.get_retriever({"k": search_k})
                if retriever:
                    self.qa_chain.retriever = retriever
                    show_success_message(f"Updated retrieval settings - K: {search_k}")
                    return True
                else:
                    show_error_message(ValueError("Failed to create retriever"), "Update Settings")
                    return False
            else:
                # Just update the config if chain isn't ready yet
                st.info(f"Retrieval settings updated - K: {search_k} (will apply when QA chain is ready)")
                return True
                
        except Exception as e:
            show_error_message(e, "Update Retrieval Settings")
            return False

def create_qa_chain_manager(api_key: str = None) -> QAChainManager:
    """
    Factory function to create QAChainManager instance
    
    Args:
        api_key (str): Google API key
        
    Returns:
        QAChainManager: Configured manager instance
    """
    return QAChainManager(api_key=api_key)