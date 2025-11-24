# System Architecture - Mermaid Diagrams

## Complete System Architecture

```mermaid
graph TB
    subgraph "User Interface Layer"
        UI[Streamlit Web App<br/>app.py]
        UI --> |User Questions| QA[Q&A Interface]
        UI --> |Document Upload| CC[Compliance Checker UI]
        UI --> |Settings| SET[Settings Page]
        UI --> |Alerts| EMAIL[Email Alerts Page]
        UI --> |Explorer| EXP[Regulation Explorer]
    end

    subgraph "Core Business Logic"
        QAS[QASystem<br/>qa_system.py]
        COMP[ComplianceChecker<br/>compliance_checker.py]
        SCR[RegulationScraper<br/>scraper.py]
        UC[UpdateChecker<br/>update_checker.py]
        DP[DocumentParser<br/>document_parser.py]
        ES[EmailAlertSystem<br/>email_alerts.py]
    end

    subgraph "Data Storage Layer"
        DB[(SQLite Database<br/>regulations.db<br/>database.py)]
        VS[ChromaDB Vector Store<br/>vector_store.py]
        CSV[sources.csv<br/>Regulation Sources]
    end

    subgraph "External Services"
        OPENAI[OpenAI API<br/>GPT-4o]
        ST[Sentence Transformers<br/>all-MiniLM-L6-v2<br/>Free Embeddings]
        SMTP[SMTP Server<br/>Email Delivery]
    end

    subgraph "Configuration"
        CFG[config.py<br/>Settings & Constants]
        PROMPTS[prompts_config.py<br/>Custom Prompts]
        ENV[.env<br/>API Keys & Secrets]
    end

    %% User Interactions
    QA --> QAS
    CC --> COMP
    SET --> SCR
    EMAIL --> ES
    EXP --> VS

    %% Q&A Flow
    QAS --> VS
    QAS --> DB
    QAS --> |Uses| OPENAI
    QAS --> |Uses| PROMPTS
    QAS --> |Fallback| ST

    %% Compliance Check Flow
    COMP --> DP
    COMP --> VS
    COMP --> |Uses| OPENAI
    COMP --> |Uses| PROMPTS
    DP --> |Parses| PDF[PDF Documents]
    DP --> |Parses| DOCX[DOCX Documents]

    %% Data Ingestion Flow
    SCR --> CSV
    SCR --> |Fetches| WEB[Web URLs]
    SCR --> |Fetches| FILE[Local Files]
    SCR --> DB
    SCR --> VS
    VS --> |Embeddings| ST
    VS --> |Optional| OPENAI

    %% Update Detection Flow
    UC --> DB
    UC --> SCR
    UC --> |Uses| OPENAI
    UC --> ES
    ES --> SMTP
    ES --> |Fallback| FILE_EMAIL[Local Email Files]

    %% Configuration
    CFG --> ENV
    QAS --> CFG
    COMP --> CFG
    SCR --> CFG
    UC --> CFG
    ES --> CFG

    %% Styling
    classDef uiClass fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef logicClass fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef dataClass fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef extClass fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef configClass fill:#fce4ec,stroke:#880e4f,stroke-width:2px

    class UI,QA,CC,SET,EMAIL,EXP uiClass
    class QAS,COMP,SCR,UC,DP,ES logicClass
    class DB,VS,CSV dataClass
    class OPENAI,ST,SMTP,WEB,FILE,PDF,DOCX extClass
    class CFG,PROMPTS,ENV,FILE_EMAIL configClass
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant Streamlit as Streamlit App
    participant QASystem as Q&A System
    participant VectorStore as ChromaDB
    participant Database as SQLite DB
    participant OpenAI as OpenAI API
    participant Scraper as Regulation Scraper
    participant UpdateChecker as Update Checker
    participant EmailSystem as Email Alerts

    Note over User,EmailSystem: Q&A Flow
    User->>Streamlit: Ask Question
    Streamlit->>QASystem: Process Question
    QASystem->>VectorStore: Search Regulations
    VectorStore-->>QASystem: Relevant Regulations
    QASystem->>OpenAI: Generate Answer (if API available)
    OpenAI-->>QASystem: Detailed Answer
    QASystem->>Database: Check Recent Updates
    Database-->>QASystem: Update Info
    QASystem-->>Streamlit: Formatted Answer + Sources
    Streamlit-->>User: Display Answer

    Note over User,EmailSystem: Compliance Check Flow
    User->>Streamlit: Upload Lease Document
    Streamlit->>QASystem: Document + City
    QASystem->>VectorStore: Find Relevant Regulations
    VectorStore-->>QASystem: Regulation Context
    QASystem->>OpenAI: Analyze Each Clause
    OpenAI-->>QASystem: Compliance Analysis
    QASystem->>Database: Save Check Results
    QASystem-->>Streamlit: Compliance Report
    Streamlit-->>User: Display Results

    Note over User,EmailSystem: Regulation Ingestion Flow
    User->>Streamlit: Load Regulations (Settings)
    Streamlit->>Scraper: Read sources.csv
    Scraper->>Scraper: Fetch from URLs/Files
    Scraper->>Database: Store Regulation Metadata
    Scraper->>VectorStore: Create Embeddings
    VectorStore->>VectorStore: Store in ChromaDB
    Scraper-->>Streamlit: Load Complete

    Note over User,EmailSystem: Update Detection Flow
    UpdateChecker->>Database: Get All Regulations
    UpdateChecker->>Scraper: Re-fetch Content
    Scraper-->>UpdateChecker: Current Content
    UpdateChecker->>UpdateChecker: Compare Hashes
    UpdateChecker->>OpenAI: Generate Summary (if changed)
    OpenAI-->>UpdateChecker: Update Summary
    UpdateChecker->>Database: Store Update
    UpdateChecker->>EmailSystem: Send Alerts
    EmailSystem->>EmailSystem: Send to Subscribers
```

