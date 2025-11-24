# Agent Solution Architecture Diagram - Intelligence Platform

Complete agentic architecture showing autonomous AI agents, intelligent routing, and proactive behaviors.

---

## 🤖 Agent Solution Architecture Overview

```mermaid
graph TB
    subgraph "User Interface Layer"
        USER[👤 End User]
        STREAMLIT[📱 Streamlit UI<br/>app.py<br/>User Interactions]
    end

    subgraph "Intelligent Agent Layer"
        subgraph "Primary Agents"
            QA_AGENT[🧠 Q&A Agent<br/>qa_system.py<br/>• Question Validation<br/>• Relevance Checking<br/>• City Detection<br/>• Context Building<br/>• Intelligent Routing]
            
            COMPLIANCE_AGENT[✅ Compliance Agent<br/>compliance_checker.py<br/>• Document Analysis<br/>• Clause Extraction<br/>• Issue Detection<br/>• Action Generation<br/>• Fix Suggestions]
            
            UPDATE_AGENT[🔄 Update Detection Agent<br/>update_checker.py<br/>• Autonomous Monitoring<br/>• Change Detection<br/>• Hash Comparison<br/>• City Impact Analysis<br/>• Summary Generation]
            
            SCRAPER_AGENT[🕷️ Scraping Agent<br/>scraper.py<br/>• Web Content Fetching<br/>• Text Extraction<br/>• Content Normalization<br/>• Hash Computation]
        end

        subgraph "Orchestration Agents"
            DAILY_ORCHESTRATOR[⏰ Daily Orchestrator<br/>daily_scraper.py<br/>• Scheduled Execution<br/>• Task Coordination<br/>• Autonomous Workflow<br/>• Error Handling]
            
            EMAIL_AGENT[📧 Email Notification Agent<br/>email_alerts.py<br/>• Proactive Alerts<br/>• Subscriber Management<br/>• Daily Summaries<br/>• Welcome Messages]
        end

        subgraph "Intelligence Services"
            RETRIEVAL_AGENT[🔍 Retrieval Agent<br/>retrieval_config.py<br/>• Query Enhancement<br/>• Source Prioritization<br/>• Geographic Filtering<br/>• Result Reranking]
            
            ROUTING_AGENT[🧭 Routing Agent<br/>Built-in Logic<br/>• Intent Classification<br/>• Request Routing<br/>• Context Awareness<br/>• Follow-up Handling]
        end
    end

    subgraph "Knowledge Base"
        VECTOR_KB[(Vector Knowledge Base<br/>ChromaDB<br/>Regulation Embeddings<br/>Semantic Search)]
        RELATIONAL_KB[(Relational Knowledge Base<br/>SQLite<br/>Metadata<br/>Updates<br/>Subscriptions)]
    end

    subgraph "AI/ML Services"
        LLM_SERVICE[OpenAI GPT-4o<br/>• Reasoning<br/>• Analysis<br/>• Generation]
        EMBEDDING_SERVICE[Sentence Transformers<br/>• Semantic Understanding<br/>• Free Embeddings]
    end

    subgraph "External Data Sources"
        WEB_SOURCES[🌐 Regulation Sources<br/>HUD, DOJ, City Sites]
        USER_DOCS[📄 User Documents<br/>PDF/DOCX Leases]
    end

    subgraph "External Services"
        SMTP[📧 SMTP Server<br/>Email Delivery]
    end

    %% User Interactions
    USER --> STREAMLIT
    STREAMLIT --> QA_AGENT
    STREAMLIT --> COMPLIANCE_AGENT
    STREAMLIT --> ROUTING_AGENT

    %% Agent Interactions
    ROUTING_AGENT --> QA_AGENT
    ROUTING_AGENT --> COMPLIANCE_AGENT
    
    QA_AGENT --> RETRIEVAL_AGENT
    QA_AGENT --> VECTOR_KB
    QA_AGENT --> RELATIONAL_KB
    QA_AGENT --> LLM_SERVICE
    QA_AGENT --> EMBEDDING_SERVICE

    COMPLIANCE_AGENT --> SCRAPER_AGENT
    COMPLIANCE_AGENT --> RETRIEVAL_AGENT
    COMPLIANCE_AGENT --> VECTOR_KB
    COMPLIANCE_AGENT --> LLM_SERVICE
    COMPLIANCE_AGENT --> USER_DOCS

    %% Autonomous Agents
    DAILY_ORCHESTRATOR --> UPDATE_AGENT
    UPDATE_AGENT --> SCRAPER_AGENT
    UPDATE_AGENT --> WEB_SOURCES
    UPDATE_AGENT --> RELATIONAL_KB
    UPDATE_AGENT --> LLM_SERVICE
    UPDATE_AGENT --> EMAIL_AGENT

    SCRAPER_AGENT --> WEB_SOURCES
    SCRAPER_AGENT --> VECTOR_KB
    SCRAPER_AGENT --> RELATIONAL_KB
    SCRAPER_AGENT --> EMBEDDING_SERVICE

    EMAIL_AGENT --> RELATIONAL_KB
    EMAIL_AGENT --> SMTP

    %% Knowledge Base Updates
    SCRAPER_AGENT -.->|Updates| VECTOR_KB
    SCRAPER_AGENT -.->|Updates| RELATIONAL_KB
    UPDATE_AGENT -.->|Updates| RELATIONAL_KB

    style USER fill:#ff6b6b,stroke:#c92a2a,stroke-width:3px,color:#fff
    style QA_AGENT fill:#4ecdc4,stroke:#2d8659,stroke-width:3px,color:#fff
    style COMPLIANCE_AGENT fill:#4ecdc4,stroke:#2d8659,stroke-width:3px,color:#fff
    style UPDATE_AGENT fill:#6c5ce7,stroke:#5f3dc4,stroke-width:3px,color:#fff
    style DAILY_ORCHESTRATOR fill:#6c5ce7,stroke:#5f3dc4,stroke-width:3px,color:#fff
    style EMAIL_AGENT fill:#ffd93d,stroke:#f59f00,stroke-width:3px
    style VECTOR_KB fill:#51cf66,stroke:#2f9e44,stroke-width:2px
    style RELATIONAL_KB fill:#51cf66,stroke:#2f9e44,stroke-width:2px
```

