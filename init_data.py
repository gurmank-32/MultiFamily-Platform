"""
Initialization script to load and index regulations
"""
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from config import SOURCES_FILE
import pandas as pd
import os

def initialize_system():
    """Initialize the system with regulations from CSV"""
    print("Initializing Housing Regulation Compliance Agent...")
    
    # Initialize components
    db = RegulationDB()
    scraper = RegulationScraper()
    vector_store = RegulationVectorStore()
    
    # Load regulations from CSV
    print(f"Loading regulations from {SOURCES_FILE}...")
    try:
        df = pd.read_csv(SOURCES_FILE)
        loaded = 0
        skipped = 0
        
        for _, row in df.iterrows():
            url = str(row.get("URL", "")).strip()
            source_name = str(row.get("Source Name", "")).strip()
            
            # Skip invalid URLs (but allow local file paths)
            if not url:
                skipped += 1
                continue
            # Allow http://, https://, file://, and local file paths
            if not (url.startswith(('http://', 'https://', 'file://')) or os.path.exists(url)):
                skipped += 1
                continue
            
            # Add to database
            db.add_regulation(
                source_name=source_name,
                url=url,
                type=str(row.get("Type", "")).strip(),
                category=str(row.get("Regulation Category", "Other")).strip()
            )
            loaded += 1
        
        print(f"✓ Loaded {loaded} regulations, skipped {skipped} invalid entries")
        
        # Index regulations in vector store
        print("Indexing regulations in vector store...")
        regulations = db.get_all_regulations()
        indexed = 0
        
        for reg in regulations:
            url = reg['url']
            # Process both web URLs and local file paths
            if url and (url.startswith(('http://', 'https://', 'file://')) or os.path.exists(url)):
                print(f"  Indexing: {reg['source_name']}...")
                content = scraper.fetch_url_content(url)
                if content:
                    chunks = scraper.chunk_text(content['content'])
                    if chunks:
                        vector_store.add_regulation_chunks(
                            regulation_id=str(reg['id']),
                            source_name=reg['source_name'],
                            url=url,
                            category=reg.get('category', 'Other'),
                            chunks=chunks
                        )
                        # Update hash in database
                        db.update_regulation_hash(url, content['hash'])
                        indexed += 1
        
        print(f"✓ Indexed {indexed} regulations")
        print("\nInitialization complete!")
        
    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_system()
