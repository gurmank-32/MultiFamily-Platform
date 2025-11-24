# Mermaid Architecture Diagrams - Intelligence Platform

Complete architecture diagrams based on the actual codebase implementation.

---

## 🏗️ System Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer - Streamlit"
        UI[app.py<br/>Main Application]
        IP[IP Agent Page<br/>Chat Interface]
        EXP[Regulation Explorer<br/>Browse & Search]
        LOG[Update Log<br/>View Changes]
        EMAIL_UI[Email Alerts<br/>Subscriptions]
        SET[Settings<br/>Data Management]
    end

    subgraph "Core Business Logic Modules"
        QAS[QASystem<br/>qa_system.py<br/>RAG Q&A Engine]
        COMP[ComplianceChecker<br/>compliance_checker.py<br/>Document Analysis]
        SCR[RegulationScraper<br/>scraper.py<br/>Web Scraping]
        UC[UpdateChecker<br/>update_checker.py<br/>Change Detection]
        DP[DocumentParser<br/>document_parser.py<br/>PDF/DOCX Parsing]
        ES[EmailAlertSystem<br/>email_alerts.py<br/>Notifications]
    end

    subgraph "Data Storage Layer"
        DB[(SQLite Database<br/>database.py<br/>regulations.db)]
        VS[ChromaDB Vector Store<br/>vector_store.py<br/>./chroma_db]
        CSV[sources.csv<br/>Regulation URLs]
    end

    subgraph "AI/ML Services"
        OPENAI[OpenAI API<br/>GPT-4o<br/>LLM Processing]
        ST[Sentence Transformers<br/>all-MiniLM-L6-v2<br/>Free Embeddings]
    end

    subgraph "Configuration & Retrieval"
        CFG[config.py<br/>Settings & Secrets]
        PROMPTS[prompts_config.py<br/>LLM Prompts]
        RETRIEVAL[retrieval_config.py<br/>Query Enhancement<br/>Source Prioritization]
    end

    subgraph "External Services"
        WEB[Web URLs<br/>Regulation Sources<br/>HUD, DOJ, City Sites]
        SMTP[SMTP Server<br/>Email Delivery]
        USER_DOCS[User Documents<br/>PDF/DOCX Leases]
    end

    %% UI to Business Logic
    UI --> IP
    UI --> EXP
    UI --> LOG
    UI --> EMAIL_UI
    UI --> SET

    IP --> QAS
    IP --> COMP
    EXP --> VS
    EXP --> DB
    LOG --> UC
    EMAIL_UI --> ES
    SET --> SCR
    SET --> VS
    SET --> DB

    %% Q&A Flow
    QAS --> VS
    QAS --> DB
    QAS --> OPENAI
    QAS --> ST
    QAS --> PROMPTS
    QAS --> RETRIEVAL
    QAS --> CFG

    %% Compliance Check Flow
    COMP --> DP
    COMP --> VS
    COMP --> DB
    COMP --> OPENAI
    COMP --> PROMPTS
    COMP --> RETRIEVAL
    DP --> USER_DOCS

    %% Data Ingestion Flow
    SCR --> CSV
    SCR --> WEB
    SCR --> DB
    SCR --> VS
    SCR --> ST

    %% Update Detection Flow
    UC --> SCR
    UC --> DB
    UC --> OPENAI
    UC --> ES

    %% Email Flow
    ES --> DB
    ES --> SMTP

    %% Vector Store Operations
    VS --> ST
    VS --> OPENAI
    VS --> RETRIEVAL
    VS --> CFG

    %% Configuration
    CFG --> PROMPTS
    CFG --> RETRIEVAL

    style UI fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px
    style QAS fill:#4ecdc4,stroke:#2d8659,stroke-width:2px
    style COMP fill:#4ecdc4,stroke:#2d8659,stroke-width:2px
    style DB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style VS fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style OPENAI fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px
    style ST fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px
