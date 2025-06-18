"""
Document processing module for loading and chunking web content
"""

import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Optional
from langchain.schema import Document

from config import config
from utils import show_error_message, show_success_message, display_processing_stats

class DocumentProcessor:
    """Handles document loading and text chunking operations"""
    
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        """
        Initialize DocumentProcessor
        
        Args:
            chunk_size (int): Size of text chunks
            chunk_overlap (int): Overlap between chunks
        """
        self.chunk_size = chunk_size or config.chunking.chunk_size
        self.chunk_overlap = chunk_overlap or config.chunking.chunk_overlap
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=config.chunking.length_function
        )
    
    def load_documents_from_urls(self, urls: List[str]) -> Optional[List[Document]]:
        """
        Load documents from a list of URLs
        
        Args:
            urls (List[str]): List of URLs to load
            
        Returns:
            Optional[List[Document]]: Loaded documents or None if failed
        """
        try:
            if not urls:
                show_error_message(ValueError("No URLs provided"), "Document Loading")
                return None
            
            with st.spinner(f"Loading content from {len(urls)} URLs..."):
                loader = WebBaseLoader(urls)
                documents = loader.load()
            
            if not documents:
                show_error_message(ValueError("No content loaded from URLs"), "Document Loading")
                return None
                
            show_success_message(
                f"Successfully loaded {len(documents)} documents",
                f"Total URLs processed: {len(urls)}"
            )
            
            return documents
            
        except Exception as e:
            show_error_message(e, "Document Loading")
            return None
    
    def chunk_documents(self, documents: List[Document]) -> Optional[List[Document]]:
        """
        Split documents into smaller chunks
        
        Args:
            documents (List[Document]): Documents to chunk
            
        Returns:
            Optional[List[Document]]: Document chunks or None if failed
        """
        try:
            if not documents:
                show_error_message(ValueError("No documents provided"), "Document Chunking")
                return None
            
            with st.spinner("Splitting documents into chunks..."):
                chunks = self.text_splitter.split_documents(documents)
            
            if not chunks:
                show_error_message(ValueError("No chunks created"), "Document Chunking")
                return None
            
            show_success_message(
                f"Successfully created {len(chunks)} text chunks",
                f"Average chunk size: ~{sum(len(chunk.page_content) for chunk in chunks) // len(chunks)} characters"
            )
            
            return chunks
            
        except Exception as e:
            show_error_message(e, "Document Chunking")
            return None
    
    def process_urls(self, urls: List[str]) -> Optional[List[Document]]:
        """
        Complete pipeline: load URLs and chunk documents
        
        Args:
            urls (List[str]): List of URLs to process
            
        Returns:
            Optional[List[Document]]: Processed document chunks or None if failed
        """
        try:
            # Load documents
            documents = self.load_documents_from_urls(urls)
            if not documents:
                return None
            
            # Chunk documents
            chunks = self.chunk_documents(documents)
            if not chunks:
                return None
            
            # Display processing statistics
            display_processing_stats(
                num_chunks=len(chunks),
                num_documents=len(documents),
                num_urls=len(urls)
            )
            
            return chunks
            
        except Exception as e:
            show_error_message(e, "Document Processing Pipeline")
            return None
    
    def get_document_info(self, documents: List[Document]) -> dict:
        """
        Get information about processed documents
        
        Args:
            documents (List[Document]): Documents to analyze
            
        Returns:
            dict: Information about documents
        """
        if not documents:
            return {}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        sources = set()
        
        for doc in documents:
            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                sources.add(doc.metadata['source'])
        
        return {
            'total_documents': len(documents),
            'total_characters': total_chars,
            'average_length': total_chars // len(documents) if documents else 0,
            'unique_sources': len(sources),
            'sources': list(sources)
        }
    
    def update_chunk_settings(self, chunk_size: int, chunk_overlap: int) -> None:
        """
        Update chunking settings
        
        Args:
            chunk_size (int): New chunk size
            chunk_overlap (int): New chunk overlap
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Reinitialize text splitter with new settings
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=config.chunking.length_function
        )
        
        st.info(f"Updated chunk settings - Size: {chunk_size}, Overlap: {chunk_overlap}")

def create_document_processor(chunk_size: int = None, chunk_overlap: int = None) -> DocumentProcessor:
    """
    Factory function to create DocumentProcessor instance
    
    Args:
        chunk_size (int): Size of text chunks
        chunk_overlap (int): Overlap between chunks
        
    Returns:
        DocumentProcessor: Configured processor instance
    """
    return DocumentProcessor(chunk_size=chunk_size, chunk_overlap=chunk_overlap)