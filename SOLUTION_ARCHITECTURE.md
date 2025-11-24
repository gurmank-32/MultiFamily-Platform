# Solution Architecture Diagram - Intelligence Platform

Complete solution architecture based on the actual codebase implementation.

---

## 🏗️ Complete Solution Architecture

```mermaid
graph TB
    subgraph "User Layer"
        USERS[👥 End Users<br/>Property Managers<br/>Leasing Professionals<br/>Legal Advisors]
        BROWSER[🌐 Web Browser<br/>Chrome, Firefox, Safari<br/>HTTPS Connection]
    end

    subgraph "Presentation Layer - Streamlit Cloud"
        STREAMLIT[📱 Streamlit Web Application<br/>app.py<br/>Python 3.13+]
        
        subgraph "UI Pages"
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
    USERS --> BROWSER
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
    style USERS fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style STREAMLIT fill:#4ecdc4,stroke:#2d8659,stroke-width:3px,color:#fff
    style QA_SERVICE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style COMP_SERVICE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style SQLITE fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style CHROMADB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style OPENAI fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style SENTENCE_TRANS fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

## 🔄 End-to-End Solution Flow

```mermaid
flowchart TD
    START([User Accesses Platform]) --> BROWSER[Web Browser]
    BROWSER --> STREAMLIT[Streamlit Cloud<br/>app.py]
    
    STREAMLIT --> CHOICE{User Action}
    
    CHOICE -->|Ask Question| QA_FLOW[Q&A Flow]
    CHOICE -->|Upload Document| COMP_FLOW[Compliance Check Flow]
    CHOICE -->|Browse Regulations| EXPLORE_FLOW[Exploration Flow]
    CHOICE -->|Subscribe to Alerts| EMAIL_FLOW[Email Subscription Flow]
    CHOICE -->|Load Regulations| INGEST_FLOW[Data Ingestion Flow]
    
    %% Q&A Flow
    QA_FLOW --> QA_VALIDATE[Validate Question<br/>Check Relevance]
    QA_VALIDATE --> QA_ENHANCE[Enhance Query<br/>Add Legal Terminology]
    QA_ENHANCE --> QA_SEARCH[Vector Search<br/>ChromaDB]
    QA_SEARCH --> QA_CONTEXT[Build Context<br/>Regulations + Updates]
    QA_CONTEXT --> QA_LLM{API Available?}
    QA_LLM -->|Yes| QA_GPT4[GPT-4o Generation]
    QA_LLM -->|No| QA_FREE[Free Mode<br/>Context Extraction]
    QA_GPT4 --> QA_RESPONSE[Return Answer + Sources]
    QA_FREE --> QA_RESPONSE
    QA_RESPONSE --> DISPLAY[Display to User]
    
    %% Compliance Flow
    COMP_FLOW --> COMP_UPLOAD[Upload Document<br/>PDF/DOCX]
    COMP_UPLOAD --> COMP_PARSE[Parse Document<br/>Extract Text]
    COMP_PARSE --> COMP_CLAUSES[Extract Clauses]
    COMP_CLAUSES --> COMP_LOOP{For Each Clause}
    COMP_LOOP --> COMP_SEARCH[Search Relevant Regulations]
    COMP_SEARCH --> COMP_ANALYZE{API Available?}
    COMP_ANALYZE -->|Yes| COMP_GPT4[GPT-4o Analysis]
    COMP_ANALYZE -->|No| COMP_RULE[Rule-based Analysis]
    COMP_GPT4 --> COMP_ISSUES[Identify Issues]
    COMP_RULE --> COMP_ISSUES
    COMP_ISSUES --> COMP_ACTIONS[Generate Action Items]
    COMP_ACTIONS --> COMP_REPORT[Compliance Report]
    COMP_REPORT --> DISPLAY
    
    %% Exploration Flow
    EXPLORE_FLOW --> EXP_SEARCH[Search Regulations]
    EXP_SEARCH --> EXP_VECTOR[Vector Search]
    EXP_VECTOR --> EXP_FILTER[Filter by Category/City]
    EXP_FILTER --> EXP_RESULTS[Display Results]
    EXP_RESULTS --> DISPLAY
    
    %% Email Flow
    EMAIL_FLOW --> EMAIL_SUB[Subscribe to City]
    EMAIL_SUB --> EMAIL_SAVE[Save to Database]
    EMAIL_SAVE --> EMAIL_WELCOME[Send Welcome Email]
    EMAIL_WELCOME --> EMAIL_DAILY[Daily Summary Reports]
    EMAIL_DAILY --> DISPLAY
    
    %% Ingestion Flow
    INGEST_FLOW --> INGEST_CSV[Read sources.csv]
    INGEST_CSV --> INGEST_SCRAPE[Scrape URLs]
    INGEST_SCRAPE --> INGEST_EXTRACT[Extract Content]
    INGEST_EXTRACT --> INGEST_HASH[Calculate Hash]
    INGEST_HASH --> INGEST_SAVE[Save to SQLite]
    INGEST_SAVE --> INGEST_CHUNK[Chunk Text]
    INGEST_CHUNK --> INGEST_EMBED[Create Embeddings]
    INGEST_EMBED --> INGEST_VECTOR[Store in ChromaDB]
    INGEST_VECTOR --> DISPLAY
    
    DISPLAY --> END([User Views Results])
    
    style START fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style END fill:#51cf66,stroke:#2f9e44,stroke-width:3px,color:#fff
    style QA_GPT4 fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style COMP_GPT4 fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 🏛️ Deployment Architecture

