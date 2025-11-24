"""
Script to reload all regulations from source.csv and re-index them
"""
import sys
import os
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from config import SOURCES_FILE

def reload_all_sources():
    """Reload all sources from CSV and re-index them"""
    print("=" * 60)
    print("Reloading Regulations from source.csv")
    print("=" * 60)
    
    # Check if source.csv exists
    if not os.path.exists(SOURCES_FILE):
        print(f"❌ Error: {SOURCES_FILE} not found!")
        print(f"Please create {SOURCES_FILE} with the following format:")
        print("category,city_name,law_name,hyperlink")
        print("Federal,Texas-Statewide,HUD Fair Housing Act,https://...")
        return False
    
    # Initialize components
    print("\n1. Initializing components...")
    db = RegulationDB()
    scraper = RegulationScraper()
    vector_store = RegulationVectorStore()
    
    # Load regulations from CSV
    print(f"\n2. Loading regulations from {SOURCES_FILE}...")
    try:
        result = db.load_regulations_from_csv(SOURCES_FILE)
        print(f"   ✅ Loaded {result['loaded']} regulations")
        print(f"   ⚠️  Skipped {result['skipped']} invalid entries")
        
        if result['loaded'] == 0:
            print("\n❌ No regulations were loaded. Please check your CSV file format.")
            return False
        
    except Exception as e:
        print(f"❌ Error loading CSV: {str(e)}")
        return False
    
    # Get all regulations
    print("\n3. Fetching all regulations from database...")
    regulations = db.get_all_regulations()
    print(f"   Found {len(regulations)} total regulations in database")
    
    # Re-index all regulations
    print("\n4. Scraping and indexing regulations in vector store...")
    print("   This may take several minutes depending on the number of sources...")
    
    indexed = 0
    skipped = 0
    errors = []
    
    for i, reg in enumerate(regulations, 1):
        url = reg.get('url', '')
        source_name = reg.get('source_name', 'Unknown')
        
        print(f"\n   [{i}/{len(regulations)}] Processing: {source_name}")
        print(f"      URL: {url[:80]}...")
        
        # Check if URL is valid
        if not url:
            print(f"      ⚠️  Skipped: No URL")
            skipped += 1
            continue
        
        # Check if it's a valid URL or file path
        is_valid = (
            url.startswith('http://') or 
            url.startswith('https://') or 
            url.startswith('file://') or 
            os.path.exists(url)
        )
        
        if not is_valid:
            print(f"      ⚠️  Skipped: Invalid URL format")
            skipped += 1
            continue
        
        try:
            # Fetch content
            print(f"      📥 Fetching content...")
            content = scraper.fetch_url_content(url)
            
            if not content or not content.get('content'):
                print(f"      ⚠️  Skipped: Could not fetch content")
                skipped += 1
                continue
            
            # Chunk text
            print(f"      ✂️  Chunking content...")
            chunks = scraper.chunk_text(content['content'])
            
            if not chunks:
                print(f"      ⚠️  Skipped: No chunks created")
                skipped += 1
                continue
            
            # Delete old chunks for this regulation (if any)
            vector_store.delete_regulation(str(reg['id']))
            
            # Add to vector store
            print(f"      💾 Indexing {len(chunks)} chunks...")
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
            print(f"      ✅ Successfully indexed!")
            
        except Exception as e:
            error_msg = str(e)
            print(f"      ❌ Error: {error_msg}")
            errors.append(f"{source_name}: {error_msg}")
            skipped += 1
            continue
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"✅ Successfully indexed: {indexed} regulations")
    print(f"⚠️  Skipped: {skipped} regulations")
    
    if errors:
        print(f"\n❌ Errors encountered: {len(errors)}")
        print("\nError details:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
    
    print("\n" + "=" * 60)
    print("✅ Reload complete!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = reload_all_sources()
    sys.exit(0 if success else 1)

