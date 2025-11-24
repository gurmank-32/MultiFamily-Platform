# Technology Stack - Intelligence Platform

Complete technology stack breakdown for the Intelligence Platform (Housing Regulation Compliance Agent).

---

## 🎯 **Core Framework & Language**

### **Frontend Framework**
- **Streamlit** (v1.28.0+)
  - Web UI framework for Python
  - Real-time chat interface
  - File upload handling
  - Multi-page application
  - Session state management
  - Custom CSS theming support

### **Programming Language**
- **Python 3.13+**
  - Main development language
  - Object-oriented architecture
  - Async/await support (where applicable)

---

## 🤖 **AI & Machine Learning**

### **Large Language Models (LLM)**
- **OpenAI GPT-4o** (Primary)
  - Model: `gpt-4o`
  - Temperature: 0 (for accuracy)
  - Used for:
    - Compliance analysis
    - Clause-by-clause document review
    - Answer generation (RAG)
    - Update summarization
  - API: OpenAI Python SDK (v1.3.0+)
  - Fallback: Free mode (rule-based analysis)

### **Embeddings**
- **Primary (Free)**: Sentence Transformers
  - Model: `all-MiniLM-L6-v2`
  - Library: `sentence-transformers` (v2.2.0+)
  - Dimensions: 384
  - Runs locally (no API needed)
  - Used for semantic search

- **Alternative (Paid)**: OpenAI Embeddings
  - Model: `text-embedding-3-small`
  - Dimensions: 1536
  - Used when API key is available
  - Higher quality but requires credits

### **Deep Learning Framework**
- **PyTorch** (v2.0.0+)
  - Backend for Sentence Transformers
  - Model inference
  - Tensor operations

### **Token Management**
- **tiktoken** (v0.5.0+)
  - Token counting for OpenAI API
  - Cost estimation
  - Context window management

---

## 💾 **Databases**

### **Relational Database**
- **SQLite3** (Built-in Python)
  - Database file: `regulations.db`
  - Tables:
    - `regulations` - Regulation metadata
    - `updates` - Update history
    - `subscribers` - Email subscriptions
  - Operations: CRUD via `database.py`
  - Schema: Auto-created on first run

### **Vector Database**
- **ChromaDB** (v0.4.15+)
  - Type: Persistent vector store
  - Path: `./chroma_db`
  - Collection: `regulations`
  - Distance metric: Cosine similarity
  - Index: HNSW (Hierarchical Navigable Small World)
  - Features:
    - Semantic search
    - Metadata filtering
    - Similarity search
    - Collection management

---

## 📄 **Document Processing**

### **PDF Parsing**
- **PyPDF2** (v3.0.0+)
  - PDF text extraction
  - Multi-page support
  - Metadata extraction
  - Used for lease document parsing

### **Word Document Parsing**
- **python-docx** (v1.1.0+)
  - DOCX file parsing
  - Text extraction
  - Paragraph handling
  - Table extraction

### **Text Processing**
- **Regular Expressions (re)**
  - Pattern matching
  - Clause extraction
  - Text cleaning
  - Format normalization

---

## 🌐 **Web Scraping & HTTP**

### **Web Scraping**
- **BeautifulSoup4** (v4.12.0+)
  - HTML parsing
  - Content extraction
  - Regulation website scraping
  - Text cleaning

- **lxml** (v4.9.0+)
  - Fast XML/HTML parser
  - Backend for BeautifulSoup
  - XPath support

### **HTTP Client**
- **requests** (v2.31.0+)
  - HTTP requests
  - URL fetching
  - Error handling
  - Timeout management
  - Session management

---

## 📊 **Data Processing**

### **Data Manipulation**
- **pandas** (v2.0.0+)
  - DataFrames for regulation data
  - CSV reading/writing
  - Data filtering
  - Aggregation

- **numpy** (v1.24.0+)
  - Numerical operations
  - Array processing
  - Mathematical computations
  - Vector operations

---

## 📧 **Email & Notifications**

### **Email System**
- **SMTP (smtplib)** - Built-in Python
  - Email sending
  - SMTP server connection
  - Authentication
  - Multi-recipient support

- **Email Providers Supported**:
  - Gmail (smtp.gmail.com:587)
  - Custom SMTP servers
  - App password authentication

