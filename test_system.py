"""
Test script to verify system components
"""
import os
from config import OPENAI_API_KEY
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore

def test_database():
    """Test database functionality"""
    print("Testing database...")
    db = RegulationDB()
    db.add_regulation(
        source_name="Test Source",
        url="https://example.com",
        type="Test",
        category="Test Category"
    )
    regulations = db.get_all_regulations()
    print(f"✓ Database test passed. Found {len(regulations)} regulations")
    return True

def test_scraper():
    """Test web scraper"""
    print("Testing scraper...")
    scraper = RegulationScraper()
    result = scraper.fetch_url_content("https://www.example.com")
    if result:
        print(f"✓ Scraper test passed. Fetched {result['length']} characters")
        return True
    else:
        print("⚠ Scraper test failed (may be due to network)")
        return False

def test_vector_store():
    """Test vector store"""
    print("Testing vector store...")
    try:
        vs = RegulationVectorStore()
        # Test embedding
        embedding = vs.create_embedding("Test text for embedding")
        if embedding and len(embedding) > 0:
            print(f"✓ Vector store test passed. Embedding dimension: {len(embedding)}")
            return True
        else:
            print("⚠ Vector store test failed")
            return False
    except Exception as e:
        print(f"⚠ Vector store test error: {str(e)}")
        return False

def test_config():
    """Test configuration"""
    print("Testing configuration...")
    if OPENAI_API_KEY:
        print("✓ OpenAI API key configured")
    else:
        print("⚠ OpenAI API key not set (set OPENAI_API_KEY in .env)")
    
    return True

def main():
    print("=" * 50)
    print("Housing Regulation Compliance Agent - System Test")
    print("=" * 50)
    print()
    
    results = []
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))
    results.append(("Scraper", test_scraper()))
    results.append(("Vector Store", test_vector_store()))
    
    print()
    print("=" * 50)
    print("Test Summary:")
    print("=" * 50)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r[1] for r in results)
    if all_passed:
        print("\n✓ All critical tests passed!")
    else:
        print("\n⚠ Some tests failed or had warnings. Check output above.")

if __name__ == "__main__":
    main()