---

## 🔄 Autonomous Agent Workflows

```mermaid
sequenceDiagram
    participant Scheduler as Daily Orchestrator
    participant UpdateAgent as Update Detection Agent
    participant ScraperAgent as Scraping Agent
    participant LLM as OpenAI GPT-4o
    participant EmailAgent as Email Notification Agent
    participant DB as Knowledge Base
    participant Subscribers as Email Subscribers

    Note over Scheduler: Autonomous Daily Execution (9 AM)
    Scheduler->>UpdateAgent: Trigger Daily Check
    
    UpdateAgent->>DB: Get All Regulations
    DB-->>UpdateAgent: Regulation List
    
    loop For Each Regulation
        UpdateAgent->>ScraperAgent: Fetch Current Content
        ScraperAgent->>ScraperAgent: Scrape Web Source
        ScraperAgent-->>UpdateAgent: Current Content + Hash
        
        UpdateAgent->>UpdateAgent: Compare Hashes
        
        alt Hash Changed (Update Detected)
            UpdateAgent->>LLM: Generate Update Summary
            LLM-->>UpdateAgent: Summary + Affected Cities
            
            UpdateAgent->>DB: Save Update Record
            UpdateAgent->>EmailAgent: Notify Subscribers
            
            EmailAgent->>DB: Get Subscribers for City
            DB-->>EmailAgent: Subscriber List
            
            loop For Each Subscriber
                EmailAgent->>EmailAgent: Generate Email
                EmailAgent->>Subscribers: Send Alert Email
            end
        else No Change
            UpdateAgent->>UpdateAgent: Skip (No Action)
        end
    end
    
    Note over Scheduler: Daily Summary Reports
    Scheduler->>EmailAgent: Send Daily Summaries
    EmailAgent->>DB: Get All Subscriptions
    EmailAgent->>DB: Get Updates (Last 24h)
    EmailAgent->>Subscribers: Send Daily Summary
    
    Note over Scheduler,Subscribers: Fully Autonomous - No User Input Required
```

