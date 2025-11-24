"""
Initialization script to load and index regulations
"""
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from config import SOURCES_FILE
import pandas as pd

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
            # Support new format: category, city_name, law_name, hyperlink
            if "hyperlink" in df.columns or "hyperlink" in str(row).lower():
                url = str(row.get("hyperlink", row.get("URL", ""))).strip()
                law_name = str(row.get("law_name", "")).strip()
                category = str(row.get("category", "")).strip()
                city_name = str(row.get("city_name", "Texas-Statewide")).strip()
                
                # Use law_name as source_name, or construct from category and city
                if law_name:
                    source_name = law_name
                else:
                    source_name = f"{category} - {city_name}"
                
                # Determine type from category
                if category.lower() == "federal":
                    reg_type = "Federal"
                elif category.lower() == "state":
                    reg_type = "State"
                elif category.lower() == "city":
                    reg_type = "City"
                else:
                    reg_type = "Other"
            else:
                # Old format: Source Name, URL, Type, Regulation Category
                url = str(row.get("URL", "")).strip()
                source_name = str(row.get("Source Name", "")).strip()
                reg_type = str(row.get("Type", "")).strip()
                category = str(row.get("Regulation Category", "Other")).strip()
                city_name = "Texas-Statewide"
            
            # Skip invalid URLs (allow http, https, and file paths)
            import os
            if not url or (not url.startswith(('http://', 'https://', 'file://')) and not os.path.exists(url)):
                skipped += 1
                continue
            
            # Add city to category if it's city-specific
            if city_name and city_name != "Texas-Statewide":
                category = f"{category} - {city_name}"
            
            # Add to database
            db.add_regulation(
                source_name=source_name,
                url=url,
                type=reg_type,
                category=category
            )
            loaded += 1
        
        print(f"✓ Loaded {loaded} regulations, skipped {skipped} invalid entries")
        
        # Index regulations in vector store
        print("Indexing regulations in vector store...")
        regulations = db.get_all_regulations()
        indexed = 0
        
        for reg in regulations:
            if reg['url'] and reg['url'].startswith('http'):
                print(f"  Indexing: {reg['source_name']}...")
                content = scraper.fetch_url_content(reg['url'])
                if content:
                    chunks = scraper.chunk_text(content['content'])
                    if chunks:
                        vector_store.add_regulation_chunks(
                            regulation_id=str(reg['id']),
                            source_name=reg['source_name'],
                            url=reg['url'],
                            category=reg.get('category', 'Other'),
                            chunks=chunks
                        )
                        # Update hash in database
                        db.update_regulation_hash(reg['url'], content['hash'])
                        indexed += 1
        
        print(f"✓ Indexed {indexed} regulations")
        print("\nInitialization complete!")
        
    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        raise

if __name__ == "__main__":
    initialize_system()
