# View All Code - Complete Guide

## 📋 Quick Answer

**All code is in:** `C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\`

**Total:** 15 Python files (~4,000+ lines of code)

---

## 📁 All Python Files (Sorted by Size)

### Large Files (Main Application Logic)

1. **`app.py`** - 967 lines
   - Main Streamlit web application
   - All UI pages and interactions
   - Chat interface, compliance checker, settings

2. **`qa_system.py`** - 576 lines
   - Question-answering system
   - RAG implementation
   - City detection, relevance checking

3. **`compliance_checker.py`** - 483 lines
   - Lease document compliance analysis
   - Clause-by-clause checking
   - Action items generation

### Medium Files (Core Functionality)

4. **`database.py`** - 260 lines
   - SQLite database operations
   - CRUD operations for regulations
   - Email subscriptions, updates

5. **`vector_store.py`** - ~176 lines
   - ChromaDB vector embeddings
   - Semantic search
   - Enhanced retrieval

6. **`scraper.py`** - ~100 lines
   - Web scraping
   - Content fetching
   - Text chunking

7. **`update_checker.py`** - ~100 lines
   - Update detection
   - Change monitoring
   - Summarization

8. **`document_parser.py`** - ~80 lines
   - PDF/DOCX parsing
   - Text extraction
   - Clause identification

9. **`email_alerts.py`** - ~75 lines
   - Email notifications
   - SMTP sending
   - File fallback

### Small Files (Configuration & Utilities)

10. **`retrieval_config.py`** - ~150 lines
    - Enhanced retrieval config
    - Query enhancement
    - Reranking algorithms

11. **`prompts_config.py`** - ~100 lines
    - LLM prompt templates
    - Customizable prompts

12. **`config.py`** - ~53 lines
    - All configuration settings
    - API keys, paths, constants

13. **`init_data.py`** - ~77 lines
    - Initialization script
    - Load from CSV

14. **`daily_scraper.py`** - ~51 lines
    - Daily automation
    - Scheduled tasks

15. **`test_system.py`** - Testing utilities

---

## 🔍 How to View Each File

### In Cursor/VS Code:
1. Open the project folder
2. Use the file explorer (left sidebar)
3. Click any `.py` file to view

### Using Command Line:
```powershell
# View a specific file
Get-Content app.py

# View with line numbers
Get-Content app.py | Select-Object -First 50

# Search for a function
Select-String -Pattern "def main" *.py
```

### Using Python:
```python
# Read any file
with open('app.py', 'r', encoding='utf-8') as f:
    print(f.read())
```

---

## 📊 Code Structure Overview

```
Agent Intellectual Platform/
│
├── 🎯 Main Application
│   ├── app.py (967 lines) - Main UI
│   ├── config.py (53 lines) - Settings
│   └── init_data.py (77 lines) - Setup
│
├── 🧠 AI/ML Components
│   ├── qa_system.py (576 lines) - Q&A engine
│   ├── compliance_checker.py (483 lines) - Compliance
│   ├── vector_store.py (176 lines) - Vector DB
│   ├── retrieval_config.py (150 lines) - Retrieval
│   └── prompts_config.py (100 lines) - Prompts
│
├── 💾 Data Management
│   ├── database.py (260 lines) - Database
│   ├── scraper.py (100 lines) - Web scraping
│   ├── update_checker.py (100 lines) - Updates
│   └── document_parser.py (80 lines) - Parsing
│
├── 📧 Notifications
│   ├── email_alerts.py (75 lines) - Email
│   └── daily_scraper.py (51 lines) - Automation
│
└── 📝 Configuration
    ├── requirements.txt - Dependencies
    ├── .env - Environment variables
    ├── sources.csv - Regulation sources
    └── .streamlit/config.toml - Streamlit config
