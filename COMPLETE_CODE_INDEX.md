# Complete Code Index - Intelligence Platform Agent

This document provides a complete index of all code files, their purposes, and where to find them.

## 📁 Project Structure

```
Agent Intellectual Platform/
├── Core Application Files
│   ├── app.py                    # Main Streamlit application (967 lines)
│   ├── config.py                 # Configuration and settings
│   ├── database.py               # SQLite database operations
│   ├── scraper.py                # Web scraping and content fetching
│   ├── vector_store.py           # ChromaDB vector embeddings
│   ├── qa_system.py              # Q&A and chat system
│   ├── compliance_checker.py     # Lease document compliance analysis
│   ├── update_checker.py         # Regulation update detection
│   ├── email_alerts.py           # Email notification system
│   ├── document_parser.py        # PDF/DOCX parsing
│   ├── init_data.py              # Initialization script
│   ├── daily_scraper.py          # Daily update automation
│   ├── retrieval_config.py       # Enhanced retrieval configuration
│   └── prompts_config.py         # LLM prompt customization
│
├── Configuration Files
│   ├── .env                      # Environment variables (API keys)
│   ├── .env.example              # Example environment file
│   ├── requirements.txt          # Python dependencies
│   └── .streamlit/config.toml    # Streamlit configuration
│
├── Data Files
│   ├── sources.csv               # Regulation source URLs
│   ├── regulations.db            # SQLite database (auto-generated)
│   └── chroma_db/                # Vector database (auto-generated)
│
├── Documentation
│   ├── README.md                 # Main project readme
│   ├── ARCHITECTURE.md           # System architecture overview
│   ├── CODE_OVERVIEW.md          # Code structure guide
│   ├── SYSTEM_ARCHITECTURE.md    # Detailed architecture with diagrams
│   ├── HOW_TO_LAUNCH.md          # Launch instructions
│   ├── HOW_TO_UPDATE_SOURCES.md  # How to update sources.csv
│   ├── PROMPT_CUSTOMIZATION_GUIDE.md
│   ├── RETRIEVAL_ENHANCEMENT_GUIDE.md
│   ├── RETRIEVAL_IMPROVEMENTS_SUMMARY.md
│   └── COMPLETE_CODE_INDEX.md    # This file
│
└── Test Files
    └── test_regulation_dallas_rent_control.html  # Test regulation file
```

## 📄 File Descriptions

### Core Application Files

#### 1. `app.py` (967 lines)
**Purpose:** Main Streamlit web application interface
**Key Features:**
- Multi-page navigation (Home, IP Agent, Regulation Explorer, Update Log, Email Alerts, Settings)
- Chat interface with conversation history
- Integrated compliance checker with file upload
- Regulation browsing and search
- Update detection and display
- Email subscription management
- Settings and data management

**Main Functions:**
- `main()` - Entry point, initializes session state
- `show_home()` - Homepage dashboard
- `show_ip_agent_page()` - Main chat interface with compliance checking
- `show_regulation_explorer()` - Browse and search regulations
- `show_update_log()` - View regulation updates
- `show_email_alerts_page()` - Email subscription management
- `show_settings()` - System settings and data management

#### 2. `config.py`
**Purpose:** Centralized configuration management
**Contains:**
- OpenAI API settings
- Database paths
- Email/SMTP configuration
- Supported cities list
- Regulation categories
- Legal disclaimer text
- Source file path

#### 3. `database.py` (260 lines)
**Purpose:** SQLite database operations
**Key Classes:**
- `RegulationDB` - Main database interface

**Main Methods:**
- `add_regulation()` - Add/update regulation
- `get_all_regulations()` - Get all regulations
- `get_regulation_by_url()` - Find by URL
- `update_regulation_hash()` - Update content hash
- `add_update()` - Record regulation update
- `get_recent_updates()` - Get update history
- `subscribe_email()` - Subscribe to alerts
- `unsubscribe_email()` - Unsubscribe
- `get_subscribers_for_city()` - Get city subscribers
- `load_regulations_from_csv()` - Import from CSV
- `save_compliance_check()` - Save compliance results

#### 4. `scraper.py`
**Purpose:** Web scraping and content extraction
**Key Classes:**
- `RegulationScraper` - Web content fetcher

**Main Methods:**
- `fetch_url_content()` - Fetch and parse web content
  - Supports HTTP/HTTPS URLs
  - Supports local file paths
  - Supports `file://` URLs
  - Generates content hash for change detection
