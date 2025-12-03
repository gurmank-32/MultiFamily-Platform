"""
Re-scrape ESA source with improved scraper
"""
from scraper import RegulationScraper
from database import RegulationDB
from vector_store import RegulationVectorStore
import sys
import io

# Fix Unicode issues
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def rescrape_esa():
    """Re-scrape ESA source and reload into system"""
    print("=" * 60)
    print("Re-scraping ESA Source")
    print("=" * 60)
    
    scraper = RegulationScraper()
    db = RegulationDB()
    vs = RegulationVectorStore()
    
    # Find ESA regulation
    esa_url = "https://guides.sll.texas.gov/animal-law/service-animals"
    print(f"\n1. Fetching content from: {esa_url}")
    
    result = scraper.fetch_url_content(esa_url)
    
    if result:
        content = result['content']
        print(f"\n2. Extracted content length: {len(content)} characters")
        
        # Show first 500 characters
        print("\n3. First 500 characters:")
        print("-" * 60)
        print(content[:500])
        print("-" * 60)
        
        # Find regulation in DB
        regulation = db.get_regulation_by_url(esa_url)
        if regulation:
            print(f"\n4. Found regulation: {regulation['source_name']}")
            print(f"   Category: {regulation['category']}")
            
            # Delete old chunks
            print("\n5. Deleting old chunks from vector store...")
            vs.delete_regulation(regulation['id'])
            
            # Create new chunks
            print("6. Creating new chunks...")
            chunks = scraper.chunk_text(content)
            print(f"   Created {len(chunks)} chunks")
            
            if chunks:
                # Show first chunk
                print(f"\n7. First chunk ({len(chunks[0])} chars):")
                print("-" * 60)
                print(chunks[0][:300])
                print("-" * 60)
                
                # Re-index
                print("\n8. Re-indexing in vector store...")
                vs.add_regulation_chunks(
                    regulation_id=regulation['id'],
                    chunks=chunks,
                    source_name=regulation['source_name'],
                    url=esa_url,
                    category=regulation['category'],
                    city=regulation.get('city', 'Texas-Statewide')
                )
                print("   Done! Re-indexed successfully.")
            else:
                print("   ERROR: No chunks created - content may be too short")
        else:
            print("   ERROR: Regulation not found in database")
    else:
        print("   ERROR: Failed to fetch content")

if __name__ == "__main__":
    rescrape_esa()

