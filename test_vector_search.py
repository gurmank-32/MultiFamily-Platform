"""Test vector store search functionality"""
from vector_store import RegulationVectorStore
from qa_system import QASystem

print("Testing Vector Store Search")
print("=" * 60)

# Test 1: Direct vector store search
print("\n1. Testing direct vector store search for 'Dallas rent'...")
try:
    vs = RegulationVectorStore()
    results = vs.search(query="Dallas rent increase limit 250", n_results=5)
    print(f"   Found {len(results)} results")
    if results:
        for i, r in enumerate(results[:3], 1):
            print(f"\n   Result {i}:")
            print(f"     Source: {r['metadata'].get('source_name', 'Unknown')}")
            print(f"     URL: {r['metadata'].get('url', 'N/A')[:80]}...")
            print(f"     Content preview: {r['document'][:150]}...")
    else:
        print("   No results found!")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: QA System search
print("\n2. Testing QA System search for 'What is new law in Dallas?'...")
try:
    qa = QASystem()
    result = qa.answer_question("What is new law in Dallas?")
    print(f"   Has information: {result.get('has_information', False)}")
    print(f"   Answer length: {len(result.get('answer', ''))}")
    print(f"   Sources: {len(result.get('sources', []))}")
    if result.get('answer'):
        print(f"   Answer preview: {result['answer'][:200]}...")
    if result.get('sources'):
        for src in result['sources'][:3]:
            print(f"     - {src.get('source', 'Unknown')}: {src.get('url', 'N/A')[:60]}...")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: ESA search
print("\n3. Testing search for 'What is ESA?'...")
try:
    qa = QASystem()
    result = qa.answer_question("What is ESA?")
    print(f"   Has information: {result.get('has_information', False)}")
    print(f"   Answer length: {len(result.get('answer', ''))}")
    print(f"   Sources: {len(result.get('sources', []))}")
    if result.get('answer'):
        print(f"   Answer preview: {result['answer'][:200]}...")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete!")