- `chunk_text()` - Split text into chunks for embedding
- `extract_relevant_sections()` - Extract keyword-based sections

#### 5. `vector_store.py`
**Purpose:** Vector embeddings and semantic search
**Key Classes:**
- `RegulationVectorStore` - ChromaDB vector store manager

**Main Methods:**
- `create_embedding()` - Generate embeddings (free or OpenAI)
- `add_regulation_chunks()` - Index regulation chunks
- `search()` - Enhanced semantic search with:
  - Query enhancement
  - Source reliability prioritization
  - Geographical filtering
  - Intelligent reranking
- `delete_regulation()` - Remove regulation from index

**Features:**
- Free embeddings using Sentence Transformers
- OpenAI embeddings as optional upgrade
- Enhanced retrieval with multiple ranking factors

#### 6. `qa_system.py` (576 lines)
**Purpose:** Question-answering system with RAG
**Key Classes:**
- `QASystem` - Main Q&A interface

**Main Methods:**
- `answer_question()` - Answer single question
- `answer_question_with_context()` - Answer with chat history
- `_generate_llm_answer()` - Generate answer using LLM
- `_extract_answer_from_context()` - Free mode answer extraction
- `_detect_city()` - Auto-detect city from question
- `_check_relevance()` - Filter irrelevant questions
- `_validate_question()` - Validate question quality

**Features:**
- City auto-detection
- Legal jargon explanation
- Scenario-based questions
- Follow-up question handling
- Out-of-scope detection
- Free mode (no API required)
- Enhanced retrieval integration

#### 7. `compliance_checker.py` (483 lines)
**Purpose:** Lease document compliance analysis
**Key Classes:**
- `ComplianceChecker` - Compliance analysis engine

**Main Methods:**
- `check_compliance()` - Main compliance check function
- `analyze_clause_compliance()` - Analyze individual clause
- `_analyze_clause_with_openai()` - OpenAI-based analysis
- `_analyze_clause_free_mode()` - Free rule-based analysis
- `_generate_action_items()` - Generate action items
- `refine_clause()` - Generate compliant clause versions

**Features:**
- PDF and DOCX support
- Clause-by-clause analysis
- Specific violation detection
- Action items generation
- Document/poster recommendations
- Free mode fallback
- Enhanced retrieval integration

#### 8. `update_checker.py`
**Purpose:** Detect regulation updates
**Key Classes:**
- `UpdateChecker` - Update detection system

**Main Methods:**
- `check_for_updates()` - Check all regulations for changes
- `_summarize_update()` - Generate update summary using LLM
- `_identify_affected_cities()` - Detect which cities are affected

**Features:**
- Hash-based change detection
- Automatic summarization
- City impact analysis
- Update logging

#### 9. `email_alerts.py`
**Purpose:** Email notification system
**Key Classes:**
- `EmailAlertSystem` - Email sender

**Main Methods:**
- `send_update_alert()` - Send update notification
- `send_welcome_email()` - Send welcome message
- `notify_subscribers()` - Notify all city subscribers
- `_save_email_to_file()` - Save email to file (fallback)

**Features:**
- SMTP email sending
- File-based fallback (for testing)
- Welcome emails
- Update notifications
- Unsubscribe links

#### 10. `document_parser.py`
**Purpose:** Parse PDF and DOCX documents
**Key Classes:**
- `DocumentParser` - Document parser

**Main Methods:**
- `parse_document()` - Parse uploaded document
- `_parse_pdf()` - Extract text from PDF
- `_parse_docx()` - Extract text from DOCX
- `extract_clauses()` - Extract lease clauses

**Features:**
- PDF text extraction
- DOCX text extraction
- Clause identification
- Structured output

#### 11. `init_data.py`
**Purpose:** Initialization script
**Main Function:**
- `initialize_system()` - Load and index all regulations from CSV

**Usage:**
```bash
python init_data.py
```

#### 12. `daily_scraper.py`
**Purpose:** Daily update automation
**Key Classes:**
- `DailyScraper` - Automated daily checking

**Main Methods:**
- `run_daily_check()` - Run daily update check
- `run_daily_scraper()` - Main loop for continuous operation

**Usage:**
```bash
python daily_scraper.py
```

