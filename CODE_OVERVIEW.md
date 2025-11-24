# Complete Code Overview

## Where to Find Everything

All code is in: `C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\`

---

## Core Application Files

### 1. **app.py** (Main Application)
- **Purpose:** Streamlit web interface
- **Key Functions:**
  - `main()` - Entry point, routing
  - `show_qa_page()` - Q&A interface
  - `show_compliance_checker()` - Document upload & analysis
  - `show_email_alerts()` - Subscription management
  - `show_settings()` - Data management
- **Lines:** ~450

### 2. **config.py** (Configuration)
- **Purpose:** All settings and constants
- **Key Variables:**
  - `OPENAI_API_KEY` - API configuration
  - `SUPPORTED_CITIES` - City list
  - `REGULATION_CATEGORIES` - Category list
  - `LEGAL_DISCLAIMER` - Disclaimer text
- **Lines:** ~50

### 3. **database.py** (Data Storage)
- **Purpose:** SQLite database operations
- **Key Classes:**
  - `RegulationDB` - All database operations
- **Key Methods:**
  - `add_regulation()` - Store regulations
  - `subscribe_email()` - Email subscriptions
  - `unsubscribe_email()` - Unsubscribe
  - `get_recent_updates()` - Get updates
- **Lines:** ~230

### 4. **qa_system.py** (Q&A Engine)
- **Purpose:** RAG-based question answering
- **Key Classes:**
  - `QASystem` - Main Q&A handler
- **Key Methods:**
  - `answer_question()` - Main Q&A logic
  - `_generate_llm_answer()` - LLM processing
  - `_extract_answer_from_context()` - Free mode
- **Features:**
  - City auto-detection
  - Scope checking (Texas only)
  - Basic definition answers
  - Scenario question handling
- **Lines:** ~220

### 5. **compliance_checker.py** (Compliance Analysis)
- **Purpose:** Document compliance checking
- **Key Classes:**
  - `ComplianceChecker` - Main checker
- **Key Methods:**
  - `check_compliance()` - Main analysis
  - `analyze_clause_compliance()` - Per-clause analysis
  - `_generate_action_items()` - Action item generation
- **Features:**
  - ESA violation detection
  - Fair Housing checks
  - Action items generation
- **Lines:** ~250

### 6. **vector_store.py** (Vector Database)
- **Purpose:** ChromaDB integration & embeddings
- **Key Classes:**
  - `RegulationVectorStore` - Vector operations
- **Key Methods:**
  - `create_embedding()` - Generate embeddings
  - `add_regulation_chunks()` - Index regulations
  - `search()` - Semantic search
- **Features:**
  - Free embeddings (Sentence Transformers)
  - OpenAI embeddings (fallback)
- **Lines:** ~105

### 7. **scraper.py** (Web Scraping)
- **Purpose:** Fetch regulation content
- **Key Classes:**
  - `RegulationScraper` - Web scraper
- **Key Methods:**
  - `fetch_url_content()` - Get web content
  - `chunk_text()` - Text chunking
- **Lines:** ~60

### 8. **document_parser.py** (Document Parsing)
- **Purpose:** Parse PDF/DOCX files
- **Key Classes:**
  - `DocumentParser` - Document parser
- **Key Methods:**
  - `parse_document()` - Main parser
  - `extract_clauses()` - Clause extraction
- **Lines:** ~80

### 9. **update_checker.py** (Update Detection)
- **Purpose:** Detect regulation changes
- **Key Classes:**
  - `UpdateChecker` - Update detector
- **Key Methods:**
  - `check_for_updates()` - Main check
  - `generate_update_summary()` - LLM summary
  - `detect_affected_cities()` - City detection
- **Lines:** ~85

### 10. **email_alerts.py** (Email System)
- **Purpose:** Email notifications
- **Key Classes:**
  - `EmailAlertSystem` - Email handler
- **Key Methods:**
  - `send_welcome_email()` - Welcome message
  - `send_update_alert()` - Update notifications
  - `notify_subscribers()` - Bulk notifications
- **Lines:** ~75

### 11. **daily_scraper.py** (Scheduled Tasks)
- **Purpose:** Daily automatic updates
- **Key Classes:**
  - `DailyScraper` - Scheduler
- **Key Methods:**
  - `run_daily_check()` - Daily execution
  - `start_scheduler()` - Schedule setup
- **Lines:** ~50

---

## Configuration Files

### **requirements.txt**
All Python packages needed:
- streamlit, openai, chromadb
- sentence-transformers, torch
- pandas, beautifulsoup4
- PyPDF2, python-docx
- etc.

### **.env**
Environment variables:
- `OPENAI_API_KEY`
- `SMTP_EMAIL`, `SMTP_PASSWORD`
- etc.

### **.streamlit/config.toml**
Streamlit configuration

### **sources.csv**
Regulation sources (71 entries)

---

## Data Files

### **regulations.db** (SQLite)
Created at runtime, contains:
- `regulations` table
- `updates` table
- `email_alerts` table
- `compliance_checks` table

### **chroma_db/** (Directory)
ChromaDB vector store (created at runtime)

---

## How to View All Code

### Option 1: In Cursor/VS Code
1. Open the folder in Cursor
2. Use file explorer (left sidebar)
3. Click any `.py` file to view

### Option 2: Command Line
```powershell
# List all Python files
Get-ChildItem -Filter *.py

# View a specific file
Get-Content app.py

# Count lines of code
Get-ChildItem -Filter *.py | ForEach-Object { (Get-Content $_.FullName | Measure-Object -Line).Lines }
```

### Option 3: File Explorer
Navigate to:
`C:\Users\safaa\OneDrive\Desktop\Agent Intellectual Platform\`

---

## Package Dependencies

See `requirements.txt` for complete list. Main packages:

**Core:**
- streamlit (web UI)
- openai (LLM)
- chromadb (vector DB)

**AI/ML:**
- sentence-transformers (free embeddings)
- torch (ML framework)

**Data:**
- pandas (data processing)
- beautifulsoup4 (web scraping)
- PyPDF2, python-docx (document parsing)

**Utilities:**
- python-dotenv (config)
- schedule (task scheduling)
- smtplib (email, built-in)

---

## Total Code Statistics

- **Python Files:** ~11 core files
- **Total Lines:** ~1,500+ lines of code
- **Configuration Files:** 4 files
- **Documentation:** 10+ markdown files

---

## Quick Access Commands

```powershell
# View all files
Get-ChildItem

# View Python files only
Get-ChildItem *.py

# View code in a file
Get-Content app.py | more

# Search for a function
Select-String -Pattern "def answer_question" *.py
```