### **Email Storage (Fallback)**
- **File-based storage** (`emails/` folder)
  - Local email backup
  - Offline email storage
  - Text file format (.txt)

---

## 🔍 **Retrieval & Search**

### **RAG (Retrieval Augmented Generation)**
- **Custom RAG Implementation**
  - Query enhancement
  - Context building
  - Source prioritization
  - Geographic filtering
  - Result reranking

### **Query Enhancement**
- **Legal Terminology Expansion**
  - Synonym mapping
  - Domain-specific terms
  - Context-aware expansion

### **Source Prioritization**
- **Authoritative Source Ranking**
  - Government sources (.gov)
  - Educational sources (.edu)
  - Legal sources
  - News/blog sources (lower priority)

### **Geographic Filtering**
- **City-Specific Search**
  - Dallas, Houston, Austin, San Antonio
  - Texas-Statewide
  - Location-based filtering

---

## ⚙️ **Configuration & Environment**

### **Environment Management**
- **python-dotenv** (v1.0.0+)
  - `.env` file loading
  - Local development
  - Secret management

### **Streamlit Secrets** (Cloud)
- **st.secrets**
  - Streamlit Cloud integration
  - Secure secret storage
  - No `.env` file needed in cloud

### **Configuration Files**
- **config.py** - Application settings
- **.streamlit/config.toml** - Streamlit configuration
- **sources.csv** - Regulation source URLs

---

## 🛠️ **Utilities & Libraries**

### **Hashing**
- **hashlib** (Built-in Python)
  - Content hashing (SHA-256)
  - Change detection
  - Duplicate detection

### **Date/Time**
- **datetime** (Built-in Python)
  - Timestamp management
  - Date formatting
  - Time-based queries

### **JSON Processing**
- **json** (Built-in Python)
  - Data serialization
  - Configuration storage
  - API responses

### **File I/O**
- **io** (Built-in Python)
  - BytesIO for file handling
  - Memory file operations
  - Stream processing

### **OS Operations**
- **os** (Built-in Python)
  - File system operations
  - Environment variables
  - Path management

---

## 🚀 **Deployment & Hosting**

### **Cloud Platform**
- **Streamlit Cloud** (Free Tier)
  - Hosting platform
  - Automatic deployments
  - GitHub integration
  - Public repository support

### **Version Control**
- **Git**
  - Code versioning
  - GitHub integration
  - Deployment triggers

---

## 📦 **Project Structure**

```
Intelligence Platform/
├── app.py                    # Streamlit UI (Frontend)
├── config.py                 # Configuration & secrets
├── database.py               # SQLite operations
├── vector_store.py           # ChromaDB & embeddings
├── qa_system.py              # RAG Q&A system
├── compliance_checker.py     # LLM compliance analysis
├── document_parser.py        # PDF/DOCX parsing
├── scraper.py                # Web scraping
├── update_checker.py         # Change detection
├── email_alerts.py           # Email notifications
├── daily_scraper.py          # Scheduled tasks
├── retrieval_config.py       # Search enhancements
├── prompts_config.py         # LLM prompts
├── requirements.txt          # Dependencies
├── sources.csv               # Regulation URLs
├── .streamlit/
│   └── config.toml          # Streamlit config
└── chroma_db/                # Vector database (runtime)
```

---

## 🔄 **Data Flow Architecture**

### **1. Regulation Ingestion**
```
CSV → Database → Scraper → Text Extraction → Chunking → Embeddings → ChromaDB
```

### **2. Question Answering (RAG)**
```
User Question → Query Enhancement → Vector Search → Context Building → LLM → Answer
```

### **3. Compliance Checking**
```
Document Upload → Parsing → Clause Extraction → Vector Search → LLM Analysis → Report
```

### **4. Update Detection**
```
URL Fetch → Hash Comparison → Change Detection → LLM Summarization → Email Alert
```

---

## 🎨 **UI Components**

### **Streamlit Components Used**
- `st.title()` - Page titles
- `st.markdown()` - Rich text
- `st.chat_message()` - Chat interface
- `st.chat_input()` - User input
- `st.file_uploader()` - Document upload
- `st.expander()` - Collapsible sections
- `st.dataframe()` - Data tables
- `st.selectbox()` - Dropdowns
- `st.button()` - Actions
- `st.info()` / `st.success()` / `st.error()` - Alerts
- `st.spinner()` - Loading indicators
- `st.sidebar` - Navigation

