"""
Vector store module using ChromaDB for regulation embeddings
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import openai
from config import OPENAI_API_KEY, OPENAI_MODEL, VECTOR_DB_PATH
from retrieval_config import (
    enhance_query_with_terminology, 
    rerank_results, 
    filter_by_geography,
    calculate_source_reliability
)
import hashlib

class RegulationVectorStore:
    def __init__(self, db_path: str = VECTOR_DB_PATH, use_free_embeddings: bool = True):
        """
        Initialize ChromaDB client and collection.

        Newer versions of Chroma use a tenant/database model and can raise:
        ValueError: \"Could not connect to tenant default_tenant. Are you sure it exists?\"

        To be compatible across versions and avoid tenant issues, prefer the
        Settings-based client with a persistent DuckDB+Parquet backend. Fall
        back to PersistentClient only if needed.
        """
        try:
            # Preferred initialization for newer Chroma versions
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=db_path,
                anonymized_telemetry=False,
            ))
        except Exception:
            # Fallback for older versions that expect PersistentClient
            self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name="regulations",
            metadata={"hnsw:space": "cosine"}
        )
        self.use_free_embeddings = use_free_embeddings
        self.embedding_model = None
        
        # Initialize free embedding model if using free embeddings
        if use_free_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                # Using a lightweight, fast model that works well for legal text.
                # Force CPU device to avoid PyTorch meta-tensor issues on some setups.
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
                print("Using free embeddings (Sentence Transformers, CPU)")
            except ImportError:
                print("Warning: sentence-transformers not installed. Install with: pip install sentence-transformers")
                self.use_free_embeddings = False
            except Exception as e:
                # If anything goes wrong initializing the free model (e.g. PyTorch/meta tensor bugs),
                # fall back to non-free embeddings so the app can still start.
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
            # Fallback to OpenAI (requires API key and credits)
            try:
                from openai import OpenAI
                if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
                    print("Warning: OpenAI API key not configured. Using free embeddings instead.")
                    # Try to initialize free model if not already done
                    if not self.embedding_model:
                        from sentence_transformers import SentenceTransformer
                        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                        self.use_free_embeddings = True
                        return self.create_embedding(text)  # Retry with free model
                    return None
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                return response.data[0].embedding
            except Exception as e:
                print(f"Error creating OpenAI embedding: {str(e)}")
                # Try free model as fallback
                if not self.embedding_model:
                    try:
                        from sentence_transformers import SentenceTransformer
                        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                        self.use_free_embeddings = True
                        return self.create_embedding(text)  # Retry with free model
                    except:
                        pass
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
    
    def search(self, query: str, n_results: int = 5, 
               category_filter: Optional[str] = None,
               context: Optional[Dict] = None,
               prioritize_reliable: bool = True,
               filter_geography: Optional[str] = None) -> List[Dict]:
        """
        Enhanced search with query enhancement, source prioritization, and reranking
        
        Args:
            query: Search query
            n_results: Number of results to return
            category_filter: Filter by category (deprecated, use where clause)
            context: Context dict with 'city' and other info
            prioritize_reliable: Whether to prioritize authoritative sources
            filter_geography: City name to filter by (e.g., "Dallas")
        """
        try:
            # Enhance query with legal terminology
            enhanced_query = enhance_query_with_terminology(query, context)
            
            # Create query embedding from enhanced query
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
                # If ChromaDB is corrupted, return empty results and log error
                error_msg = str(db_error)
                if "hnsw" in error_msg.lower() or "index" in error_msg.lower() or "corrupt" in error_msg.lower():
                    print(f"Warning: ChromaDB index error detected. The database may need to be rebuilt. Error: {error_msg}")
                    # Return empty results instead of crashing
                    return []
                else:
                    # Re-raise other errors
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
            # Catch any other errors and return empty results
            print(f"Error in vector search: {str(e)}")
            return []
    
    def delete_regulation(self, regulation_id: str):
        """Delete all chunks for a regulation"""
        # Get all chunks for this regulation
        results = self.collection.get(
            where={"regulation_id": regulation_id}
        )
        if results['ids']:
            self.collection.delete(ids=results['ids'])
