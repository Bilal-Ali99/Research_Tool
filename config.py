"""
Configuration setting for the research tool
"""

import os
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ChunkingConfig:
    """Configuration for the text chunking parameter"""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    length_function = len

@dataclass
class EmbeddingConfig:
    """Configuration for embedding model"""
    model_name: str = "models/embedding-001"

@dataclass
class LLMConfig:
    """Configuration for Language Model"""
    model_name: str = "gemini-2.0-flash"
    temperature: float = 0.7

@dataclass
class RetrievalConfig:
    """Configuration for retrieval setting"""
    search_k: int = 3
    chain_type: str = "stuff"

@dataclass
class StreamlitConfig:
    """Configuration for Streamlit UI"""
    page_title: str = "Research Tool"
    page_icon: str = "🔍"
    layout: str = "wide"

class Config:
    """Main Configuration class"""

    def __init__(self):
        self.chunking = ChunkingConfig()
        self.embedding = EmbeddingConfig()
        self.llm = LLMConfig()
        self.retrieval = RetrievalConfig()
        self.streamlit = StreamlitConfig()

    def set_api_key(self, api_key: str) -> None:
        """Set the Google API Key in Environment"""
        os.environ["GEMINI_API_KEY"]  = api_key

    def get_api_key(self) -> Optional[str]:
        """Get the Google API Key from environment"""
        return os.environ.get("GEMINI_API_KEY")