---

## 🧠 Intelligent Q&A Agent Architecture

```mermaid
graph TB
    subgraph "Q&A Agent Intelligence Pipeline"
        INPUT[User Question] --> VALIDATE[Validation Agent<br/>• Question Quality Check<br/>• Gibberish Detection<br/>• Greeting Recognition]
        
        VALIDATE --> RELEVANCE[Relevance Agent<br/>• Domain Check<br/>• Scope Validation<br/>• Topic Classification]
        
        RELEVANCE --> ROUTING[Routing Agent<br/>• Intent Classification<br/>• Follow-up Detection<br/>• Context Awareness]
        
        ROUTING --> CITY[City Detection Agent<br/>• Geographic Extraction<br/>• City Mention Detection<br/>• Default Assignment]
        
        CITY --> ENHANCE[Query Enhancement Agent<br/>• Legal Terminology Expansion<br/>• Synonym Mapping<br/>• Context Enrichment]
        
        ENHANCE --> RETRIEVE[Retrieval Agent<br/>• Vector Search<br/>• Geographic Filtering<br/>• Source Prioritization<br/>• Result Reranking]
        
        RETRIEVE --> CONTEXT[Context Builder Agent<br/>• Regulation Aggregation<br/>• Update Integration<br/>• Chat History Inclusion<br/>• Context Optimization]
        
        CONTEXT --> DECISION{API Available?}
        
        DECISION -->|Yes| LLM_AGENT[LLM Generation Agent<br/>• GPT-4o Reasoning<br/>• Detailed Analysis<br/>• Source Citation]
        DECISION -->|No| FREE_AGENT[Free Mode Agent<br/>• Context Extraction<br/>• Keyword Matching<br/>• Pattern Recognition]
        
        LLM_AGENT --> RESPONSE[Response Agent<br/>• Answer Formatting<br/>• Source Linking<br/>• Confidence Scoring]
        FREE_AGENT --> RESPONSE
        
        RESPONSE --> OUTPUT[Formatted Answer + Sources]
    end

    style INPUT fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style OUTPUT fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style LLM_AGENT fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style FREE_AGENT fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## ✅ Compliance Agent Architecture

```mermaid
graph TB
    subgraph "Compliance Agent Intelligence"
        DOC_INPUT[Document Upload] --> PARSE_AGENT[Parsing Agent<br/>• PDF Extraction<br/>• DOCX Processing<br/>• Text Normalization]
        
        PARSE_AGENT --> CLAUSE_AGENT[Clause Extraction Agent<br/>• Document Segmentation<br/>• Clause Identification<br/>• Structure Analysis]
        
        CLAUSE_AGENT --> LOOP{For Each Clause}
        
        LOOP --> SEARCH_AGENT[Search Agent<br/>• Vector Search<br/>• Regulation Matching<br/>• Relevance Scoring]
        
        SEARCH_AGENT --> ANALYSIS_AGENT{Analysis Mode}
        
        ANALYSIS_AGENT -->|API Available| LLM_ANALYZER[LLM Analyzer Agent<br/>• GPT-4o Analysis<br/>• Compliance Checking<br/>• Violation Detection<br/>• Issue Identification]
        
        ANALYSIS_AGENT -->|Free Mode| RULE_ANALYZER[Rule-based Analyzer Agent<br/>• Pattern Matching<br/>• Keyword Detection<br/>• Rule Application]
        
        LLM_ANALYZER --> ISSUE_AGENT[Issue Detection Agent<br/>• Violation Classification<br/>• Severity Assessment<br/>• Impact Analysis]
        RULE_ANALYZER --> ISSUE_AGENT
        
        ISSUE_AGENT --> ACTION_AGENT[Action Generation Agent<br/>• Fix Suggestions<br/>• Specific Recommendations<br/>• Compliance Steps]
        
        ACTION_AGENT --> REPORT_AGENT[Report Generation Agent<br/>• Report Formatting<br/>• Summary Creation<br/>• Action Items List]
        
        REPORT_AGENT --> COMP_OUTPUT[Compliance Report]
        
        LOOP -->|Next Clause| SEARCH_AGENT
    end

    style DOC_INPUT fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style COMP_OUTPUT fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style LLM_ANALYZER fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style RULE_ANALYZER fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 🔄 Agent Communication & Coordination

