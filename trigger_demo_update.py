"""
Script to manually trigger the Dallas rent control demo update
This ensures the update appears in the Update Log and sends email alerts
"""
from database import RegulationDB
from scraper import RegulationScraper
from update_checker import UpdateChecker
from email_alerts import EmailAlertSystem
import os

def trigger_demo_update():
    """Trigger the Dallas rent control demo update"""
    db = RegulationDB()
    scraper = RegulationScraper()
    email_system = EmailAlertSystem()
    
    # Path to the demo HTML file (relative path for cross-platform compatibility)
    demo_url = "test_rent_control_dallas_demo.html"
    
    # Convert to absolute path for file existence check
    demo_path = os.path.abspath(demo_url)
    if not os.path.exists(demo_path):
        print(f"Error: Demo file not found at {demo_path}")
        print(f"Looking for: {demo_url}")
        return
    
    # Get or create regulation entry
    reg = db.get_regulation_by_url(demo_url)
    
    if not reg:
        # Add the regulation if it doesn't exist
        regulation_id = db.add_regulation(
            source_name="Dallas Rent Control 2025 (DEMO)",
            url=demo_url,
            type="Local",
            category="Rent Control",
            content_hash=None
        )
        print(f"Added new regulation with ID: {regulation_id}")
    else:
        regulation_id = reg['id']
        print(f"Found existing regulation with ID: {regulation_id}")
    
    # Fetch current content
    content_data = scraper.fetch_url_content(demo_url)
    if not content_data:
        print("Error: Could not fetch content from demo file")
        return
    
    # Generate update summary
    update_summary = """Dallas has enacted a new rent control policy that prohibits landlords from raising rent by more than $250 above the tenant's existing monthly rent. This cap applies regardless of property improvements, upgrades, or neighborhood characteristics.

For leasing managers, this means every rent increase must be reviewed carefully before issuing renewal offers or updated lease agreements. Standard automated percentage-increase clauses (like 5–10% annual increases) must be paused or rewritten to ensure they never exceed a $250 difference.

Property managers must maintain detailed rent-change records for each tenant to prove that no unlawful increase occurred. Staff must also review budgeting and revenue planning, since limiting increases might reduce projected income for the property."""
    
    # Add the update to the database
    update_id = db.add_update(
        regulation_id=regulation_id,
        update_summary=update_summary,
        affected_cities=["Dallas"]
    )
    
    print(f"[SUCCESS] Created update entry with ID: {update_id}")
    
    # Update the content hash so it won't trigger again automatically
    db.update_regulation_hash(demo_url, content_data['hash'])
    
    # Send email alerts to all Dallas subscribers
    update_data = {
        "source_name": "Dallas Rent Control 2025 (DEMO)",
        "url": demo_url,
        "summary": update_summary,
        "affected_cities": ["Dallas"],
        "category": "Rent Control"
    }
    
    notified = email_system.notify_subscribers(update_data)
    
    if notified:
        print(f"[SUCCESS] Sent email alerts to {len(notified)} Dallas subscribers:")
        for email in notified:
            print(f"   - {email}")
    else:
        print("[INFO] No Dallas subscribers found. No emails sent.")
    
    print("\n[DONE] Demo update triggered successfully!")
    print("   - Update added to database")
    print("   - Email alerts sent to subscribers")
    print("   - Update will appear in the Update Log")

if __name__ == "__main__":
    trigger_demo_update()

