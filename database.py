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
        
        # Alerts log table for duplicate prevention
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                regulation_title TEXT NOT NULL,
                category TEXT,
                change_hash TEXT NOT NULL,
                date_emailed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                regulation_id INTEGER,
                update_id INTEGER,
                UNIQUE(city, regulation_title, category, change_hash)
            )
        """)
        
        # Add city column to regulations if it doesn't exist (for better tracking)
        try:
            cursor.execute("ALTER TABLE regulations ADD COLUMN city TEXT")
        except sqlite3.OperationalError:
            pass  # Column already exists
        
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
    
    def get_all_subscribers(self) -> List[str]:
        """Get all active subscribers (for Texas-Statewide alerts)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT email FROM email_alerts WHERE active = 1")
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
        """Load regulations from CSV or Excel file - REQUIRED: sources.xlsx with columns: category, city, level, hyperlink
        Returns: {'loaded': count of new regulations, 'skipped': count of invalid/skipped, 'existing': count of already existing, 'new_urls': list of new URLs}
        """
        loaded = 0
        skipped = 0
        existing = 0
        new_urls = []
        
        # Check if file is Excel (.xlsx) or CSV
        if csv_path.endswith('.xlsx') or csv_path.endswith('.xls'):
            try:
                # Read Excel file
                df = pd.read_excel(csv_path, engine='openpyxl')
            except ImportError:
                # Try with xlrd for older Excel files
                try:
                    df = pd.read_excel(csv_path, engine='xlrd')
                except:
                    raise ImportError("Please install openpyxl: pip install openpyxl")
            except Exception as e:
                raise Exception(f"Error reading Excel file: {str(e)}")
        else:
            # Read CSV file
            df = pd.read_csv(csv_path)
        
        # Normalize column names (case-insensitive, handle variations)
        df.columns = df.columns.str.strip().str.lower()
        
        # Map column names to standard names
        column_mapping = {
            'hyperlink': 'hyperlink',
            'url': 'hyperlink',
            'link': 'hyperlink',
            'category': 'category',
            'regulation category': 'category',
            'regulation_category': 'category',
            'city': 'city',
            'city_name': 'city',
            'level': 'level',
            'type': 'level',
            'law_name': 'source_name',
            'source_name': 'source_name',
            'source name': 'source_name',
            'name': 'source_name'
        }
        
        # Rename columns to standard names
        for old_col in df.columns:
            for key, value in column_mapping.items():
                if old_col == key or old_col.replace('_', ' ').replace('-', ' ') == key.replace('_', ' '):
                    if value not in df.columns or df.columns.get_loc(value) == df.columns.get_loc(old_col):
                        df.rename(columns={old_col: value}, inplace=True)
                    break
        
        # REQUIRED COLUMNS: category, level, hyperlink (city is optional, defaults to Texas-Statewide)
        required_columns = ['category', 'level', 'hyperlink']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns in sources file: {', '.join(missing_columns)}. Required columns: category, level, hyperlink (city is optional)")
        
        for _, row in df.iterrows():
            # Get required columns
            url = str(row.get("hyperlink", "")).strip()
            category = str(row.get("category", "")).strip()
            city = str(row.get("city", "Texas-Statewide")).strip() if "city" in df.columns else "Texas-Statewide"
            level = str(row.get("level", "")).strip()
            
            # Get optional source_name if available
            source_name = str(row.get("source_name", "")).strip()
            if not source_name:
                # Construct source_name from category and city
                source_name = f"{category} - {city}" if category and city else "Unknown Source"
            
            # Determine type from level
            level_lower = level.lower()
            if 'federal' in level_lower:
                reg_type = "Federal"
            elif 'state' in level_lower or 'texas' in level_lower:
                reg_type = "State"
            elif 'city' in level_lower or 'local' in level_lower:
                reg_type = "City"
            else:
                # Try to infer from category or city
                if category.lower() == "federal":
                    reg_type = "Federal"
                elif city and city != "Texas-Statewide":
                    reg_type = "City"
                else:
                    reg_type = "State"
            
            # Skip invalid URLs (allow http, https, and file paths)
            if not url or (not url.startswith(('http://', 'https://', 'file://')) and not os.path.exists(url)):
                skipped += 1
                continue
            
            # Check if regulation already exists
            existing_reg = self.get_regulation_by_url(url)
            if existing_reg:
                # Regulation already exists - skip adding it again
                existing += 1
                continue
            
            # Add city to category if it's city-specific
            if city and city != "Texas-Statewide":
                category = f"{category} - {city}"
            
            self.add_regulation(
                source_name=source_name,
                url=url,
                type=reg_type,
                category=category
            )
            loaded += 1
            new_urls.append(url)
        
        return {
            "loaded": loaded,
            "skipped": skipped,
            "existing": existing,
            "new_urls": new_urls
        }