```

---

## 🔄 Component Interaction Diagram

```mermaid
graph LR
    subgraph "Input Sources"
        CSV[sources.csv<br/>Regulation URLs]
        WEB_URLS[Web URLs<br/>HUD, DOJ, City Sites]
        USER_FILES[User Documents<br/>PDF/DOCX]
    end

    subgraph "Processing Layer"
        SCR[scraper.py<br/>Fetch & Extract]
        DP[document_parser.py<br/>Parse Documents]
        RETRIEVAL[retrieval_config.py<br/>Enhance Queries]
    end

    subgraph "Storage Layer"
        DB[database.py<br/>SQLite<br/>Metadata]
        VS[vector_store.py<br/>ChromaDB<br/>Embeddings]
    end

    subgraph "AI Processing"
        QAS[qa_system.py<br/>RAG Q&A]
        COMP[compliance_checker.py<br/>Analysis]
        UC[update_checker.py<br/>Change Detection]
    end

    subgraph "Output Layer"
        UI[app.py<br/>Streamlit UI]
        EMAIL[email_alerts.py<br/>Notifications]
    end

    CSV --> SCR
    WEB_URLS --> SCR
    SCR --> DB
    SCR --> VS
    USER_FILES --> DP
    DP --> COMP
    COMP --> VS
    COMP --> QAS
    QAS --> VS
    QAS --> DB
    QAS --> RETRIEVAL
    UC --> SCR
    UC --> DB
    UC --> EMAIL
    QAS --> UI
    COMP --> UI
    DB --> UI
    VS --> UI

    style CSV fill:#e9ecef
    style WEB_URLS fill:#e9ecef
    style USER_FILES fill:#e9ecef
    style UI fill:#ff6b6b
    style EMAIL fill:#ff6b6b
```

---

## 📊 Data Flow: Q&A (RAG Pipeline)

```mermaid
sequenceDiagram
    participant User
    participant Streamlit as app.py
    participant QASystem as qa_system.py
    participant Retrieval as retrieval_config.py
    participant VectorStore as vector_store.py
    participant ChromaDB as ChromaDB
    participant Database as database.py
    participant OpenAI as OpenAI API
    participant SentenceTrans as Sentence Transformers

    User->>Streamlit: Ask Question
    Streamlit->>QASystem: answer_question_with_context()
    
    QASystem->>QASystem: _validate_question()
    QASystem->>QASystem: _check_relevance()
    QASystem->>QASystem: _detect_city()
    
    QASystem->>Retrieval: enhance_query_with_terminology()
    Retrieval-->>QASystem: Enhanced Query
    
    QASystem->>VectorStore: search(query, context, filter_geography)
    VectorStore->>Retrieval: enhance_query_with_terminology()
    VectorStore->>SentenceTrans: create_embedding() [Free Mode]
    SentenceTrans-->>VectorStore: Embedding Vector
    VectorStore->>ChromaDB: query(query_embedding, n_results)
    ChromaDB-->>VectorStore: Similar Regulations
    VectorStore->>Retrieval: filter_by_geography()
    VectorStore->>Retrieval: rerank_results()
    VectorStore-->>QASystem: Top Relevant Regulations
    
    QASystem->>Database: get_recent_updates()
    Database-->>QASystem: Recent Updates
    
    QASystem->>QASystem: Build Context String
    
    alt OpenAI API Available
        QASystem->>OpenAI: _generate_llm_answer()
        OpenAI-->>QASystem: Detailed Answer
    else Free Mode
        QASystem->>QASystem: _extract_answer_from_context()
        QASystem-->>QASystem: Keyword-based Answer
    end
    
    QASystem-->>Streamlit: Answer + Sources
    Streamlit-->>User: Display Answer with Sources
