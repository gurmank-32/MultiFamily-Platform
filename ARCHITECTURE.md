# Housing Regulation Compliance Agent - Architecture

## Is This Agentic AI?

**Partially Yes** - This system combines:
- **RAG (Retrieval Augmented Generation)** - Main architecture
- **Agentic Components** - Autonomous update checking, email notifications
- **Traditional AI** - LLM-powered analysis and Q&A

### Agentic Features:
✅ **Autonomous Update Detection** - Daily scraping without user input
✅ **Proactive Email Alerts** - Notifies users automatically
✅ **Self-Managing Database** - Tracks changes and updates
✅ **Intelligent Routing** - Routes questions to appropriate handlers

### Non-Agentic (Reactive) Features:
- Q&A system responds to user queries
- Compliance checking requires user upload
- Manual regulation loading

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
│                    (Streamlit Web App)                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐         │
│  │   Home   │ │   Q&A    │ │Compliance│ │  Email   │         │
│  │   Page   │ │   Page   │ │ Checker  │ │  Alerts  │         │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LOGIC LAYER                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  QASystem    │  │ Compliance   │  │ Update       │         │
│  │              │  │ Checker      │  │ Checker      │         │
│  │ - RAG Query  │  │ - Document   │  │ - Hash       │         │
│  │ - City       │  │   Parsing    │  │   Compare    │         │
│  │   Detection  │  │ - Clause     │  │ - LLM        │         │
│  │ - LLM        │  │   Analysis   │  │   Summary    │         │
│  │   Answer     │  │ - Action     │  │ - City       │         │
│  │              │  │   Items      │  │   Detection  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Scraper     │  │  Email       │  │  Document    │         │
│  │              │  │  Alerts      │  │  Parser      │         │
│  │ - Web Fetch  │  │ - Welcome    │  │ - PDF        │         │
│  │ - Text       │  │   Email      │  │   Parsing    │         │
│  │   Extract    │  │ - Update     │  │ - DOCX       │         │
│  │ - Hash       │  │   Alerts     │  │   Parsing    │         │
│  │   Compute    │  │ - Unsubscribe│  │ - Clause     │         │
│  │              │  │              │  │   Extraction │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA & AI LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  Vector      │  │  Database    │  │  LLM         │         │
│  │  Store       │  │  (SQLite)    │  │  (OpenAI)    │         │
│  │              │  │              │  │              │         │
│  │ - ChromaDB   │  │ - Regulations│  │ - GPT-4     │         │
│  │ - Free       │  │ - Updates    │  │   Turbo     │         │
│  │   Embeddings │  │ - Email      │  │ - Embeddings│         │
│  │   (Sentence  │  │   Subscriptions│ │   (optional)│         │
│  │   Transformers)│ │ - Compliance │  │              │         │
│  │ - Semantic   │  │   Checks     │  │              │         │
│  │   Search     │  │              │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  sources.csv │  │  Web URLs    │  │  User        │         │
│  │              │  │  (Scraping)  │  │  Documents   │         │
│  │ - Regulation │  │ - HUD        │  │ - PDF Leases │         │
│  │   Links      │  │ - DOJ        │  │ - DOCX Leases│         │
│  │ - Categories │  │ - City Codes │  │              │         │
│  │ - Types      │  │ - State Laws │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Flow Diagrams

### 1. Q&A Flow (RAG Pipeline)

```
User Question
    │
    ▼
[City Detection] ──→ Extract city from question
    │
    ▼
[Scope Check] ──→ Is it Texas? ──→ NO ──→ Return "Out of Scope"
    │                                   
    YES                                
    │
    ▼
[Vector Search] ──→ Search regulations (ChromaDB)
    │
    ▼
[Context Retrieval] ──→ Get top 7 relevant regulations
    │
    ▼
[LLM Processing] ──→ Generate answer (GPT-4 or Free Mode)
    │
    ▼
[Answer + Sources] ──→ Return to user
```

### 2. Compliance Check Flow

