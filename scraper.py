"""
Web scraping module for regulation content extraction
"""
import requests
from bs4 import BeautifulSoup
import hashlib
from typing import Optional, Dict, List
import time
import re
import os

class RegulationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_url_content(self, url: str) -> Optional[Dict]:
        """Fetch and extract text content from URL or file path"""
        try:
            # Handle file:// URLs or local file paths
            if url.startswith('file://'):
                # Convert file:// URL to local path
                file_path = url.replace('file:///', '').replace('file://', '')
                # Handle Windows paths
                if file_path.startswith('/'):
                    file_path = file_path[1:]
                file_path = file_path.replace('/', '\\')
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif os.path.exists(url):
                # Direct file path
                with open(url, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif url.startswith(('http://', 'https://')):
                # Web URL
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                content = response.text
            else:
                return None
            
            # Parse HTML (works for both web and file content)
            soup = BeautifulSoup(content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Calculate hash
            content_hash = hashlib.sha256(text.encode()).hexdigest()
            
            return {
                "url": url,
                "content": text,
                "hash": content_hash,
                "length": len(text)
            }
        
        except Exception as e:
            print(f"Error fetching {url}: {str(e)}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks for embedding"""
        if not text:
            return []
        
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def extract_relevant_sections(self, text: str, keywords: List[str]) -> List[str]:
        """Extract sections containing specific keywords"""
        sections = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                sections.append(sentence.strip())
        
        return sections
