"""Check indexing status of regulations"""
import pandas as pd
from database import RegulationDB
from config import SOURCES_FILE

# Check Excel file
print("=" * 60)
print("CHECKING EXCEL FILE")
print("=" * 60)
df = pd.read_excel(SOURCES_FILE, engine='openpyxl')
print(f"Total sources in Excel: {len(df)}")
print(f"\nColumns: {list(df.columns)}")

# Check for ESA
print("\n" + "=" * 60)
print("CHECKING FOR ESA SOURCES")
print("=" * 60)
esa_mask = df.astype(str).apply(lambda x: x.str.contains('ESA', case=False, na=False)).any(axis=1)
esa_sources = df[esa_mask]
print(f"Found {len(esa_sources)} sources with 'ESA'")
if len(esa_sources) > 0:
    print("\nESA Sources:")
    for idx, row in esa_sources.iterrows():
        source_name = str(row.get('source_name', row.get('Source Name', 'N/A')))
        category = str(row.get('category', row.get('Regulation Category', 'N/A')))
        hyperlink = str(row.get('hyperlink', row.get('URL', 'N/A')))
        if hyperlink != 'N/A' and len(hyperlink) > 80:
            hyperlink = hyperlink[:80] + "..."
        print(f"  - {source_name} | {category} | {hyperlink}")

# Check for Dallas Rent Control
print("\n" + "=" * 60)
print("CHECKING FOR DALLAS RENT CONTROL")
print("=" * 60)
dallas_mask = df.astype(str).apply(lambda x: x.str.contains('rent control|dallas', case=False, na=False)).any(axis=1)
dallas_sources = df[dallas_mask]
print(f"Found {len(dallas_sources)} Dallas Rent Control sources")
if len(dallas_sources) > 0:
    for idx, row in dallas_sources.iterrows():
        source_name = str(row.get('source_name', row.get('Source Name', 'N/A')))
        hyperlink = str(row.get('hyperlink', row.get('URL', 'N/A')))
        if hyperlink != 'N/A' and len(hyperlink) > 80:
            hyperlink = hyperlink[:80] + "..."
        print(f"  - {source_name} | {hyperlink}")

# Check database
print("\n" + "=" * 60)
print("CHECKING DATABASE")
print("=" * 60)
db = RegulationDB()
all_regs = db.get_all_regulations()
print(f"Total regulations in database: {len(all_regs)}")

# Check indexed (has content_hash)
indexed = [r for r in all_regs if r.get('content_hash')]
print(f"Indexed regulations (has hash): {len(indexed)}")
print(f"Unindexed regulations: {len(all_regs) - len(indexed)}")

# Check ESA in database
esa_regs = [r for r in all_regs if 'ESA' in str(r.get('source_name', '')).upper() or 'ESA' in str(r.get('category', '')).upper()]
print(f"\nESA regulations in database: {len(esa_regs)}")
for reg in esa_regs:
    has_hash = "INDEXED" if reg.get('content_hash') else "NOT INDEXED"
    print(f"  - {reg['source_name']} | {has_hash}")

# Check Dallas in database
dallas_regs = [r for r in all_regs if 'Dallas' in str(r.get('source_name', '')) or 'dallas' in str(r.get('url', '')).lower()]
print(f"\nDallas regulations in database: {len(dallas_regs)}")
for reg in dallas_regs:
    has_hash = "INDEXED" if reg.get('content_hash') else "NOT INDEXED"
    print(f"  - {reg['source_name']} | {has_hash}")

