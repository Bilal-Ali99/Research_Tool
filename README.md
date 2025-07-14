
# Research Tool - Modular Project Structure


## 📁 Project Structure


research_tool

├── main.py                 # Main application entry point

├── config.py               # Configuration settings and parameters

├── utils.py                # Utility functions and helpers

├── document_processor.py   # Document loading and chunking

├── vector_store.py         # Vector store and embeddings management

├── qa_chain.py             # Question answering chain management

├── ui.py                   # Streamlit user interface

├── requirements.txt        # Python dependencies

└── README.md              # This file
## 🚀 Quick Setup

###  Create Project Directory

    bash
    mkdir research_tool
    cd research_tool

### Create Virtual Environment
    bash
    python -m venv venv
    # Activate virtual environment
    # Windows:
    venv\Scripts\activate
    # macOS/Linux:
    source venv/bin/activate

### Install Dependencies
    
    bash
    pip install -r requirements.txt

### Run the Application
    
    bash
    streamlit run main.py
## 📋 Module Descriptions

### 🔧 config.py
* Purpose: Central configuration management
    * Features:
        * Dataclass-based configuration
        * Chunking parameters
        * LLM and embedding settings
        * Retrieval configuration
        * API key management

### 🛠️ utils.py
* Purpose: Common utility functions
    * Features:
        * URL validation and parsing
        * Text processing utilities
        * Error handling helpers
        * Streamlit display utilities
        * API setup functions


### 📄 document_processor.py

* Purpose: Document loading and text processing
    * Features:

       * Web content loading from URLs
       * Intelligent text chunking
       * Document metadata handling
       * Processing statistics
       * Configurable chunk parameters

### 🗄️ vector_store.py

* Purpose: Vector database management
    * Features:
       * Google Generative AI embeddings
       * FAISS vector store operations
       * Similarity search functionality
       * Vector store persistence
       * Retriever creation for chains

### 🤖 qa_chain.py

* Purpose: Question answering functionality
    * Features:
       * RetrievalQAWithSourcesChain setup
       * Google Generative AI LLM integration
       * Custom prompt templates
       * Source attribution
       * Retrieval parameter management



### 🖥️ ui.py

* Purpose: Streamlit user interface
    * Features:
       * Responsive web interface
       * Real-time configuration
       * URL processing workflow
       * Interactive querying
       * Results visualization



### 🏁 main.py

* Purpose: Application entry point
    * Features:
       * Path configuration
       * Application initialization
       * Clean startup process
## 🔄 Application Flow

1. Initialization: Load configuration and setup components
2. API Configuration: User enters Google API key
3. URL Processing:
   * User inputs URLs
   * Documents are loaded and chunked
   * Embeddings are created
   * Vector store is built


4. QA Chain Setup: RetrievalQAWithSourcesChain is configured
5. Querying: User asks questions and receives answers with sources
## ⚙️ Configuration Options


### Chunking Parameters

* Chunk Size: 500-2000 characters (default: 1000)
* Chunk Overlap: 50-500 characters (default: 200)

### LLM Settings

* Model: Gemini Pro
* Temperature: 0.7 (adjustable)

### Retrieval Settings

* Documents Retrieved: 1-10 (default: 3)
* Chain Type: "stuff" (default)


## 🔧 Customization Guide

### Adding New Features

#### New Configuration Options:
    python
    # In config.py
    @dataclass
    class NewFeatureConfig:
        parameter1: str = "default_value"
        parameter2: int = 42

#### New Utility Functions:
    python
    # In utils.py
    def new_utility_function(param):
        """Your new utility function"""
        return processed_result

#### Extending Document Processing:
    python
    # In document_processor.py
    def new_processing_method(self, documents):
        """Additional document processing"""
        return processed_documents


### Custom Prompt Templates
    python
    # In qa_chain.py
    custom_template = """
    Use the following context to answer the question:
    {summaries}

    Question: {question}
    Answer with detailed explanation:
    """

    qa_manager.create_custom_prompt(custom_template)
## 🐛 Troubleshooting



### Common Issues

1. Import Errors:

* Ensure all files are in the same directory
* Check Python path configuration
* Verify virtual environment activation


2. API Configuration:

* Verify Google API key is valid
* Check API quota and limits
* Ensure Gemini API access is enabled


3. Memory Issues:

* Reduce chunk size for large documents
* Process fewer URLs simultaneously
* Consider using FAISS with disk storage


4. URL Loading Failures:

* Check URL accessibility
* Some sites block automated requests
* Try different URLs or add delays



### Performance Optimization

1. For Large Datasets:

* Increase chunk size to reduce total chunks
* Use FAISS disk storage for persistence
* Consider batch processing


2. For Better Accuracy:

* Reduce chunk size for more precise retrieval
* Increase retrieval k parameter
* Fine-tune overlap parameters
## 📚 Usage Examples

### Basic Usage
    python
    # After running streamlit run main.py
    # 1. Enter API key in sidebar
    # 2. Input URLs in text area
    # 3. Click "Process URLs"
    # 4. Ask questions in query section

### Programmatic Usage
    python
    from document_processor import create_document_processor
    from vector_store import create_vector_store_manager
    from qa_chain import create_qa_chain_manager

    # Initialize components
    processor = create_document_processor()
    vector_manager = create_vector_store_manager(api_key)
    qa_manager = create_qa_chain_manager(api_key)

    # Process documents
    chunks = processor.process_urls(urls)
    vector_store = vector_manager.create_vector_store(chunks)
    qa_manager.setup_qa_chain(vector_manager)

    # Ask questions
    response = qa_manager.ask_question("Your question here")

## 🔒 Security Considerations

* Never commit API keys to version control
* Use environment variables for production
* Implement rate limiting for API calls
* Validate all user inputs
* Sanitize URLs before processing
## 🚀 Deployment Options

### Local Development
    bash
    streamlit run main.py
### Streamlit Cloud

1. Push code to GitHub repository
2. Connect to Streamlit Cloud
3. Add API key to secrets
4. Deploy application

### Docker Deployment
    docker
    fileFROM python:3.9-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install -r requirements.txt
    COPY . .
    EXPOSE 8501
    CMD ["streamlit", "run", "main.py"]
## 📈 Future Enhancements

* Support for multiple LLM providers
* Document type detection and specialized processing
* Batch URL processing with progress tracking
* Vector store persistence and caching
* Advanced query preprocessing
* Multi-language support
* API endpoint for headless operation