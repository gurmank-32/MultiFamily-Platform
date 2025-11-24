# Solution Architecture - Mermaid Diagrams

Complete solution architecture diagrams for Intelligence Platform using Mermaid syntax.

---

## 🏗️ Complete Solution Architecture

```mermaid
graph TB
    subgraph "User Layer"
        USER[👤 End Users<br/>Property Managers<br/>Leasing Professionals<br/>Legal Advisors]
        BROWSER[🌐 Web Browser<br/>Chrome, Firefox, Safari<br/>HTTPS/TLS Connection]
    end

    subgraph "Presentation Layer - Streamlit Cloud"
        STREAMLIT[📱 Streamlit Web Application<br/>app.py<br/>Python 3.13+<br/>Session State Management]
        
        subgraph "UI Components"
            IP_PAGE[💬 IP Agent Page<br/>Chat Interface<br/>Q&A System]
            EXPLORER[📚 Regulation Explorer<br/>Browse & Search]
            COMPLIANCE[✅ Compliance Checker<br/>Document Upload]
            UPDATES[📢 Update Log<br/>Change History]
            EMAIL_UI[📧 Email Alerts<br/>Subscriptions]
            SETTINGS[⚙️ Settings<br/>Data Management]
        end
    end

    subgraph "Application Layer - Business Logic"
        subgraph "Core Services"
            QA_SERVICE[QASystem<br/>qa_system.py<br/>RAG Engine<br/>Question Answering]
            COMP_SERVICE[ComplianceChecker<br/>compliance_checker.py<br/>Document Analysis<br/>Clause Review]
            SCRAPER_SERVICE[RegulationScraper<br/>scraper.py<br/>Web Scraping<br/>Content Extraction]
            UPDATE_SERVICE[UpdateChecker<br/>update_checker.py<br/>Change Detection<br/>Hash Comparison]
            EMAIL_SERVICE[EmailAlertSystem<br/>email_alerts.py<br/>Notifications<br/>Daily Summaries]
            PARSER_SERVICE[DocumentParser<br/>document_parser.py<br/>PDF/DOCX Parsing<br/>Text Extraction]
        end

        subgraph "Enhancement Services"
            RETRIEVAL[retrieval_config.py<br/>Query Enhancement<br/>Source Prioritization<br/>Geographic Filtering<br/>Result Reranking]
            PROMPTS[prompts_config.py<br/>LLM Prompts<br/>Custom Instructions<br/>Subject Enhancement]
        end
    end

    subgraph "Data Layer"
        subgraph "Relational Database"
            SQLITE[(SQLite Database<br/>database.py<br/>regulations.db<br/>• Regulation Metadata<br/>• Update History<br/>• Email Subscriptions<br/>• Compliance Checks)]
        end

        subgraph "Vector Database"
            CHROMADB[(ChromaDB Vector Store<br/>vector_store.py<br/>./chroma_db<br/>• Regulation Embeddings<br/>• Semantic Search Index<br/>• Metadata Filtering<br/>• Similarity Matching)]
        end

        subgraph "Configuration & Source Data"
            CONFIG[config.py<br/>Settings & Secrets<br/>Environment Variables]
            CSV[sources.csv<br/>Regulation URLs<br/>Source Metadata]
        end
    end

    subgraph "AI/ML Services"
        subgraph "LLM Services"
            OPENAI[OpenAI API<br/>GPT-4o Model<br/>• Q&A Generation<br/>• Compliance Analysis<br/>• Update Summarization<br/>• Clause Refinement]
        end

        subgraph "Embedding Services"
            SENTENCE_TRANS[Sentence Transformers<br/>all-MiniLM-L6-v2<br/>Free Embeddings<br/>384 Dimensions<br/>Local Processing]
            OPENAI_EMBED[OpenAI Embeddings<br/>text-embedding-3-small<br/>1536 Dimensions<br/>Optional Premium]
        end
    end

    subgraph "External Data Sources"
        WEB_SOURCES[🌐 Web Regulation Sources<br/>• HUD.gov<br/>• DOJ.gov<br/>• Texas.gov<br/>• City Government Sites<br/>• Legal Databases]
    end

    subgraph "External Services"
        SMTP_SERVER[📧 SMTP Email Server<br/>Gmail / Custom SMTP<br/>TLS Encryption<br/>Email Delivery]
    end

    subgraph "User Input"
        USER_DOCS[📄 User Documents<br/>PDF Lease Documents<br/>DOCX Lease Documents<br/>Upload via UI]
    end

    %% User to Presentation Layer
    USER --> BROWSER
    BROWSER -->|HTTPS| STREAMLIT
    STREAMLIT --> IP_PAGE
    STREAMLIT --> EXPLORER
    STREAMLIT --> COMPLIANCE
    STREAMLIT --> UPDATES
    STREAMLIT --> EMAIL_UI
    STREAMLIT --> SETTINGS

    %% Presentation to Application Layer
    IP_PAGE --> QA_SERVICE
    COMPLIANCE --> COMP_SERVICE
    EXPLORER --> CHROMADB
    EXPLORER --> SQLITE
    UPDATES --> UPDATE_SERVICE
    EMAIL_UI --> EMAIL_SERVICE
    SETTINGS --> SCRAPER_SERVICE
    SETTINGS --> CHROMADB
    SETTINGS --> SQLITE

    %% Application Layer Interactions
    QA_SERVICE --> RETRIEVAL
    QA_SERVICE --> PROMPTS
    QA_SERVICE --> CHROMADB
    QA_SERVICE --> SQLITE
    QA_SERVICE --> OPENAI
    QA_SERVICE --> SENTENCE_TRANS

    COMP_SERVICE --> PARSER_SERVICE
    COMP_SERVICE --> RETRIEVAL
    COMP_SERVICE --> PROMPTS
    COMP_SERVICE --> CHROMADB
    COMP_SERVICE --> SQLITE
    COMP_SERVICE --> OPENAI

    PARSER_SERVICE --> USER_DOCS

    SCRAPER_SERVICE --> CSV
    SCRAPER_SERVICE --> WEB_SOURCES
    SCRAPER_SERVICE --> SQLITE
    SCRAPER_SERVICE --> CHROMADB
    SCRAPER_SERVICE --> SENTENCE_TRANS

    UPDATE_SERVICE --> SCRAPER_SERVICE
    UPDATE_SERVICE --> SQLITE
    UPDATE_SERVICE --> OPENAI
    UPDATE_SERVICE --> EMAIL_SERVICE

    EMAIL_SERVICE --> SQLITE
    EMAIL_SERVICE --> SMTP_SERVER

    %% Data Layer
    CHROMADB --> SENTENCE_TRANS
    CHROMADB --> OPENAI_EMBED
    CHROMADB --> RETRIEVAL

    %% Configuration
    STREAMLIT --> CONFIG
    QA_SERVICE --> CONFIG
    COMP_SERVICE --> CONFIG
    EMAIL_SERVICE --> CONFIG

    %% Styling
    style USER fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style STREAMLIT fill:#4ecdc4,stroke:#2d8659,stroke-width:3px,color:#fff
    style QA_SERVICE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style COMP_SERVICE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style SQLITE fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style CHROMADB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style OPENAI fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style SENTENCE_TRANS fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

## 🔄 Solution Architecture - Deployment View

```mermaid
graph TB
    subgraph "Client Side"
        USER_CLIENT[👤 End User]
        BROWSER_CLIENT[🌐 Web Browser<br/>HTTPS/TLS]
    end

    subgraph "Streamlit Cloud Platform"
        subgraph "Application Runtime"
            STREAMLIT_APP[📱 Streamlit Application<br/>app.py<br/>Python 3.13<br/>Session State Management]
            
            subgraph "Python Modules"
                MODULES[Core Modules<br/>• qa_system.py<br/>• compliance_checker.py<br/>• scraper.py<br/>• update_checker.py<br/>• email_alerts.py<br/>• document_parser.py<br/>• database.py<br/>• vector_store.py]
            end
        end

        subgraph "Data Persistence"
            PERSISTENT_DB[(SQLite Database<br/>regulations.db<br/>Persistent Storage)]
            PERSISTENT_VECTOR[(ChromaDB<br/>./chroma_db<br/>Persistent Vector Store)]
        end

        subgraph "Configuration"
            SECRETS[🔐 Streamlit Secrets<br/>API Keys<br/>SMTP Credentials]
            CONFIG_FILE[config.toml<br/>Streamlit Settings]
        end
    end

    subgraph "External APIs & Services"
        OPENAI_API[OpenAI API<br/>api.openai.com<br/>GPT-4o<br/>Embeddings]
        SMTP_EXTERNAL[SMTP Server<br/>smtp.gmail.com:587<br/>Email Delivery]
        WEB_EXTERNAL[Web Sources<br/>HUD, DOJ, City Sites<br/>Regulation URLs]
    end

    subgraph "Source Control"
        GITHUB[📦 GitHub Repository<br/>Public Repository<br/>Auto-deploy on Push]
    end

    USER_CLIENT --> BROWSER_CLIENT
    BROWSER_CLIENT -->|HTTPS| STREAMLIT_APP
    STREAMLIT_APP --> MODULES
    MODULES --> PERSISTENT_DB
    MODULES --> PERSISTENT_VECTOR
    MODULES --> OPENAI_API
    MODULES --> SMTP_EXTERNAL
    MODULES --> WEB_EXTERNAL
    STREAMLIT_APP --> SECRETS
    STREAMLIT_APP --> CONFIG_FILE
    GITHUB -->|Auto Deploy| STREAMLIT_APP

    style USER_CLIENT fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style STREAMLIT_APP fill:#4ecdc4,stroke:#2d8659,stroke-width:3px,color:#fff
    style PERSISTENT_DB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style PERSISTENT_VECTOR fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style OPENAI_API fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style GITHUB fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 🎯 Solution Architecture - Component View

