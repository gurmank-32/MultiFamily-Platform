import pandas as pd
from config import SOURCES_FILE

def add_missing_sources():
    try:
        df = pd.read_excel(SOURCES_FILE, engine='openpyxl')
    except FileNotFoundError:
        print(f"Error: {SOURCES_FILE} not found.")
        return
    
    new_sources = [
        {
            'Source Name': 'Texas Assistance Animal Housing Law',
            'URL': 'https://gov.texas.gov/organization/disabilities/assistance_animals',
            'Type': 'State',
            'Regulation Category': 'ESA'
        },
        {
            'Source Name': 'HUD Housing Programs',
            'URL': 'https://www.hud.gov/topics/rental_assistance',
            'Type': 'Federal',
            'Regulation Category': 'HUD'
        }
    ]
    
    existing_urls = df['URL'].tolist() if 'URL' in df.columns else []
    to_add = [s for s in new_sources if s['URL'] not in existing_urls]
    
    if to_add:
        new_df = pd.DataFrame(to_add)
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_excel(SOURCES_FILE, index=False, engine='openpyxl')
        print(f"Added {len(to_add)} new sources:")
        for source in to_add:
            print(f"  - {source['Source Name']}: {source['URL']}")
    else:
        print("All sources already exist in the Excel file.")

if __name__ == "__main__":
    add_missing_sources()

