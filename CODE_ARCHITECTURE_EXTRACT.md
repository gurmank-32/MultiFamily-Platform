# Code Architecture - 5 Key Components

## 1️⃣ Excel Source File Loading

**File:** `database.py`  
**Method:** `load_regulations_from_csv()`  
**File Path:** `finalsource11.xlsx` (defined in `config.py`)

```python
# config.py
SOURCES_FILE = "finalsource11.xlsx"

# database.py - load_regulations_from_csv()
def load_regulations_from_csv(self, csv_path: str):
    """Load regulations from CSV or Excel file - REQUIRED: sources.xlsx with columns: category, city, level, hyperlink"""
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
    
    # REQUIRED COLUMNS: category, level, hyperlink (city is optional, defaults to Texas-Statewide)
    required_columns = ['category', 'level', 'hyperlink']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValueError(f"Missing required columns in sources file: {', '.join(missing_columns)}")
    
    # DataFrame structure:
    # - category: str (e.g., "ESA", "Rent Control", "HUD")
    # - city: str (e.g., "Dallas", "Austin", "Federal", "Texas-Statewide")
    # - level: str (e.g., "Federal", "State", "City")
    # - hyperlink: str (URL or file path)
    # - source_name: str (optional, auto-generated if missing)
    
    for _, row in df.iterrows():
        url = str(row.get("hyperlink", "")).strip()
        category = str(row.get("category", "")).strip()
        city = str(row.get("city", "Texas-Statewide")).strip() if "city" in df.columns else "Texas-Statewide"
        level = str(row.get("level", "")).strip()
        source_name = str(row.get("source_name", "")).strip()
        
        # Add to database...
```

---

## 2️⃣ Web Scraping / Content Ingestion

**File:** `scraper.py`  
**Class:** `RegulationScraper`  
**Method:** `fetch_url_content()`

```python
import requests
from bs4 import BeautifulSoup
import PyPDF2  # For PDF support
import hashlib
import re

class RegulationScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_url_content(self, url: str) -> Optional[Dict]:
        """Fetch and extract text content from URL or file path"""
        try:
            is_pdf = False
            content = None
            
            # Handle file:// URLs or local file paths
            if url.startswith('file://'):
                file_path = url.replace('file:///', '').replace('file://', '')
                file_path = file_path.replace('/', '\\')  # Windows paths
                
                if file_path.lower().endswith('.pdf'):
                    # Handle PDF files
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
                    content_hash = hashlib.sha256(text.encode()).hexdigest()
                    
                    return {
                        "url": url,
                        "content": text,
                        "hash": content_hash,
                        "length": len(text)
                    }
                else:
                    # Handle HTML files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
            
            elif url.startswith(('http://', 'https://')):
                # Web URL - fetch with requests
                response = self.session.get(url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Check if it's a PDF
                content_type = response.headers.get('Content-Type', '').lower()
                is_pdf = url.lower().endswith('.pdf') or 'application/pdf' in content_type
                
                # Check if it's a Canva site (JavaScript-rendered)
                is_canva = 'canva.site' in url.lower() or 'canva.com' in url.lower()
                
                if is_canva:
                    # Extract from script tags for Canva sites
                    soup = BeautifulSoup(response.text, 'html.parser')
                    scripts = soup.find_all('script')
                    all_text = ""
                    for script in scripts:
                        if script.string and ('landlords' in script.string.lower() or 'rent' in script.string.lower()):
                            sentences = re.findall(r'[A-Z][^.!?]*[.!?]', script.string)
                            if sentences:
                                all_text += ' '.join(sentences) + " "
                    # ... extract content from HTML
                
                elif is_pdf:
                    # Handle PDF from URL
                    pdf_content = response.content
                    pdf_file = io.BytesIO(pdf_content)
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    content = text
                else:
                    # Handle HTML content
                    content = response.text
            
            # Parse HTML with BeautifulSoup
            if not is_pdf and content:
                soup = BeautifulSoup(content, 'html.parser')
                
                # Find main content (article, main tags, or largest div)
                main_content = None
                for tag_name in ['article', 'main']:
                    tag = soup.find(tag_name)
                    if tag and len(tag.get_text(strip=True)) > 200:
                        main_content = tag
                        break
                
                if not main_content:
                    # Find largest div with substantial content
                    all_divs = soup.find_all('div')
                    largest_div = None
                    largest_size = 0
                    for div in all_divs:
                        text_len = len(div.get_text(strip=True))
                        if text_len > 500:
                            # Skip navigation
                            div_class = ' '.join(div.get('class', [])).lower()
                            skip_keywords = ['nav', 'menu', 'sidebar', 'footer', 'header']
                            if not any(kw in div_class for kw in skip_keywords):
                                if text_len > largest_size:
                                    largest_size = text_len
                                    largest_div = div
                    if largest_div:
                        main_content = largest_div
                
                # Extract text from main content
                if main_content:
                    for element in main_content(["script", "style"]):
                        element.decompose()
                    text = main_content.get_text(separator=' ')
                else:
                    # Fallback: remove navigation from whole page
                    for element in soup(["script", "style", "nav", "footer", "header"]):
                        element.decompose()
                    text = soup.get_text(separator=' ')
                
                # Clean text
                text = re.sub(r'https?://[^\s]+', '', text)
                text = re.sub(r'\s+', ' ', text).strip()
            
            # Calculate hash
            content_hash = hashlib.sha256(text.encode()).hexdigest()
            
            return {
                "url": url,
                "content": text,
                "hash": content_hash,
                "length": len(text)
            }
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        # Implementation for chunking text...
```