## Component Interaction Diagram

```mermaid
graph LR
    subgraph "Input Sources"
        CSV[sources.csv]
        WEB[Web URLs]
        LOCAL[Local Files]
        USER_DOC[User Documents]
    end

    subgraph "Processing Layer"
        SCR[Scraper<br/>Fetches & Parses]
        DP[Document Parser<br/>PDF/DOCX]
        VS[Vector Store<br/>Embeddings & Search]
    end

    subgraph "Analysis Layer"
        QAS[Q&A System<br/>RAG + LLM]
        COMP[Compliance<br/>Checker]
        UC[Update<br/>Checker]
    end

    subgraph "Storage"
        DB[(SQLite<br/>Metadata)]
        CHROMA[(ChromaDB<br/>Vectors)]
    end

    subgraph "Output"
        UI[Streamlit UI]
        EMAIL[Email Alerts]
    end

    CSV --> SCR
    WEB --> SCR
    LOCAL --> SCR
    USER_DOC --> DP

    SCR --> DB
    SCR --> VS
    DP --> COMP
    VS --> CHROMA

    DB --> QAS
    CHROMA --> QAS
    DB --> COMP
    CHROMA --> COMP
    DB --> UC

    QAS --> UI
    COMP --> UI
    UC --> EMAIL
    UC --> UI

    style CSV fill:#e3f2fd
    style WEB fill:#e3f2fd
    style LOCAL fill:#e3f2fd
    style USER_DOC fill:#e3f2fd
    style SCR fill:#f3e5f5
    style DP fill:#f3e5f5
    style VS fill:#f3e5f5
    style QAS fill:#fff3e0
    style COMP fill:#fff3e0
    style UC fill:#fff3e0
    style DB fill:#e8f5e9
    style CHROMA fill:#e8f5e9
    style UI fill:#fce4ec
    style EMAIL fill:#fce4ec
```

## Technology Stack Diagram

```mermaid
graph TB
    subgraph "Frontend"
        STREAMLIT[Streamlit<br/>Python Web Framework]
    end

    subgraph "Backend - Python Modules"
        APP[app.py<br/>Main Application]
        QA[qa_system.py<br/>Q&A Engine]
        COMP[compliance_checker.py<br/>Document Analysis]
        SCR[scraper.py<br/>Web Scraping]
        DB_MOD[database.py<br/>SQLite Operations]
        VEC[vector_store.py<br/>Vector Operations]
        PARSE[document_parser.py<br/>PDF/DOCX Parsing]
        UPDATE[update_checker.py<br/>Change Detection]
        EMAIL_MOD[email_alerts.py<br/>Notifications]
    end

    subgraph "AI/ML Services"
        OPENAI_API[OpenAI GPT-4o<br/>LLM for Q&A & Analysis]
        SENT_TRANS[Sentence Transformers<br/>Free Embeddings]
    end

    subgraph "Data Storage"
        SQLITE[(SQLite<br/>regulations.db)]
        CHROMA[(ChromaDB<br/>Vector Database)]
        CSV_FILE[sources.csv<br/>Regulation URLs]
    end

    subgraph "Configuration"
        CONFIG[config.py<br/>Settings]
        PROMPTS[prompts_config.py<br/>Custom Prompts]
        ENV_FILE[.env<br/>Secrets]
    end

    subgraph "External"
        WEB_URLS[Web URLs<br/>Regulation Sources]
        SMTP_SERVER[SMTP Server<br/>Email Delivery]
    end

    STREAMLIT --> APP
    APP --> QA
    APP --> COMP
    APP --> SCR
    APP --> DB_MOD
    APP --> EMAIL_MOD

    QA --> VEC
    QA --> OPENAI_API
    QA --> SENT_TRANS
    QA --> PROMPTS

    COMP --> PARSE
    COMP --> VEC
    COMP --> OPENAI_API
    COMP --> PROMPTS

    SCR --> WEB_URLS
    SCR --> CSV_FILE
    SCR --> DB_MOD
    SCR --> VEC

    VEC --> CHROMA
    VEC --> SENT_TRANS
    VEC --> OPENAI_API

    DB_MOD --> SQLITE
    UPDATE --> DB_MOD
    UPDATE --> OPENAI_API
    UPDATE --> EMAIL_MOD

    EMAIL_MOD --> SMTP_SERVER

    CONFIG --> ENV_FILE
    APP --> CONFIG
    QA --> CONFIG
    COMP --> CONFIG

    style STREAMLIT fill:#ff6b6b
    style APP fill:#4ecdc4
    style QA fill:#45b7d1
    style COMP fill:#45b7d1
    style OPENAI_API fill:#f9ca24
    style SENT_TRANS fill:#f9ca24
    style SQLITE fill:#6c5ce7
    style CHROMA fill:#6c5ce7
    style CONFIG fill:#a29bfe
```