```

---

## 📋 Data Flow: Compliance Checking

```mermaid
sequenceDiagram
    participant User
    participant Streamlit as app.py
    participant Compliance as compliance_checker.py
    participant Parser as document_parser.py
    participant VectorStore as vector_store.py
    participant ChromaDB as ChromaDB
    participant Database as database.py
    participant OpenAI as OpenAI API

    User->>Streamlit: Upload Document (PDF/DOCX)
    User->>Streamlit: Select City
    Streamlit->>Compliance: check_compliance(document, city)
    
    Compliance->>Parser: parse_document(file_content, filename)
    alt PDF File
        Parser->>Parser: parse_pdf() [PyPDF2]
    else DOCX File
        Parser->>Parser: parse_docx() [python-docx]
    end
    Parser-->>Compliance: Document Text
    
    Compliance->>Compliance: extract_clauses()
    Compliance-->>Compliance: List of Clauses
    
    loop For Each Clause
        Compliance->>VectorStore: search(clause_text, city)
        VectorStore->>ChromaDB: Semantic Search
        ChromaDB-->>VectorStore: Relevant Regulations
        VectorStore-->>Compliance: Top 5 Regulations
        
        alt OpenAI API Available
            Compliance->>OpenAI: _analyze_clause_with_openai()
            OpenAI-->>Compliance: Compliance Analysis
        else Free Mode
            Compliance->>Compliance: _analyze_clause_free_mode()
            Compliance-->>Compliance: Rule-based Analysis
        end
    end
    
    Compliance->>Compliance: _generate_action_items()
    Compliance->>Database: Store Check Results (optional)
    Compliance-->>Streamlit: Compliance Report
    Streamlit-->>User: Display Report with Issues & Fixes
```

---

## 🔄 Data Flow: Regulation Ingestion

```mermaid
flowchart TD
    START[User Clicks: Load Regulations from CSV] --> READ[Read sources.csv]
    READ --> LOOP{For Each URL}
    
    LOOP --> FETCH[scraper.py: fetch_regulation_content]
    FETCH --> EXTRACT[Extract Text with BeautifulSoup]
    EXTRACT --> CLEAN[Clean & Normalize Text]
    CLEAN --> HASH[Calculate Content Hash]
    HASH --> CHECK{Exists in DB?}
    
    CHECK -->|No| SAVE_DB[Save to SQLite<br/>database.py]
    CHECK -->|Yes| SKIP[Skip Duplicate]
    
    SAVE_DB --> CHUNK[Chunk Text into Segments]
    CHUNK --> EMBED[Create Embeddings]
    
    EMBED --> EMBED_CHECK{API Key Available?}
    EMBED_CHECK -->|Yes| OPENAI_EMBED[OpenAI: text-embedding-3-small]
    EMBED_CHECK -->|No| FREE_EMBED[Sentence Transformers: all-MiniLM-L6-v2]
    
    OPENAI_EMBED --> STORE
    FREE_EMBED --> STORE
    
    STORE[Store in ChromaDB<br/>vector_store.py]
    STORE --> METADATA[Add Metadata:<br/>- source_name<br/>- category<br/>- city<br/>- url]
    METADATA --> NEXT{More URLs?}
    
    NEXT -->|Yes| LOOP
    NEXT -->|No| DONE[Complete!]
    SKIP --> NEXT
    
    style START fill:#ff6b6b
    style DONE fill:#51cf66
    style OPENAI_EMBED fill:#6c5ce7
    style FREE_EMBED fill:#6c5ce7
