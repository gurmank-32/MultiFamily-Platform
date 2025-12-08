"""
Script to update the last_checked date for Dallas Rent Control demo source to today
"""
from database import RegulationDB
from datetime import datetime
import sqlite3
import os

def update_dallas_demo_date():
    """Update last_checked date for Dallas Rent Control demo source"""
    db = RegulationDB()
    
    # Connect to database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Find all Dallas Rent Control regulations
    cursor.execute("""
        SELECT id, source_name, url, last_checked 
        FROM regulations 
        WHERE source_name LIKE '%Dallas Rent Control%' 
           OR url LIKE '%dallas_rent%' 
           OR url LIKE '%test_rent_control%'
           OR url LIKE '%rent_control_dallas%'
    """)
    rows = cursor.fetchall()
    
    print("Found Dallas Rent Control regulations:")
    for row in rows:
        print(f"  ID: {row[0]}, Name: {row[1]}, URL: {row[2]}, Last Checked: {row[3]}")
    
    # Update all Dallas Rent Control demo sources to today
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute("""
        UPDATE regulations 
        SET last_checked = ?
        WHERE source_name LIKE '%Dallas Rent Control%' 
           OR url LIKE '%dallas_rent%' 
           OR url LIKE '%test_rent_control%'
           OR url LIKE '%rent_control_dallas%'
    """, (today,))
    
    updated_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Updated {updated_count} regulation(s) to today's date: {today}")

if __name__ == "__main__":
    update_dallas_demo_date()