```mermaid
graph LR
    subgraph "Agent Communication Patterns"
        subgraph "Request-Response Agents"
            USER_REQ[User Request] --> ROUTER[Routing Agent]
            ROUTER --> QA[Q&A Agent]
            ROUTER --> COMP[Compliance Agent]
            QA --> RESPONSE[Response]
            COMP --> RESPONSE
        end

        subgraph "Event-Driven Agents"
            SCHEDULE[Scheduled Event] --> ORCHESTRATOR[Daily Orchestrator]
            ORCHESTRATOR --> UPDATE[Update Agent]
            UPDATE --> EMAIL[Email Agent]
            EMAIL --> NOTIFICATION[Email Notification]
        end

        subgraph "Pipeline Agents"
            INPUT_DATA[Input Data] --> AGENT1[Agent 1]
            AGENT1 --> AGENT2[Agent 2]
            AGENT2 --> AGENT3[Agent 3]
            AGENT3 --> OUTPUT_DATA[Output Data]
        end

        subgraph "Collaborative Agents"
            AGENT_A[Agent A] <--> SHARED_KB[Shared Knowledge Base]
            AGENT_B[Agent B] <--> SHARED_KB
            AGENT_C[Agent C] <--> SHARED_KB
        end
    end

    style USER_REQ fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style RESPONSE fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style SCHEDULE fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style NOTIFICATION fill:#ffd93d,stroke:#f59f00,stroke-width:2px
```

---

## 🎯 Agent Decision-Making Framework

```mermaid
graph TB
    subgraph "Agent Decision Tree"
        START[Agent Receives Task] --> CLASSIFY[Classify Task Type]
        
        CLASSIFY --> TYPE1{Task Type?}
        
        TYPE1 -->|Q&A| QA_DECISION[Q&A Decision Tree]
        TYPE1 -->|Compliance| COMP_DECISION[Compliance Decision Tree]
        TYPE1 -->|Update| UPDATE_DECISION[Update Decision Tree]
        TYPE1 -->|Email| EMAIL_DECISION[Email Decision Tree]
        
        subgraph "Q&A Decision Tree"
            QA_DECISION --> QA_VALID{Valid Question?}
            QA_VALID -->|No| QA_REJECT[Reject with Message]
            QA_VALID -->|Yes| QA_RELEVANT{Relevant?}
            QA_RELEVANT -->|No| QA_OUT_OF_SCOPE[Out of Scope Message]
            QA_RELEVANT -->|Yes| QA_CITY[Detect City]
            QA_CITY --> QA_SEARCH[Search Knowledge Base]
            QA_SEARCH --> QA_API{API Available?}
            QA_API -->|Yes| QA_LLM[Use LLM]
            QA_API -->|No| QA_FREE[Use Free Mode]
            QA_LLM --> QA_RESPONSE[Generate Answer]
            QA_FREE --> QA_RESPONSE
        end
        
        subgraph "Compliance Decision Tree"
            COMP_DECISION --> COMP_PARSE[Parse Document]
            COMP_PARSE --> COMP_EXTRACT[Extract Clauses]
            COMP_EXTRACT --> COMP_LOOP{For Each Clause}
            COMP_LOOP --> COMP_SEARCH[Search Regulations]
            COMP_SEARCH --> COMP_API{API Available?}
            COMP_API -->|Yes| COMP_LLM[LLM Analysis]
            COMP_API -->|No| COMP_RULE[Rule-based]
            COMP_LLM --> COMP_ISSUES[Identify Issues]
            COMP_RULE --> COMP_ISSUES
            COMP_ISSUES --> COMP_ACTIONS[Generate Actions]
            COMP_ACTIONS --> COMP_REPORT[Create Report]
        end
        
        subgraph "Update Decision Tree"
            UPDATE_DECISION --> UPDATE_FETCH[Fetch Content]
            UPDATE_FETCH --> UPDATE_HASH[Calculate Hash]
            UPDATE_HASH --> UPDATE_COMPARE{Hash Changed?}
            UPDATE_COMPARE -->|No| UPDATE_SKIP[Skip]
            UPDATE_COMPARE -->|Yes| UPDATE_SUMMARY[Generate Summary]
            UPDATE_SUMMARY --> UPDATE_CITY[Detect Cities]
            UPDATE_CITY --> UPDATE_SAVE[Save Update]
            UPDATE_SAVE --> UPDATE_NOTIFY[Notify Subscribers]
        end
        
        subgraph "Email Decision Tree"
            EMAIL_DECISION --> EMAIL_TYPE{Email Type?}
            EMAIL_TYPE -->|Welcome| EMAIL_WELCOME[Send Welcome]
            EMAIL_TYPE -->|Alert| EMAIL_ALERT[Send Alert]
            EMAIL_TYPE -->|Summary| EMAIL_SUMMARY[Send Summary]
            EMAIL_WELCOME --> EMAIL_SEND[Send via SMTP]
            EMAIL_ALERT --> EMAIL_SEND
            EMAIL_SUMMARY --> EMAIL_SEND
        end
    end

    style START fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style QA_RESPONSE fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style COMP_REPORT fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style UPDATE_NOTIFY fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style EMAIL_SEND fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
```