---

## 🔐 **Security & Privacy**

### **Secret Management**
- Environment variables (local)
- Streamlit secrets (cloud)
- No hardcoded credentials
- `.gitignore` protection

### **Data Privacy**
- Local database storage
- No external data sharing
- User data isolation
- Secure email transmission (TLS)

---

## 📈 **Performance Optimizations**

### **Caching**
- Streamlit session state
- Embedding model caching
- Database connection pooling

### **Efficient Search**
- HNSW indexing (ChromaDB)
- Cosine similarity (fast)
- Metadata filtering
- Result reranking

### **Lazy Loading**
- On-demand model loading
- Embedding generation caching
- Database query optimization

---

## 🔌 **API Integrations**

### **OpenAI API**
- Endpoint: `https://api.openai.com/v1`
- Models: `gpt-4o`, `text-embedding-3-small`
- Authentication: API key
- Rate limiting: Handled
- Error handling: Graceful fallback

### **SMTP**
- Protocol: SMTP/TLS
- Port: 587 (TLS)
- Authentication: Username/password
- Fallback: File storage

---

## 📚 **Key Libraries Summary**

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| **UI** | streamlit | ≥1.28.0 | Web interface |
| **LLM** | openai | ≥1.3.0 | GPT-4 API |
| **Vector DB** | chromadb | ≥0.4.15 | Semantic search |
| **Embeddings** | sentence-transformers | ≥2.2.0 | Free embeddings |
| **ML** | torch | ≥2.0.0 | Deep learning |
| **Data** | pandas | ≥2.0.0 | Data manipulation |
| **Data** | numpy | ≥1.24.0 | Numerical ops |
| **Scraping** | beautifulsoup4 | ≥4.12.0 | HTML parsing |
| **Scraping** | lxml | ≥4.9.0 | XML/HTML parser |
| **HTTP** | requests | ≥2.31.0 | Web requests |
| **PDF** | PyPDF2 | ≥3.0.0 | PDF parsing |
| **DOCX** | python-docx | ≥1.1.0 | Word docs |
| **Tokens** | tiktoken | ≥0.5.0 | Token counting |
| **Config** | python-dotenv | ≥1.0.0 | Environment vars |

---

## 🆚 **Free vs Paid Components**

### **✅ Free Components**
- Streamlit (UI framework)
- SQLite (database)
- ChromaDB (vector store)
- Sentence Transformers (embeddings)
- PyTorch (ML framework)
- BeautifulSoup (scraping)
- All document parsers
- Email system (SMTP)

### **💰 Paid Components (Optional)**
- OpenAI API (GPT-4o)
  - Cost: ~$0.01-0.03 per 1K tokens
  - Used for: Compliance analysis, Q&A
  - Alternative: Free rule-based mode

---

## 🎯 **Technology Highlights**

1. **Hybrid AI Approach**: Free embeddings + Optional paid LLM
2. **Dual Database**: SQLite (metadata) + ChromaDB (vectors)
3. **RAG Architecture**: Retrieval Augmented Generation for Q&A
4. **Multi-format Support**: PDF, DOCX document parsing
5. **Real-time Updates**: Change detection via content hashing
6. **Cloud-Ready**: Streamlit Cloud deployment
7. **Scalable**: Modular architecture
8. **Free Tier Compatible**: Works without API keys

---

## 📝 **Version Information**

- **Python**: 3.13+
- **Streamlit**: 1.28.0+
- **OpenAI SDK**: 1.3.0+
- **ChromaDB**: 0.4.15+
- **Sentence Transformers**: 2.2.0+
- **PyTorch**: 2.0.0+

---

## 🔮 **Future Technology Considerations**

### **Potential Additions**
- **LangChain** - LLM orchestration (currently minimal use)
- **LlamaIndex** - Advanced RAG framework
- **Local LLMs** - Ollama, LM Studio integration
- **PostgreSQL** - For larger scale deployments
- **Redis** - Caching layer
- **Celery** - Background task processing
- **Docker** - Containerization
- **Kubernetes** - Orchestration (enterprise)

---

**Last Updated**: November 2024
**Project**: Intelligence Platform (Housing Regulation Compliance Agent)

