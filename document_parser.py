"""
Document parser for lease documents (PDF, DOCX)
"""
import PyPDF2
import re
from docx import Document
from typing import List, Dict, Optional
import io

class DocumentParser:
    def __init__(self):
        pass
    
    def parse_document(self, file_content: bytes, filename: str) -> Dict:
        """Parse document and extract text"""
        file_ext = filename.lower().split('.')[-1]
        
        if file_ext == 'pdf':
            return self.parse_pdf(file_content)
        elif file_ext in ['docx', 'doc']:
            return self.parse_docx(file_content)
        else:
            raise ValueError(f"Unsupported file type: {file_ext}")
    
    def parse_pdf(self, file_content: bytes) -> Dict:
        """Parse PDF file"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            pages = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text + "\n"
                pages.append({
                    "page": page_num + 1,
                    "text": page_text
                })
            
            return {
                "text": text,
                "pages": pages,
                "total_pages": len(pages)
            }
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {str(e)}")
    
    def parse_docx(self, file_content: bytes) -> Dict:
        """Parse DOCX file"""
        try:
            doc_file = io.BytesIO(file_content)
            doc = Document(doc_file)
            
            text = ""
            paragraphs = []
            
            for para in doc.paragraphs:
                para_text = para.text.strip()
                if para_text:
                    text += para_text + "\n"
                    paragraphs.append(para_text)
            
            return {
                "text": text,
                "paragraphs": paragraphs,
                "total_paragraphs": len(paragraphs)
            }
        except Exception as e:
            raise ValueError(f"Error parsing DOCX: {str(e)}")
    
    def extract_clauses(self, text: str) -> List[Dict]:
        """Extract clauses from lease document"""
        clauses = []
        
        # Split by common clause markers
        clause_patterns = [
            r'\n\s*\d+[\.\)]\s+',  # Numbered clauses (1. 2. etc.)
            r'\n\s*[A-Z][A-Z\s]+\s*\n',  # ALL CAPS headings
            r'\n\s*Section\s+\d+',  # Section markers
            r'\n\s*ARTICLE\s+\d+',  # Article markers
        ]
        
        # Try to split by numbered clauses first
        import re
        parts = re.split(r'\n\s*\d+[\.\)]\s+', text)
        
        for i, part in enumerate(parts):
            if part.strip():
                # Try to extract clause title
                lines = part.strip().split('\n')
                title = lines[0][:100] if lines else f"Clause {i+1}"
                content = '\n'.join(lines)
                
                clauses.append({
                    "number": i + 1,
                    "title": title,
                    "content": content,
                    "full_text": part.strip()
                })
        
        # If no numbered clauses found, split by paragraphs
        if len(clauses) <= 1:
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            clauses = [
                {
                    "number": i + 1,
                    "title": para[:100],
                    "content": para,
                    "full_text": para
                }
                for i, para in enumerate(paragraphs)
            ]
        
        return clauses
