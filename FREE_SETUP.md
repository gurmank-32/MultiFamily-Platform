# Free Setup Instructions

## ✅ Good News!

I've modified the code to work **completely FREE** for most features!

## What Changed

1. **Free Embeddings**: Now uses Hugging Face's Sentence Transformers (completely free)
2. **Graceful Fallback**: If OpenAI API isn't available, it uses free alternatives
3. **Manual Review Mode**: Compliance checking suggests manual review if no API

## Install Free Dependencies

Run this command to install the free embedding library:

```bash
pip install sentence-transformers torch
```

This will download a free AI model that runs on your computer (no API needed).

## What Works for FREE

✅ **Vector Search** - Semantic search of regulations (FREE)
✅ **Regulation Browsing** - View and explore regulations (FREE)
✅ **Document Parsing** - Parse PDF/DOCX files (FREE)
✅ **Update Detection** - Detect when regulations change (FREE)
✅ **Basic Compliance** - Manual review suggestions (FREE)

⚠️ **Advanced Compliance** - Detailed AI analysis (requires API, but you can do manual review)

## How to Use

1. **Install free dependencies:**
   ```bash
   pip install sentence-transformers torch
   ```

2. **Restart the app:**
   ```bash
   streamlit run app.py
   ```

3. **Use the app!** Most features work without any API key.

## For Compliance Checking

You have two options:

### Option 1: Manual Review (FREE)
- Upload your lease document
- The app will find relevant regulations
- You review clauses manually against regulations
- No API needed!

### Option 2: AI Analysis (Requires API)
- If you want AI-powered compliance checking
- You'll need to add OpenAI credits
- But you can use the app for everything else without paying!

## Next Steps

1. Install: `pip install sentence-transformers torch`
2. Restart the app
3. Start using it - most features work for free!

The app will automatically use free embeddings instead of OpenAI when possible.
