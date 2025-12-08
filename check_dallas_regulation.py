"""
Script to check the specific Dallas Rent Control regulation
"""
from database import RegulationDB
import sqlite3

def check_dallas_regulation():
    """Check the specific regulation"""
    db = RegulationDB()
    
    # Connect to database
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    
    # Find the specific one the user mentioned
    cursor.execute("""
        SELECT id, source_name, url, last_checked 
        FROM regulations 
        WHERE url = 'file:///C:/Users/safaa/OneDrive/Desktop/Agent Intellectual Platform/dallas_rent_control_policy.html'
           OR source_name = 'Dallas Rent Control Policy - Maximum Rent Increase Cap'
    """)
    rows = cursor.fetchall()
    
    print("Found regulation:")
    for row in rows:
        print(f"  ID: {row[0]}")
        print(f"  Name: {row[1]}")
        print(f"  URL: {row[2]}")
        print(f"  Last Checked: {row[3]}")
    
    conn.close()

if __name__ == "__main__":
    check_dallas_regulation()

