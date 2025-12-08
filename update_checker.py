"""
Regulation update checker module
"""
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from config import OPENAI_API_KEY, OPENAI_MODEL, TEMPERATURE, SUPPORTED_CITIES
from typing import List, Dict
import re
import os

class UpdateChecker:
    def __init__(self):
        self.db = RegulationDB()
        self.scraper = RegulationScraper()
        self.vector_store = RegulationVectorStore()
    
    def check_for_updates(self) -> List[Dict]:
        """Check all regulations for updates"""
        regulations = self.db.get_all_regulations()
        updates = []
        checked = 0
        changed = 0
        
        for reg in regulations:
            url = reg['url']
            
            # Skip invalid URLs (but allow local file paths)
            if not url:
                continue
            # Allow http://, https://, file://, and local file paths
            if not (url.startswith(('http://', 'https://', 'file://')) or os.path.exists(url)):
                continue
            
            checked += 1
            
            # Fetch current content
            content_data = self.scraper.fetch_url_content(url)
            if not content_data:
                continue
            
            current_hash = content_data['hash']
            stored_hash = reg.get('content_hash')
            
            # If no stored hash, this is first time - store it but don't create update
            if not stored_hash:
                self.db.update_regulation_hash(url, current_hash)
                continue
            
            # If hash changed, there's an update
            if current_hash != stored_hash:
                changed += 1
                # Generate update summary
                summary = self.generate_update_summary(
                    reg['source_name'],
                    content_data['content'],
                    reg.get('category', '')
                )
                
                # Detect affected cities
                affected_cities = self.detect_affected_cities(
                    content_data['content'],
                    reg.get('category', '')
                )
                
                # Save update
                update_id = self.db.add_update(
                    regulation_id=reg['id'],
                    update_summary=summary,
                    affected_cities=affected_cities
                )
                
                # Update hash
                self.db.update_regulation_hash(url, current_hash)
                
                # Re-index in vector store
                chunks = self.scraper.chunk_text(content_data['content'])
                if chunks:
                    self.vector_store.add_regulation_chunks(
                        regulation_id=str(reg['id']),
                        source_name=reg['source_name'],
                        url=url,
                        category=reg.get('category', 'Other'),
                        chunks=chunks
                    )
                
                updates.append({
                    "regulation_id": reg['id'],
                    "source_name": reg['source_name'],
                    "url": url,
                    "summary": summary,
                    "affected_cities": affected_cities,
                    "category": reg.get('category', 'Unknown')
                })
        
        # Log results
        print(f"Update check complete: Checked {checked} regulations, found {changed} updates")
        
        return updates
    
    def generate_update_summary(self, source_name: str, content: str, category: str) -> str:
        """Generate summary of regulation update using LLM"""
        # Check if OpenAI API is available
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            return f"Update detected in {source_name} ({category}). Content hash changed. Manual review recommended. Content length: {len(content)} characters."
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # Take first 5000 chars for summary
            content_sample = content[:5000]
            
            prompt = f"""Analyze this regulation update and provide a concise summary.

Source: {source_name}
Category: {category}

Content excerpt:
{content_sample}

Provide a brief summary (2-3 sentences) of what changed or what this regulation covers.
Focus on key compliance requirements for housing/rental properties in Texas."""

            response = client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a legal compliance expert specializing in Texas housing regulations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=TEMPERATURE,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            return f"Update detected in {source_name}. Content hash changed. Manual review recommended."
    
    def detect_affected_cities(self, content: str, category: str) -> List[str]:
        """Detect which cities are affected by this regulation"""
        affected = []
        content_lower = content.lower()
        
        # Check for city mentions
        city_keywords = {
            "Dallas": ["dallas", "dallas county"],
            "Houston": ["houston", "harris county"],
            "Austin": ["austin", "travis county"],
            "San Antonio": ["san antonio", "bexar county"]
        }
        
        for city, keywords in city_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                affected.append(city)
        
        # If no specific city mentioned, check category
        if not affected:
            if "local" in category.lower() or "city" in category.lower():
                # Try to infer from category or source
                if "dallas" in category.lower():
                    affected.append("Dallas")
                elif "houston" in category.lower():
                    affected.append("Houston")
                elif "austin" in category.lower():
                    affected.append("Austin")
                elif "san antonio" in category.lower():
                    affected.append("San Antonio")
            else:
                # State or federal - affects all
                affected.append("Texas-Statewide")
        
        if not affected:
            affected.append("Texas-Statewide")
        
        return affected
