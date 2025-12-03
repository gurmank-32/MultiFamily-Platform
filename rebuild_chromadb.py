"""Rebuild ChromaDB from scratch"""
import os
import shutil
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore

print("=" * 60)
print("REBUILDING CHROMADB DATABASE")
print("=" * 60)

# Step 1: Backup/Remove old ChromaDB
print("\n1. Removing old ChromaDB database...")
chroma_path = "chroma_db"
backup_path = "chroma_db_backup_old"

if os.path.exists(chroma_path):
    try:
        # Try to rename first (works even if files are locked)
        if os.path.exists(backup_path):
            try:
                shutil.rmtree(backup_path)
            except:
                pass
        os.rename(chroma_path, backup_path)
        print(f"   SUCCESS: Moved {chroma_path} to {backup_path}")
    except Exception as e:
        try:
            # If rename fails, try direct delete
            shutil.rmtree(chroma_path)
            print(f"   SUCCESS: Deleted {chroma_path}")
        except Exception as e2:
            print(f"   WARNING: Error removing {chroma_path}: {e2}")
            print("   The database may be in use. Please:")
            print("   1. Close the Streamlit app if it's running")
            print("   2. Manually delete the 'chroma_db' folder")
            print("   3. Run this script again")
            exit(1)

# Step 2: Initialize new database and vector store
print("\n2. Initializing new database and vector store...")
db = RegulationDB()
scraper = RegulationScraper()
vector_store = RegulationVectorStore()  # This will create a new database
print("   SUCCESS: New vector store created")

# Step 3: Get all regulations from database
print("\n3. Loading regulations from database...")
regulations = db.get_all_regulations()
print(f"   Found {len(regulations)} regulations")

# Step 4: Index all regulations
print("\n4. Indexing regulations...")
indexed = 0
skipped = 0
errors = []

for idx, reg in enumerate(regulations, 1):
    url = reg.get('url', '')
    source_name = reg.get('source_name', 'Unknown')
    
    if idx % 10 == 0:
        print(f"   Progress: {idx}/{len(regulations)} ({indexed} indexed, {skipped} skipped)")
    
    try:
        # Fetch content
        content = scraper.fetch_url_content(url)
        
        if not content or not content.get('content'):
            skipped += 1
            continue
        
        # Chunk text
        chunks = scraper.chunk_text(content['content'])
        
        if not chunks:
            skipped += 1
            continue
        
        # Add to vector store
        vector_store.add_regulation_chunks(
            regulation_id=str(reg['id']),
            source_name=source_name,
            url=url,
            category=reg.get('category', 'Other'),
            chunks=chunks
        )
        
        # Update hash in database
        db.update_regulation_hash(url, content['hash'])
        
        indexed += 1
        
    except Exception as e:
        errors.append(f"{source_name}: {str(e)}")
        skipped += 1

print(f"\nSUCCESS: Rebuild complete!")
print(f"   Indexed: {indexed}")
print(f"   Skipped: {skipped}")
if errors:
    print(f"   Errors: {len(errors)}")
    print("\n   First 5 errors:")
    for error in errors[:5]:
        print(f"     - {error}")

# Step 5: Test search
print("\n5. Testing search...")
test_results = vector_store.search("What is ESA?", n_results=3)
print(f"   Found {len(test_results)} results for 'What is ESA?'")
if test_results:
    print(f"   SUCCESS: Search is working!")
    print(f"   First result: {test_results[0].get('source_name', 'N/A')}")
else:
    print(f"   WARNING: No results found")