```mermaid
graph LR
    subgraph "Frontend Components"
        UI[Streamlit UI<br/>app.py]
        CHAT[Chat Interface]
        UPLOAD[File Upload]
        EXPLORE[Regulation Explorer]
    end

    subgraph "Application Components"
        QA[Q&A System<br/>qa_system.py]
        COMP[Compliance<br/>compliance_checker.py]
        SCRAPE[Scraper<br/>scraper.py]
        UPDATE[Update Checker<br/>update_checker.py]
        EMAIL[Email System<br/>email_alerts.py]
    end

    subgraph "Data Components"
        VECTOR[Vector Store<br/>vector_store.py]
        DB[Database<br/>database.py]
        PARSER[Document Parser<br/>document_parser.py]
    end

    subgraph "AI Components"
        EMBED[Embeddings<br/>Gen AI]
        LLM[LLM<br/>GPT-4o]
        RANK[Ranking<br/>retrieval_config.py]
    end

    UI --> CHAT
    UI --> UPLOAD
    UI --> EXPLORE
    
    CHAT --> QA
    UPLOAD --> COMP
    EXPLORE --> VECTOR
    
    QA --> VECTOR
    QA --> DB
    QA --> EMBED
    QA --> LLM
    QA --> RANK
    
    COMP --> PARSER
    COMP --> VECTOR
    COMP --> LLM
    
    SCRAPE --> DB
    SCRAPE --> VECTOR
    SCRAPE --> EMBED
    
    UPDATE --> SCRAPE
    UPDATE --> DB
    UPDATE --> EMAIL
    
    VECTOR --> EMBED
    DB --> SQLITE[(SQLite)]
    VECTOR --> CHROMA[(ChromaDB)]

    style UI fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style QA fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style LLM fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style CHROMA fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    style SQLITE fill:#51cf66,stroke:#2f9e44,stroke-width:2px
```

