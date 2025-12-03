"""
Automated Update Checker - Scheduled Agent
Checks all sources in finalsource11.xlsx for updates and sends email alerts
with duplicate prevention
"""
import pandas as pd
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from email_alerts import EmailAlertSystem
from config import SOURCES_FILE
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Optional
import sqlite3
import os
import sys

class AutomatedUpdateChecker:
    def __init__(self):
        self.db = RegulationDB()
        self.scraper = RegulationScraper()
        self.vector_store = RegulationVectorStore()
        self.email_system = EmailAlertSystem()
        
    def check_all_sources_for_updates(self) -> List[Dict]:
        """Check all sources in finalsource11.xlsx for updates"""
        print("=" * 60)
        print("AUTOMATED UPDATE CHECKER")
        print(f"Checking sources from: {SOURCES_FILE}")
        print("=" * 60)
        
        try:
            # Load sources from Excel
            df = pd.read_excel(SOURCES_FILE)
            print(f"\n[OK] Loaded {len(df)} sources from Excel file")
        except Exception as e:
            print(f"[ERROR] Failed to load sources file: {str(e)}")
            return []
        
        updates_detected = []
        checked_count = 0
        updated_count = 0
        
        # Process each source
        for idx, row in df.iterrows():
            hyperlink = row.get('hyperlink', '').strip()
            source_name = row.get('source_name', '').strip()
            category = row.get('category', '').strip()
            city = row.get('city', '').strip()
            level = row.get('level', '').strip()
            
            if not hyperlink or pd.isna(hyperlink):
                continue
            
            # Skip non-HTTP URLs (local files, etc.)
            if not hyperlink.startswith(('http://', 'https://')):
                continue
            
            checked_count += 1
            print(f"\n[{checked_count}] Checking: {source_name[:50]}...")
            print(f"     URL: {hyperlink[:60]}...")
            
            # Check for update
            update_info = self._check_single_source(
                hyperlink=hyperlink,
                source_name=source_name,
                category=category,
                city=city,
                level=level
            )
            
            if update_info:
                updated_count += 1
                updates_detected.append(update_info)
                print(f"     [UPDATE DETECTED] - Will send alerts to subscribers")
        
        print("\n" + "=" * 60)
        print(f"SUMMARY: Checked {checked_count} sources, found {updated_count} updates")
        print("=" * 60)
        
        return updates_detected
    
    def _check_single_source(self, hyperlink: str, source_name: str, category: str, city: str, level: str) -> Optional[Dict]:
        """Check a single source for updates"""
        try:
            # Fetch current content
            content_data = self.scraper.fetch_url_content(hyperlink)
            if not content_data or not content_data.get('content'):
                print(f"     [SKIP] Could not fetch content")
                return None
            
            current_hash = content_data['hash']
            current_content = content_data['content']
            
            # Get or create regulation in database
            existing_reg = self.db.get_regulation_by_url(hyperlink)
            
            if existing_reg:
                regulation_id = existing_reg['id']
                stored_hash = existing_reg.get('content_hash')
                
                # Check if hash changed
                if stored_hash and stored_hash == current_hash:
                    # No change
                    return None
                
                # Hash changed - there's an update!
                print(f"     [CHANGE DETECTED] Hash changed")
            else:
                # New regulation - add it
                regulation_id = self.db.add_regulation(
                    source_name=source_name,
                    url=hyperlink,
                    type=level,
                    category=category,
                    content_hash=current_hash
                )
                print(f"     [NEW REGULATION] Added to database (ID: {regulation_id})")
                stored_hash = None  # First time, don't send alert
            
            # Determine affected cities
            affected_cities = self._detect_affected_cities(current_content, category, city)
            
            # Generate change hash for duplicate prevention
            change_hash = self._generate_change_hash(source_name, category, affected_cities, current_hash)
            
            # Check if alert was already sent for this change
            if self._is_duplicate_alert(affected_cities, source_name, category, change_hash):
                print(f"     [SKIP] Duplicate alert already sent")
                # Update hash anyway
                self.db.update_regulation_hash(hyperlink, current_hash)
                return None
            
            # Generate update summary
            summary = self._generate_update_summary(source_name, current_content, category, stored_hash)
            
            # Create update entry
            update_id = self.db.add_update(
                regulation_id=regulation_id,
                update_summary=summary,
                affected_cities=affected_cities
            )
            
            # Update regulation hash
            self.db.update_regulation_hash(hyperlink, current_hash)
            
            # Re-index in vector store
            chunks = self.scraper.chunk_text(current_content)
            if chunks:
                self.vector_store.delete_regulation(str(regulation_id))
                self.vector_store.add_regulation_chunks(
                    regulation_id=str(regulation_id),
                    source_name=source_name,
                    url=hyperlink,
                    category=category,
                    chunks=chunks
                )
            
            # Log alert to prevent duplicates
            self._log_alert_sent(affected_cities, source_name, category, change_hash, regulation_id, update_id)
            
            # Return update info for email sending
            return {
                'regulation_id': regulation_id,
                'update_id': update_id,
                'source_name': source_name,
                'url': hyperlink,
                'category': category,
                'city': city,
                'affected_cities': affected_cities,
                'update_summary': summary,
                'change_hash': change_hash
            }
            
        except Exception as e:
            print(f"     [ERROR] {str(e)}")
            return None
    
    def _detect_affected_cities(self, content: str, category: str, source_city: str) -> List[str]:
        """Detect which cities are affected by this regulation"""
        affected = []
        content_lower = content.lower()
        category_lower = category.lower() if category else ""
        
        # City keywords
        city_keywords = {
            "Dallas": ["dallas", "dallas county"],
            "Houston": ["houston", "harris county"],
            "Austin": ["austin", "travis county"],
            "San Antonio": ["san antonio", "bexar county"]
        }
        
        # Check content for city mentions
        for city, keywords in city_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                if city not in affected:
                    affected.append(city)
        
        # Check category for city
        for city in city_keywords.keys():
            if city.lower() in category_lower:
                if city not in affected:
                    affected.append(city)
        
        # Check source_city column
        if source_city and pd.notna(source_city):
            source_city_clean = str(source_city).strip()
            for city in city_keywords.keys():
                if city.lower() == source_city_clean.lower():
                    if city not in affected:
                        affected.append(city)
        
        # If no specific city, check if it's state or federal
        if not affected:
            if "federal" in category_lower or "state" in category_lower or level and "State" in level:
                affected.append("Texas-Statewide")
            else:
                # Default to source city or statewide
                if source_city:
                    affected.append(source_city)
                else:
                    affected.append("Texas-Statewide")
        
        return affected if affected else ["Texas-Statewide"]
    
    def _generate_change_hash(self, source_name: str, category: str, cities: List[str], content_hash: str) -> str:
        """Generate a unique hash for this change to prevent duplicates"""
        combined = f"{source_name}|{category}|{','.join(sorted(cities))}|{content_hash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _is_duplicate_alert(self, cities: List[str], source_name: str, category: str, change_hash: str) -> bool:
        """Check if this alert was already sent"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        # Check for each city
        for city in cities:
            cursor.execute("""
                SELECT id FROM alerts_log
                WHERE city = ? AND regulation_title = ? AND category = ? AND change_hash = ?
            """, (city, source_name, category, change_hash))
            
            if cursor.fetchone():
                conn.close()
                return True
        
        conn.close()
        return False
    
    def _log_alert_sent(self, cities: List[str], source_name: str, category: str, change_hash: str, regulation_id: int, update_id: int):
        """Log that an alert was sent to prevent duplicates"""
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        for city in cities:
            try:
                cursor.execute("""
                    INSERT INTO alerts_log (city, regulation_title, category, change_hash, regulation_id, update_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (city, source_name, category, change_hash, regulation_id, update_id))
            except sqlite3.IntegrityError:
                # Duplicate - already logged
                pass
        
        conn.commit()
        conn.close()
    
    def _generate_update_summary(self, source_name: str, content: str, category: str, old_hash: Optional[str]) -> str:
        """Generate a summary of what changed"""
        if not old_hash:
            # First time - just describe the regulation
            return f"New regulation added: {source_name}. This regulation is now being tracked for updates."
        
        # Content changed - provide basic summary
        content_preview = content[:500].replace('\n', ' ').strip()
        return f"Update detected in {source_name}. Content has changed. Review the source document for specific changes and compliance implications."
    
    def send_alerts_for_updates(self, updates: List[Dict]):
        """Send email alerts for all detected updates"""
        if not updates:
            print("\n[INFO] No updates to alert subscribers about")
            return
        
        print("\n" + "=" * 60)
        print("SENDING EMAIL ALERTS")
        print("=" * 60)
        
        for update in updates:
            affected_cities = update['affected_cities']
            
            print(f"\nRegulation: {update['source_name']}")
            print(f"Affected Cities: {', '.join(affected_cities)}")
            
            # Send alert for each city
            for city in affected_cities:
                if city == "Texas-Statewide":
                    # Send to all subscribers
                    subscribers = self.db.get_all_subscribers()
                else:
                    subscribers = self.db.get_subscribers_for_city(city)
                
                if not subscribers:
                    print(f"  [{city}] No subscribers")
                    continue
                
                print(f"  [{city}] Sending to {len(subscribers)} subscriber(s)")
                
                # Send alert with proper format (one email per subscriber)
                for subscriber_email in subscribers:
                    self.email_system.send_regulation_update_alert(
                        email_list=[subscriber_email],  # Send one at a time
                        city=city,
                        regulation_title=update['source_name'],
                        category=update['category'],
                        url=update['url'],
                        update_summary=update['update_summary'],
                        date_detected=datetime.now()
                    )
        
        print("\n[OK] All alerts sent")

def main():
    """Main function to run the automated update checker"""
    checker = AutomatedUpdateChecker()
    
    # Check all sources for updates
    updates = checker.check_all_sources_for_updates()
    
    # Send email alerts
    checker.send_alerts_for_updates(updates)
    
    print("\n" + "=" * 60)
    print("AUTOMATED UPDATE CHECK COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()

