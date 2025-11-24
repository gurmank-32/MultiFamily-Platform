# Technology Stack - Quick Reference

## 🎯 **Core Stack**

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | Streamlit 1.28+ | Web UI framework |
| **Language** | Python 3.13+ | Main programming language |
| **LLM** | OpenAI GPT-4o | AI compliance analysis |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) | Free semantic search |
| **Vector DB** | ChromaDB 0.4+ | Vector storage & search |
| **Relational DB** | SQLite3 | Metadata storage |
| **ML Framework** | PyTorch 2.0+ | Deep learning backend |

## 📦 **Key Libraries**

### **AI & ML**
- `openai` - GPT-4 API client
- `sentence-transformers` - Free embeddings
- `torch` - PyTorch framework
- `tiktoken` - Token counting

### **Data Processing**
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `chromadb` - Vector database

### **Document Processing**
- `PyPDF2` - PDF parsing
- `python-docx` - Word document parsing

### **Web & Scraping**
- `requests` - HTTP client
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

### **Utilities**
- `python-dotenv` - Environment variables
- `streamlit` - UI framework

## 🗄️ **Databases**

1. **SQLite** (`regulations.db`)
   - Regulation metadata
   - Update history
   - Email subscriptions

2. **ChromaDB** (`./chroma_db`)
   - Vector embeddings
   - Semantic search
   - Similarity matching

## 🤖 **AI Models**

### **LLM**
- **Model**: GPT-4o
- **Provider**: OpenAI
- **Use**: Compliance analysis, Q&A
- **Cost**: ~$0.01-0.03 per 1K tokens

### **Embeddings**
- **Free**: `all-MiniLM-L6-v2` (384 dims)
- **Paid**: `text-embedding-3-small` (1536 dims)
- **Library**: Sentence Transformers

## 🚀 **Deployment**

- **Platform**: Streamlit Cloud (Free)
- **Repository**: GitHub (Public)
- **Secrets**: Streamlit Secrets
- **Config**: `.streamlit/config.toml`

## 📊 **Architecture Pattern**

**RAG (Retrieval Augmented Generation)**
```
Query → Vector Search → Context → LLM → Answer
```

## 🔄 **Data Flow**

1. **Ingestion**: CSV → SQLite → Scrape → Embed → ChromaDB
2. **Q&A**: Question → Search → Context → LLM → Answer
3. **Compliance**: Document → Parse → Search → LLM → Report
4. **Updates**: URL → Hash → Compare → Summarize → Alert

## 💰 **Cost Breakdown**

### **Free**
- ✅ Streamlit Cloud hosting
- ✅ SQLite database
- ✅ ChromaDB vector store
- ✅ Sentence Transformers embeddings
- ✅ All document parsers
- ✅ Web scraping tools

### **Paid (Optional)**
- 💰 OpenAI API: ~$5-20/month (typical usage)
- 💰 Email service: Free (Gmail) or paid SMTP

## 📁 **File Structure**

```
app.py              # Main UI
config.py           # Configuration
database.py         # SQLite ops
vector_store.py     # ChromaDB + embeddings
qa_system.py         # RAG system
compliance_checker.py # LLM analysis
document_parser.py   # PDF/DOCX
scraper.py          # Web scraping
retrieval_config.py # Search enhancements
```

## 🎨 **UI Framework**

**Streamlit Components**:
- Chat interface (`st.chat_message`)
- File upload (`st.file_uploader`)
- Data tables (`st.dataframe`)
- Navigation (`st.sidebar`)
- Alerts (`st.info`, `st.success`)

## 🔐 **Security**

- Environment variables (`.env`)
- Streamlit secrets (cloud)
- No hardcoded credentials
- TLS email encryption

---

**For detailed information, see `TECHNOLOGY_STACK.md`**