---

## 🔄 Solution Architecture - Data Flow View

```mermaid
flowchart TD
    START([User Question]) --> UI[Streamlit UI]
    
    UI --> VALID{Validation}
    VALID -->|Invalid| ERROR[Error Message]
    VALID -->|Valid| ENHANCE[Query Enhancement]
    
    ENHANCE --> EMBED[Generate Embedding]
    EMBED --> SEARCH[Vector Search]
    SEARCH --> FILTER[Geographic Filter]
    FILTER --> RANK[Ranking]
    RANK --> CONTEXT[Build Context]
    
    CONTEXT --> TOKEN{Tokenize}
    TOKEN --> LLM_DEC{LLM Available?}
    
    LLM_DEC -->|Yes| GPT4[GPT-4o]
    LLM_DEC -->|No| FREE[Free Mode]
    
    GPT4 --> FORMAT[Format Response]
    FREE --> FORMAT
    FORMAT --> DISPLAY[Display Answer]
    DISPLAY --> END([User Sees Answer])
    
    ERROR --> END

    style START fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style GPT4 fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style FREE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style END fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

## 🏛️ Solution Architecture - Layered View

```mermaid
graph TB
    subgraph "Layer 1: User Interface"
        L1_UI[Streamlit Web UI<br/>app.py<br/>User Interactions]
    end

    subgraph "Layer 2: Application Services"
        L2_QA[Q&A Service<br/>qa_system.py]
        L2_COMP[Compliance Service<br/>compliance_checker.py]
        L2_SCRAPE[Scraping Service<br/>scraper.py]
        L2_UPDATE[Update Service<br/>update_checker.py]
    end

    subgraph "Layer 3: Data Services"
        L3_VECTOR[Vector Service<br/>vector_store.py]
        L3_DB[Database Service<br/>database.py]
        L3_PARSER[Parser Service<br/>document_parser.py]
    end

    subgraph "Layer 4: AI/ML Services"
        L4_EMBED[Embedding Service<br/>Gen AI]
        L4_LLM[LLM Service<br/>GPT-4o]
        L4_RANK[Ranking Service<br/>retrieval_config.py]
    end

    subgraph "Layer 5: Data Storage"
        L5_VECTOR_DB[(ChromaDB<br/>Vector Store)]
        L5_REL_DB[(SQLite<br/>Relational DB)]
    end

    subgraph "Layer 6: External Services"
        L6_OPENAI[OpenAI API]
        L6_SMTP[SMTP Server]
        L6_WEB[Web Sources]
    end

    L1_UI --> L2_QA
    L1_UI --> L2_COMP
    L1_UI --> L2_SCRAPE
    L1_UI --> L2_UPDATE
    
    L2_QA --> L3_VECTOR
    L2_QA --> L3_DB
    L2_COMP --> L3_PARSER
    L2_COMP --> L3_VECTOR
    L2_SCRAPE --> L3_DB
    L2_SCRAPE --> L3_VECTOR
    
    L3_VECTOR --> L4_EMBED
    L3_VECTOR --> L4_RANK
    L2_QA --> L4_LLM
    L2_COMP --> L4_LLM
    
    L4_EMBED --> L5_VECTOR_DB
    L3_DB --> L5_REL_DB
    L3_VECTOR --> L5_VECTOR_DB
    
    L4_LLM --> L6_OPENAI
    L4_EMBED --> L6_OPENAI
    L2_UPDATE --> L6_WEB
    L2_UPDATE --> L6_SMTP

    style L1_UI fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style L4_LLM fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style L5_VECTOR_DB fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    style L5_REL_DB fill:#51cf66,stroke:#2f9e44,stroke-width:2px
