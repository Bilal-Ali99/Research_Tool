"""
Utility functions for the Research Tool
"""

import streamlit as st
import google.generativeai as genai
from urllib.parse import urlparse
from typing import List, Tuple
import re

def validate_url(url: str) -> bool:
    """
    Validate if the URL is properly formatted
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def parse_urls_from_input(urls_input: str) -> List[str]:
    """
    Parse URLs from multi-line input text
    
    Args:
        urls_input (str): Multi-line string containing URLs
        
    Returns:
        List[str]: List of cleaned URLs
    """
    if not urls_input:
        return []
    
    # Split by newlines and clean up
    urls = [url.strip() for url in urls_input.split('\n') if url.strip()]
    return urls

def validate_urls(urls: List[str]) -> Tuple[List[str], List[str]]:
    """
    Validate a list of URLs and separate valid from invalid ones
    
    Args:
        urls (List[str]): List of URLs to validate
        
    Returns:
        Tuple[List[str], List[str]]: (valid_urls, invalid_urls)
    """
    valid_urls = []
    invalid_urls = []
    
    for url in urls:
        if validate_url(url):
            valid_urls.append(url)
        else:
            invalid_urls.append(url)
    
    return valid_urls, invalid_urls

def setup_gemini_api(api_key: str) -> bool:
    """
    Setup Gemini API with the provided key
    
    Args:
        api_key (str): Google API key
        
    Returns:
        bool: True if setup successful, False otherwise
    """
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error setting up Gemini API: {str(e)}")
        return False

def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespaces and special characters
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
    
    return text.strip()

def truncate_text(text: str, max_length: int = 300, suffix: str = "...") -> str:
    """
    Truncate text to specified length
    
    Args:
        text (str): Text to truncate
        max_length (int): Maximum length
        suffix (str): Suffix to add when truncating
        
    Returns:
        str: Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def format_sources(sources: str) -> str:
    """
    Format sources string for better display
    
    Args:
        sources (str): Sources string
        
    Returns:
        str: Formatted sources
    """
    if not sources:
        return "No sources available"
    
    # Split by common delimiters and clean up
    source_list = re.split(r'[,;]', sources)
    formatted_sources = []
    
    for source in source_list:
        source = source.strip()
        if source:
            formatted_sources.append(f"• {source}")
    
    return '\n'.join(formatted_sources) if formatted_sources else sources

def display_processing_stats(num_chunks: int, num_documents: int, num_urls: int) -> None:
    """
    Display processing statistics in Streamlit
    
    Args:
        num_chunks (int): Number of chunks created
        num_documents (int): Number of documents processed
        num_urls (int): Number of URLs processed
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("URLs Processed", num_urls)
    with col2:
        st.metric("Documents Created", num_documents)
    with col3:
        st.metric("Text Chunks", num_chunks)

def show_error_message(error: Exception, context: str = "") -> None:
    """
    Display formatted error message in Streamlit
    
    Args:
        error (Exception): Exception that occurred
        context (str): Additional context about where error occurred
    """
    error_msg = f"Error in {context}: {str(error)}" if context else f"Error: {str(error)}"
    st.error(error_msg)

def show_success_message(message: str, details: str = None) -> None:
    """
    Display formatted success message in Streamlit
    
    Args:
        message (str): Main success message
        details (str): Additional details to show
    """
    st.success(message)
    if details:
        st.info(details)