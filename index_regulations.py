"""
Script to index regulations that haven't been indexed yet
"""
import sys
import os
import time
# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore

def index_unindexed_regulations():
    """Index only regulations that haven't been indexed yet"""
    print("=" * 70)
    print("INDEXING UNINDEXED REGULATIONS")
    print("=" * 70)
    
    # Initialize components
    print("\n1. Initializing components...")
    db = RegulationDB()
    scraper = RegulationScraper()
    vector_store = RegulationVectorStore()
    
    # Get all regulations
    print("\n2. Fetching regulations from database...")
    regulations = db.get_all_regulations()
    print(f"   Found {len(regulations)} total regulations in database")
    
    # Filter to only unindexed regulations
    to_index = [reg for reg in regulations 
                if not reg.get('content_hash') 
                and reg.get('url', '').startswith(('http://', 'https://', 'file://'))]
    
    total_to_index = len(to_index)
    
    if total_to_index == 0:
        print("\n✅ All regulations are already indexed!")
        return True
    
    print(f"\n3. Found {total_to_index} regulation(s) that need indexing")
    estimated_time = total_to_index * 3  # ~3 seconds per URL
    print(f"   Estimated time: {estimated_time//60} min {estimated_time%60} sec")
    print("\n4. Starting indexing process...\n")
    
    indexed = 0
    skipped = 0
    errors = []
    start_time = time.time()
    
    for idx, reg in enumerate(to_index, 1):
        url = reg.get('url', '')
        source_name = reg.get('source_name', 'Unknown')
        
        # Progress update
        progress = (idx / total_to_index) * 100
        elapsed = time.time() - start_time
        if idx > 1:
            avg_time = elapsed / idx
            remaining = (total_to_index - idx) * avg_time
            print(f"[{idx}/{total_to_index}] ({progress:.1f}%) | Remaining: ~{int(remaining//60)} min {int(remaining%60)} sec")
        else:
            print(f"[{idx}/{total_to_index}] ({progress:.1f}%)")
        
        print(f"   Processing: {source_name}")
        print(f"   URL: {url[:80]}...")
        
        try:
            # Fetch content
            content = scraper.fetch_url_content(url)
            
            if not content or not content.get('content'):
                print(f"   ⚠️  Skipped: Could not fetch content\n")
                skipped += 1
                continue
            
            # Chunk text
            chunks = scraper.chunk_text(content['content'])
            
            if not chunks:
                print(f"   ⚠️  Skipped: No chunks created\n")
                skipped += 1
                continue
            
            # Delete old chunks for this regulation (if any)
            vector_store.delete_regulation(str(reg['id']))
            
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
            print(f"   ✅ Successfully indexed {len(chunks)} chunks!\n")
            
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Error: {error_msg}\n")
            errors.append(f"{source_name}: {error_msg}")
            skipped += 1
            continue
    
    # Summary
    total_time = time.time() - start_time
    print("\n" + "=" * 70)
    print("INDEXING SUMMARY")
    print("=" * 70)
    print(f"✅ Successfully indexed: {indexed} regulation(s)")
    print(f"⚠️  Skipped: {skipped} regulation(s)")
    print(f"⏱️  Total time: {int(total_time//60)} min {int(total_time%60)} sec")
    
    if errors:
        print(f"\n❌ Errors encountered: {len(errors)}")
        print("\nError details (first 5):")
        for error in errors[:5]:
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more errors")
    
    print("\n" + "=" * 70)
    print("✅ Indexing complete!")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    try:
        success = index_unindexed_regulations()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Indexing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