---

## 3️⃣ Embedding + Vector Database Setup

**File:** `vector_store.py`  
**Class:** `RegulationVectorStore`  
**Database:** ChromaDB (DuckDB + Parquet backend)  
**Embedding Model:** Sentence Transformers `all-MiniLM-L6-v2` (free) or OpenAI `text-embedding-3-small` (paid)

```python
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

class RegulationVectorStore:
    def __init__(self, db_path: str = "./chroma_db", use_free_embeddings: bool = True):
        """
        Initialize ChromaDB client and collection.
        Uses DuckDB+Parquet backend for persistence.
        """
        try:
            # Preferred initialization for newer Chroma versions
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=db_path,
                anonymized_telemetry=False,
            ))
        except Exception:
            # Fallback for older versions
            self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="regulations",
            metadata={"hnsw:space": "cosine"}  # Cosine similarity
        )
        
        self.use_free_embeddings = use_free_embeddings
        self.embedding_model = None
        
        # Initialize free embedding model (Sentence Transformers)
        if use_free_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                # Using lightweight, fast model for legal text
                # Force CPU device to avoid PyTorch meta-tensor issues
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                print("Using free embeddings (Sentence Transformers, CPU)")
            except ImportError:
                print("Warning: sentence-transformers not installed")
                self.use_free_embeddings = False
            except Exception as e:
                print(f"Warning: could not initialize free embedding model: {e}")
                self.embedding_model = None
                self.use_free_embeddings = False
    
    def create_embedding(self, text: str) -> List[float]:
        """Create embedding using free model or OpenAI"""
        if self.use_free_embeddings and self.embedding_model:
            try:
                # Use free sentence transformers model
                embedding = self.embedding_model.encode(text, convert_to_numpy=True).tolist()
                return embedding
            except Exception as e:
                print(f"Error creating free embedding: {str(e)}")
                return None
        else:
            # Fallback to OpenAI (requires API key)
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"Error creating OpenAI embedding: {str(e)}")
                return None
    
    def add_regulation_chunks(self, regulation_id: str, source_name: str, 
                             url: str, category: str, chunks: List[str]):
        """Add regulation chunks to vector store"""
        if not chunks:
            return
        
        embeddings = []
        ids = []
        metadatas = []
        documents = []
        
        for i, chunk in enumerate(chunks):
            embedding = self.create_embedding(chunk)
            if embedding:
                chunk_id = f"{regulation_id}_{i}"
                ids.append(chunk_id)
                embeddings.append(embedding)
                metadatas.append({
                    "source_name": source_name,
                    "url": url,
                    "category": category,
                    "chunk_index": i
                })
                documents.append(chunk)
        
        if ids:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                metadatas=metadatas,
                documents=documents
            )
```

