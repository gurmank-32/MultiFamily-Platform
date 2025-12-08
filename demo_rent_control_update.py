"""
Demo script to add Dallas rent control test source and trigger update detection
"""
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from update_checker import UpdateChecker
from email_alerts import EmailAlertSystem
import os

def setup_demo():
    """Set up the demo by adding source and checking for updates"""
    print("Setting up Dallas Rent Control Demo...")
    
    db = RegulationDB()
    scraper = RegulationScraper()
    vector_store = RegulationVectorStore()
    update_checker = UpdateChecker()
    email_system = EmailAlertSystem()
    
    # Demo source details
    source_name = "Dallas Rent Control 2025 (DEMO)"
    url = os.path.abspath("test_rent_control_dallas_demo.html")
    category = "Rent Control"
    source_type = "Local"
    
    print(f"\n1. Adding source: {source_name}")
    print(f"   URL: {url}")
    
    # Check if file exists
    if not os.path.exists(url):
        print(f"   ERROR: File not found at {url}")
        return
    
    # Check if already in database
    existing = db.get_regulation_by_url(url)
    
    if existing:
        print(f"   Source already exists (ID: {existing['id']})")
        regulation_id = existing['id']
        # Update hash to trigger change detection
        content = scraper.fetch_url_content(url)
        if content:
            db.update_regulation_hash(url, content['hash'])
            print(f"   Updated hash to trigger change detection")
    else:
        # Add new regulation
        regulation_id = db.add_regulation(
            source_name=source_name,
            url=url,
            type=source_type,
            category=category
        )
        print(f"   Added to database (ID: {regulation_id})")
    
    # Index in vector store
    print(f"\n2. Indexing content in vector store...")
    content = scraper.fetch_url_content(url)
    if content:
        chunks = scraper.chunk_text(content['content'])
        if chunks:
            vector_store.add_regulation_chunks(
                regulation_id=str(regulation_id),
                source_name=source_name,
                url=url,
                category=category,
                chunks=chunks
            )
            print(f"   Indexed {len(chunks)} chunks")
    
    # Check for updates (this should detect the new content)
    print(f"\n3. Checking for updates...")
    updates = update_checker.check_for_updates()
    
    if updates:
        print(f"   Found {len(updates)} update(s)")
        for update in updates:
            if update['source_name'] == source_name:
                print(f"\n   Update detected for: {update['source_name']}")
                print(f"   Affected cities: {', '.join(update['affected_cities'])}")
                print(f"   Summary: {update['summary'][:200]}...")
                
                # Send email alerts
                print(f"\n4. Sending email alerts to subscribers...")
                notified = email_system.notify_subscribers(update)
                if notified:
                    print(f"   Sent alerts to {len(notified)} subscriber(s): {', '.join(notified)}")
                else:
                    print(f"   No subscribers found for affected cities")
    else:
        print(f"   No updates detected (content may already be indexed)")
        # Force an update by clearing the hash and re-checking
        print(f"\n   Forcing update detection...")
        db.update_regulation_hash(url, "")  # Clear hash
        updates = update_checker.check_for_updates()
        if updates:
            for update in updates:
                if update['source_name'] == source_name:
                    print(f"   Update detected!")
                    notified = email_system.notify_subscribers(update)
                    if notified:
                        print(f"   Sent alerts to {len(notified)} subscriber(s)")
    
    print(f"\n✅ Demo setup complete!")
    print(f"\nNext steps:")
    print(f"  1. Subscribe to Dallas alerts in the app (Email Alerts page)")
    print(f"  2. Check the Update Log page to see the update")
    print(f"  3. Check your email for the alert")

if __name__ == "__main__":
    setup_demo()