```
User Uploads Document
    │
    ▼
[Document Parser] ──→ Extract text (PDF/DOCX)
    │
    ▼
[Clause Extraction] ──→ Split into clauses
    │
    ▼
[Vector Search] ──→ Find relevant regulations for each clause
    │
    ▼
[LLM Analysis] ──→ Check compliance per clause
    │
    ▼
[Issue Detection] ──→ Identify violations
    │
    ▼
[Action Items] ──→ Generate specific fixes
    │
    ▼
[Report] ──→ Return compliance report
```

### 3. Daily Update Flow (Agentic)

```
[Scheduled Task] ──→ Daily at 9 AM
    │
    ▼
[Fetch All URLs] ──→ From database
    │
    ▼
[Scrape Content] ──→ Get current content
    │
    ▼
[Hash Compare] ──→ Compare with stored hash
    │
    ├─→ NO CHANGE ──→ Skip
    │
    CHANGE
    │
    ▼
[LLM Summary] ──→ Generate update summary
    │
    ▼
[City Detection] ──→ Detect affected cities
    │
    ▼
[Save Update] ──→ Store in database
    │
    ▼
[Email Subscribers] ──→ Send alerts automatically
```

### 4. Email Subscription Flow

```
User Subscribes
    │
    ▼
[Save to DB] ──→ Store email + city
    │
    ▼
[Send Welcome Email] ──→ SMTP
    │
    ▼
[Update Detected] ──→ Daily scraper finds change
    │
    ▼
[Get Subscribers] ──→ Query database
    │
    ▼
[Send Alert] ──→ Email notification
```

---

## Technology Stack

### Frontend
- **Streamlit** - Web UI framework

### Backend
- **Python 3.13** - Main language
- **SQLite** - Database
- **ChromaDB** - Vector database

### AI/ML
- **OpenAI GPT-4 Turbo** - LLM (optional, requires API key)
- **Sentence Transformers** - Free embeddings (all-MiniLM-L6-v2)
- **LangChain** - (Available but not heavily used)

### Data Processing
- **BeautifulSoup4** - Web scraping
- **PyPDF2** - PDF parsing
- **python-docx** - DOCX parsing
- **pandas** - Data manipulation

### Utilities
- **schedule** - Daily task scheduling
- **smtplib** - Email sending
- **requests** - HTTP requests

---

## File Structure

```
Agent Intellectual Platform/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── database.py              # SQLite database operations
├── scraper.py               # Web scraping module
├── vector_store.py          # ChromaDB vector store
├── qa_system.py             # Q&A RAG system
├── compliance_checker.py    # Compliance analysis
├── document_parser.py       # PDF/DOCX parsing
├── update_checker.py        # Update detection
├── email_alerts.py          # Email notification system
├── daily_scraper.py         # Scheduled daily updates
├── init_data.py             # Data initialization script
├── test_system.py           # System testing
├── requirements.txt         # Python dependencies
├── sources.csv              # Regulation sources
├── .env                     # Environment variables
├── .streamlit/
│   └── config.toml         # Streamlit config
└── chroma_db/              # Vector database (created at runtime)
```

---

## Data Flow

1. **Initialization:**
   - Load `sources.csv` → Database
   - Scrape URLs → Extract text → Chunk → Embed → Vector Store

2. **Query Processing:**
   - User question → City detection → Vector search → LLM answer

3. **Compliance Check:**
   - Upload document → Parse → Extract clauses → Search regulations → LLM analysis → Report

4. **Update Detection:**
   - Daily scrape → Hash compare → If changed → Summarize → Email subscribers

---

## Agentic vs Non-Agentic

### Agentic Components (Autonomous):
- ✅ Daily scraper runs automatically
- ✅ Email alerts sent proactively
- ✅ Update detection without user input
- ✅ City detection from questions

### Non-Agentic (Reactive):
- User-triggered Q&A
- User-uploaded compliance checks
- Manual regulation loading

**Overall:** Hybrid system - RAG-based with agentic automation features.