**Configuration:**
- **Vector DB Path:** `./chroma_db` (defined in `config.py`)
- **Similarity Metric:** Cosine similarity
- **Embedding Dimensions:** 384 (all-MiniLM-L6-v2) or 1536 (OpenAI)

---

## 4️⃣ Retrieval Code (Search / Similarity Matching)

**File:** `vector_store.py` + `qa_system.py`  
**Method:** `search()` in `RegulationVectorStore`  
**Method:** `answer_question()` in `QASystem`

```python
# vector_store.py
def search(self, query: str, n_results: int = 5, 
           category_filter: Optional[str] = None,
           context: Optional[Dict] = None,
           prioritize_reliable: bool = True,
           filter_geography: Optional[str] = None) -> List[Dict]:
    """
    Enhanced search with query enhancement, source prioritization, and reranking
    """
    try:
        # Enhance query with legal terminology (from retrieval_config.py)
        enhanced_query = enhance_query_with_terminology(query, context)
        
        # Create query embedding
        query_embedding = self.create_embedding(enhanced_query)
        if not query_embedding:
            return []
        
        # Get more results initially for reranking (2x requested)
        initial_n = n_results * 2 if prioritize_reliable else n_results
        
        # Build where clause for filtering
        where = {}
        if category_filter:
            where["category"] = category_filter
        
        # Search with enhanced query - handle ChromaDB corruption gracefully
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=initial_n,
                where=where if where else None
            )
        except Exception as db_error:
            # If ChromaDB is corrupted, return empty results
            error_msg = str(db_error)
            if "hnsw" in error_msg.lower() or "index" in error_msg.lower():
                print(f"Warning: ChromaDB index error detected. Error: {error_msg}")
                return []
            else:
                raise
        
        # Format results
        formatted_results = []
        if results['ids'] and len(results['ids'][0]) > 0:
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else 0.0
                })
        
        # Filter by geography if specified
        if filter_geography:
            formatted_results = filter_by_geography(formatted_results, filter_geography)
        
        # Rerank results if prioritizing reliable sources
        if prioritize_reliable and formatted_results:
            formatted_results = rerank_results(formatted_results, query, context)
        
        # Return top n_results
        return formatted_results[:n_results]
    except Exception as e:
        print(f"Error in vector search: {str(e)}")
        return []

# qa_system.py - answer_question()
def answer_question(self, question: str, city: str = None) -> Dict:
    """Answer a question using RAG from regulations"""
    
    # Detect key terms for strict filtering
    key_terms = {
        "hud": ["hud", "housing and urban development", "department of housing"],
        "esa": ["esa", "emotional support animal", "emotional support", "assistance animal"],
        "rent control": ["rent control", "rent cap", "rent limit"],
        # ... more terms
    }
    
    # Determine which key term is being asked about
    detected_key_term = None
    for term, keywords in key_terms.items():
        if any(kw in question.lower() for kw in keywords):
            detected_key_term = term
            break
    
    # Search with keyword-strict filtering
    if detected_key_term:
        strict_query = f"{detected_key_term} {question}"
        # Add synonyms for semantic matching
        if detected_key_term in synonym_mapping:
            synonyms = synonym_mapping[detected_key_term]
            strict_query = f"{strict_query} {' '.join(synonyms)}"
    else:
        strict_query = enhanced_query
    
    # Increase results for ESA/HUD to ensure we find relevant content
    n_search_results = 30 if detected_key_term in ["esa", "hud"] else 20
    
    search_results = self.vector_store.search(
        query=strict_query,
        n_results=n_search_results,
        context={"city": final_city},
        prioritize_reliable=True,
        filter_geography=final_city if final_city != "Texas-Statewide" else None
    )
    
    # KEYWORD-STRICT FILTERING: Filter results to only include chunks that mention the key term
    if detected_key_term:
        filtered_results = []
        key_term_keywords = key_terms[detected_key_term]
        
        for result in search_results:
            doc_lower = result['document'].lower()
            # Only include if document actually mentions the key term
            if any(kw in doc_lower for kw in key_term_keywords):
                # For ESA questions, exclude service animal content
                if detected_key_term == "esa":
                    service_animal_indicators = ["service animal", "service dog", "ada service", "trained to perform"]
                    is_service_animal_content = any(indicator in doc_lower for indicator in service_animal_indicators)
                    if not is_service_animal_content:
                        # Prioritize definition chunks
                        definition_keywords = ["emotional support animal", "esa is", "provides comfort"]
                        has_definition = any(dk in doc_lower for dk in definition_keywords)
                        if has_definition:
                            filtered_results.insert(0, result)  # Boost priority
                        else:
                            if "emotional support" in doc_lower or "esa" in doc_lower:
                                filtered_results.append(result)
                else:
                    filtered_results.append(result)
        
        search_results = filtered_results[:15]
    
    # Extract context and generate answer...
```