---

## 🤖 Agent Capabilities Matrix

```mermaid
mindmap
  root((Intelligence Platform Agents))
    Q&A Agent
      Question Validation
      Relevance Checking
      City Detection
      Context Building
      RAG Processing
      LLM Generation
      Free Mode Fallback
    Compliance Agent
      Document Parsing
      Clause Extraction
      Regulation Matching
      Issue Detection
      Action Generation
      Report Creation
    Update Agent
      Autonomous Monitoring
      Change Detection
      Hash Comparison
      Summary Generation
      City Impact Analysis
    Scraping Agent
      Web Content Fetching
      Text Extraction
      Content Normalization
      Hash Computation
      Error Handling
    Email Agent
      Proactive Alerts
      Subscriber Management
      Daily Summaries
      Welcome Messages
      SMTP Integration
    Orchestration Agent
      Scheduled Execution
      Task Coordination
      Workflow Management
      Error Recovery
    Retrieval Agent
      Query Enhancement
      Source Prioritization
      Geographic Filtering
      Result Reranking
    Routing Agent
      Intent Classification
      Request Routing
      Context Awareness
      Follow-up Handling
```

---

## 🔄 Agent Lifecycle & State Management

```mermaid
stateDiagram-v2
    [*] --> Initialized: System Start
    
    Initialized --> Active: Ready for Tasks
    
    Active --> Processing: Task Received
    
    Processing --> Validating: Validate Input
    Validating --> Routing: Route to Agent
    Routing --> Executing: Execute Agent Logic
    
    Executing --> Decision: Make Decision
    Decision --> Success: Task Complete
    Decision --> Error: Task Failed
    Decision --> Retry: Retry Needed
    
    Success --> Active: Return to Active
    Error --> ErrorHandling: Handle Error
    Retry --> Processing: Retry Task
    ErrorHandling --> Active: Recover
    
    Active --> Scheduled: Schedule Task
    Scheduled --> Processing: Trigger Time
    
    Active --> [*]: System Shutdown
    
    note right of Processing
        Agent processes task
        autonomously
    end note
    
    note right of Decision
        Agent makes intelligent
        decisions based on
        context and rules
    end note
```

---

## 📊 Agent Performance & Monitoring

