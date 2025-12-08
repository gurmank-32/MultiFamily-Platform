# Regulation Ingestion Pipeline Guide

## Overview

The `ingest_sources.py` script provides a complete ingestion pipeline that:
1. ✅ Reads the Excel file `finalsource11.xlsx`
2. ✅ Scrapes text content from each hyperlink (HTML, PDF, Canva sites)
3. ✅ Splits content into overlapping chunks (600 chars with 100 char overlap)
4. ✅ Creates embeddings using Sentence Transformers (free) or OpenAI (paid)
5. ✅ Saves embeddings & metadata into ChromaDB collection "regulations"
6. ✅ Updates SQLite database with regulation metadata
7. ✅ Persists the database to disk

## Usage

### Basic Usage

```bash
python ingest_sources.py
```

### With Custom Excel File

```python
from ingest_sources import ingest_regulations
ingest_regulations("path/to/your/sources.xlsx")
```

## What It Does

### 1. Excel File Reading
- Reads `finalsource11.xlsx` (or custom path)
- Normalizes column names (handles variations like `url`, `hyperlink`, `link`)
- Required columns: `hyperlink`, `category`, `level`
- Optional columns: `city`, `source_name`

### 2. Content Scraping
- Supports HTTP/HTTPS URLs
- Supports local files (`file://` URLs)
- Supports PDF files (extracts text)
- Supports Canva sites (JavaScript-rendered content)
- Extracts main content, removes navigation/menus
- Calculates content hash for change detection

### 3. Text Chunking
- Splits text into ~600 character chunks
- 100 character overlap between chunks
- Minimum chunk size: 200-400 characters
- Preserves word boundaries

### 4. Embedding & Storage
- Creates embeddings using Sentence Transformers `all-MiniLM-L6-v2` (free)
- Falls back to OpenAI `text-embedding-3-small` if API key available
- Stores in ChromaDB collection "regulations"
- Metadata includes: `source_name`, `url`, `category`, `chunk_index`

### 5. Database Integration
- Adds/updates regulations in SQLite database (`regulations.db`)
- Tracks content hash to detect changes
- Skips re-indexing if content unchanged
- Updates `last_checked` timestamp

## Output

The script provides detailed progress output:

```
============================================================
REGULATION INGESTION PIPELINE
============================================================
Reading sources from: finalsource11.xlsx
✅ Loaded 98 rows from Excel file

📊 Processing 98 sources...
------------------------------------------------------------

[1/98] Processing: ESA - Federal
   URL: https://adata.org/legal_brief/assistance-animals...
   📄 Extracted 15420 characters, created 25 chunks
   ✅ Added to database (ID: 1)
   ✅ Successfully indexed 25 chunks

...

============================================================
🎉 INGESTION COMPLETE
============================================================
📊 Statistics:
   Total sources: 98
   ✅ Processed: 85
   ⚠️  Skipped: 10
   ❌ Errors: 3
   📄 Total chunks indexed: 2,145
   ⏱️  Time elapsed: 245.3 seconds
============================================================
```

## Error Handling

The script handles:
- ✅ Missing URLs (skips with warning)
- ✅ Invalid URL formats (skips with warning)
- ✅ Failed content fetching (skips with error message)
- ✅ Insufficient content (< 300 chars, skips)
- ✅ Chunking failures (skips with warning)
- ✅ Network errors (continues with next source)
- ✅ ChromaDB errors (logs and continues)

## Database Persistence

ChromaDB automatically persists to disk using DuckDB+Parquet backend:
- **Storage location:** `./chroma_db/` directory
- **Persistence:** Automatic (no manual save needed)
- **Format:** DuckDB database + Parquet files

## Re-running Ingestion

The script is **idempotent**:
- ✅ Checks if regulation already exists
- ✅ Compares content hash to detect changes
- ✅ Only re-indexes if content changed
- ✅ Skips unchanged sources (saves time)

## Troubleshooting

### Issue: "No module named 'openpyxl'"
**Solution:** `pip install openpyxl`

### Issue: "No module named 'sentence_transformers'"
**Solution:** `pip install sentence-transformers`

### Issue: "ChromaDB index error"
**Solution:** Delete `./chroma_db/` directory and re-run ingestion

### Issue: "SSL certificate verify failed"
**Solution:** Some sites may have SSL issues. The script will skip them and continue.

### Issue: "Not enough content"
**Solution:** Some URLs may return minimal content. Check the URL manually. Minimum is 300 characters.

## Integration with App

After running ingestion:
1. ✅ ChromaDB is populated with embeddings
2. ✅ SQLite database has regulation metadata
3. ✅ Vector search will find content
4. ✅ QA system can answer questions

**Note:** You may need to restart the Streamlit app to reload the vector store.

## Performance

- **Average time per source:** ~3-5 seconds
- **Chunking:** ~0.1 seconds per source
- **Embedding:** ~0.5-1 second per chunk (CPU)
- **Total time for 100 sources:** ~5-10 minutes

## Next Steps

After ingestion:
1. Test the QA system: `python -c "from qa_system import QASystem; qa = QASystem(); print(qa.answer_question('What is ESA?'))"`
2. Check vector store: Count documents in ChromaDB
3. Verify sources: Check SQLite database for regulation records

