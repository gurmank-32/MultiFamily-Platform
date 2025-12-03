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
import io
try:
    import PyPDF2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    print("Warning: PyPDF2 not installed. PDF files will not be supported. Install with: pip install PyPDF2")

class RegulationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_url_content(self, url: str) -> Optional[Dict]:
        """Fetch and extract text content from URL or file path - STRICT CLEANING"""
        try:
            is_pdf = False
            content = None
            
            # Handle file:// URLs or local file paths
            if url.startswith('file://'):
                # Convert file:// URL to local path
                file_path = url.replace('file:///', '').replace('file://', '')
                # Handle Windows paths
                if file_path.startswith('/'):
                    file_path = file_path[1:]
                file_path = file_path.replace('/', '\\')
                
                # Check if it's a PDF
                if file_path.lower().endswith('.pdf'):
                    is_pdf = True
                    if not PDF_SUPPORT:
                        print(f"Error: PDF support not available. Install PyPDF2 to process {url}")
                        return None
                    try:
                        with open(file_path, 'rb') as f:
                            pdf_content = f.read()
                        pdf_file = io.BytesIO(pdf_content)
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        
                        text = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        
                        text = re.sub(r'\s+', ' ', text).strip()
                        if not text or len(text) < 50:
                            print(f"Warning: PDF {url} extracted very little text ({len(text)} chars)")
                            return None
                        
                        content_hash = hashlib.sha256(text.encode()).hexdigest()
                        return {
                            "url": url,
                            "content": text,
                            "hash": content_hash,
                            "length": len(text)
                        }
                    except Exception as e:
                        print(f"Error parsing PDF {url}: {str(e)}")
                        return None
                else:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
            elif os.path.exists(url):
                # Direct file path
                if url.lower().endswith('.pdf'):
                    is_pdf = True
                    if not PDF_SUPPORT:
                        print(f"Error: PDF support not available. Install PyPDF2 to process {url}")
                        return None
                    try:
                        with open(url, 'rb') as f:
                            pdf_content = f.read()
                        pdf_file = io.BytesIO(pdf_content)
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        
                        text = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        
                        text = re.sub(r'\s+', ' ', text).strip()
                        if not text or len(text) < 50:
                            print(f"Warning: PDF {url} extracted very little text ({len(text)} chars)")
                            return None
                        
                        content_hash = hashlib.sha256(text.encode()).hexdigest()
                        return {
                            "url": url,
                            "content": text,
                            "hash": content_hash,
                            "length": len(text)
                        }
                    except Exception as e:
                        print(f"Error parsing PDF {url}: {str(e)}")
                        return None
                else:
                    with open(url, 'r', encoding='utf-8') as f:
                        content = f.read()
            elif url.startswith(('http://', 'https://')):
                # Web URL
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Check if it's a PDF file
                content_type = response.headers.get('Content-Type', '').lower()
                is_pdf = url.lower().endswith('.pdf') or 'application/pdf' in content_type or 'pdf' in content_type
                
                # Check if it's a Canva site (JavaScript-rendered content)
                is_canva = 'canva.site' in url.lower() or 'canva.com' in url.lower()
                
                if is_canva:
                    # For Canva sites, extract content from the full HTML response
                    # Canva embeds content in script tags as JSON
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # First, try to extract from script tags that contain the actual content
                    all_text = ""
                    scripts = soup.find_all('script')
                    for script in scripts:
                        if script.string:
                            script_text = script.string
                            # Look for the actual content text (not just code)
                            # Search for patterns that indicate content paragraphs
                            if 'landlords' in script_text.lower() or 'rent' in script_text.lower():
                                # Extract text between quotes or in JSON-like structures
                                # Try to find readable sentences
                                sentences = re.findall(r'[A-Z][^.!?]*[.!?]', script_text)
                                if sentences:
                                    all_text += ' '.join(sentences) + " "
                    
                    # Also try to get text from the full HTML (sometimes Canva renders it)
                    full_html_text = response.text
                    # Look for the content in the HTML directly
                    if 'landlords are now prohibited' in full_html_text.lower():
                        # Extract the paragraph
                        content_match = re.search(
                            r'landlords are now prohibited[^<]*?\.(?:\s+[A-Z][^<]*?\.)*',
                            full_html_text,
                            re.IGNORECASE | re.DOTALL
                        )
                        if content_match:
                            all_text = content_match.group()
                    
                    # If we still don't have good content, use the body text
                    if len(all_text.strip()) < 200:
                        body_text = soup.get_text()
                        # Filter out navigation and keep substantial paragraphs
                        lines = [line.strip() for line in body_text.split('\n') if len(line.strip()) > 50]
                        all_text = ' '.join(lines)
                    
                    # Clean up the text
                    text = re.sub(r'\s+', ' ', all_text).strip()
                    
                    if not text or len(text) < 50:
                        print(f"Warning: Canva site {url} extracted very little text ({len(text)} chars)")
                        return None
                    
                    # Calculate hash
                    content_hash = hashlib.sha256(text.encode()).hexdigest()
                    
                    return {
                        "url": url,
                        "content": text,
                        "hash": content_hash,
                        "length": len(text)
                    }
                
                if is_pdf:
                    # Handle PDF file
                    if not PDF_SUPPORT:
                        print(f"Error: PDF support not available. Install PyPDF2 to process {url}")
                        return None
                    
                    try:
                        pdf_content = response.content
                        pdf_file = io.BytesIO(pdf_content)
                        pdf_reader = PyPDF2.PdfReader(pdf_file)
                        
                        text = ""
                        for page in pdf_reader.pages:
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text + "\n"
                        
                        # Clean up the text
                        text = re.sub(r'\s+', ' ', text).strip()
                        
                        if not text or len(text) < 50:
                            print(f"Warning: PDF {url} extracted very little text ({len(text)} chars)")
                            return None
                        
                        # Calculate hash
                        content_hash = hashlib.sha256(text.encode()).hexdigest()
                        
                        return {
                            "url": url,
                            "content": text,
                            "hash": content_hash,
                            "length": len(text)
                        }
                    except Exception as e:
                        print(f"Error parsing PDF {url}: {str(e)}")
                        return None
                else:
                    # Handle HTML content
                    content = response.text
            else:
                return None
            
            # Parse HTML (works for both web and file content)
            if not is_pdf and content:
                soup = BeautifulSoup(content, 'html.parser')
            
            # FIRST: Find main content BEFORE removing navigation (to avoid breaking structure)
            main_content = None
            
            # Strategy 1: Look for article, main tags
            for tag_name in ['article', 'main']:
                tag = soup.find(tag_name)
                if tag and len(tag.get_text(strip=True)) > 200:
                    main_content = tag
                    break
            
            # Strategy 2: Find the largest div with substantial content (most reliable)
            if not main_content:
                all_divs = soup.find_all('div')
                largest_div = None
                largest_size = 0
                for div in all_divs:
                    # Get text length
                    text_len = len(div.get_text(strip=True))
                    
                    # Skip if too small
                    if text_len < 500:
                        continue
                    
                    # Skip if clearly navigation
                    div_class = ' '.join(div.get('class', [])).lower()
                    div_id = div.get('id', '').lower()
                    skip_keywords = ['nav', 'menu', 'sidebar', 'footer', 'header', 'search', 'breadcrumb']
                    if any(keyword in div_class for keyword in skip_keywords) or \
                       any(keyword in div_id for keyword in skip_keywords):
                        continue
                    
                    # This is likely main content - use the largest one
                    if text_len > largest_size:
                        largest_size = text_len
                        largest_div = div
                
                if largest_div:
                    main_content = largest_div
            
            # NOW remove navigation elements from the main content
            if main_content:
                # Remove scripts, styles from main content
                for element in main_content(["script", "style"]):
                    element.decompose()
                # Extract text - use space separator and strip whitespace, but keep content
                text = main_content.get_text(separator=' ')
                text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
            else:
                # Fallback: Remove navigation from whole page first
                for element in soup(["script", "style", "nav", "footer", "header", 
                                   "aside", "sidebar", "menu", "navigation", 
                                   "tags", "tag", "trending", "related", "share",
                                   "social", "advertisement", "ad", "ads", "banner"]):
                    element.decompose()
                text = soup.get_text(separator=' ')
                text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
            
            # MINIMAL CLEANING - We've already extracted main content, just clean URLs
            # Remove URL patterns (but keep surrounding text)
            text = re.sub(r'https?://[^\s]+', '', text)
            text = re.sub(r'www\.[^\s]+', '', text)
            
            # Normalize whitespace (multiple spaces -> single space)
            text = re.sub(r'\s+', ' ', text)
            text = text.strip()
            
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
    
    def chunk_text(self, text: str, chunk_size: int = 600, overlap: int = 100) -> List[str]:
        """Split text into chunks for embedding - 400-800 characters with regex noise removal"""
        if not text:
            return []
        
        # Simple chunking - split text into overlapping chunks of 400-800 characters
        # No additional filtering needed - text is already clean from fetch_url_content
        chunks = []
        
        # Split text into words
        words = text.split()
        if not words:
            return []
        
        # Create chunks of approximately 600 characters (target size)
        current_chunk_words = []
        current_chunk_len = 0
        target_size = 600
        overlap_size = 100  # Overlap between chunks
        
        for word in words:
            word_len = len(word) + 1  # +1 for space
            current_chunk_words.append(word)
            current_chunk_len += word_len
            
            # If chunk is at least target size, save it
            if current_chunk_len >= target_size:
                chunk_text = ' '.join(current_chunk_words)
                if len(chunk_text) >= 400:  # Minimum size
                    chunks.append(chunk_text)
                
                # Keep last few words for overlap (approximately last 100 chars)
                overlap_words = []
                overlap_len = 0
                for w in reversed(current_chunk_words):
                    overlap_words.insert(0, w)
                    overlap_len += len(w) + 1
                    if overlap_len >= overlap_size:
                        break
                
                current_chunk_words = overlap_words
                current_chunk_len = overlap_len
        
        # Add remaining chunk if it's large enough
        if current_chunk_words:
            chunk_text = ' '.join(current_chunk_words)
            if len(chunk_text) >= 200:  # Smaller minimum for last chunk
                chunks.append(chunk_text)
        
        return chunks if chunks else []
    
    def extract_relevant_sections(self, text: str, keywords: List[str]) -> List[str]:
        """Extract sections containing specific keywords"""
        sections = []
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            if any(keyword.lower() in sentence.lower() for keyword in keywords):
                sections.append(sentence.strip())
        
        return sections