```mermaid
graph TB
    subgraph "Client Side"
        USER[👤 End User]
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

    USER --> BROWSER_CLIENT
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

    style USER fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style STREAMLIT_APP fill:#4ecdc4,stroke:#2d8659,stroke-width:3px,color:#fff
    style PERSISTENT_DB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style PERSISTENT_VECTOR fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style OPENAI_API fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style GITHUB fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 🔐 Security & Data Flow Architecture

```mermaid
graph TB
    subgraph "User Input"
        USER_INPUT[User Input<br/>Questions, Documents, Settings]
    end

    subgraph "Authentication & Authorization"
        STREAMLIT_AUTH[Streamlit Cloud<br/>GitHub OAuth<br/>Session Management]
        SECRETS_MGMT[Secrets Management<br/>Streamlit Secrets<br/>Environment Variables]
    end

    subgraph "Data Processing"
        INPUT_VALIDATION[Input Validation<br/>Question Validation<br/>Relevance Checking<br/>File Type Verification]
        DATA_SANITIZATION[Data Sanitization<br/>Text Cleaning<br/>SQL Injection Prevention<br/>XSS Prevention]
    end

    subgraph "Secure Storage"
        ENCRYPTED_DB[(Encrypted at Rest<br/>SQLite Database<br/>regulations.db)]
        ENCRYPTED_VECTOR[(Encrypted at Rest<br/>ChromaDB<br/>./chroma_db)]
        SECURE_SECRETS[Secure Secrets Storage<br/>API Keys<br/>SMTP Credentials]
    end

    subgraph "Secure Communication"
        HTTPS[HTTPS/TLS<br/>Browser to Streamlit<br/>Encrypted Transport]
        API_TLS[TLS/SSL<br/>OpenAI API<br/>SMTP Server]
    end

    subgraph "Data Privacy"
        NO_DATA_SHARING[No External Data Sharing<br/>User Data Isolation<br/>Local Processing]
        LEGAL_DISCLAIMER[Legal Disclaimer<br/>Informational Only<br/>No Legal Advice]
    end

    USER_INPUT --> STREAMLIT_AUTH
    STREAMLIT_AUTH --> INPUT_VALIDATION
    INPUT_VALIDATION --> DATA_SANITIZATION
    DATA_SANITIZATION --> ENCRYPTED_DB
    DATA_SANITIZATION --> ENCRYPTED_VECTOR
    SECRETS_MGMT --> SECURE_SECRETS
    HTTPS --> API_TLS
    NO_DATA_SHARING --> LEGAL_DISCLAIMER

    style USER_INPUT fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style ENCRYPTED_DB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style ENCRYPTED_VECTOR fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style HTTPS fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style API_TLS fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

## 📊 Data Architecture

```mermaid
erDiagram
    REGULATIONS ||--o{ UPDATES : "has"
    REGULATIONS ||--o{ REGULATION_CHUNKS : "contains"
    REGULATIONS ||--o{ COMPLIANCE_CHECKS : "checked_against"
    SUBSCRIBERS ||--o{ SUBSCRIPTIONS : "has"
    UPDATES ||--o{ EMAIL_ALERTS : "triggers"
    
    REGULATIONS {
        int id PK
        string source_name
        string url UK
        string type
        string category
        string content_hash
        datetime last_checked
        text metadata
    }
    
    UPDATES {
        int id PK
        int regulation_id FK
        string summary
        text affected_cities
        datetime detected_at
        string old_hash
        string new_hash
    }
    
    REGULATION_CHUNKS {
        string id PK
        int regulation_id FK
        text chunk_text
        vector embedding
        text metadata
    }
    
    SUBSCRIBERS {
        int id PK
        string email UK
        datetime subscribed_at
    }
    
    SUBSCRIPTIONS {
        int id PK
        int subscriber_id FK
        string city
        datetime subscribed_at
    }
    
    COMPLIANCE_CHECKS {
        int id PK
        string document_name
        string city
        datetime checked_at
        text results
    }
    
    EMAIL_ALERTS {
        int id PK
        int update_id FK
        int subscriber_id FK
        datetime sent_at
        string status
    }
```

---

## 🔄 RAG (Retrieval Augmented Generation) Architecture