```

---

## 🚀 Quick Access to Key Files

### To understand the main flow:
1. **Start here:** `app.py` (main entry point)
2. **Then read:** `qa_system.py` (how questions are answered)
3. **Then read:** `compliance_checker.py` (how compliance works)

### To understand data flow:
1. **Start here:** `sources.csv` (input)
2. **Then read:** `database.py` (storage)
3. **Then read:** `vector_store.py` (search)

### To customize:
1. **Prompts:** `prompts_config.py`
2. **Retrieval:** `retrieval_config.py`
3. **Settings:** `config.py`

---

## 📖 File-by-File Breakdown

### 1. app.py (967 lines)
**What it does:**
- Creates the Streamlit web interface
- Handles all user interactions
- Routes to different pages
- Manages chat history
- Handles file uploads
- Displays results

**Key functions:**
- `main()` - Entry point
- `show_ip_agent_page()` - Main chat page
- `show_regulation_explorer()` - Browse regulations
- `show_settings()` - Settings page

**Read this to understand:**
- How the UI works
- How user interactions are handled
- How pages are structured

---

### 2. qa_system.py (576 lines)
**What it does:**
- Answers user questions
- Uses RAG (Retrieval Augmented Generation)
- Detects cities from questions
- Filters irrelevant questions
- Handles follow-up questions
- Explains legal jargon

**Key functions:**
- `answer_question()` - Main Q&A
- `answer_question_with_context()` - With chat history
- `_generate_llm_answer()` - LLM processing
- `_detect_city()` - City detection

**Read this to understand:**
- How questions are answered
- How RAG works
- How context is built

---

### 3. compliance_checker.py (483 lines)
**What it does:**
- Analyzes lease documents
- Checks compliance with regulations
- Identifies violations
- Generates action items
- Provides fix suggestions

**Key functions:**
- `check_compliance()` - Main check
- `analyze_clause_compliance()` - Per-clause analysis
- `_generate_action_items()` - Action items
- `refine_clause()` - Generate fixes

**Read this to understand:**
- How compliance checking works
- How violations are detected
- How action items are generated

---

### 4. database.py (260 lines)
**What it does:**
- Manages SQLite database
- Stores regulations
- Manages email subscriptions
- Tracks updates
- Saves compliance checks

**Key functions:**
- `add_regulation()` - Add regulation
- `get_all_regulations()` - Get all
- `subscribe_email()` - Subscribe
- `load_regulations_from_csv()` - Import CSV

**Read this to understand:**
- How data is stored
- Database schema
- Data operations

---

### 5. vector_store.py (176 lines)
**What it does:**
- Manages ChromaDB vector database
- Creates embeddings
- Performs semantic search
- Enhanced retrieval with reranking

**Key functions:**
- `create_embedding()` - Generate embeddings
- `add_regulation_chunks()` - Index content
- `search()` - Semantic search

**Read this to understand:**
- How embeddings work
- How semantic search works
- How retrieval is enhanced

---

### 6. scraper.py (~100 lines)
**What it does:**
- Fetches web content
- Parses HTML
- Extracts text
- Generates content hashes
- Chunks text

**Key functions:**
- `fetch_url_content()` - Get content
- `chunk_text()` - Split text
- `extract_relevant_sections()` - Extract sections

**Read this to understand:**
- How content is fetched
- How text is processed
- How changes are detected

---

### 7. update_checker.py (~100 lines)
**What it does:**
- Detects regulation updates
- Compares content hashes
- Generates summaries
- Identifies affected cities

**Key functions:**
- `check_for_updates()` - Check all
- `_summarize_update()` - Summarize
- `_identify_affected_cities()` - Detect cities

**Read this to understand:**
- How updates are detected
- How summaries are generated

---

### 8. document_parser.py (~80 lines)
**What it does:**
- Parses PDF files
- Parses DOCX files
- Extracts text
- Identifies clauses

**Key functions:**
- `parse_document()` - Main parser
- `_parse_pdf()` - PDF parsing
- `_parse_docx()` - DOCX parsing
- `extract_clauses()` - Extract clauses

**Read this to understand:**
- How documents are parsed
- How text is extracted

---

### 9. email_alerts.py (~75 lines)
**What it does:**
- Sends email notifications
- Sends welcome emails
- Sends update alerts
- Saves to file (fallback)

**Key functions:**
- `send_welcome_email()` - Welcome
- `send_update_alert()` - Update alert
- `notify_subscribers()` - Notify all

**Read this to understand:**
- How emails are sent
- How notifications work

---

### 10. retrieval_config.py (~150 lines)
**What it does:**
- Configures enhanced retrieval
- Enhances queries with terminology
- Calculates source reliability
- Filters by geography
- Reranks results

**Key functions:**
- `enhance_query_with_terminology()` - Enhance query
- `calculate_source_reliability()` - Score sources
- `filter_by_geography()` - Filter by city
- `rerank_results()` - Rerank

**Read this to understand:**
- How retrieval is enhanced
- How queries are improved
- How results are ranked

---

### 11. prompts_config.py (~100 lines)
**What it does:**
- Defines LLM prompts
- Customizable templates
- Context-aware prompts

**Key functions:**
- Prompt templates for Q&A
- Prompt templates for compliance
- Prompt templates for updates

**Read this to understand:**
- How prompts are structured
- How to customize prompts

---

### 12. config.py (53 lines)
**What it does:**
- Centralizes all configuration
- API keys
- Database paths
- City lists
- Categories

**Key variables:**
- `OPENAI_API_KEY`
- `SUPPORTED_CITIES`
- `REGULATION_CATEGORIES`
- `LEGAL_DISCLAIMER`

**Read this to understand:**
- All system settings
- Configuration structure

---

### 13. init_data.py (77 lines)
**What it does:**
- Initializes the system
- Loads from CSV
- Scrapes content
- Indexes in vector store

**Key functions:**
- `initialize_system()` - Main init

**Read this to understand:**
- How system is initialized
- How data is loaded

---

### 14. daily_scraper.py (51 lines)
**What it does:**
- Runs daily update checks
- Automates scraping
- Schedules tasks

**Key functions:**
- `run_daily_check()` - Daily check
- `run_daily_scraper()` - Main loop

**Read this to understand:**
- How automation works
- How daily checks run

---

## 🎯 Recommended Reading Order

### For Understanding the System:
1. `config.py` - Understand settings
2. `app.py` - Understand UI
3. `qa_system.py` - Understand Q&A
4. `compliance_checker.py` - Understand compliance
5. `database.py` - Understand data storage
6. `vector_store.py` - Understand search

### For Customization:
1. `prompts_config.py` - Customize prompts
2. `retrieval_config.py` - Customize retrieval
3. `config.py` - Change settings

### For Adding Features:
1. `app.py` - Add UI elements
2. `database.py` - Add data operations
3. `qa_system.py` or `compliance_checker.py` - Add logic

---

## 📝 Summary

**Total Code:**
- 15 Python files
- ~4,000+ lines of code
- Well-organized and documented

**Main Components:**
- UI: `app.py`
- Q&A: `qa_system.py`
- Compliance: `compliance_checker.py`
- Data: `database.py`, `vector_store.py`
- Scraping: `scraper.py`, `update_checker.py`

**All files are in:**
`C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\`

---

## 🔧 Next Steps

1. **Browse files in your IDE** - Open the folder in Cursor/VS Code
2. **Read key files** - Start with `app.py`, then `qa_system.py`
3. **Understand flow** - Follow data from CSV → Database → Vector Store → Answers
4. **Customize** - Edit `prompts_config.py` and `retrieval_config.py`
5. **Extend** - Add new features by modifying existing files

---

**Created:** 2024
**Last Updated:** 2024