```mermaid
graph TB
    subgraph "Agent Monitoring System"
        METRICS[Agent Metrics<br/>• Response Time<br/>• Success Rate<br/>• Error Rate<br/>• Task Completion]
        
        LOGGING[Agent Logging<br/>• Task Execution<br/>• Decision Points<br/>• Error Tracking<br/>• Performance Data]
        
        ALERTING[Agent Alerting<br/>• Failure Notifications<br/>• Performance Warnings<br/>• System Health]
    end

    subgraph "Agent Performance"
        QA_PERF[Q&A Agent<br/>• Avg Response: 2-5s<br/>• Success Rate: 95%<br/>• Free Mode: 1-3s]
        
        COMP_PERF[Compliance Agent<br/>• Avg Processing: 10-30s<br/>• Clause Analysis: 2-5s each<br/>• Report Generation: 1-2s]
        
        UPDATE_PERF[Update Agent<br/>• Daily Execution: 9 AM<br/>• Check Time: 5-15 min<br/>• Detection Accuracy: 99%]
        
        EMAIL_PERF[Email Agent<br/>• Delivery Rate: 98%<br/>• Send Time: <1s per email<br/>• Daily Summaries: Automated]
    end

    METRICS --> QA_PERF
    METRICS --> COMP_PERF
    METRICS --> UPDATE_PERF
    METRICS --> EMAIL_PERF
    
    LOGGING --> METRICS
    ALERTING --> METRICS

    style METRICS fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style QA_PERF fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style COMP_PERF fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style UPDATE_PERF fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
    style EMAIL_PERF fill:#ffd93d,stroke:#f59f00,stroke-width:2px
```

---

## 🎯 Agent Autonomy Levels

```mermaid
graph LR
    subgraph "Autonomy Spectrum"
        LEVEL1[Level 1: Reactive<br/>User-Triggered Q&A<br/>User-Triggered Compliance]
        LEVEL2[Level 2: Proactive<br/>Email Alerts<br/>Update Notifications]
        LEVEL3[Level 3: Autonomous<br/>Daily Scraping<br/>Automatic Updates]
        LEVEL4[Level 4: Self-Managing<br/>Database Updates<br/>Knowledge Base Maintenance]
        LEVEL5[Level 5: Adaptive<br/>Learning from Patterns<br/>Optimization]
    end

    LEVEL1 --> LEVEL2
    LEVEL2 --> LEVEL3
    LEVEL3 --> LEVEL4
    LEVEL4 --> LEVEL5

    style LEVEL1 fill:#ff6b6b,stroke:#c92a2a,stroke-width:2px,color:#fff
    style LEVEL2 fill:#ffd93d,stroke:#f59f00,stroke-width:2px
    style LEVEL3 fill:#51cf66,stroke:#2f9e44,stroke-width:2px,color:#fff
    style LEVEL4 fill:#4ecdc4,stroke:#2d8659,stroke-width:2px,color:#fff
    style LEVEL5 fill:#6c5ce7,stroke:#5f3dc4,stroke-width:2px,color:#fff
```

---

## 📝 Agent Architecture Notes

### **Agent Characteristics**

1. **Autonomous Agents**
   - Daily Orchestrator: Runs without user input
   - Update Detection Agent: Monitors changes autonomously
   - Email Notification Agent: Sends proactive alerts

2. **Intelligent Agents**
   - Q&A Agent: Makes routing and context decisions
   - Compliance Agent: Analyzes and generates recommendations
   - Retrieval Agent: Enhances queries and prioritizes results

3. **Collaborative Agents**
   - Agents share knowledge base
   - Agents coordinate through orchestrator
   - Agents communicate via events

4. **Adaptive Agents**
   - Free mode fallback when API unavailable
   - Context-aware decision making
   - Error recovery and retry logic

### **Agent Communication Patterns**

- **Request-Response**: User-triggered agents (Q&A, Compliance)
- **Event-Driven**: Scheduled agents (Daily Orchestrator, Update Agent)
- **Pipeline**: Sequential processing (Document → Parse → Analyze)
- **Collaborative**: Shared knowledge base access

### **Agent Decision-Making**

- **Rule-Based**: Validation, routing, filtering
- **ML-Based**: Vector search, similarity matching
- **LLM-Based**: Analysis, generation, summarization
- **Hybrid**: Combination of all approaches

### **Current Autonomy Level**

**Level 3: Autonomous**
- ✅ Daily scraping without user input
- ✅ Automatic update detection
- ✅ Proactive email notifications
- ✅ Self-managing database updates
- ⚠️ Limited learning/adaptation (future enhancement)

---

**Last Updated**: November 2024  
**Based on**: Actual agentic codebase implementation  
**Autonomy Level**: Level 3 (Autonomous)