```mermaid
graph LR
    subgraph "Query Processing"
        Q[User Question] --> VAL[Validation]
        VAL --> CITY[City Detection]
        CITY --> ENHANCE[Query Enhancement<br/>retrieval_config.py]
    end

    subgraph "Retrieval Phase"
        ENHANCE --> EMBED[Create Embedding]
        EMBED -->|Free Mode| ST_EMBED[Sentence Transformers<br/>all-MiniLM-L6-v2]
        EMBED -->|Premium| OPENAI_EMBED[OpenAI<br/>text-embedding-3-small]
        ST_EMBED --> SEARCH[Vector Search<br/>ChromaDB]
        OPENAI_EMBED --> SEARCH
        SEARCH --> FILTER[Geographic Filtering]
        FILTER --> RERANK[Source Prioritization<br/>Reranking]
        RERANK --> TOP_K[Top K Results]
    end

    subgraph "Context Building"
        TOP_K --> REGS[Relevant Regulations]
        REGS --> UPDATES[Recent Updates<br/>from SQLite]
        UPDATES --> HISTORY[Chat History]
        HISTORY --> CONTEXT[Build Context String]
    end

    subgraph "Generation Phase"
        CONTEXT --> PROMPT[Build LLM Prompt<br/>prompts_config.py]
        PROMPT --> LLM{API Available?}
        LLM -->|Yes| GPT4[GPT-4o<br/>Detailed Answer]
        LLM -->|No| FREE[Free Mode<br/>Context Extraction]
        GPT4 --> ANSWER[Final Answer]
        FREE --> ANSWER
    end

    subgraph "Response"
        ANSWER --> SOURCES[Source Links]
        SOURCES --> USER[Return to User]
    end

    style Q fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style ANSWER fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style GPT4 fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style FREE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 🎯 Component Interaction Matrix

```mermaid
graph TB
    subgraph "Presentation Components"
        APP[app.py]
    end

    subgraph "Business Logic Components"
        QA[qa_system.py]
        COMP[compliance_checker.py]
        SCR[scraper.py]
        UC[update_checker.py]
        ES[email_alerts.py]
        DP[document_parser.py]
    end

    subgraph "Data Access Components"
        DB[database.py]
        VS[vector_store.py]
    end

    subgraph "Configuration Components"
        CFG[config.py]
        PROMPTS[prompts_config.py]
        RET[retrieval_config.py]
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
    CFG --> RET

    style APP fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style QA fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style COMP fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style DB fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style VS fill:#ffd93d,stroke:#f59f00,stroke-width:2px
```

---

## 📈 Scalability & Performance Architecture

```mermaid
graph TB
    subgraph "Performance Optimizations"
        CACHE[Session State Caching<br/>Streamlit Session State<br/>Component Reuse]
        LAZY_LOAD[Lazy Loading<br/>On-demand Model Loading<br/>Embedding Caching]
        INDEXING[HNSW Indexing<br/>ChromaDB<br/>Fast Similarity Search]
        BATCH[Batch Processing<br/>Regulation Ingestion<br/>Embedding Generation]
    end

    subgraph "Scalability Features"
        STATELESS[Stateless Components<br/>Module-based Design<br/>Easy Scaling]
        PERSISTENT[Persistent Storage<br/>SQLite + ChromaDB<br/>Data Persistence]
        FREE_TIER[Free Tier Compatible<br/>Works without API<br/>Sentence Transformers]
    end

    subgraph "Resource Management"
        MEMORY[Memory Efficient<br/>Chunked Processing<br/>Streaming]
        CPU[CPU Optimization<br/>Vectorized Operations<br/>NumPy/Pandas]
        STORAGE[Storage Optimization<br/>Compressed Embeddings<br/>Efficient Indexing]
    end

    CACHE --> STATELESS
    LAZY_LOAD --> MEMORY
    INDEXING --> CPU
    BATCH --> STORAGE
    STATELESS --> PERSISTENT
    PERSISTENT --> FREE_TIER

    style CACHE fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style INDEXING fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style FREE_TIER fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 📝 Architecture Notes

### **Key Design Decisions**

1. **Hybrid AI Approach**
   - Free embeddings (Sentence Transformers) for semantic search
   - Optional OpenAI API for advanced analysis
   - Graceful degradation when API unavailable

2. **Dual Database Strategy**
   - SQLite for structured metadata
   - ChromaDB for vector embeddings
   - Separation of concerns

3. **Modular Architecture**
   - Each module has single responsibility
   - Easy to test and maintain
   - Configurable components

4. **Cloud-Native Design**
   - Streamlit Cloud deployment
   - Persistent storage
   - Auto-scaling capabilities

5. **Security First**
   - Secrets management
   - Input validation
   - Secure communication (HTTPS/TLS)

### **Technology Choices**

- **Streamlit**: Rapid UI development, Python-native
- **SQLite**: Lightweight, embedded, no server needed
- **ChromaDB**: Open-source, persistent, efficient vector search
- **Sentence Transformers**: Free, local, no API dependency
- **OpenAI GPT-4o**: State-of-the-art LLM for complex analysis

### **Deployment Model**

- **Platform**: Streamlit Cloud (Free Tier)
- **Repository**: GitHub (Public)
- **Auto-deploy**: On git push
- **Scaling**: Automatic (Streamlit Cloud handles)

---

**Last Updated**: November 2024  
**Based on**: Actual codebase implementation  
**Version**: 1.0