---

## 5️⃣ Agent/System Instructions (Prompt Template + RAG Guardrails)

**File:** `qa_system.py`  
**Method:** `_generate_llm_answer()`  
**Guardrails:** `guardrails_config.py`

```python
# guardrails_config.py
GUARDRAIL_RESPONSES = {
    "nonsense": "I'm here to assist with housing and leasing policies specifically for Texas cities...",
    "irrelevant": "I'm here to assist with housing and leasing policies specifically for Texas cities...",
    "out_of_scope_geography": "At this time, I only provide information on housing and leasing regulations within Dallas, Austin, Houston, and San Antonio, Texas...",
    "missing_information": "I apologize — I do not currently have this information in my data sources. Please check back later for updates.",
    # ... more responses
}

# qa_system.py - _generate_llm_answer()
def _generate_llm_answer(self, question: str, context: str, city: str) -> str:
    """Generate answer using OpenAI LLM - STRICT RULES"""
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""You are a Leasing Compliance Answer Assistant. You ONLY answer questions about HOUSING and LEASING compliance rules and policies in Dallas, Austin, Houston, and San Antonio, Texas.

DATA POLICY (STRICT MODE):
- You MUST cite at least one verifiable source from the provided Data Source (Excel hyperlinks and scraped text).
- If NO MATCHING SOURCE is found: respond with EXACT message: "I apologize — I do not currently have this information in my data sources. Please check back later for updates."
- NEVER use general model knowledge, speculation, assumptions, or outside content.
- NO fallback to public information or OpenAI knowledge
- NO mention of sources not present in Excel
- NO government encyclopedia content
- NO long prefaces or disclaimers outside guardrail rules

STRICT RULES (MANDATORY):
1. ONLY use information from the provided context chunks - NO outside knowledge
2. If information is NOT in the context, respond EXACTLY: "I apologize — I do not currently have this information in my data sources. Please check back later for updates."
3. DO NOT guess, hallucinate, or combine unrelated text
4. DO NOT use HUD/DOJ/ESA definitions from your own memory
5. DO NOT add "Applicable To" sections
6. DO NOT add legal disclaimers in the answer text
7. DO NOT dump menus, tags, or junk text from websites
8. DO NOT answer with general definitions not found in scraped data
9. DO NOT use prior model knowledge - ONLY scraped text
10. DO NOT copy long legal paragraphs - summarize concisely in plain language
11. NO emojis, NO hashtags, NO bold formatting

MANDATORY RESPONSE FORMAT (STRICT - Follow exactly):

[ANSWER]

Short, clear explanation in paragraphs using ONLY verified source content. Maximum 4-6 sentences. Be direct and factual. Use proper punctuation and complete sentences. Do NOT use bullet lists. Do NOT include sources or URLs in the answer text.

[SOURCES]

- Name: hyperlink

(Each source on a new line with format: - Source Name: https://url)

SPECIFIC TOPIC RULES:
- When answering "What is an ESA" or "What is ESA": You MUST start with "An Emotional Support Animal (ESA) is an animal that provides emotional or mental-health support to a person with a disability." Then explain: ESAs are not pets under housing law and must be allowed in rental housing as a reasonable accommodation when a tenant provides appropriate documentation. ESAs do not require specialized training like service animals, and landlords generally cannot charge pet rent or enforce breed and weight restrictions for them. Keep it brief (4-6 sentences).

- When answering "What is HUD": You MUST start with "HUD stands for the U.S. Department of Housing and Urban Development" and explain that it enforces national housing nondiscrimination laws, including ESA protections under the Fair Housing Act. HUD investigates complaints, issues fines for violations, and publishes official guidance that landlords and leasing teams must follow. Keep it brief (4-6 sentences).

- When answering "What is ESA Law in [City]": Start with "[City] does not have its own separate ESA ordinance" or similar, then explain that ESA rules come from federal Fair Housing Act requirements and HUD enforcement guidance, which apply statewide in Texas. Keep it brief (4-6 sentences).

CRITICAL ANSWER FORMAT RULES:
- ALWAYS start your answer with a complete sentence that directly answers the question using the question term (e.g., for "What is ESA?", start with "ESA is...")
- NEVER start with connecting words like "However", "But", "Also", "Additionally", "Furthermore"
- NEVER start mid-sentence or with a fragment from the middle of a paragraph
- Your first sentence must be a complete, standalone statement that answers "What is X?" using proper punctuation
- Make sure your answer is complete and ends with a proper sentence with correct punctuation
- Use proper punctuation throughout (periods, commas, etc.)
- Keep the answer concise - maximum 4-6 sentences total

Always assume audience is a leasing professional needing quick, concise compliance guidance. Write in a clear, professional, direct style with proper punctuation. Be brief and accurate.

Question: {question}
City Context: {city or 'Texas-Statewide'}

Scraped Text Chunks (ONLY use these - NO outside knowledge):
{clean_context[:5000]}

CRITICAL: If the scraped text chunks above do NOT contain information that directly answers the question, you MUST respond EXACTLY: "I apologize — I do not currently have this information in my data sources. Please check back later for updates."

SOURCE MATCH RULES:
- Perform semantic matching for synonyms:
  - ESA → "Assistance Animal"
  - HUD → "Fair Housing Act" or "Federal Housing"
  - Voucher → "Section 8"
  - Disability → "Reasonable Accommodation"
  - Pets → "Assistance Animal Notice"
  - Rent Cap → "Rent Stabilization / Tenant Protections"
- If a synonym is used but the root concept is present in data sources, USE IT.

Provide answer in the EXACT format specified above using ONLY the chunks above."""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a Leasing Compliance Answer Assistant. Provide clear, concise Texas housing law compliance guidance to leasing managers. Format: **Answer:** followed by a concise explanation in plain language (1-2 paragraphs, maximum 4-6 sentences total). No bullet lists. Only use information from provided chunks. Never use outside knowledge. Always start with the question term (e.g., 'ESA is...' for 'What is ESA?'). Use proper punctuation throughout. Make sure your answer is complete and ends with proper punctuation. If information is missing, say the missing message. Do not include URLs or source citations in the answer. Be concise and direct."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        max_tokens=400
    )
    
    answer = response.choices[0].message.content.strip()
    # Parse [ANSWER] and [SOURCES] sections...
    return answer
```

