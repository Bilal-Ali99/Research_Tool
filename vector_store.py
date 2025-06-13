"""
Vector store management module for embeddings and similarity search
"""

import streamlit as st

from langchain.vectorstores import FAISS
from langchain.schema import Document
from typing import List, Optional, Tuple
import os

from config import config
from utils import show_error_message, show_success_message

class VectorStoreManager:
    """Manages vector store operations including embeddings and similarity search"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize VectorStoreManager
        
        Args:
            api_key (str): Google API key for embeddings
        """
        self.api_key = api_key or config.get_api_key()
        self.embeddings = None
        self.vector_store = None
        
        if self.api_key:
            self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> bool:
        """
        Initialize Google Generative AI embeddings
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=config.embedding.model_name,
                google_api_key=self.api_key
            )
            return True
        except Exception as e:
            show_error_message(e, "Embeddings Initialization")
            return False
    
    def create_vector_store(self, documents: List[Document]) -> Optional[FAISS]:
        """
        Create FAISS vector store from documents
        
        Args:
            documents (List[Document]): Documents to vectorize
            
        Returns:
            Optional[FAISS]: Vector store or None if failed
        """
        try:
            if not documents:
                show_error_message(ValueError("No documents provided"), "Vector Store Creation")
                return None
            
            if not self.embeddings:
                if not self._initialize_embeddings():
                    return None
            
            with st.spinner("Creating embeddings and building vector store..."):
                # Create vector store from documents
                vector_store = FAISS.from_documents(documents, self.embeddings)
            
            self.vector_store = vector_store
            
            show_success_message(
                "Vector store created successfully!",
                f"Indexed {len(documents)} document chunks"
            )
            
            return vector_store
            
        except Exception as e:
            show_error_message(e, "Vector Store Creation")
            return None
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Add more documents to existing vector store
        
        Args:
            documents (List[Document]): Documents to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.vector_store:
                show_error_message(ValueError("No vector store exists"), "Adding Documents")
                return False
            
            if not documents:
                show_error_message(ValueError("No documents provided"), "Adding Documents")
                return False
            
            with st.spinner("Adding new documents to vector store..."):
                self.vector_store.add_documents(documents)
            
            show_success_message(f"Added {len(documents)} documents to vector store")
            return True
            
        except Exception as e:
            show_error_message(e, "Adding Documents")
            return False
    
    def similarity_search(self, query: str, k: int = None) -> List[Document]:
        """
        Perform similarity search on vector store
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Document]: Similar documents
        """
        try:
            if not self.vector_store:
                show_error_message(ValueError("No vector store available"), "Similarity Search")
                return []
            
            k = k or config.retrieval.search_k
            
            with st.spinner(f"Searching for similar documents..."):
                results = self.vector_store.similarity_search(query, k=k)
            
            return results
            
        except Exception as e:
            show_error_message(e, "Similarity Search")
            return []
    
    def similarity_search_with_scores(self, query: str, k: int = None) -> List[Tuple[Document, float]]:
        """
        Perform similarity search with relevance scores
        
        Args:
            query (str): Search query
            k (int): Number of results to return
            
        Returns:
            List[Tuple[Document, float]]: Documents with similarity scores
        """
        try:
            if not self.vector_store:
                show_error_message(ValueError("No vector store available"), "Similarity Search")
                return []
            
            k = k or config.retrieval.search_k
            
            with st.spinner("Searching with relevance scores..."):
                results = self.vector_store.similarity_search_with_score(query, k=k)
            
            return results
            
        except Exception as e:
            show_error_message(e, "Similarity Search with Scores")
            return []
    
    def get_retriever(self, search_kwargs: dict = None):
        """
        Get retriever for use with chains
        
        Args:
            search_kwargs (dict): Search configuration
            
        Returns:
            Retriever object or None if failed
        """
        try:
            if not self.vector_store:
                show_error_message(ValueError("No vector store available"), "Retriever Creation")
                return None
            
            search_kwargs = search_kwargs or {"k": config.retrieval.search_k}
            return self.vector_store.as_retriever(search_kwargs=search_kwargs)
            
        except Exception as e:
            show_error_message(e, "Retriever Creation")
            return None
    
    def save_vector_store(self, path: str) -> bool:
        """
        Save vector store to disk
        
        Args:
            path (str): Path to save vector store
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.vector_store:
                show_error_message(ValueError("No vector store to save"), "Save Vector Store")
                return False
            
            with st.spinner("Saving vector store..."):
                self.vector_store.save_local(path)
            
            show_success_message(f"Vector store saved to {path}")
            return True
            
        except Exception as e:
            show_error_message(e, "Save Vector Store")
            return False
    
    def load_vector_store(self, path: str) -> bool:
        """
        Load vector store from disk
        
        Args:
            path (str): Path to load vector store from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.embeddings:
                if not self._initialize_embeddings():
                    return False
            
            with st.spinner("Loading vector store..."):
                self.vector_store = FAISS.load_local(path, self.embeddings)
            
            show_success_message(f"Vector store loaded from {path}")
            return True
            
        except Exception as e:
            show_error_message(e, "Load Vector Store")
            return False
    
    def get_store_info(self) -> dict:
        """
        Get information about the current vector store
        
        Returns:
            dict: Vector store information
        """
        if not self.vector_store:
            return {"status": "No vector store available"}
        
        try:
            # Get basic info
            info = {
                "status": "Active",
                "embedding_model": config.embedding.model_name,
                "search_type": "Similarity Search"
            }
            
            # Try to get vector count (FAISS specific)
            if hasattr(self.vector_store, 'index'):
                info["vector_count"] = self.vector_store.index.ntotal
            
            return info
            
        except Exception as e:
            return {"status": f"Error getting info: {str(e)}"}

def create_vector_store_manager(api_key: str = None) -> VectorStoreManager:
    """
    Factory function to create VectorStoreManager instance
    
    Args:
        api_key (str): Google API key
        
    Returns:
        VectorStoreManager: Configured manager instance
    """
    return VectorStoreManager(api_key=api_key)