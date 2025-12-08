"""
Script to ensure ALL regulations have a valid last_checked timestamp
"""
from database import RegulationDB
from datetime import datetime
import sqlite3

def ensure_all_dates():
    """Ensure all regulations have a valid last_checked timestamp"""
    db = RegulationDB()
    
    # Connect to database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Get all regulations
    cursor.execute("SELECT id, source_name, url, last_checked FROM regulations")
    all_regs = cursor.fetchall()
    
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    updated_count = 0
    
    print(f"Checking {len(all_regs)} regulations...")
    
    for reg in all_regs:
        reg_id, source_name, url, last_checked = reg
        
        # Check if last_checked is NULL, empty, or invalid
        needs_update = False
        if last_checked is None:
            needs_update = True
            reason = "NULL"
        elif last_checked == '':
            needs_update = True
            reason = "empty"
        elif last_checked == 'Never':
            needs_update = True
            reason = "'Never'"
        else:
            # Try to parse the date to see if it's valid
            try:
                datetime.strptime(str(last_checked)[:19], '%Y-%m-%d %H:%M:%S')
            except:
                needs_update = True
                reason = "invalid format"
        
        if needs_update:
            cursor.execute("""
                UPDATE regulations 
                SET last_checked = ?
                WHERE id = ?
            """, (today, reg_id))
            updated_count += 1
            if updated_count <= 10:  # Show first 10
                print(f"  Updating ID {reg_id}: {source_name[:50]} ({reason})")
    
    conn.commit()
    conn.close()
    
    print(f"\n[SUCCESS] Updated {updated_count} regulation(s) to today's date: {today}")
    print(f"All {len(all_regs)} regulations now have valid last_checked dates.")

if __name__ == "__main__":
    ensure_all_dates()

