"""Check and fix source indexing issues"""
import pandas as pd
from database import RegulationDB
from config import SOURCES_FILE

print("=" * 60)
print("Checking Sources and Database Status")
print("=" * 60)

# Check Excel file
print("\n1. Checking Excel file...")
df = pd.read_excel(SOURCES_FILE, engine='openpyxl')
print(f"   Total sources in Excel: {len(df)}")

# Check for ESA sources
esa_sources = df[df.apply(lambda row: 'esa' in str(row).lower() or 'emotional support' in str(row).lower() or 'assistance animal' in str(row).lower(), axis=1)]
print(f"   ESA-related sources: {len(esa_sources)}")
if len(esa_sources) > 0:
    print("   ESA sources found:")
    for idx, row in esa_sources.iterrows():
        print(f"     - {row.get('source_name', 'Unknown')} ({row.get('category', 'N/A')})")

# Check for Dallas test source
dallas_test = df[df['source_name'].str.contains('Dallas Rent Control', case=False, na=False)]
print(f"\n   Dallas test source: {len(dallas_test)}")
if len(dallas_test) > 0:
    for idx, row in dallas_test.iterrows():
        print(f"     - {row.get('source_name')}")
        print(f"       URL: {row.get('hyperlink', 'N/A')[:80]}...")

# Check database
print("\n2. Checking database...")
db = RegulationDB()
regs = db.get_all_regulations()
print(f"   Total regulations in database: {len(regs)}")

indexed = [r for r in regs if r.get('content_hash')]
not_indexed = [r for r in regs if not r.get('content_hash')]
print(f"   Indexed (have hash): {len(indexed)}")
print(f"   Not indexed (no hash): {len(not_indexed)}")

# Check for Dallas test in database
dallas_in_db = [r for r in regs if 'dallas' in r.get('source_name', '').lower() or 'rent control' in r.get('source_name', '').lower()]
print(f"\n   Dallas regulations in database: {len(dallas_in_db)}")
for r in dallas_in_db:
    has_hash = r.get('content_hash') is not None
    print(f"     - {r.get('source_name')}: indexed={has_hash}")

# Check for ESA in database
esa_in_db = [r for r in regs if 'esa' in r.get('source_name', '').lower() or 'emotional support' in r.get('source_name', '').lower()]
print(f"\n   ESA regulations in database: {len(esa_in_db)}")
for r in esa_in_db:
    has_hash = r.get('content_hash') is not None
    print(f"     - {r.get('source_name')}: indexed={has_hash}")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Excel sources: {len(df)}")
print(f"Database regulations: {len(regs)}")
print(f"Indexed in vector store: {len(indexed)}")
print(f"Need indexing: {len(not_indexed)}")

if len(not_indexed) > 0:
    print("\n⚠️  Some regulations need to be indexed!")
    print("   Go to Settings page and click 'Re-Index All Regulations'")
else:
    print("\n✅ All regulations appear to be indexed!")

