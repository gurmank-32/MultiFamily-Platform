"""
Update checker module for detecting regulation changes
"""
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from config import OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, SUPPORTED_CITIES
from typing import List, Dict
import re

class UpdateChecker:
    def __init__(self):
        """Initialize update checker with database, scraper, and vector store"""
        try:
            self.db = RegulationDB()
            self.scraper = RegulationScraper()
            # Initialize vector store, but handle if it fails
            try:
                self.vector_store = RegulationVectorStore()
            except Exception as e:
                print(f"Warning: Vector store initialization failed: {e}")
                self.vector_store = None
        except Exception as e:
            print(f"Warning: UpdateChecker initialization error: {e}")
            self.db = None
            self.scraper = None
            self.vector_store = None
    
    def check_for_updates(self) -> List[Dict]:
        """
        Check for regulation updates by comparing content hashes.
        Returns a list of update dictionaries.
        """
        if not self.db or not self.scraper:
            return []
        
        updates = []
        
        try:
            # Get all regulations from database
            regulations = self.db.get_all_regulations()
            
            for reg in regulations:
                url = reg.get('url')
                if not url or not url.startswith(('http://', 'https://')):
                    continue
                
                # Fetch current content
                content_data = self.scraper.fetch_url_content(url)
                if not content_data or not content_data.get('content'):
                    continue
                
                current_hash = content_data['hash']
                stored_hash = reg.get('content_hash')
                
                # Check if content changed
                if stored_hash and stored_hash != current_hash:
                    # Update detected
                    update_info = {
                        'regulation_id': reg['id'],
                        'source_name': reg.get('source_name', 'Unknown'),
                        'url': url,
                        'category': reg.get('category', ''),
                        'city': self._detect_city_from_content(content_data['content'], reg.get('category', '')),
                        'detected_date': reg.get('last_checked', ''),
                        'summary': self._generate_summary(content_data['content'], reg.get('source_name', '')),
                        'hyperlink': url
                    }
                    updates.append(update_info)
                    
                    # Update hash in database
                    self.db.update_regulation_hash(url, current_hash)
                    
                    # Re-index in vector store if available
                    if self.vector_store is not None:
                        try:
                            chunks = self.scraper.chunk_text(content_data['content'])
                            if chunks:
                                self.vector_store.add_regulation_chunks(
                                    chunks=chunks,
                                    source_name=reg.get('source_name', ''),
                                    url=url,
                                    category=reg.get('category', ''),
                                    geography=update_info['city']
                                )
                        except Exception as e:
                            print(f"Warning: Failed to re-index regulation: {e}")
        
        except Exception as e:
            print(f"Error checking for updates: {e}")
        
        return updates
    
    def _detect_city_from_content(self, content: str, category: str) -> str:
        """Detect which city the content relates to"""
        content_lower = content.lower()
        
        for city in SUPPORTED_CITIES:
            if city.lower() in content_lower:
                return city
        
        return "Texas-Statewide"
    
    def _generate_summary(self, content: str, source_name: str) -> str:
        """Generate a brief summary of the regulation content"""
        # Simple extraction - take first few sentences
        sentences = re.split(r'[.!?]+', content)
        summary = ' '.join(sentences[:3]).strip()
        
        if len(summary) > 200:
            summary = summary[:200] + "..."
        
        return summary if summary else f"Update detected in {source_name}"