```

---

## 🔐 Solution Architecture - Security & Data Flow

```mermaid
graph TB
    subgraph "Security Layers"
        SEC1[HTTPS/TLS<br/>Encrypted Transport]
        SEC2[Streamlit Secrets<br/>Secure Key Storage]
        SEC3[Input Validation<br/>Sanitization]
        SEC4[SQL Injection Prevention<br/>Parameterized Queries]
    end

    subgraph "Data Flow Security"
        DATA1[User Input] --> SEC3
        SEC3 --> SEC4
        SEC4 --> SEC1
        SEC1 --> SEC2
    end

    subgraph "API Security"
        API1[OpenAI API<br/>TLS/SSL]
        API2[SMTP<br/>TLS Encryption]
    end

    SEC2 --> API1
    SEC2 --> API2

    style SEC1 fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style SEC2 fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style API1 fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style API2 fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

## 📊 Solution Architecture - Technology Stack View

```mermaid
mindmap
  root((Intelligence Platform))
    Frontend
      Streamlit
      Python 3.13
      Session State
    Backend
      Python Modules
      Business Logic
      Service Layer
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
      Streamlit Secrets
    External
      OpenAI API
      SMTP Server
      Web URLs
```

---

## 🔄 Solution Architecture - Request/Response Flow

```mermaid
sequenceDiagram
    participant U as User
    participant UI as Streamlit UI
    participant BE as Backend Services
    participant AI as AI Services
    participant DB as Databases
    participant EXT as External APIs

    U->>UI: Ask Question
    UI->>BE: Process Request
    BE->>BE: Validate & Enhance
    BE->>AI: Generate Embedding
    AI->>DB: Vector Search
    DB-->>AI: Search Results
    AI->>AI: Rank & Filter
    BE->>DB: Query Metadata
    DB-->>BE: Regulation Data
    BE->>EXT: LLM API Call
    EXT-->>BE: LLM Response
    BE->>UI: Format Response
    UI-->>U: Display Answer
```

---

## 🎯 Solution Architecture - System Integration View

```mermaid
graph TB
    subgraph "Integration Points"
        INT1[User Interface Integration<br/>Streamlit ↔ Backend]
        INT2[Backend ↔ AI Services<br/>Embedding & LLM]
        INT3[Backend ↔ Databases<br/>SQLite & ChromaDB]
        INT4[Backend ↔ External APIs<br/>OpenAI & SMTP]
        INT5[Data Ingestion Integration<br/>Scraper ↔ Databases]
    end

    subgraph "Data Flow Integration"
        DF1[User Input Flow]
        DF2[Query Processing Flow]
        DF3[Response Generation Flow]
        DF4[Data Ingestion Flow]
    end

    INT1 --> DF1
    DF1 --> INT2
    INT2 --> DF2
    DF2 --> INT3
    INT3 --> DF3
    DF3 --> INT1
    INT5 --> INT3
    INT4 --> DF2

    style INT1 fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style INT2 fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style INT3 fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style INT4 fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

**Last Updated**: November 2024  
**Platform**: Intelligence Platform  
**Based on**: Complete codebase implementation