**Guardrail Logic:**
- **Geographic Scope:** Only Dallas, Austin, Houston, San Antonio, Texas
- **Topic Scope:** Only housing/leasing regulations
- **Missing Information:** Returns exact message if no matching source found
- **Legal Advice:** Disclaims legal advice requests
- **Irrelevant Topics:** Filters out non-housing questions

---

## Summary

1. **Excel Loading:** `database.py` → `load_regulations_from_csv()` → Reads `finalsource11.xlsx` with columns: `category`, `city`, `level`, `hyperlink`, `source_name`

2. **Scraping:** `scraper.py` → `RegulationScraper.fetch_url_content()` → Uses `requests` + `BeautifulSoup` for HTML, `PyPDF2` for PDFs, special handling for Canva sites

3. **Embeddings + Vector DB:** `vector_store.py` → ChromaDB with DuckDB+Parquet, Sentence Transformers `all-MiniLM-L6-v2` (free) or OpenAI embeddings (paid)

4. **Retrieval:** `vector_store.py` → `search()` with query enhancement, reranking, geography filtering + `qa_system.py` → `answer_question()` with keyword-strict filtering

5. **Agent Instructions:** `qa_system.py` → `_generate_llm_answer()` with strict RAG prompt + `guardrails_config.py` for guardrail responses