## System Flow - Complete User Journey

```mermaid
flowchart TD
    START([User Opens App]) --> HOME[Intelligence Platform]
    
    HOME --> CHOICE{User Action}
    
    CHOICE -->|Ask Question| QA_FLOW[Q&A Flow]
    CHOICE -->|Upload Document| COMP_FLOW[Compliance Check]
    CHOICE -->|Load Regulations| LOAD_FLOW[Load Regulations]
    CHOICE -->|Subscribe Alerts| EMAIL_FLOW[Email Subscription]
    CHOICE -->|Explore Data| EXPLORE_FLOW[Regulation Explorer]
    
    subgraph QA_FLOW[Q&A Flow]
        QA1[User Types Question] --> QA2[Validate Question]
        QA2 --> QA3[Check Relevance]
        QA3 --> QA4[Search Vector Store]
        QA4 --> QA5[Get Regulations]
        QA5 --> QA6{API Available?}
        QA6 -->|Yes| QA7[OpenAI GPT-4o]
        QA6 -->|No| QA8[Free Mode Extraction]
        QA7 --> QA9[Generate Answer]
        QA8 --> QA9
        QA9 --> QA10[Format with Sources]
        QA10 --> QA11[Display to User]
    end
    
    subgraph COMP_FLOW[Compliance Check]
        C1[Upload PDF/DOCX] --> C2[Parse Document]
        C2 --> C3[Extract Clauses]
        C3 --> C4[Search Regulations]
        C4 --> C5[Analyze Each Clause]
        C5 --> C6{API Available?}
        C6 -->|Yes| C7[OpenAI Analysis]
        C6 -->|No| C8[Rule-Based Check]
        C7 --> C9[Identify Violations]
        C8 --> C9
        C9 --> C10[Generate Fixes]
        C10 --> C11[Display Report]
    end
    
    subgraph LOAD_FLOW[Load Regulations]
        L1[Read sources.csv] --> L2[For Each URL/File]
        L2 --> L3[Scrape Content]
        L3 --> L4[Extract Text]
        L4 --> L5[Create Embeddings]
        L5 --> L6[Store in ChromaDB]
        L6 --> L7[Save Metadata to SQLite]
        L7 --> L8[Complete]
    end
    
    subgraph EMAIL_FLOW[Email Subscription]
        E1[Enter Email + Cities] --> E2[Save to Database]
        E2 --> E3[Send Welcome Email]
        E3 --> E4[Daily Update Check]
        E4 --> E5{Updates Found?}
        E5 -->|Yes| E6[Send Alert Email]
        E5 -->|No| E7[Continue Monitoring]
    end
    
    subgraph EXPLORE_FLOW[Regulation Explorer]
        EX1[Search Regulations] --> EX2[Query Vector Store]
        EX2 --> EX3[Display Results]
        EX3 --> EX4[Show Metadata]
    end
    
    QA11 --> END([User Sees Answer])
    C11 --> END
    L8 --> END
    E6 --> END
    EX4 --> END
```

## Database Schema

```mermaid
erDiagram
    REGULATIONS ||--o{ UPDATES : has
    REGULATIONS ||--o{ COMPLIANCE_CHECKS : referenced_by
    SUBSCRIPTIONS ||--o{ ALERTS : receives
    
    REGULATIONS {
        int id PK
        string source_name
        string url
        string category
        text content
        string content_hash
        datetime created_at
        datetime updated_at
    }
    
    UPDATES {
        int id PK
        int regulation_id FK
        string update_summary
        string affected_cities
        datetime detected_at
        string url
        string source_name
        string category
    }
    
    COMPLIANCE_CHECKS {
        int id PK
        string document_name
        boolean is_compliant
        text issues_found
        text result_summary
        datetime checked_at
    }
    
    SUBSCRIPTIONS {
        int id PK
        string email
        string cities
        datetime subscribed_at
        boolean is_active
    }
    
    ALERTS {
        int id PK
        int subscription_id FK
        int update_id FK
        datetime sent_at
        string status
    }
```

