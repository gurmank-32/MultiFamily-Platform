"""
Script to update all regulations to have a last_checked timestamp
"""
from database import RegulationDB
from datetime import datetime
import sqlite3

def update_all_last_checked():
    """Update all regulations to have a last_checked timestamp"""
    db = RegulationDB()
    
    # Connect to database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Find all regulations without a last_checked date
    cursor.execute("""
        SELECT id, source_name, url, last_checked 
        FROM regulations 
        WHERE last_checked IS NULL OR last_checked = ''
    """)
    rows_without_date = cursor.fetchall()
    
    print(f"Found {len(rows_without_date)} regulations without last_checked date:")
    for row in rows_without_date[:10]:  # Show first 10
        print(f"  ID: {row[0]}, Name: {row[1][:50]}")
    if len(rows_without_date) > 10:
        print(f"  ... and {len(rows_without_date) - 10} more")
    
    # Update all regulations without a last_checked date to today
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        UPDATE regulations 
        SET last_checked = ?
        WHERE last_checked IS NULL OR last_checked = ''
    """, (today,))
    
    updated_count = cursor.rowcount
    conn.commit()
    
    # Also update any that have very old dates or invalid formats to today
    cursor.execute("""
        UPDATE regulations 
        SET last_checked = ?
        WHERE last_checked < '2020-01-01' OR last_checked = 'Never'
    """, (today,))
    
    updated_old_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    total_updated = updated_count + updated_old_count
    print(f"\n[SUCCESS] Updated {total_updated} regulation(s) to today's date: {today}")
    print(f"  - {updated_count} regulations that had NULL/empty dates")
    print(f"  - {updated_old_count} regulations that had very old dates")

if __name__ == "__main__":
    update_all_last_checked()