#### 13. `retrieval_config.py`
**Purpose:** Enhanced retrieval configuration
**Contains:**
- Query enhancement functions
- Source reliability scoring
- Geographical filtering
- Reranking algorithms

**Key Functions:**
- `enhance_query_with_terminology()` - Add legal terms to query
- `calculate_source_reliability()` - Score source reliability
- `filter_by_geography()` - Filter by city/region
- `rerank_results()` - Multi-factor reranking

#### 14. `prompts_config.py`
**Purpose:** LLM prompt customization
**Contains:**
- Q&A prompts
- Compliance analysis prompts
- Update summarization prompts
- Customizable templates

**Key Features:**
- Easy prompt modification
- Template-based system
- Context-aware prompts

### Configuration Files

#### `.env`
**Purpose:** Environment variables
**Contains:**
- `OPENAI_API_KEY` - OpenAI API key (optional)
- `SMTP_SERVER` - Email server
- `SMTP_PORT` - Email port
- `SMTP_EMAIL` - Email address
- `SMTP_PASSWORD` - Email password

#### `requirements.txt`
**Purpose:** Python dependencies
**Contains:**
- All required Python packages
- Version specifications

#### `.streamlit/config.toml`
**Purpose:** Streamlit configuration
**Contains:**
- Theme settings
- Server configuration
- UI preferences

### Data Files

#### `sources.csv`
**Purpose:** Regulation source URLs
**Format:**
```csv
Source Name,URL,Type,Regulation Category
Dallas Rent Control,https://...,Web,Rent Caps
```

#### `regulations.db`
**Purpose:** SQLite database
**Tables:**
- `regulations` - Regulation metadata
- `updates` - Update history
- `email_alerts` - Email subscriptions
- `compliance_checks` - Compliance check history

#### `chroma_db/`
**Purpose:** Vector database
**Contains:**
- Regulation embeddings
- Searchable vector index

## 🔧 Key Technologies

1. **Streamlit** - Web framework
2. **ChromaDB** - Vector database
3. **SQLite** - Relational database
4. **OpenAI API** - LLM (optional)
5. **Sentence Transformers** - Free embeddings
6. **BeautifulSoup** - HTML parsing
7. **PyPDF2** - PDF parsing
8. **python-docx** - DOCX parsing
9. **pandas** - CSV handling

## 📊 Code Statistics

- **Total Python Files:** 14
- **Total Lines of Code:** ~4,000+
- **Main Application:** 967 lines
- **Largest Modules:**
  - `app.py`: 967 lines
  - `qa_system.py`: 576 lines
  - `compliance_checker.py`: 483 lines

## 🚀 How to View Code

### Option 1: View in IDE
Open the project folder in your IDE (VS Code, PyCharm, etc.) and browse files.

### Option 2: Read Individual Files
Use the file reading tools to view specific files:
- `read_file("app.py")` - Main application
- `read_file("qa_system.py")` - Q&A system
- `read_file("compliance_checker.py")` - Compliance checker
- etc.

### Option 3: Use Code Search
Use semantic search to find specific functionality:
- "How does compliance checking work?"
- "Where is email sending handled?"
- "How are regulations indexed?"

## 📝 Next Steps

1. **Read Core Files:**
   - Start with `app.py` for the main interface
   - Review `qa_system.py` for Q&A logic
   - Check `compliance_checker.py` for compliance analysis

2. **Understand Data Flow:**
   - CSV → Database → Scraper → Vector Store
   - User Question → Vector Search → LLM → Answer
   - Document Upload → Parser → Compliance Check → Results

3. **Customize:**
   - Edit `prompts_config.py` for prompt tuning
   - Edit `retrieval_config.py` for search optimization
   - Edit `config.py` for settings

4. **Extend:**
   - Add new regulation categories
   - Add new cities
   - Add new document types
   - Add new features

## 🔍 Quick Reference

**Where to find:**
- **Main UI:** `app.py`
- **Q&A Logic:** `qa_system.py`
- **Compliance:** `compliance_checker.py`
- **Database:** `database.py`
- **Scraping:** `scraper.py`
- **Vector Search:** `vector_store.py`
- **Email:** `email_alerts.py`
- **Updates:** `update_checker.py`
- **Config:** `config.py`
- **Prompts:** `prompts_config.py`
- **Retrieval:** `retrieval_config.py`

---

**Last Updated:** 2024
**Total Files:** 14 Python files + configuration + documentation

