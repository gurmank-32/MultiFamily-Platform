"""
Complete ingestion pipeline for regulations from Excel file
Reads finalsource11.xlsx, scrapes content, chunks it, and stores in ChromaDB
"""
import pandas as pd
import numpy as np
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from database import RegulationDB
from config import SOURCES_FILE
import time
import hashlib
import re

FORCE_REINGEST = True


def normalize_ocr_text(text: str) -> str:
    """Normalize OCR-like text artifacts (vertical characters, broken words)."""
    if not text:
        return text
    # Remove single-character line breaks into proper sentences
    text = re.sub(r"(?<=\w)\s*\n\s*(?=\w)", " ", text)
    # Collapse double/triple newlines
    text = re.sub(r"\n{2,}", "\n", text)
    # Remove spacing between every character: D a l l a s -> Dallas (heuristic)
    text = re.sub(r"(\b\w\s)(?=\w\s)", lambda m: m.group(0).replace(" ", ""), text)
    # Remove stray hyphens from OCR word splits
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    return text.strip()


def ingest_regulations(csv_path=None):
    """
    Complete ingestion pipeline:
    1. Reads Excel file
    2. Scrapes content from each hyperlink
    3. Chunks the content
    4. Stores embeddings in ChromaDB
    5. Updates SQLite database with regulation metadata
    """
    if csv_path is None:
        csv_path = SOURCES_FILE
    
    print("=" * 60)
    print("REGULATION INGESTION PIPELINE")
    print("=" * 60)
    print(f"Reading sources from: {csv_path}")
    
    # Initialize components
    scraper = RegulationScraper()
    vector_store = RegulationVectorStore()
    db = RegulationDB()
    
    # Read Excel file
    try:
        df = pd.read_excel(csv_path, engine='openpyxl')
        print(f"[OK] Loaded {len(df)} rows from Excel file")
    except Exception as e:
        print(f"[ERROR] Error reading Excel file: {e}")
        return
    
    # Normalize column names
    df.columns = df.columns.str.strip().str.lower()
    
    # Map Excel-style headers to internal names (align with database loader)
    column_mapping = {
        "hyperlink": "hyperlink",
        "url": "hyperlink",
        "link": "hyperlink",
        "regulation category": "category",
        "regulation_category": "category",
        "category": "category",
        "source name": "source_name",
        "source_name": "source_name",
        "law_name": "source_name",
        "name": "source_name",
    }
    for old_col in list(df.columns):
        target = None
        for key, value in column_mapping.items():
            if old_col == key or old_col.replace("_", " ").replace("-", " ") == key.replace("_", " "):
                target = value
                break
        if target and (target not in df.columns or df.columns.get_loc(target) == df.columns.get_loc(old_col)):
            df.rename(columns={old_col: target}, inplace=True)
    
    # Map column names to standard names
    column_mapping = {
        'hyperlink': 'hyperlink',
        'url': 'hyperlink',
        'link': 'hyperlink',
        'category': 'category',
        'city': 'city',
        'level': 'level',
        'type': 'level',
        'source_name': 'source_name',
        'source name': 'source_name',
        'name': 'source_name'
    }
    
    # Rename columns
    for old_col in df.columns:
        for key, value in column_mapping.items():
            if old_col == key or old_col.replace('_', ' ').replace('-', ' ') == key.replace('_', ' '):
                if value not in df.columns or df.columns.get_loc(value) == df.columns.get_loc(old_col):
                    df.rename(columns={old_col: value}, inplace=True)
                break
    
    # Check required columns
    if 'hyperlink' not in df.columns:
        print("[ERROR] Missing required column: hyperlink")
        return
    
    # Statistics
    total_sources = len(df)
    processed = 0
    skipped = 0
    errors = 0
    total_chunks = 0
    
    start_time = time.time()
    
    print(f"\n[INFO] Processing {total_sources} sources...")
    print("-" * 60)
    
    # Process each row
    for idx, row in df.iterrows():
        # Get URL from hyperlink column first, then try URL column, handle NaN properly
        url_raw = row.get("hyperlink", "")
        if pd.isna(url_raw) or str(url_raw).strip().lower() in ["nan", "none", ""]:
            # Try URL column as fallback
            url_raw = row.get("url", "")
        
        if pd.isna(url_raw) or str(url_raw).strip().lower() in ["nan", "none", ""]:
            skipped += 1
            continue  # Skip empty rows silently
        
        url = str(url_raw).strip()
        
        # Get other fields with NaN handling
        # Use original Regulation Category semantics, then normalize for ESA/HUD/Rent Control
        category_raw = row.get("category", "")
        category_str = str(category_raw).strip() if not pd.isna(category_raw) else "Other"
        raw_category = category_str.lower().strip()
        
        if "esa" in raw_category or "emotional support" in raw_category:
            category = "esa"
        elif "hud" in raw_category or "housing and urban development" in raw_category:
            category = "hud"
        elif "rent" in raw_category or "increase" in raw_category:
            category = "rent control"
        else:
            category = raw_category or "other"
        
        city_raw = row.get("city", "")
        city = str(city_raw).strip() if "city" in df.columns and not pd.isna(city_raw) else "Texas-Statewide"
        
        level_raw = row.get("level", "")
        level = str(level_raw).strip() if not pd.isna(level_raw) else "Unknown"
        
        source_name_raw = row.get("source_name", "")
        source_name = str(source_name_raw).strip() if not pd.isna(source_name_raw) and str(source_name_raw).lower() != "nan" else ""
        
        # Generate source name if missing
        if not source_name:
            source_name = f"{category} - {city}" if category and city else f"Source {idx + 1}"
        
        # Skip if URL is invalid format
        if not (url.startswith('http://') or url.startswith('https://') or 
                url.startswith('file://') or url.replace('\\', '/').startswith('/')):
            skipped += 1
            continue
        
        print(f"\n[{idx + 1}/{total_sources}] Processing: {source_name}")
        print(f"   URL: {url[:80]}...")
        
        try:
            # Fetch content
            content_obj = scraper.fetch_url_content(url)
            
            if not content_obj:
                print(f"   [WARNING] Could not fetch content, skipping")
                skipped += 1
                continue
            
            content = content_obj.get("content", "")
            # Normalize OCR/vertical text artifacts before chunking
            content = normalize_ocr_text(content)
            content_hash = content_obj.get("hash", "")
            
            if not content or len(content) < 300:
                print(f"   [WARNING] Not enough content ({len(content)} chars), skipping")
                skipped += 1
                continue
            
            # Chunk text
            chunks = scraper.chunk_text(content)
            
            if not chunks:
                print(f"   [WARNING] Failed to split content into chunks, skipping")
                skipped += 1
                continue
            
            print(f"   [INFO] Extracted {len(content)} characters, created {len(chunks)} chunks")
            
            # Check if regulation already exists in database
            existing_reg = db.get_regulation_by_url(url)
            
            if existing_reg:
                regulation_id = str(existing_reg['id'])
                # Check if content has changed
                if not FORCE_REINGEST and existing_reg.get('content_hash') == content_hash:
                    print(f"   [INFO] Content unchanged, skipping indexing")
                    skipped += 1
                    continue
                else:
                    print(f"   [UPDATE] Content changed or FORCE_REINGEST enabled, re-indexing...")
                    # Delete old chunks
                    vector_store.delete_regulation(regulation_id)
            else:
                # Add new regulation to database
                regulation_id = str(db.add_regulation(
                    source_name=source_name,
                    url=url,
                    type=level,
                    category=category,
                    content_hash=content_hash
                ))
                print(f"   [OK] Added to database (ID: {regulation_id})")
            
            # Add chunks to vector store (category is already normalized)
            vector_store.add_regulation_chunks(
                regulation_id=regulation_id,
                source_name=source_name,
                url=url,
                category=category,
                chunks=chunks
            )
            
            # Update hash in database
            db.update_regulation_hash(url, content_hash)
            
            processed += 1
            total_chunks += len(chunks)
            print(f"   [OK] Successfully indexed {len(chunks)} chunks")
            
        except Exception as e:
            print(f"   [ERROR] Error processing {url[:50]}...: {e}")
            errors += 1
            import traceback
            traceback.print_exc()
            continue
    
    # Persist ChromaDB to disk
    print("\n" + "-" * 60)
    print("[INFO] Persisting ChromaDB to disk...")
    try:
        # ChromaDB with DuckDB+Parquet backend persists automatically
        # But we can try to explicitly persist if using PersistentClient
        if hasattr(vector_store.client, 'persist'):
            vector_store.client.persist()
            print("[OK] Database persisted successfully")
        else:
            print("[INFO] Database uses automatic persistence (DuckDB+Parquet)")
    except Exception as e:
        print(f"[WARNING] Persistence note: {e}")
    
    # Summary
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)
    print(f"Statistics:")
    print(f"   Total sources: {total_sources}")
    print(f"   [OK] Processed: {processed}")
    print(f"   [WARNING] Skipped: {skipped}")
    print(f"   [ERROR] Errors: {errors}")
    print(f"   Total chunks indexed: {total_chunks}")
    print(f"   Time elapsed: {elapsed_time:.1f} seconds")
    print("=" * 60)

if __name__ == "__main__":
    ingest_regulations()

