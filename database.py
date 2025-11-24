"""
Database module for storing regulations and updates
"""
import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

class RegulationDB:
    def __init__(self, db_path: str = "regulations.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Regulations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS regulations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                type TEXT,
                category TEXT,
                content_hash TEXT,
                last_checked TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Updates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS updates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                regulation_id INTEGER,
                update_summary TEXT,
                affected_cities TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (regulation_id) REFERENCES regulations(id)
            )
        """)
        
        # Email alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                city TEXT NOT NULL,
                subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                active INTEGER DEFAULT 1
            )
        """)
        
        # Compliance checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compliance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT,
                checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_compliant INTEGER,
                issues_found TEXT,
                result_summary TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_regulation(self, source_name: str, url: str, type: str, category: str, content_hash: str = None):
        """Add or update a regulation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO regulations (source_name, url, type, category, content_hash, last_checked)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (source_name, url, type, category, content_hash, datetime.now()))
        
        conn.commit()
        regulation_id = cursor.lastrowid
        conn.close()
        return regulation_id
    
    def get_regulation_by_url(self, url: str) -> Optional[Dict]:
        """Get regulation by URL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regulations WHERE url = ?", (url,))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                "id": row[0],
                "source_name": row[1],
                "url": row[2],
                "type": row[3],
                "category": row[4],
                "content_hash": row[5],
                "last_checked": row[6],
                "created_at": row[7]
            }
        return None
    
    def get_all_regulations(self) -> List[Dict]:
        """Get all regulations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM regulations")
        rows = cursor.fetchall()
        conn.close()
        
        columns = ["id", "source_name", "url", "type", "category", "content_hash", "last_checked", "created_at"]
        return [dict(zip(columns, row)) for row in rows]
    
    def update_regulation_hash(self, url: str, content_hash: str):
        """Update content hash and last_checked timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE regulations 
            SET content_hash = ?, last_checked = ?
            WHERE url = ?
        """, (content_hash, datetime.now(), url))
        conn.commit()
        conn.close()
    
    def add_update(self, regulation_id: int, update_summary: str, affected_cities: List[str]):
        """Add a regulation update"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO updates (regulation_id, update_summary, affected_cities)
            VALUES (?, ?, ?)
        """, (regulation_id, update_summary, json.dumps(affected_cities)))
        conn.commit()
        update_id = cursor.lastrowid
        conn.close()
        return update_id
    
    def get_recent_updates(self, limit: int = 50) -> List[Dict]:
        """Get recent updates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.*, r.source_name, r.url, r.category
            FROM updates u
            JOIN regulations r ON u.regulation_id = r.id
            ORDER BY u.detected_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        conn.close()
        
        columns = ["id", "regulation_id", "update_summary", "affected_cities", "detected_at", 
                  "source_name", "url", "category"]
        return [dict(zip(columns, row)) for row in rows]
    
    def subscribe_email(self, email: str, city: str) -> bool:
        """Subscribe email for city alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if already subscribed
        cursor.execute("SELECT id FROM email_alerts WHERE email = ? AND city = ? AND active = 1", 
                      (email, city))
        if cursor.fetchone():
            conn.close()
            return False
        
        cursor.execute("""
            INSERT INTO email_alerts (email, city)
            VALUES (?, ?)
        """, (email, city))
        conn.commit()
        conn.close()
        return True
    
    def unsubscribe_email(self, email: str, city: str) -> bool:
        """Unsubscribe email from city alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE email_alerts 
            SET active = 0 
            WHERE email = ? AND city = ? AND active = 1
        """, (email, city))
        
        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()
        
        return rows_affected > 0
    
    def get_user_subscriptions(self, email: str) -> List[Dict]:
        """Get all active subscriptions for an email"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT city, subscribed_at 
            FROM email_alerts 
            WHERE email = ? AND active = 1
            ORDER BY subscribed_at DESC
        """, (email,))
        rows = cursor.fetchall()
        conn.close()
        
        return [{"city": row[0], "subscribed_at": row[1]} for row in rows]
    
    def get_subscribers_for_city(self, city: str) -> List[str]:
        """Get all active subscribers for a city"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM email_alerts WHERE city = ? AND active = 1", (city,))
        emails = [row[0] for row in cursor.fetchall()]
        conn.close()
        return emails
    
    def save_compliance_check(self, document_name: str, is_compliant: bool, 
                             issues_found: str, result_summary: str):
        """Save compliance check result"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO compliance_checks (document_name, is_compliant, issues_found, result_summary)
            VALUES (?, ?, ?, ?)
        """, (document_name, 1 if is_compliant else 0, issues_found, result_summary))
        conn.commit()
        conn.close()
    
    def load_regulations_from_csv(self, csv_path: str):
        """Load regulations from CSV file - supports both old and new formats"""
        df = pd.read_csv(csv_path)
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
            if not url or (not url.startswith(('http://', 'https://', 'file://')) and not os.path.exists(url)):
                skipped += 1
                continue
            
            # Add city to category if it's city-specific
            if city_name and city_name != "Texas-Statewide":
                category = f"{category} - {city_name}"
            
            self.add_regulation(
                source_name=source_name,
                url=url,
                type=reg_type,
                category=category
            )
            loaded += 1
        
        return {"loaded": loaded, "skipped": skipped}
