"""
Helper script to load and index a single source from sources.csv.
Used for quick demos without re-indexing everything.
"""

import pandas as pd
from database import RegulationDB
from scraper import RegulationScraper
from vector_store import RegulationVectorStore
from config import SOURCES_FILE


def index_single_source(source_name_match: str):
    """Load and index a single source whose Source Name contains source_name_match."""
    db = RegulationDB()
    scraper = RegulationScraper()
    vector_store = RegulationVectorStore()

    print(f"Reading sources from {SOURCES_FILE} ...")
    df = pd.read_csv(SOURCES_FILE)

    # Normalize columns
    df.columns = [c.strip() for c in df.columns]

    if "Source Name" not in df.columns or "URL" not in df.columns:
        raise ValueError("sources.csv must contain 'Source Name' and 'URL' columns")

    # Find matching row(s)
    mask = df["Source Name"].str.contains(source_name_match, case=False, na=False)
    matches = df[mask]

    if matches.empty:
        print(f"No sources found matching: {source_name_match}")
        return

    for _, row in matches.iterrows():
        source_name = str(row["Source Name"]).strip()
        url = str(row["URL"]).strip()
        category = str(row.get("Regulation Category", "Other")).strip()
        type_ = str(row.get("Type", "")).strip()

        print(f"\nIndexing single source: {source_name}")
        print(f"URL: {url}")

        # Check if already in DB
        existing = db.get_regulation_by_url(url)
        if existing:
            reg_id = existing["id"]
            print(f"Already in database (id={reg_id}), re-indexing chunks...")
        else:
            reg_id = db.add_regulation(
                source_name=source_name,
                url=url,
                type=type_,
                category=category,
            )
            print(f"Added to database with id={reg_id}")

        # Fetch content (supports local HTML and web)
        content_obj = scraper.fetch_url_content(url)
        if not content_obj or not content_obj.get("content"):
            print("Failed to fetch content; nothing indexed.")
            continue

        text = content_obj["content"]
        chunks = scraper.chunk_text(text)
        if not chunks:
            print("No chunks created; nothing indexed.")
            continue

        vector_store.add_regulation_chunks(
            regulation_id=str(reg_id),
            source_name=source_name,
            url=url,
            category=category,
            chunks=chunks,
        )

        # Save hash
        db.update_regulation_hash(url, content_obj["hash"])

        print(f"Indexed {len(chunks)} chunks for {source_name}")


if __name__ == "__main__":
    # Default to the Dallas Section 8 demo source
    index_single_source("Dallas Section 8")