```

---

## 🔔 Data Flow: Update Detection & Email Alerts

```mermaid
sequenceDiagram
    participant Scheduler as daily_scraper.py
    participant UpdateChecker as update_checker.py
    participant Scraper as scraper.py
    participant Database as database.py
    participant OpenAI as OpenAI API
    participant EmailSystem as email_alerts.py
    participant SMTP as SMTP Server
    participant Subscribers

    Note over Scheduler: Daily at 9 AM (or Manual Trigger)
    Scheduler->>UpdateChecker: check_for_updates()
    
    UpdateChecker->>Database: get_all_regulations()
    Database-->>UpdateChecker: List of Regulations
    
    loop For Each Regulation
        UpdateChecker->>Scraper: fetch_regulation_content(url)
        Scraper->>Scraper: Fetch from Web
        Scraper-->>UpdateChecker: Current Content
        
        UpdateChecker->>UpdateChecker: Calculate Hash
        UpdateChecker->>Database: Compare with Stored Hash
        
        alt Hash Changed
            UpdateChecker->>OpenAI: Generate Summary (if API available)
            OpenAI-->>UpdateChecker: Update Summary
            UpdateChecker->>UpdateChecker: Detect Affected Cities
            UpdateChecker->>Database: save_update()
            UpdateChecker->>EmailSystem: Notify Subscribers
        else No Change
            UpdateChecker->>UpdateChecker: Skip
        end
    end
    
    EmailSystem->>Database: get_subscribers_for_city(city)
    Database-->>EmailSystem: Subscriber List
    
    loop For Each Subscriber
        EmailSystem->>EmailSystem: Generate Email Content
        EmailSystem->>SMTP: Send Email
        SMTP-->>Subscribers: Email Alert
    end
    
    Note over Scheduler,Subscribers: Daily Summary Reports
    Scheduler->>EmailSystem: send_daily_summaries_to_all_subscribers()
    EmailSystem->>Database: Get All Subscriptions
    EmailSystem->>Database: Get Updates for Last 24 Hours
    EmailSystem->>SMTP: Send Daily Summary
    SMTP-->>Subscribers: Daily Summary Email
```

---

## 🗂️ Module Dependency Graph

```mermaid
graph TD
    subgraph "Entry Point"
        APP[app.py]
    end

    subgraph "Core Modules"
        QA[qa_system.py]
        COMP[compliance_checker.py]
        SCR[scraper.py]
        UC[update_checker.py]
        ES[email_alerts.py]
    end

    subgraph "Supporting Modules"
        DB[database.py]
        VS[vector_store.py]
        DP[document_parser.py]
        RET[retrieval_config.py]
        PROMPTS[prompts_config.py]
    end

    subgraph "Configuration"
        CFG[config.py]
    end

    APP --> QA
    APP --> COMP
    APP --> SCR
    APP --> UC
    APP --> ES
    APP --> DB
    APP --> VS
    APP --> CFG

    QA --> VS
    QA --> DB
    QA --> PROMPTS
    QA --> RET
    QA --> CFG

    COMP --> DP
    COMP --> VS
    COMP --> DB
    COMP --> PROMPTS
    COMP --> RET
    COMP --> CFG

    SCR --> DB
    SCR --> VS
    SCR --> RET

    UC --> SCR
    UC --> DB
    UC --> ES

    ES --> DB
    ES --> CFG

    VS --> RET
    VS --> CFG

    CFG --> PROMPTS

    style APP fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px
    style QA fill:#4ecdc4,stroke:#2d8659,stroke-width:2px
    style COMP fill:#4ecdc4,stroke:#2d8659,stroke-width:2px
    style DB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style VS fill:#ffd93d,stroke:#f59f00,stroke-width:2px
