# How to Update Sources (sources.csv)

## Quick Answer

**No, you don't need to "reupload" anything!** Just:

1. **Edit `sources.csv`** - Add/modify/remove hyperlinks
2. **Click "Load Regulations from CSV"** in Settings page
3. **Done!** The system automatically scrapes and indexes new sources

## Step-by-Step Process

### 1. Edit sources.csv

Open `sources.csv` in Excel or any text editor and:
- **Add new rows** with new hyperlinks
- **Modify existing rows** to update URLs or categories
- **Delete rows** to remove sources

**CSV Format:**
```csv
Source Name,URL,Type,Regulation Category
Dallas Rent Control,https://dallas.gov/rent-control,Web,Rent Caps
New Source,https://example.com/new-law,Web,ESA
```

### 2. Load from CSV

1. Open the app
2. Go to **Settings** page (sidebar)
3. Click **"📥 Load Regulations from CSV"** button
4. Wait for processing (shows progress)

### 3. What Happens Automatically

The system will:
- ✅ Read all URLs from `sources.csv`
- ✅ Add new regulations to database
- ✅ **Automatically scrape content** from new URLs
- ✅ **Automatically index** in vector store (for search)
- ✅ Skip invalid URLs (shows count)

### 4. Verify

- Check **Regulation Explorer** page to see all loaded regulations
- Try asking a question related to your new sources
- Check if new sources appear in search results

## Important Notes

### New Sources
- **Automatically scraped** when you click "Load Regulations from CSV"
- **Automatically indexed** in vector store
- **Ready to use immediately** after loading

### Existing Sources
- If you **modify** a URL in CSV, it updates the database entry
- If you **change** category, it updates the category
- Content is **re-scraped** if the URL changed

### Local Files
- Supports local file paths (e.g., `C:\path\to\file.html`)
- Supports `file://` URLs
- Automatically detected and processed

## Troubleshooting

### Sources Not Appearing?
1. Check if URLs are valid (start with `http://`, `https://`, or are valid file paths)
2. Check if URLs are accessible (not blocked, not 404)
3. Check the "skipped" count in the success message

### Content Not Indexed?
1. Click **"🔄 Re-Index All Regulations"** button
2. This re-scrapes and re-indexes everything
3. Useful if vector store was cleared

### Need to Remove Sources?
1. Delete the row from `sources.csv`
2. Click "Load Regulations from CSV"
3. The old source stays in database but won't be updated
4. (Future: Add delete functionality)

## Best Practices

1. **Backup your CSV**: Keep a backup before making changes
2. **Test URLs**: Make sure URLs are accessible before adding
3. **Use categories**: Assign proper categories for better organization
4. **Check regularly**: Use "Check for Updates" to detect changes
5. **Monitor skipped**: If many sources are skipped, check URL validity

## Example Workflow

```
1. Edit sources.csv
   - Add: "Texas Property Code,https://texas.gov/property-code,Web,State Housing Rules"
   
2. Save sources.csv

3. Open app → Settings page

4. Click "Load Regulations from CSV"
   - Shows: "✅ Regulations loaded! (1 loaded, 0 skipped)"
   - Shows: "🔄 Now scraping content and indexing..."
   - Shows: "✅ Indexed 1 new regulation(s) in vector store!"

5. Done! New source is ready to use
```

## Summary

- ✅ **No reupload needed** - Just edit CSV and click "Load"
- ✅ **Automatic scraping** - Content fetched automatically
- ✅ **Automatic indexing** - Added to vector store automatically
- ✅ **Ready immediately** - Can use new sources right away