```

---

## 🔍 RAG (Retrieval Augmented Generation) Architecture

```mermaid
graph TB
    subgraph "Query Processing"
        Q[User Question]
        VAL[Validate & Check Relevance]
        CITY[Detect City]
        ENHANCE[Enhance Query with Terminology]
    end

    subgraph "Retrieval Layer"
        EMBED[Create Embedding<br/>Sentence Transformers or OpenAI]
        SEARCH[Vector Search in ChromaDB]
        FILTER[Filter by Geography]
        RERANK[Rerank by Source Reliability]
        TOP[Top K Results]
    end

    subgraph "Context Building"
        REGS[Relevant Regulations]
        UPDATES[Recent Updates]
        HISTORY[Chat History]
        CONTEXT[Build Context String]
    end

    subgraph "Generation Layer"
        PROMPT[Build LLM Prompt]
        LLM{API Available?}
        GPT4[GPT-4o Generation]
        FREE[Free Mode: Extract from Context]
        ANSWER[Final Answer]
    end

    subgraph "Response"
        SOURCES[Source Links]
        DISPLAY[Display to User]
    end

    Q --> VAL
    VAL --> CITY
    CITY --> ENHANCE
    ENHANCE --> EMBED
    EMBED --> SEARCH
    SEARCH --> FILTER
    FILTER --> RERANK
    RERANK --> TOP
    TOP --> REGS
    REGS --> CONTEXT
    UPDATES --> CONTEXT
    HISTORY --> CONTEXT
    CONTEXT --> PROMPT
    PROMPT --> LLM
    LLM -->|Yes| GPT4
    LLM -->|No| FREE
    GPT4 --> ANSWER
    FREE --> ANSWER
    ANSWER --> SOURCES
    SOURCES --> DISPLAY

    style Q fill:#ff6b6b
    style ANSWER fill:#51cf66
    style GPT4 fill:#6c5ce7
    style FREE fill:#6c5ce7
```

---

## 📁 File Structure with Relationships

```mermaid
graph LR
    subgraph "Root Directory"
        APP[app.py]
        CONFIG[config.py]
        CSV[sources.csv]
    end

    subgraph "Core Logic"
        QA[qa_system.py]
        COMP[compliance_checker.py]
        SCR[scraper.py]
        UC[update_checker.py]
        ES[email_alerts.py]
    end

    subgraph "Data Layer"
        DB[database.py]
        VS[vector_store.py]
        DP[document_parser.py]
    end

    subgraph "Configuration"
        PROMPTS[prompts_config.py]
        RET[retrieval_config.py]
    end

    subgraph "Storage"
        SQLITE[(regulations.db)]
        CHROMA[(chroma_db/)]
    end

    APP --> QA
    APP --> COMP
    APP --> SCR
    APP --> UC
    APP --> ES
    APP --> CONFIG

    QA --> VS
    QA --> DB
    QA --> PROMPTS
    QA --> RET

    COMP --> DP
    COMP --> VS
    COMP --> DB
    COMP --> PROMPTS

    SCR --> CSV
    SCR --> DB
    SCR --> VS

    UC --> SCR
    UC --> DB
    UC --> ES

    ES --> DB

    VS --> CHROMA
    DB --> SQLITE

    CONFIG --> PROMPTS
    CONFIG --> RET

    style APP fill:#ff6b6b
    style SQLITE fill:#ffd93d
    style CHROMA fill:#ffd93d
```

---

## 🎯 Technology Stack Visualization

```mermaid
mindmap
  root((Intelligence Platform))
    Frontend
      Streamlit
      Python 3.13
      Multi-page UI
    AI/ML
      OpenAI GPT-4o
      Sentence Transformers
      PyTorch
      RAG Architecture
    Databases
      SQLite
        Metadata
        Updates
        Subscriptions
      ChromaDB
        Vector Store
        Embeddings
        Semantic Search
    Processing
      Web Scraping
        BeautifulSoup
        Requests
      Document Parsing
        PyPDF2
        python-docx
      Data Manipulation
        Pandas
        NumPy
    Configuration
      config.py
      prompts_config.py
      retrieval_config.py
      .env / Secrets
    External
      OpenAI API
      SMTP Server
      Web URLs
```

---

## 📝 Notes

- **All diagrams are based on actual code** from the project
- **Module names match actual file names** in the codebase
- **Data flows reflect real function calls** and interactions
- **Technology choices** match `requirements.txt` and imports

---

**Last Updated**: November 2024  
**Based on**: Actual codebase analysis

